from pydantic import BaseModel
from typing import Annotated, Optional
from typing_extensions import TypedDict, List
from datetime import datetime
from uuid import UUID
from langgraph.graph.message import add_messages

class Request(BaseModel):
    text: str

class State(TypedDict):
    messages:Annotated[list,add_messages]

class IntelliAgentState(TypedDict, total=False):
    session_id: str
    user_id: int
    realm_id: str
    lead_id: int
    trace_id: Optional[str]
    span_id: Optional[str]
    messages: List[dict]  
    created_at: Optional[str]
    updated_at: Optional[str]


class AgentResponse(BaseModel):
    agent_response: str
    trace_id: str
    session_id: str
    span_id:str

class StatusResponse(BaseModel):
    status: str
    user_id: int
    realm_id: str
    lead_id: int
    query_id: UUID
    session_id: UUID
    trace_id: Optional[UUID]
    query: str
    response: Optional[str]
    timestamp: datetime

class KafkaSubmissionResponse(BaseModel):
    message: str
    query_id: UUID

class LanggraphResponse(BaseModel):
    status: str
    message: str
    query_id: str
    trace_id: str
    session_id: str

class LangStatusResponse(BaseModel):
    status: str
    user_id: int
    realm_id: str
    lead_id: int
    session_id: UUID
    trace_id: Optional[UUID]
    query: str
    response: Optional[str]
    timestamp: datetime