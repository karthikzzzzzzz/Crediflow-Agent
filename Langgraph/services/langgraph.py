import asyncio
import os
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.pregel.remote import RemoteGraph
from langgraph.graph import StateGraph, START, END
from utils.schema import State
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from langfuse.callback import CallbackHandler

load_dotenv()

langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
    session_id=str(uuid.uuid4()),
    metadata={
        "agent_id": "multi_agent_flow"
    }
)

predefined_run_id = str(uuid.uuid4())
base_url = "http://127.0.0.1:8000"

class Langgraph:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("MODEL"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.timeout = 3600

    async def process(self, request: str, memory):
        
        data_node = RemoteGraph("data-acquistion-agent", url=base_url)
        document_node = RemoteGraph("document-agent", url=base_url)
        screening_node = RemoteGraph("screening-agent", url=base_url)
        eligibility_node = RemoteGraph("eligibility-agent", url=base_url)
        report_node = RemoteGraph("report-agent", url=base_url)

        
        graph_builder = StateGraph(State)
        graph_builder.add_node("data-acquistion-agent", data_node)
        graph_builder.add_node("document-agent", document_node)
        graph_builder.add_node("screening-agent", screening_node)
        graph_builder.add_node("eligibility-agent", eligibility_node)
        graph_builder.add_node("report-agent", report_node)

        graph_builder.add_edge(START, "data-acquistion-agent")
        graph_builder.add_edge("data-acquistion-agent", "document-agent")
        graph_builder.add_edge("document-agent", "screening-agent")
        graph_builder.add_edge("screening-agent", "eligibility-agent")
        graph_builder.add_edge("eligibility-agent", "report-agent")
        graph_builder.add_edge("report-agent", END)

        graph = graph_builder.compile(checkpointer=memory)
        graph.name = "multi-agent-flow"

        try:
            result = await graph.ainvoke(
                {"messages": [{"role": "user", "content": request}]},
                config={
                    "configurable": {"thread_id": "1"},
                    "callbacks": [langfuse_handler],
                    "run_id": predefined_run_id
                }
            )
            print("Response:", result["messages"][-1].content)
            return {
                "agent_response": result["messages"][-1].content,
                "trace_id": predefined_run_id,
                "session_id": langfuse_handler.session_id,
                "span_id": langfuse_handler.metadata.get("agent_id")
            }
        except Exception as e:
            print("Error during agent flow:", str(e))
            raise

    async def run_query(self, query: str) -> dict:
        try:
            async with AsyncConnectionPool(
                conninfo="postgresql://postgres:123456@localhost:5433/MCP-Agent",
                max_size=20,
                kwargs={
                    "autocommit": True,
                    "prepare_threshold": 0,
                }
            ) as pool:
                async with pool.connection() as conn:
                    memory = AsyncPostgresSaver(conn)
                    await memory.setup()
                    return await self.process(query, memory)
        except Exception as e:
            print("Error during run_query:", str(e))
            raise


