from fastapi import HTTPException, APIRouter, Depends
from starlette import status
from kafka import KafkaProducer
from utils.database import engine, get_db
from sqlalchemy.orm import Session
from utils.models import ReportGenerationSchema
import utils.models as models
import json
from utils.schema import Request, StatusResponse, KafkaSubmissionResponse, AgentResponse
import uuid
import os
from dotenv import load_dotenv
from Report_generation_agent.services.report_generation import ReportGeneration
from Report_generation_agent.dependencies.containers import Container
from dependency_injector.wiring import inject, Provide

load_dotenv()
reportagent = APIRouter()

models.Base.metadata.create_all(engine)

producer1 = KafkaProducer(
    bootstrap_servers=[os.getenv("KAFKA_HOST")],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@reportagent.get(
    "/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/status",
    response_model=StatusResponse,
    summary="Get chat response by query ID"
)
def retrieve_chat_response(
    sessionId: str,
    realmId: str,
    userId: int,
    leadId: int,
    query_id: str,
    db: Session = Depends(get_db)
):
    log = db.query(ReportGenerationSchema).filter(ReportGenerationSchema.query_id == query_id).first()
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


@reportagent.post(
    "/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",
    response_model=AgentResponse,
    summary="Process a chat query via Report Generation agent"
)
@inject
async def process_query(
    request: Request,
    realmId: str,
    userId: int,
    leadId: int,
    sessionId: str,
    db: Session = Depends(get_db),
    chat: ReportGeneration = Depends(Provide[Container.report_service])
):
    try:
        result = await chat.run_query(request.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@reportagent.post(
    "/v2/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",
    response_model=KafkaSubmissionResponse,
    summary="Submit a chat query for Kafka listener"
)
async def verify_query(
    request: Request,
    realmId: str,
    userId: int,
    leadId: int,
    sessionId: str
):
    try:
        if not sessionId:
            raise HTTPException(status_code=500, detail="not a valid session id")

        query_text = request.text
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in request.")

        query_id = str(uuid.uuid4())
        producer1.send("risk-graph", {
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
            detail=f"Error processing query: {str(e)}"
        )
