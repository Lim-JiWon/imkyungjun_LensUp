from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas.issue import IssueListResponse, IssueDetailResponse
from services.issue_service import get_issues, get_issue_detail

router = APIRouter(prefix="/issues", tags=["issues"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[IssueListResponse])
def read_issues(db: Session = Depends(get_db)):
    issues = get_issues(db)
    return issues


@router.get("/{issue_id}", response_model=IssueDetailResponse)
def read_issue_detail(issue_id: int, db: Session = Depends(get_db)):
    issue = get_issue_detail(db, issue_id)

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return issue
