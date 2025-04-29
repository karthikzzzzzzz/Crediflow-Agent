from kafka import KafkaConsumer
import json
import asyncio
from Document_verification_agent.services.document_verification import DocumentVerification
from utils.database import get_db
from utils.models import DocumentVerificationSchema
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from dependency_injector.wiring import inject, Provide
from Document_verification_agent.dependencies.containers import Container
import os

load_dotenv()

# Create a Kafka consumer to listen to the 'risk-graph' topic
consumer = KafkaConsumer(
    'document-verification',
    bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP_SERVERS")],  # Kafka server address from environment
    group_id='document-verification-id',                  # Consumer group ID
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),  # Deserialize messages from JSON
    auto_offset_reset='earliest',                 # Start reading from the earliest offset
    enable_auto_commit=True                       # Commit offsets automatically
)


@inject
async def process_message(
    message: dict,
    chat: DocumentVerification = Provide[Container.document_service]

):
    # Get a database session
    db_gen = get_db()
    db: Session = next(db_gen)
    try:
        # Extract necessary fields from the incoming Kafka message
        query = message["query"]
        query_id = message["query_id"]
        realm_id = message["realm_id"]
        user_id = message["user_id"]
        lead_id = message["lead_id"]

        # Call the DataAcquisition agent to process the query
        result = await chat.run_query(query,user_id,realm_id,lead_id)

        # Prepare a database log entry with the agent's response and metadata
        log_entry = DocumentVerificationSchema(
            user_id=user_id,
            realm_id=realm_id,
            lead_id=lead_id,
            session_id=result["session_id"],
            trace_id=result["trace_id"],
            query_id=query_id,
            query=query,
            span_id= result["span_id"],
            response=result["agent_response"]
        )

        # Add and commit the log entry to the database
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

    except Exception as e:
        print(f"Error processing message: {str(e)}")
    finally:
        db.close()

async def main():
    print("Kafka listener started...")
    # Continuously listen to Kafka for new messages
    for message in consumer:
        await process_message(message.value)

if __name__ == "__main__":
    # Initialize the dependency injection container
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    asyncio.run(main())
