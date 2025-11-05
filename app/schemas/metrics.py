"""
Metrics summary schemas
"""
from pydantic import BaseModel, Field
from typing import List


class MetricResponseData(BaseModel):
    """Schema for metric response data in summary"""
    response_id: int
    temperature: float
    top_p: float
    value: float


class MetricSummaryItem(BaseModel):
    """Schema for individual metric summary"""
    mean: float
    median: float
    min: float
    max: float
    std_dev: float
    count: int
    responses: List[MetricResponseData]


class MetricsSummary(BaseModel):
    """Schema for complete metrics summary"""
    # This will be a dict mapping metric names to MetricSummaryItem
    # We use dict[str, MetricSummaryItem] for flexibility
    pass
