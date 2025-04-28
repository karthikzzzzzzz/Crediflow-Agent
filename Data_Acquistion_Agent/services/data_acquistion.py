import asyncio
from datetime import datetime
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.redis import AsyncRedisSaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from utils.schema import State
import psycopg2
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode,tools_condition
from mcp.client.sse import sse_client
from mcp import ClientSession
from langfuse.callback import CallbackHandler
import os 
import redis 
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
import json
import uuid
from typing import Optional, Dict
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver




langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
    session_id=str(uuid.uuid4()),
    metadata={
        "agent_id": "data_acquisition_agent"
    }
)

predefined_run_id = str(uuid.uuid4())

redis_client = redis.Redis.from_url(os.getenv("REDIS_URI"), decode_responses=True)

class DataAcquistion:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("MODEL"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.timeout=3600
    
    def persist_state_to_shortterm(self, session_id: str, state: dict, ttl: int = 600):
        redis_key = f"state:{session_id}"
        compressed_state = json.dumps(state, default=str)  
        redis_client.set(redis_key, compressed_state, ex=ttl)


    def persist_state_to_longterm(self, session_id: str, user_id: str, realm_id: str, lead_id: int, trace_id: Optional[str], span_id: Optional[str], state: dict):
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

    def load_state_from_longterm(self,session_id: str,user_id: str,realm_id: str,) -> Optional[Dict]:
        conn = psycopg2.connect(os.getenv("POSTGRES_CONN_STRING"))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT state_json
            FROM intelli_agent
            WHERE session_id = %s AND user_id = %s AND realm_id = %s
            """,
            (session_id, user_id, realm_id),
        )
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  
        return None


    def save_state(self,session_id: str,user_id: str,realm_id: str,lead_id:int,trace_id: Optional[str],span_id: Optional[str],state: dict,ttl: int = 600):
        self.persist_state_to_shortterm(session_id, state, ttl=ttl)
        self.persist_state_to_longterm(session_id, user_id, realm_id, lead_id,trace_id,span_id, state)

    def serialize_messages(self,messages):
        serialized = []
        for message in messages:
            serialized.append({
                "type": message.__class__.__name__, 
                "role": getattr(message, "role", None),
                "content": getattr(message, "content", None),
            })
        return serialized
    
    
    def persist_procedural_memory(self,case_id: Optional[str],task_name: str,steps: Optional[list],trigger_conditions: Optional[dict],created_by: str = "data_acquisition_agent"):
        
        conn = psycopg2.connect(os.getenv("POSTGRES_CONN_STRING"))
        cursor = conn.cursor()

        now = datetime.utcnow()
        procedural_id = str(uuid.uuid4())

        cursor.execute(
            """
            INSERT INTO agent_procedural_memory (id, task_name, steps, trigger_conditions, created_by, created_at, case_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                procedural_id,
                task_name,
                json.dumps(steps or []),
                json.dumps(trigger_conditions or {}),
                created_by,
                now,
                case_id
            )
        )

        conn.commit()
        cursor.close()
        conn.close()
    def persist_semantic_memory(self,user_id: int,realm_id: str,session_id: str,trace_id: Optional[str],span_id: Optional[str],case_id: Optional[str],key: str,value: Optional[str] = None,source: Optional[str] = None,vector: Optional[list] = None,tags: Optional[list] = None):
        conn = psycopg2.connect(os.getenv("POSTGRES_CONN_STRING"))
        cursor = conn.cursor()

        semantic_id = str(uuid.uuid4())


        if value is None:
            value = "risk"
        if source is None:
            source = "agent_output"
        if tags is None:
            tags = ["underwriting"]
        if vector is None:
            vector = [0.0] * 1536

        cursor.execute(
            """
            INSERT INTO agent_semantic_memory (
                id, user_id, realm_id, session_id, trace_id, span_id, case_id,
                key, value, source, vector, tags, last_updated
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (semantic_id,user_id,realm_id,session_id,trace_id,span_id,case_id,key,value,source,vector,tags)
        )

        conn.commit()
        cursor.close()
        conn.close()


    def persist_episodic_memory(self,user_id: int,realm_id: str,session_id: str,trace_id: Optional[str],span_id: Optional[str],case_id: Optional[str],summary: str,raw_state: dict):
        conn = psycopg2.connect(os.getenv("POSTGRES_CONN_STRING"))
        cursor = conn.cursor()

        episodic_id = str(uuid.uuid4())
        now = datetime.utcnow()

        cursor.execute(
            
            """
            INSERT INTO episodic_memory (id, user_id, realm_id, case_id, session_id, trace_id, span_id, timestamp, summary, raw_state)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (episodic_id,user_id,realm_id,case_id,session_id,trace_id,span_id,now,summary,json.dumps(raw_state))
        )
        conn.commit()
        cursor.close()
        conn.close()




    async def process(self,session:ClientSession, request: str,memory,user_id:int,realm_id:str,lead_id:int):

        async with MultiServerMCPClient({
            "server": {
            "url": "http://127.0.0.1:9090/sse",
            "transport": "sse",
        }
        }) as client:
            
            # POSTGRES_CONN_STRING = "postgresql://postgres:123456@localhost:5433/MCP-Agent"
            # checkpointer = AsyncPostgresSaver(conn_str=POSTGRES_CONN_STRING)
            # checkpointer.setup()
            async with AsyncRedisSaver.from_conn_string(os.getenv("REDIS_URI")) as checkpointer:
                await checkpointer.checkpoints_index.create(overwrite=False)
                await checkpointer.checkpoint_blobs_index.create(overwrite=False)
                await checkpointer.checkpoint_writes_index.create(overwrite=False)
        
                tools = await load_mcp_tools(session)
            
                graph_builder=StateGraph(State)
            
                agent = create_react_agent(self.llm,tools,checkpointer=checkpointer)
                
                

                graph_builder.add_node("document-agent",agent)
                graph_builder.add_edge(START,"document-agent")
                tool_node = ToolNode(tools=tools)
                graph_builder.add_node("tools", tool_node.ainvoke)

                graph_builder.add_conditional_edges("document-agent", tools_condition)
                graph_builder.add_edge("tools", "document-agent")
                graph_builder.add_edge("document-agent", END)


        
                graph = graph_builder.compile(checkpointer=checkpointer)
                graph.name ="data-acquistion-agent"
                
                try:
                    session_id = langfuse_handler.session_id
                    trace_id = predefined_run_id
                    span_id = langfuse_handler.metadata.get("agent_id") 

                
                    response = graph.invoke({"messages": [{"role": "user", "content": request}]},config={"configurable": {"thread_id": "1"},"callbacks": [langfuse_handler],"run_id": predefined_run_id})
                    
                    processed_response = {
                            "messages": self.serialize_messages(response["messages"])
                    }
                    steps = []
                    triggers ={}

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
                    self.persist_episodic_memory(
                        user_id=user_id,
                        realm_id=realm_id,
                        session_id=session_id,
                        trace_id=trace_id,
                        span_id=span_id,
                        case_id=str(uuid.uuid4()),
                        summary=response["messages"][-1].content,
                        raw_state=processed_response,
                    )
                    self.persist_semantic_memory(
                        user_id=user_id,
                        realm_id=realm_id,
                        session_id=session_id,
                        trace_id=trace_id,
                        span_id=span_id,
                        case_id=str(uuid.uuid4()),
                        key=str(uuid.uuid4())
                    )
                    self.persist_procedural_memory(
                        case_id=str(uuid.uuid4()),
                        task_name="data_acquisition_task",
                        steps=steps,
                        trigger_conditions=triggers,
                        created_by="data_acquisition_agent"
                    )
                    
                    
                    return {
                    "agent_response": response["messages"][-1].content,
                    "trace_id": predefined_run_id,
                    "session_id":langfuse_handler.session_id,
                    "span_id": langfuse_handler.metadata.get("agent_id")
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

        
        
    async def run_query(self, query:str,user_id:int,realm_id:str,lead_id:int) -> dict:
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
                    return await self.process(session,query,memory,user_id,realm_id,lead_id)
                except Exception as e:
                    print("Error during process_query:", str(e))



