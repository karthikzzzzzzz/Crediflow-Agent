from sqlalchemy import Column, String, Text, TIMESTAMP,func, Integer,JSON,text,ARRAY,Float
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

class AgentState(Base):
    __tablename__ = "intelli_agent"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String)
    user_id = Column(String, nullable=False)
    lead_id = Column(String, nullable=False)
    realm_id = Column(String, nullable=False)
    trace_id = Column(String, nullable=True)
    span_id = Column(String, nullable=True)
    state = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

class AgentSemanticMemory(Base):
    __tablename__ = "agent_semantic_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False)
    realm_id = Column(String(64))
    session_id = Column(String(64))
    trace_id = Column(String(64))
    span_id = Column(String(64))
    case_id = Column(String(64))
    key = Column(Text, nullable=False)
    value = Column(Text)
    source = Column(Text)
    vector = Column(ARRAY(Float))
    tags = Column(ARRAY(Text))
    last_updated = Column(TIMESTAMP, nullable=False)

class AgentProceduralMemory(Base):
    __tablename__ = "agent_procedural_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_name = Column(Text)
    steps = Column(JSON)
    trigger_conditions = Column(JSON)
    created_by = Column(Text)
    created_at = Column(TIMESTAMP)
    case_id = Column(String(64))

class EpisodicMemory(Base):
    __tablename__ = "episodic_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False)
    realm_id = Column(String(64))
    case_id = Column(String(64))
    session_id = Column(String(64))
    trace_id = Column(String(64))
    span_id = Column(String(64))
    timestamp = Column(TIMESTAMP)
    summary = Column(Text)
    raw_state = Column(JSON)