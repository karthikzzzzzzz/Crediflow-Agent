from fastapi import HTTPException, APIRouter, Depends
from starlette import status
from kafka import KafkaProducer
from utils.database import engine, get_db
from sqlalchemy.orm import Session
from utils.models import Logs
import utils.models as models
import json
from utils.schema import Request
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

backagent = APIRouter()
models.Base.metadata.create_all(engine)


def create_kafka_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP_SERVERS")],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )


@backagent.post(
    "/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",
    summary="Process a chat query to back office agent"
)
async def chat_request(
    request: Request,
    realmId: str,
    userId: int,
    leadId: int,
    sessionId: str,
    producer: KafkaProducer = Depends(create_kafka_producer)
):
    try:
        query_text = request.text
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in request.")

        query_id = str(uuid.uuid4())

        producer.send("back-office", {
            "query": query_text,
            "log_id": query_id,
            "realm_id": realmId,
            "user_id": userId,
            "lead_id": leadId,
            "session_id": sessionId,
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


@backagent.get(
    "/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/status",
    summary="Get chat response by session ID"
)
def retrieve_chat_response(
    sessionId: str,
    query_id: str,
    realmId: str,
    userId: int,
    leadId: int,
    db: Session = Depends(get_db)
):
    log = db.query(Logs).filter(Logs.id == query_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"Query ID {query_id} not found.")

    return {
        "status": "completed" if log.response else "pending",
        "response": log.response
    }
