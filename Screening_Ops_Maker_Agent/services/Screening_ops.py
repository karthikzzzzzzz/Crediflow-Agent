import asyncio
from datetime import datetime
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.redis import RedisSaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from utils.schema import State
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode,tools_condition
from mcp.client.sse import sse_client
from mcp import ClientSession
from langgraph.pregel import RetryPolicy
from langfuse.callback import CallbackHandler
import os 
import uuid
from dotenv import load_dotenv

load_dotenv()


RetryPolicy()

langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
    session_id=str(uuid.uuid4())
)
predefined_run_id = str(uuid.uuid4())

class ScreeningOps:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("MODEL"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.timeout=3600
    

    async def process(self,session:ClientSession, request: str,memory):

        async with MultiServerMCPClient({
            "server": {
            "url": "http://127.0.0.1:9090/sse",
            "transport": "sse",
        }
        }) as client:
            with RedisSaver.from_conn_string(os.getenv("REDIS_URI")) as checkpointer:
                checkpointer.setup()
            
    
                graph_builder=StateGraph(State)

            
                agent = create_react_agent(self.llm,client.get_tools(),checkpointer=checkpointer)
                
                

                graph_builder.add_node("screening-agent",agent,retry=RetryPolicy(max_attempts=5))
                graph_builder.add_edge(START,"screening-agent")
                tool_node = ToolNode(tools=client.get_tools())
                graph_builder.add_node("tools", tool_node.ainvoke)

                graph_builder.add_conditional_edges("screening-agent", tools_condition)
                graph_builder.add_edge("tools", "screening-agent")
                graph_builder.add_edge("screening-agent", END)

        
                graph = graph_builder.compile(checkpointer=checkpointer)
                graph.name = "screening-agent"

                
        
                try:
                    response = graph.invoke({"messages": [{"role": "user", "content": request}]},config={"configurable": {"thread_id": "1"},"callbacks": [langfuse_handler],"run_id": predefined_run_id})
                    
                    print("response",response["messages"][-1].content)
                    return {
                    "agent_response": response["messages"][-1].content,
                    "trace_id": predefined_run_id,
                    "session_id":langfuse_handler.session_id
                }
                except Exception as e:
                    print(e)

            # except asyncio.TimeoutError:
            #     logging.warning(f"[{datetime.now()}] Agent exceeded SLA timeout of {self.timeout}s. Falling back.")
            #     tools= client.get_tools()
            #     print(tools)
            #     human_tool=[]
            #     for tool in tools:
            #         if tool.name=="human_assistance":
            #             human_tool.append(tool)
            #     print(human_tool)
            #     result = await session.call_tool("human_assistance", {"query": request})
            #     return result

        
        
    async def run_query(self, query:str) -> dict:
        server_url = os.getenv("SSE_SERVER_URL")
        async with sse_client(url=server_url) as streams:
            async with ClientSession(*streams) as session:
                try:
                    pool = AsyncConnectionPool(
                    conninfo="postgresql://postgres:123456@localhost:5433/MCP-Agent",
                    max_size=20, 
                    kwargs={
                        "autocommit": True,
                        "prepare_threshold": 0,
                        "row_factory": dict_row,
                    },
                    )           
                    await session.initialize()
                    memory = await pool.open()
                    await session.initialize()
                    return await self.process(session,query,memory)
                except Exception as e:
                    print("Error during process_query:", str(e))


chat1 = ScreeningOps()
