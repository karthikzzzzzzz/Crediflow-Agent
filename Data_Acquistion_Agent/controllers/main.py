from fastapi import HTTPException,APIRouter,Depends
from starlette import status
from kafka import KafkaProducer
from config.database import engine
from config.database import get_db
from sqlalchemy.orm import Session
from config.models import Logs
import config.models as models
import json
from config.schema import Request
import random
import os 
from dotenv import load_dotenv
from Eligibility_Check_Agent.services.Eligibility_check import chat1

dataagent = APIRouter()
load_dotenv()
models.Base.metadata.create_all(engine)

producer1 = KafkaProducer(
    bootstrap_servers=[os.getenv("KAFKA_HOST")],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@dataagent.get("/data-acquistion-agent/api/get-response/{log_id}")
def retrieve_chat_response(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Logs).filter(Logs.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    return {
        "status": "completed" if log.response else "pending",
        "response": log.response
    }  

@dataagent.post("/data-acquistion-agent/api/v1/chat-completions")
async def process_query(request:Request,db:Session=Depends(get_db)):
    try:
        result = await chat1.run_query(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing query: {str(e)}")
    

@dataagent.post("/data-acquistion-agent/api/v2/chat-completions")
async def verify_query(request: Request):
    try:
        query_text = request.text
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in request.")
        query_id = random.randint(100000, 999999)
        producer1.send("risk-graph", {
            "query": query_text,
            "log_id": query_id
        })
        return {"message": "Query received. Processing via Kafka...", "query_id":{query_id}}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing query: {str(e)}")
    
