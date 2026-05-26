from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DashboardMapDataRequest(BaseModel):
    batch_id: Optional[str] = None
    source: Optional[str] = None
    target: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None

    meta: Dict[str, Any] = Field(default_factory=dict)
    region_summary: Dict[str, Any] = Field(default_factory=dict)
    organization_summary: Dict[str, Any] = Field(default_factory=dict)

    region_rank: List[Dict[str, Any]] = Field(default_factory=list)
    organization_rank: List[Dict[str, Any]] = Field(default_factory=list)
    category_stats: List[Dict[str, Any]] = Field(default_factory=list)
    issues: List[Dict[str, Any]] = Field(default_factory=list)


class DashboardMapDataResponse(BaseModel):
    id: Optional[int] = None
    batch_id: Optional[str] = None
    source: Optional[str] = None
    target: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None

    meta: Dict[str, Any] = Field(default_factory=dict)
    region_summary: Dict[str, Any] = Field(default_factory=dict)
    organization_summary: Dict[str, Any] = Field(default_factory=dict)

    region_rank: List[Dict[str, Any]] = Field(default_factory=list)
    organization_rank: List[Dict[str, Any]] = Field(default_factory=list)
    category_stats: List[Dict[str, Any]] = Field(default_factory=list)
    issues: List[Dict[str, Any]] = Field(default_factory=list)

    created_at: Optional[str] = None
