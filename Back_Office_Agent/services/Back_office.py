from dataclasses import dataclass, field
from typing import cast
import openai
from openai.types import ChatModel
from dotenv import load_dotenv
from mcp import ClientSession
import json
from mcp.client.sse import sse_client
from mcp import ClientSession
import logging
from langfuse.callback import CallbackHandler
from langgraph.pregel import RetryPolicy
import os

RetryPolicy()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)


load_dotenv()

openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url=os.getenv("OPENAI_BASE_URL"))


@dataclass
class BankOffice:
    messages: list[ChatModel] = field(default_factory=list)
    MAX_MEMORY: int = 5

    system_prompt: str = """You are an expert underwriting agent. If the user enters some other messages which is not related to these tasks, answer the messages with your knowledge
    Your job is to assess the financial eligibility of loan applicants using tools for:
    - Bank Statement Analysis
    - Credit Score Check
    - GST Analysis
    - Risk Score Computation
    - Report Generation
    Use these tools as needed and provide a concise risk evaluation.
    When selecting a tool, explain:
        - Why you selected this tool
        - What inputs you’re using
        - What result you expect"""
  
    def __post_init__(self):
        self.messages.append({"role": "system", "content": self.system_prompt})
    
    def chat_history(self):
        system_msg = [msg for msg in self.messages if msg["role"] == "system"]
        user_assistant_msgs = [msg for msg in self.messages if msg["role"] in ("user", "assistant")]
        trimmed = user_assistant_msgs[-(self.MAX_MEMORY * 2):]  
        self.messages = system_msg + trimmed
    
    async def process_query(self, session: ClientSession, query: str) -> dict:
        response = await session.list_tools()
        logger.info("Successfully fetched tools")
        logger.debug(f"Available tools: {response.tools}")

        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                },
            }
            for tool in response.tools
        ]
        logger.debug(f"Prepared tool schemas: {available_tools}")

        res = await openai_client.chat.completions.create(
            model="llama3.1",
            messages=self.messages + [{"role": "user", "content": query}],
            tools=available_tools,
        )
        logger.info("Model response received")

        assistant_message_content = []

        for choice in res.choices:
            if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    result = await session.call_tool(tool_name, cast(dict, tool_args))
                    tool_result = result.content[0].text if result.content else "No response from tool."

                    assistant_message_content.append(
                        {
                            "tool_name": tool_name,
                            "args": tool_args,
                            "result": tool_result,
                            "explanation": f"Selected tool '{tool_name}' because it matches query intent. Arguments: {tool_args}"
                        }
                    )

                    self.messages.append({"role": "assistant", "content": json.dumps(assistant_message_content)})
                    self.chat_history()
                    self.messages.append({"role": "user", "content": tool_result})
                    self.chat_history()
            else:
                self.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                self.chat_history()

        return {
            "responses": assistant_message_content[0]["result"] if assistant_message_content else res.choices[0].message.content,
            "context": self.messages,
            "reasoning": assistant_message_content
        }


    async def run_query(self, query: str) -> dict:
        server_url = os.getenv("SSE_SERVER_URL")
        async with sse_client(url=server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                try:
                    await session.initialize()
                    return await self.process_query(session, query)
                except Exception as e:
                    print("Error during process_query:", str(e))

chat = BankOffice()