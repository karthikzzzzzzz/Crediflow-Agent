import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.redis import RedisSaver
from langgraph.prebuilt import create_react_agent
from langgraph.pregel import RetryPolicy
from config.schema import State
from langchain.schema import HumanMessage

load_dotenv()


langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)

class HumanInLoopAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("MODEL"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )

    async def review_and_edit(self, request: str) -> str:

        print("[Human Review] Reviewing request:", request)
        review_msg = input("Enter the review comments")
        edited_request = request + review_msg
        return edited_request
    async def human_approve(self, reviewed_request: str) -> bool:
        print(f"Reviewed Request: {reviewed_request}")
        approval = input("Do you approve this request? (y/n): ")  
        
        if approval.lower() == 'y':
            print("Request approved by human.")
            return True
        else:
            print("Request rejected by human.")
            return False

    async def process_query(self, request):
        try:
            
            graph_builder = StateGraph(State)

            agent = create_react_agent(self.llm, tools=[])
            graph_builder.add_node("react-agent", agent, retry=RetryPolicy(max_attempts=5))

            async def human_review_node(state: State):
                print("Entered human review step.")
                request = state["messages"][-1] 
                reviewed = await self.review_and_edit(request.content)  
                is_approved = await self.human_approve(reviewed)
                if is_approved:
                    state["messages"].append(HumanMessage(content=reviewed)) 
                else:
                    state["messages"].append(HumanMessage(content="Request rejected by human."))
                
                return state

            graph_builder.add_node("human-review", human_review_node)
            graph_builder.add_edge(START, "human-review")
            graph_builder.add_edge("human-review", "react-agent")
            graph_builder.add_edge("react-agent", END)

            graph = graph_builder.compile()
            graph.name = "human-in-loop-agent"
                
            response = await graph.ainvoke(
                    {"messages": [{"role": "user", "content": request}]},
                    config={"configurable": {"thread_id": "1"}, "callbacks": [langfuse_handler]}
            )
            print(response)
                
            return {
                    "output": response["messages"][-1].content
            }

        except Exception as e:
            print("Error in process_query:", str(e))
       


hil = HumanInLoopAgent()
