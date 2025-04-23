from langgraph.pregel.remote import RemoteGraph
from config.schema import State
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
import asyncio
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    secret_key="sk-lf-1e0bd6b6-e048-464b-aee3-d38e00ce9470",
    public_key="pk-lf-c17460d4-cd56-4440-8318-679027e60a03",
    host="http://localhost:3000", 
)

base_url ="http://127.0.0.1:8000"
graph_name ="chat"

async def main():
    async with AsyncConnectionPool(conninfo="postgresql://postgres:123456@localhost:5433/MCP-Agent") as pool,pool.connection() as conn:
        memory= AsyncPostgresSaver(conn)
        await memory.setup()

        data_node = RemoteGraph("data-acquistion-agent", url=base_url)
        document_node = RemoteGraph("document-agent", url=base_url)
        screening_node = RemoteGraph("screening-agent", url=base_url)
        eligibility_node = RemoteGraph("eligibility-agent", url=base_url)
        report_node = RemoteGraph("report-agent", url=base_url)

        graph_builder = StateGraph(State)
        graph_builder.add_node("data-acquistion-agent",data_node)
        graph_builder.add_node("document-agent", document_node)
        graph_builder.add_node("screening-agent", screening_node)
        graph_builder.add_node("eligibility-agent", eligibility_node)
        graph_builder.add_node("report-agent", report_node)

        graph_builder.add_edge(START, "data-acquistion-agent")
        graph_builder.add_edge("data-acquistion-agent","document-agent")
        graph_builder.add_edge("document-agent", "screening-agent")
        graph_builder.add_edge("screening-agent", "eligibility-agent")
        graph_builder.add_edge("eligibility-agent", "report-agent")
        graph_builder.add_edge("report-agent", END)

        graph = graph_builder.compile(checkpointer=memory)

        request = "hello"
        result = graph.ainvoke({"messages": [{"role": "user", "content": request}]},config={"configurable": {"thread_id": "1"},"callbacks": [langfuse_handler]})
        return result


if __name__ =="__main__":
    asyncio.run(main())