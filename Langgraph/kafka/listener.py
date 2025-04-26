from kafka import KafkaConsumer
import json
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from Langgraph.dependencies.containers import Container
from Langgraph.services.langgraph import Langgraph
from utils.database import get_db
from utils.models import IntelliAgentSchema 

load_dotenv()

consumer = KafkaConsumer(
    'intelli-agent-topic',
    bootstrap_servers=[os.getenv("KAFKA_HOST")],
    group_id='intelli-agent-group', 
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

@inject
async def process_message(
    message: dict,
    chat: Langgraph = Provide[Container.langgraph_service]
):
    db_gen = get_db()
    db: Session = next(db_gen)
    try:
       
        query = message["query"]
        realm_id = message["realm_id"]
        user_id = message["user_id"]
        lead_id = message["lead_id"]
        trace_id = message["trace_id"]
        session_id = message["session_id"]

      
        result = await chat.run_query(query)

       
        log_entry = IntelliAgentSchema(
            user_id=user_id,
            realm_id=realm_id,
            lead_id=lead_id,
            session_id=session_id,
            trace_id=trace_id,
            query=query,
            span_id=result["span_id"],         
            response=result["agent_response"],  
            timestamp=result["timestamp"] if "timestamp" in result else None  
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

    except Exception as e:
        print(f"Error processing message: {str(e)}")
    finally:
        db.close()

async def main():
    print("Kafka IntelliAgent listener started...")
    for message in consumer:
        await process_message(message.value)

if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    asyncio.run(main())
