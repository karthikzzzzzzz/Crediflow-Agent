from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
import uuid
import json
import os
from dotenv import load_dotenv
from kafka import KafkaProducer

from utils.database import engine, get_db
from utils.models import IntelliAgentSchema 
from utils.schema import Request, LanggraphResponse,LangStatusResponse

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
    response_model=LangStatusResponse,
    summary="Get IntelliAgent response by query ID"
)
def retrieve_intelliagent_response(
    sessionId: str,
    realmId: str,
    userId: int,
    leadId: int,
    trace_id: str,
    db: Session = Depends(get_db)
):
    log = db.query(IntelliAgentSchema).filter(IntelliAgentSchema.trace_id == trace_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"Trace ID {trace_id} not found.")

    return {
        "status": "completed" if log.response else "pending",
        "user_id": userId,
        "realm_id": realmId,
        "lead_id": leadId,
        "session_id": sessionId,
        "trace_id": trace_id,
        "query": log.query,
        "response": log.response,
        "timestamp": log.timestamp,
    }

@intelliagent.post(
    "/v2/intelli-agent/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",
    response_model=LanggraphResponse,
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
            raise HTTPException(status_code=400, detail="Invalid session id.")

        query_text = request.text
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in request.")

        trace_id = str(uuid.uuid4())
     

        producer.send("intelli-agent-topic", {
            "query": query_text,
            "user_id": userId,
            "realm_id": realmId,
            "lead_id": leadId,
            "trace_id": trace_id,
            "session_id": sessionId
        })

        return {
            "status": "success",
            "message": "Query received. Processing via Kafka...",
            "trace_id": trace_id,
            "session_id": sessionId
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting query: {str(e)}"
        )
