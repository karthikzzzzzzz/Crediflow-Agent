from fastapi import HTTPException,APIRouter,Depends
from starlette import status
from kafka import KafkaProducer
from utils.database import engine
from utils.database import get_db
from sqlalchemy.orm import Session
from utils.models import Logs
import utils.models as models
import json
from utils.schema import Request
import random

backagent= APIRouter()

models.Base.metadata.create_all(engine)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


@backagent.post("/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision", summary="Process a chat query to back office agent")
async def chat_request(request: Request,realmId:str,userId:int,leadId:int, sessionId:str):
    try:
        query_text = request.text
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in request.")
        query_id = random.randint(100000, 999999)
        producer.send("risk", {
            "query": query_text,
            "log_id": query_id
        })
        return {"message": "Query received. Processing via Kafka...", "query_id":{query_id}}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing query: {str(e)}")
    
@backagent.get("/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/status ", summary="Get chat response by session ID")
def retrieve_chat_response(sessionId: int,realmId:str,userId:int,leadId:int, db: Session = Depends(get_db)):
    log = db.query(Logs).filter(Logs.id == sessionId).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    return {
        "status": "completed" if log.response else "pending",
        "response": log.response
    }  

