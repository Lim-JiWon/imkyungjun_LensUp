from typing import List, Optional
from pydantic import BaseModel, Field


class KeywordTrendItem(BaseModel):
    date: str
    value: int


class RegionRankingItem(BaseModel):
    rank: int
    region: str
    count: int
    ratio: Optional[float] = None


class OrganizationRankingItem(BaseModel):
    rank: int
    organization: str
    count: int
    ratio: Optional[float] = None


class DashboardExtrasRequest(BaseModel):
    region_rankings: List[RegionRankingItem] = Field(default_factory=list)
    organization_rankings: List[OrganizationRankingItem] = Field(default_factory=list)


class AnalysisIssueItem(BaseModel):
    issue_key: str
    issue_type: str
    title: str
    summary: str

    forecast: Optional[str] = None

    causes: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    rising_keywords: List[str] = Field(default_factory=list)
    related_keywords: List[str] = Field(default_factory=list)
    keyword_trends: List[KeywordTrendItem] = Field(default_factory=list)
    search_aliases: List[str] = Field(default_factory=list)

    category: Optional[str] = None
    category_tags: List[str] = Field(default_factory=list)
    cluster_keywords: List[str] = Field(default_factory=list)

    status: str
    risk_level: str
    score: float
    complaint_count: int
    top_keyword: str


class AnalysisBatchRequest(BaseModel):
    batch_id: str
    generated_at: str
    source: Optional[str] = None
    target: str
    date_from: str
    date_to: str

    dashboard_extras: Optional[DashboardExtrasRequest] = None

    issues: List[AnalysisIssueItem]
