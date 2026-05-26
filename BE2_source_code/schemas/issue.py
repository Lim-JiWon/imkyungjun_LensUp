from typing import Optional

from pydantic import BaseModel, Field


class KeywordTrendResponse(BaseModel):
    date: str
    value: int


class IssueBaseResponse(BaseModel):
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
    batch_id: Optional[str] = None
    summary: Optional[str] = None
    forecast: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    rising_keywords: list[str] = Field(default_factory=list)
    related_keywords: list[str] = Field(default_factory=list)
    causes: list[str] = Field(default_factory=list)
    keyword_trends: list[KeywordTrendResponse] = Field(default_factory=list)


class IssueListResponse(IssueBaseResponse):
    pass


class IssueDetailResponse(IssueBaseResponse):
    pass
