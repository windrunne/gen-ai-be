"""
Experiment schemas
"""
from pydantic import BaseModel, Field
from typing import List


class ExperimentCreate(BaseModel):
    """Schema for creating a new experiment"""
    name: str = Field(..., min_length=1, max_length=255, description="Experiment name")
    prompt: str = Field(..., min_length=1, description="Input prompt for LLM")
    temperature_range: List[float] = Field(
        ..., 
        min_items=1,
        description="List of temperature values to test (0.0-2.0)"
    )
    top_p_range: List[float] = Field(
        ..., 
        min_items=1,
        description="List of top_p values to test (0.0-1.0)"
    )
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum tokens per response")


class ExperimentResponse(BaseModel):
    """Schema for experiment response"""
    id: int
    name: str
    prompt: str
    created_at: str
    
    class Config:
        from_attributes = True


class ExperimentDetail(ExperimentResponse):
    """Schema for detailed experiment view"""
    response_count: int = Field(default=0, description="Number of responses generated")
