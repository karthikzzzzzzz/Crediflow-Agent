import asyncio
from datetime import datetime
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.redis import RedisSaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from utils.schema import State
import psycopg2
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from mcp.client.sse import sse_client
from mcp import ClientSession
from langgraph.pregel import RetryPolicy
from langfuse.callback import CallbackHandler
import os
import redis
from dotenv import load_dotenv
import json
import uuid
from typing import Optional

load_dotenv()

RetryPolicy()

langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
    session_id=str(uuid.uuid4()),
    metadata={
        "agent_id": "eligibility_checker_agent"
    }
)

predefined_run_id = str(uuid.uuid4())

redis_client = redis.Redis.from_url(os.getenv("REDIS_URI"), decode_responses=True)

class EligibilityCheck:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("MODEL"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.timeout = 3600

    def persist_state_to_shortterm(self, session_id: str, state: dict, ttl: int = 600):
        redis_key = f"state:{session_id}"
        compressed_state = json.dumps(state, default=str)
        redis_client.set(redis_key, compressed_state, ex=ttl)

    def persist_state_to_longterm(
        self,
        session_id: str,
        user_id: str,
        realm_id: str,
        lead_id: int,
        trace_id: Optional[str],
        span_id: Optional[str],
        state: dict
    ):
        conn = psycopg2.connect(os.getenv("POSTGRES_CONN_STRING"))
        cursor = conn.cursor()
        new_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO intelli_agent (id, session_id, user_id, lead_id, realm_id, trace_id, span_id, state, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (new_id, session_id, user_id, lead_id, realm_id, trace_id, span_id, json.dumps(state))
        )
        conn.commit()
        cursor.close()
        conn.close()

    def save_state(
        self,
        session_id: str,
        user_id: str,
        realm_id: str,
        lead_id: int,
        trace_id: Optional[str],
        span_id: Optional[str],
        state: dict,
        ttl: int = 600
    ):
        self.persist_state_to_shortterm(session_id, state, ttl=ttl)
        self.persist_state_to_longterm(session_id, user_id, realm_id, lead_id, trace_id, span_id, state)

    def serialize_messages(self, messages):
        serialized = []
        for message in messages:
            serialized.append({
                "type": message.__class__.__name__,
                "role": getattr(message, "role", None),
                "content": getattr(message, "content", None),
            })
        return serialized

    async def process(self, session: ClientSession, request: str, memory, user_id: int, realm_id: str, lead_id: int):
        async with MultiServerMCPClient({
            "server": {
                "url": "http://127.0.0.1:9090/sse",
                "transport": "sse",
            }
        }) as client:
            with RedisSaver.from_conn_string(os.getenv("REDIS_URI")) as checkpointer:
                checkpointer.setup()

                graph_builder = StateGraph(State)

                agent = create_react_agent(self.llm, client.get_tools(), checkpointer=checkpointer)

                graph_builder.add_node("document-agent", agent, retry=RetryPolicy(max_attempts=5))
                graph_builder.add_edge(START, "document-agent")

                tool_node = ToolNode(tools=client.get_tools())
                graph_builder.add_node("tools", tool_node.ainvoke)

                graph_builder.add_conditional_edges("document-agent", tools_condition)
                graph_builder.add_edge("tools", "document-agent")
                graph_builder.add_edge("document-agent", END)

                graph = graph_builder.compile(checkpointer=checkpointer)
                graph.name = "eligibility-agent"

                try:
                    session_id = langfuse_handler.session_id
                    trace_id = predefined_run_id
                    span_id = langfuse_handler.metadata.get("agent_id")

                    response = graph.invoke(
                        {"messages": [{"role": "user", "content": request}]},
                        config={
                            "configurable": {"thread_id": "1"},
                            "callbacks": [langfuse_handler],
                            "run_id": predefined_run_id
                        }
                    )

                    processed_response = {
                        "messages": self.serialize_messages(response["messages"])
                    }

                    self.save_state(
                        session_id=session_id,
                        user_id=user_id,
                        realm_id=realm_id,
                        lead_id=lead_id,
                        trace_id=trace_id,
                        span_id=span_id,
                        state=processed_response,
                        ttl=600
                    )

                    return {
                        "agent_response": response["messages"][-1].content,
                        "trace_id": predefined_run_id,
                        "session_id": langfuse_handler.session_id,
                        "span_id": langfuse_handler.metadata.get("agent_id")
                    }
                except Exception as e:
                    print(e)

    async def run_query(self, query: str, user_id: int, realm_id: str, lead_id: int) -> dict:
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
                    return await self.process(session, query, memory, user_id, realm_id, lead_id)
                except Exception as e:
                    print("Error during run_query:", str(e))
