from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class Aggregate(BaseModel):
    consumers: int = 0
    hits: int = 0
    two_xx_responses: int = 0
    three_xx_responses: int = 0
    four_xx_responses: int = 0
    five_xx_responses: int = 0


class TimeseriesPeriod(Enum):
    today = "today"
    last_7_days = "last_7_days"
    last_30_days = "last_30_days"


class Timeseries(BaseModel):
    period: str
    hits: int


class RequestDetails(BaseModel):
    method: str
    origin: str
    user_agent: str
    platform: str
    endpoint: str


class Metadata(BaseModel):
    request_details: RequestDetails
    status_code: int


class Stats(BaseModel):
    project_id: str
    request_time: datetime
    response_time: datetime
    metadata: Metadata


class ConsumersBreakdown(BaseModel):
    consumer: str
    hits: int


class PlatformBreakdown(BaseModel):
    platform: str
    hits: int


class UserAgentBreakdown(BaseModel):
    user_agent: str
    hits: int


class Breakdown(BaseModel):
    top_consumers: List[ConsumersBreakdown] = []
    top_platforms: List[PlatformBreakdown] = []
    top_user_agents: List[UserAgentBreakdown] = []
