from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide
import uuid
import json
import os
from dotenv import load_dotenv
from kafka import KafkaProducer

from utils.database import engine, get_db
from utils.models import IntelliAgentSchema 
from utils.schema import Request, StatusResponse, KafkaSubmissionResponse, AgentResponse
from Langgraph.dependencies.containers import Container
from Langgraph.services.langgraph import Langgraph  

load_dotenv()
intelliagent = APIRouter()

from utils import models
models.Base.metadata.create_all(engine)

producer = KafkaProducer(
    bootstrap_servers=[os.getenv("KAFKA_HOST")],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@intelliagent.get(
    "/v1/intelli-agent/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/status",
    response_model=StatusResponse,
    summary="Get IntelliAgent response by query ID"
)
def retrieve_intelliagent_response(
    sessionId: str,
    realmId: str,
    userId: int,
    leadId: int,
    query_id: str,
    db: Session = Depends(get_db)
):
    log = db.query(IntelliAgentSchema).filter(IntelliAgentSchema.query_id == query_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"Query ID {query_id} not found.")

    return {
        "status": "completed" if log.response else "pending",
        "user_id": log.user_id,
        "realm_id": log.realm_id,
        "lead_id": log.lead_id,
        "query_id": log.query_id,
        "session_id": log.session_id,
        "trace_id": log.trace_id,
        "query": log.query,
        "response": log.response,
        "timestamp": log.timestamp,
    }

@intelliagent.post(
    "/v1/intelli-agent/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",
    response_model=AgentResponse,
    summary="Process a query via IntelliAgentFlow"
)
@inject
async def process_intelliagent_query(
    request: Request,
    realmId: str,
    userId: int,
    leadId: int,
    sessionId: str,
    db: Session = Depends(get_db),
    chat: Langgraph = Depends(Provide[Container.langgraph_service])
):
    try:
        result = await chat.run_query(request.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@intelliagent.post(
    "/v2/intelli-agent/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",
    response_model=KafkaSubmissionResponse,
    summary="Submit a query for IntelliAgent Kafka listener"
)
async def submit_intelliagent_query(
    request: Request,
    realmId: str,
    userId: int,
    leadId: int,
    sessionId: str
):
    try:
        if not sessionId:
            raise HTTPException(status_code=500, detail="Invalid session id")

        query_text = request.text
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in request.")

        query_id = str(uuid.uuid4())
        producer.send("intelli-agent-topic", {
            "query": query_text,
            "user_id": userId,
            "realm_id": realmId,
            "lead_id": leadId,
            "query_id": query_id,
        })

        return {
            "message": "Query received. Processing via Kafka...",
            "query_id": query_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting query: {str(e)}"
        )
