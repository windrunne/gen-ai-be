"""
Database models for LLM Lab
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Experiment(Base):
    """Experiment model - represents a single experiment run"""
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    responses = relationship("Response", back_populates="experiment", cascade="all, delete-orphan")


class Response(Base):
    """Response model - represents a single LLM response with parameters"""
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    
    # LLM Parameters
    temperature = Column(Float, nullable=False)
    top_p = Column(Float, nullable=False)
    max_tokens = Column(Integer, default=1000)
    
    # Response data
    text = Column(Text, nullable=False)
    finish_reason = Column(String(50))
    
    # Validation metadata (stores validation results)
    validation_metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    experiment = relationship("Experiment", back_populates="responses")
    metrics = relationship("Metric", back_populates="response", cascade="all, delete-orphan")


class Metric(Base):
    """Metric model - stores calculated quality metrics for responses"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)
    
    # Metric name and value
    name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    
    metadata_json = Column(JSONB, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    response = relationship("Response", back_populates="metrics")
