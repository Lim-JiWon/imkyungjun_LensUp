from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from database import SessionLocal
from schemas.analysis_result import AnalysisBatchRequest
from schemas.dashboard_map_data import DashboardMapDataRequest
from services.analysis_ingest_service import ingest_analysis_batch
from models.dashboard_extra_snapshot import DashboardExtraSnapshot

load_dotenv()

router = APIRouter(prefix="/admin/pipeline", tags=["admin-pipeline"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(x_api_key: str = Header(...)):
    server_api_key = os.getenv("PIPELINE_API_KEY")

    if not server_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PIPELINE_API_KEY is not configured on server.",
        )

    if x_api_key != server_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid pipeline api key.",
        )


def pydantic_to_dict(payload):
    if hasattr(payload, "model_dump"):
        return payload.model_dump()

    return payload.dict()


@router.post("/ingest")
def ingest_pipeline_result(
    payload: AnalysisBatchRequest,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    result = ingest_analysis_batch(db, payload)

    return {
        "message": "analysis batch ingested successfully",
        "batch_id": payload.batch_id,
        "target": payload.target,
        "saved_issue_count": result.get("saved_issue_count", 0),
        "skipped_issue_count": result.get("skipped_issue_count", 0),
    }


@router.post("/map-data")
def ingest_dashboard_map_data(
    payload: DashboardMapDataRequest,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    payload_dict = pydantic_to_dict(payload)

    batch_id = payload.batch_id

    if not batch_id:
        meta = payload.meta or {}
        batch_id = meta.get("batch_id") or meta.get("batchId")

    snapshot = DashboardExtraSnapshot(
        batch_id=batch_id,
        source=payload.source,
        target=payload.target,
        date_from=payload.date_from,
        date_to=payload.date_to,
        payload_json=payload_dict,
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "message": "dashboard map data snapshot saved successfully",
        "snapshot_id": snapshot.id,
        "batch_id": snapshot.batch_id,
        "source": snapshot.source,
        "target": snapshot.target,
        "date_from": snapshot.date_from,
        "date_to": snapshot.date_to,
        "region_rank_count": len(payload.region_rank),
        "organization_rank_count": len(payload.organization_rank),
        "category_stats_count": len(payload.category_stats),
        "issue_count": len(payload.issues),
    }
