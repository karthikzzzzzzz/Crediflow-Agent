from pydantic import BaseModel
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class Request(BaseModel):
    text: str

class State(TypedDict):
    messages:Annotated[list,add_messages]


class AgentResponse(BaseModel):
    agent_response: str

class StatusResponse(BaseModel):
    status: str
    response: str | None

class KafkaSubmissionResponse(BaseModel):
    message: str
    query_id: int