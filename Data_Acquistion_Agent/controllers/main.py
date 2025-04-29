# File: Data_acquistion_agent/controllers/main.py

from fastapi import HTTPException, APIRouter, Depends
from starlette import status
from kafka import KafkaProducer
from utils.database import engine
from utils.database import get_db
from sqlalchemy.orm import Session
from utils.models import DataAcquisitionSchema
import utils.models as models
from dependency_injector.wiring import inject, Provide
import json
from utils.schema import Request, StatusResponse, KafkaSubmissionResponse, AgentResponse
import uuid
import os
from dotenv import load_dotenv
from Data_acquistion_agent.services.data_acquistion import DataAcquistion
from Data_acquistion_agent.dependencies.containers import Container


dataagent = APIRouter()
load_dotenv()
models.Base.metadata.create_all(engine)


def create_kafka_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP_SERVERS")],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )


@dataagent.get(
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
    log = db.query(DataAcquisitionSchema).filter(DataAcquisitionSchema.query_id == query_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

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


@dataagent.post(
    "/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",
    response_model=AgentResponse,
    summary="Process a chat query via Data acquisition agent"
)
@inject
async def process_query(
    request: Request,
    realmId: str,
    userId: int,
    leadId: int,
    sessionId: str,
    db: Session = Depends(get_db),
    chat: DataAcquistion = Depends(Provide[Container.data_acquisition_service])
):
    try:
        result = await chat.run_query(request.text,userId,realmId,leadId)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@dataagent.post(
    "/v2/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",
    response_model=KafkaSubmissionResponse,
    summary="Submit a chat query for Kafka listener"
)
async def verify_query(
    request: Request,
    realmId: str,
    userId: int,
    leadId: int,
    sessionId: str,
    producer: KafkaProducer = Depends(create_kafka_producer) 
):
    try:
        if not sessionId:
            raise HTTPException(status_code=500, detail="Not a valid session id")

        query_text = request.text
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in request.")

        query_id = str(uuid.uuid4())
        producer.send("data-acquisition", {
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
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
