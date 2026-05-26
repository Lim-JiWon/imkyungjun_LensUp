from sqlalchemy.orm import Session, joinedload

from models.issue import Issue


def get_issues(db: Session):
    issues = (
        db.query(Issue)
        .options(joinedload(Issue.summaries))
        .order_by(Issue.id.desc())
        .all()
    )

    result = []
    for issue in issues:
        summary_text = None
        forecast_text = None

        for item in issue.summaries:
            if item.summary_type == "summary":
                summary_text = item.summary_text
            elif item.summary_type == "forecast":
                forecast_text = item.summary_text

        result.append({
            "id": issue.id,
            "issue_key": issue.issue_key,
            "title": issue.title,
            "target": issue.target,
            "status": issue.status,
            "risk_level": issue.risk_level,
            "score": issue.score,
            "complaint_count": issue.complaint_count,
            "top_keyword": issue.top_keyword,
            "batch_id": issue.batch_id,
            "summary": summary_text,
            "forecast": forecast_text,
        })

    return result


def get_issue_detail(db: Session, issue_id: int):
    issue = (
        db.query(Issue)
        .options(joinedload(Issue.summaries))
        .filter(Issue.id == issue_id)
        .first()
    )

    if not issue:
        return None

    summary_text = None
    forecast_text = None

    for item in issue.summaries:
        if item.summary_type == "summary":
            summary_text = item.summary_text
        elif item.summary_type == "forecast":
            forecast_text = item.summary_text

    return {
        "id": issue.id,
        "issue_key": issue.issue_key,
        "title": issue.title,
        "target": issue.target,
        "status": issue.status,
        "risk_level": issue.risk_level,
        "score": issue.score,
        "complaint_count": issue.complaint_count,
        "top_keyword": issue.top_keyword,
        "batch_id": issue.batch_id,
        "summary": summary_text,
        "forecast": forecast_text,
    }
