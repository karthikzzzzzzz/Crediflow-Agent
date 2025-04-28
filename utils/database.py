from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os 
from dotenv import load_dotenv

load_dotenv()

URL_DATABASE = os.getenv("POSTGRES_CONN_STRING")


engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autoflush=False,bind=engine)

Base= declarative_base()


# creates the session for the database ops
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()