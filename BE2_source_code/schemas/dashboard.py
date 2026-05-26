from typing import List, Optional
from pydantic import BaseModel, Field


class KeywordTrendResponse(BaseModel):
    date: str
    value: int


class DashboardStatsResponse(BaseModel):
    total_issues: int
    high_risk_issues: int
    average_score: float


class DashboardIssueItemResponse(BaseModel):
    id: int
    issue_key: Optional[str] = None
    title: str
    source: Optional[str] = None
    target: Optional[str] = None
    status: Optional[str] = None
    risk_level: Optional[str] = None
    score: Optional[float] = None
    complaint_count: Optional[int] = None
    top_keyword: Optional[str] = None
    category: Optional[str] = None
    category_tags: List[str] = Field(default_factory=list)
    cluster_keywords: List[str] = Field(default_factory=list)
    batch_id: Optional[str] = None
    summary: Optional[str] = None


class DashboardListResponse(BaseModel):
    stats: DashboardStatsResponse
    issues: List[DashboardIssueItemResponse] = Field(default_factory=list)


class DashboardDetailResponse(BaseModel):
    id: int
    issue_key: Optional[str] = None
    title: str
    summary: Optional[str] = None
    forecast: Optional[str] = None

    risk_level: Optional[str] = None
    score: Optional[float] = None
    complaint_count: Optional[int] = None
    top_keyword: Optional[str] = None
    category: Optional[str] = None

    signal_status: Optional[str] = None
    trend_direction: Optional[str] = None
    signal_message: Optional[str] = None

    keywords: List[str] = Field(default_factory=list)
    rising_keywords: List[str] = Field(default_factory=list)
    related_keywords: List[str] = Field(default_factory=list)
    category_tags: List[str] = Field(default_factory=list)
    cluster_keywords: List[str] = Field(default_factory=list)
    causes: List[str] = Field(default_factory=list)
    keyword_trends: List[KeywordTrendResponse] = Field(default_factory=list)
