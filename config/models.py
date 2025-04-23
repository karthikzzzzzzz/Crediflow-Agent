from config.database import Base
from sqlalchemy import Column,Integer,String

class Logs(Base):
    __tablename__='user_logs'
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    query=Column(String)
    response=Column(String)
