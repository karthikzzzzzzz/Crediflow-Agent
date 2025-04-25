from kafka import KafkaConsumer
import json
import asyncio
from Eligibility_check_agent.services.eligibility_check import EligibilityCheck
from utils.database import get_db
from utils.models import EligibilityCheckerSchema
from sqlalchemy.orm import Session
import os 
from dotenv import load_dotenv
from dependency_injector.wiring import inject, Provide
from Eligibility_check_agent.dependencies.containers import Container

load_dotenv()

consumer = KafkaConsumer(
    'risk-graph',
    bootstrap_servers=[os.getenv("KAFKA_HOST")],
    group_id='risk-graph-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

@inject
async def process_message(
    message: dict,
    chat: EligibilityCheck  = Provide[Container.data_acquisition_service]
):
    db_gen = get_db()
    db: Session = next(db_gen)
    try:
        query = message["query"]
        query_id = message["query_id"]
        realm_id = message["realm_id"]
        user_id = message["user_id"]
        lead_id = message["lead_id"]


        result = await chat.run_query(query)

        log_entry = EligibilityCheckerSchema(
            user_id=user_id,
            realm_id=realm_id,
            lead_id=lead_id,
            session_id=result["session_id"],
            trace_id=result["trace_id"],
            query_id=query_id,
            query=query,
            response=result["agent_response"]
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)


    except Exception as e:
        print(f"Error processing message: {str(e)}")
    finally:
        db.close()

async def main():
    print("Kafka listener started...")
    for message in consumer:
        await process_message(message.value)

if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    asyncio.run(main())
