from kafka import KafkaConsumer
import json
import asyncio
from Back_office_agent.services.back_office import chat
from utils.database import get_db
from utils.models import Logs
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

consumer = KafkaConsumer(
    'back-office',
    bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP_SERVERS")],
    group_id="back-office-id",
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

async def process_message(message):
    db_gen = get_db()
    db: Session = next(db_gen)
    try:
        query = message["query"]
        log_id = message["log_id"]
        result = await chat.run_query(query)
        log_entry = Logs(id=log_id, query=query, response=result["responses"])
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

    except Exception as e:
        print(f"Error processing message: {str(e)}")


async def main():
    print("Kafka listener started...")
    for message in consumer:
        await process_message(message.value)

if __name__ == "__main__":
    asyncio.run(main())
