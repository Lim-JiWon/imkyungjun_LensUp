from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas.collect import CollectRequest, CollectResponse
from services.public_data_collector import collect_public_data

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/collect", response_model=CollectResponse)
def run_collect(request: CollectRequest, db: Session = Depends(get_db)):
    collected_count = collect_public_data(db, request.source)

    return CollectResponse(
        success=True,
        message="데이터 수집 완료",
        collected_count=collected_count
    )
