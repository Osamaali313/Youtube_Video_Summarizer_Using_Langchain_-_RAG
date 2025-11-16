"""
Database models for PostgreSQL
"""
from sqlalchemy import create_engine, Column, String, Integer, Text, JSON, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
import json

from app.config import settings

# Create base class
Base = declarative_base()

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================================================
# Models
# =============================================================================

class Summary(Base):
    """Video summary model"""
    __tablename__ = "summaries"

    id = Column(String, primary_key=True, index=True)
    video_id = Column(String, index=True, nullable=False)
    video_url = Column(String, nullable=False)
    video_title = Column(String)
    video_author = Column(String)
    video_duration = Column(Integer)  # Duration in seconds
    thumbnail_url = Column(String)

    # Summary data
    content = Column(Text, nullable=False)
    mode = Column(String, nullable=False)  # quick, standard, research, educational
    language = Column(String, default="en")

    # Timestamps and citations
    timestamps = Column(JSON)  # List of {time, text} dicts
    citations = Column(JSON)   # List of citation strings

    # Metadata
    processing_time = Column(Float)  # Processing time in seconds
    credibility_score = Column(Float)  # From fact-checker (0.0-1.0)

    # Features used
    features = Column(JSON)  # Dict of enabled features

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "video_id": self.video_id,
            "video_url": self.video_url,
            "video_title": self.video_title,
            "video_author": self.video_author,
            "video_duration": self.video_duration,
            "thumbnail_url": self.thumbnail_url,
            "content": self.content,
            "mode": self.mode,
            "language": self.language,
            "timestamps": self.timestamps,
            "citations": self.citations,
            "processing_time": self.processing_time,
            "credibility_score": self.credibility_score,
            "features": self.features,
            "created_at": int(self.created_at.timestamp() * 1000) if self.created_at else None,
            "updated_at": int(self.updated_at.timestamp() * 1000) if self.updated_at else None,
        }


class Conversation(Base):
    """Q&A conversation model"""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    summary_id = Column(String, index=True, nullable=False)
    video_id = Column(String, index=True, nullable=False)

    # Conversation data
    messages = Column(JSON, nullable=False)  # List of {role, content, timestamp} dicts

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "summary_id": self.summary_id,
            "video_id": self.video_id,
            "messages": self.messages,
            "created_at": int(self.created_at.timestamp() * 1000) if self.created_at else None,
            "updated_at": int(self.updated_at.timestamp() * 1000) if self.updated_at else None,
        }


class FactCheck(Base):
    """Fact-check results model"""
    __tablename__ = "fact_checks"

    id = Column(String, primary_key=True, index=True)
    summary_id = Column(String, index=True, nullable=False)
    video_id = Column(String, index=True, nullable=False)

    # Fact-check data
    claims = Column(JSON, nullable=False)  # List of claim dicts
    overall_assessment = Column(Text)
    credibility_score = Column(Float)
    total_claims = Column(Integer)
    checked_claims = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "summary_id": self.summary_id,
            "video_id": self.video_id,
            "claims": self.claims,
            "overall_assessment": self.overall_assessment,
            "credibility_score": self.credibility_score,
            "total_claims": self.total_claims,
            "checked_claims": self.checked_claims,
            "created_at": int(self.created_at.timestamp() * 1000) if self.created_at else None,
        }


class ResearchResult(Base):
    """Research findings model"""
    __tablename__ = "research_results"

    id = Column(String, primary_key=True, index=True)
    summary_id = Column(String, index=True, nullable=False)
    video_id = Column(String, index=True, nullable=False)

    # Research data
    topic = Column(String, nullable=False)
    findings = Column(JSON)  # List of finding dicts
    summary = Column(Text)
    sources = Column(JSON)   # List of source URLs
    search_query = Column(String)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "summary_id": self.summary_id,
            "video_id": self.video_id,
            "topic": self.topic,
            "findings": self.findings,
            "summary": self.summary,
            "sources": self.sources,
            "search_query": self.search_query,
            "created_at": int(self.created_at.timestamp() * 1000) if self.created_at else None,
        }


class APIUsage(Base):
    """API usage tracking"""
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String, index=True, nullable=False)
    ip_address = Column(String, index=True)
    user_agent = Column(String)

    # Request data
    video_id = Column(String, index=True)
    mode = Column(String)
    processing_time = Column(Float)
    success = Column(Boolean, default=True)
    error_message = Column(Text)

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "ip_address": self.ip_address,
            "video_id": self.video_id,
            "mode": self.mode,
            "processing_time": self.processing_time,
            "success": self.success,
            "timestamp": int(self.timestamp.timestamp() * 1000) if self.timestamp else None,
        }


# =============================================================================
# Database Functions
# =============================================================================

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_summary(db_session, summary_data: dict) -> Summary:
    """Create a new summary"""
    summary = Summary(**summary_data)
    db_session.add(summary)
    db_session.commit()
    db_session.refresh(summary)
    return summary


def get_summary(db_session, summary_id: str) -> Optional[Summary]:
    """Get summary by ID"""
    return db_session.query(Summary).filter(Summary.id == summary_id).first()


def get_summaries_by_video(db_session, video_id: str) -> list[Summary]:
    """Get all summaries for a video"""
    return db_session.query(Summary).filter(Summary.video_id == video_id).all()


def delete_summary(db_session, summary_id: str) -> bool:
    """Delete a summary"""
    summary = get_summary(db_session, summary_id)
    if summary:
        db_session.delete(summary)
        db_session.commit()
        return True
    return False
