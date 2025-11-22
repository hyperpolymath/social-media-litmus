"""Database connection and models"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass


class PolicyChange(Base):
    """Policy change model"""
    __tablename__ = "policy_changes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_document_id = Column(UUID(as_uuid=True), nullable=False)
    previous_snapshot_id = Column(UUID(as_uuid=True))
    current_snapshot_id = Column(UUID(as_uuid=True))
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    change_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="unknown")
    confidence_score = Column(Numeric(3, 2), default=0.00)
    affected_sections = Column(JSON, default=list)
    change_summary = Column(Text)
    impact_assessment = Column(Text)
    requires_member_notification = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    false_positive = Column(Boolean, default=False)
    metadata = Column(JSON, default=dict)


class NLPAnalysis(Base):
    """NLP analysis results model"""
    __tablename__ = "nlp_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_change_id = Column(UUID(as_uuid=True), nullable=False)
    detected_at = Column(DateTime, nullable=False)
    analysis_type = Column(String(100), nullable=False)
    model_name = Column(String(255))
    model_version = Column(String(100))
    result = Column(JSON, nullable=False)
    confidence_score = Column(Numeric(3, 2))
    processing_time_ms = Column(Integer)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class GuidanceDraft(Base):
    """Member guidance draft model"""
    __tablename__ = "guidance_drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    content_markdown = Column(Text, nullable=False)
    content_html = Column(Text)
    draft_type = Column(String(50), default="regular")
    status = Column(String(50), default="draft")
    related_changes = Column(JSON, default=list)
    target_platforms = Column(JSON, default=list)
    generated_by = Column(String(50))
    ai_model = Column(String(255))
    drafted_by = Column(String(255))
    drafted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime)
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    published_at = Column(DateTime)
    archived_at = Column(DateTime)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


async def init_db():
    """Initialize database connection"""
    # Test connection
    async with engine.begin() as conn:
        # Don't create tables - they're managed by migrations
        pass


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        yield session
