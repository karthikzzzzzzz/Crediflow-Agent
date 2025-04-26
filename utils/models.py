from sqlalchemy import Column, String, Text, TIMESTAMP,func, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from utils.database import Base

class DataAcquisitionSchema(Base):
    __tablename__ = "data_acquisition"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String)
    realm_id = Column(String)
    lead_id = Column(String)
    session_id = Column(UUID, nullable=False)
    trace_id = Column(String, nullable=False)
    query_id = Column(UUID(as_uuid=True))
    span_id = Column(String)
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    

class DocumentVerificationSchema(Base):
    __tablename__ = "document_verification"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String)
    realm_id = Column(String)
    lead_id = Column(String)
    session_id = Column(UUID, nullable=False)
    trace_id = Column(String, nullable=False)
    query_id = Column(UUID(as_uuid=True))
    span_id = Column(String)
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    

class EligibilityCheckerSchema(Base):
    __tablename__ = "eligibility_checker"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String)
    realm_id = Column(String)
    lead_id = Column(String)
    session_id = Column(UUID, nullable=False)
    trace_id = Column(String, nullable=False)
    query_id = Column(UUID(as_uuid=True))
    span_id = Column(String)
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

class ReportGenerationSchema(Base):
    __tablename__ = "report_generation"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String)
    realm_id = Column(String)
    lead_id = Column(String)
    span_id = Column(String)
    session_id = Column(UUID, nullable=False)
    trace_id = Column(String, nullable=False)
    query_id = Column(UUID(as_uuid=True))
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

class ScreeningOpsSchema(Base):
    __tablename__ = "screening_ops"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String)
    realm_id = Column(String)
    lead_id = Column(String)
    span_id = Column(String)
    session_id = Column(UUID, nullable=False)
    trace_id = Column(String, nullable=False)
    query_id = Column(UUID(as_uuid=True))
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Logs(Base):
    __tablename__='user_logs'
    __table_args__ = {'extend_existing': True}
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    query=Column(String)
    response=Column(String)

class IntelliAgentSchema(Base):
    __tablename__ = "intelliagent_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    realm_id = Column(String(255), nullable=False)
    lead_id = Column(Integer, nullable=False)
    session_id = Column(String(255), nullable=False)
    trace_id = Column(String(255), unique=True, nullable=False)
    span_id = Column(String(255), nullable=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())