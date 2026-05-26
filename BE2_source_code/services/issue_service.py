from sqlalchemy.orm import Session, joinedload

from models.issue import Issue


def get_issues(db: Session):
    issues = (
        db.query(Issue)
        .options(
            joinedload(Issue.summaries),
            joinedload(Issue.keywords),
            joinedload(Issue.causes),
        )
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

        keyword_items = [k for k in issue.keywords if k.keyword_type == "keyword"]
        rising_items = [k for k in issue.keywords if k.keyword_type == "rising"]

        keyword_list = [
            item.keyword
            for item in sorted(keyword_items, key=lambda x: x.keyword_order)
        ]

        rising_keyword_list = [
            item.keyword
            for item in sorted(rising_items, key=lambda x: x.keyword_order)
        ]

        cause_list = [
            item.cause_text
            for item in sorted(issue.causes, key=lambda x: x.cause_order)
        ]

        result.append({
            "id": issue.id,
            "issue_key": issue.issue_key,
            "title": issue.title,
            "source": issue.source,
            "target": issue.target,
            "status": issue.status,
            "risk_level": issue.risk_level,
            "score": issue.score,
            "complaint_count": issue.complaint_count,
            "top_keyword": issue.top_keyword,
            "batch_id": issue.batch_id,
            "summary": summary_text,
            "forecast": forecast_text,
            "keywords": keyword_list,
            "rising_keywords": rising_keyword_list,
            "causes": cause_list,
        })

    return result


def get_issue_detail(db: Session, issue_id: int):
    issue = (
        db.query(Issue)
        .options(
            joinedload(Issue.summaries),
            joinedload(Issue.keywords),
            joinedload(Issue.causes),
        )
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

        # 🔥 먼저 필터 → 그 다음 정렬
    keyword_items = [k for k in issue.keywords if k.keyword_type == "keyword"]
    rising_items = [k for k in issue.keywords if k.keyword_type == "rising"]

    keyword_list = [
        item.keyword
        for item in sorted(keyword_items, key=lambda x: x.keyword_order)
    ]

    rising_keyword_list = [
        item.keyword
        for item in sorted(rising_items, key=lambda x: x.keyword_order)
    ]

    cause_list = [
        item.cause_text
        for item in sorted(issue.causes, key=lambda x: x.cause_order)
    ]

    return {
        "id": issue.id,
        "issue_key": issue.issue_key,
        "title": issue.title,
        "source": issue.source,
        "target": issue.target,
        "status": issue.status,
        "risk_level": issue.risk_level,
        "score": issue.score,
        "complaint_count": issue.complaint_count,
        "top_keyword": issue.top_keyword,
        "batch_id": issue.batch_id,
        "summary": summary_text,
        "forecast": forecast_text,
        "keywords": keyword_list,
        "rising_keywords": rising_keyword_list,
        "causes": cause_list,
    }
