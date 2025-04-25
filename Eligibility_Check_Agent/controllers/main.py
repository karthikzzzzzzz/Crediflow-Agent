from fastapi import HTTPException,APIRouter,Depends
from starlette import status
from kafka import KafkaProducer
from utils.database import engine
from utils.database import get_db
from sqlalchemy.orm import Session
from utils.models import Logs
import utils.models as models
import json
from utils.schema import Request, StatusResponse, KafkaSubmissionResponse,AgentResponse
import random
import os 
from dotenv import load_dotenv
from dependency_injector.wiring import inject, Provide
from Eligibility_check_agent.services.eligibility_check import EligibilityCheck
from Eligibility_check_agent.dependencies.containers import Container

eligibilityagent = APIRouter()
load_dotenv()
models.Base.metadata.create_all(engine)

producer1 = KafkaProducer(
    bootstrap_servers=[os.getenv("KAFKA_HOST")],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@eligibilityagent.get("/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/status",response_model=StatusResponse, summary="Get chat response by session ID")
def retrieve_chat_response(sessionId: int,realmId:str,userId:int,leadId:int, db: Session = Depends(get_db)):
    log = db.query(Logs).filter(Logs.id == sessionId).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    return {
        "status": "completed" if log.response else "pending",
        "response": log.response
    }  

@eligibilityagent.post("/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",response_model=AgentResponse, summary="Process a chat query via eligibility checker agent")
@inject
async def process_query(request:Request,realmId:str,userId:int,leadId:int, sessionId:str,db:Session=Depends(get_db),chat: EligibilityCheck = Depends(Provide[Container.eligibility_service])):
    try:
        result = await chat.run_query(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing query: {str(e)}")
    

@eligibilityagent.post("/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision",response_model=KafkaSubmissionResponse, summary="Submit a chat query for Kafka listener")
async def verify_query(request: Request,realmId:str,userId:int,leadId:int, sessionId:str):
    try:
        query_text = request.text
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in request.")
        query_id = random.randint(100000, 999999)
        producer1.send("risk-graph", {
            "query": query_text,
            "log_id": query_id
        })
        return {"message": "Query received. Processing via Kafka...", "query_id":query_id}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing query: {str(e)}")
    
