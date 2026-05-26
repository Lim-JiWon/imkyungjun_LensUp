from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.issue import Issue
from models.issue_summary import IssueSummary
from models.issue_keyword import IssueKeyword
from models.issue_cause import IssueCause
from models.issue_keyword_trend import IssueKeywordTrend
from models.dashboard_region_ranking import DashboardRegionRanking
from models.dashboard_extra_snapshot import DashboardExtraSnapshot
from schemas.dashboard import DashboardListResponse, DashboardDetailResponse
from schemas.dashboard_map_data import DashboardMapDataResponse

router = APIRouter(tags=["dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_trend_direction(keyword_trends):
    if not keyword_trends or len(keyword_trends) < 2:
        return "no_data"

    first_value = keyword_trends[0].get("value")
    last_value = keyword_trends[-1].get("value")

    if first_value is None or last_value is None:
        return "no_data"

    if first_value == 0:
        if last_value > 0:
            return "increasing"
        return "stable"

    change_rate = (last_value - first_value) / abs(first_value)

    if change_rate >= 0.05:
        return "increasing"

    if change_rate <= -0.05:
        return "decreasing"

    return "stable"


def get_signal_status(risk_level, score, complaint_count, trend_direction):
    score = score or 0
    complaint_count = complaint_count or 0

    if risk_level in ["high", "critical"] or score >= 80:
        if trend_direction == "increasing":
            return "확산 가능"
        return "고위험 관찰"

    if trend_direction == "increasing":
        return "증가 징후"

    if complaint_count >= 1000 or score >= 60:
        return "관찰 필요"

    if trend_direction == "decreasing":
        return "완화 흐름"

    return "지속 관찰"


def build_signal_message(
    top_keyword,
    related_keywords,
    trend_direction,
    signal_status,
    score,
    complaint_count,
):
    issue_name = top_keyword or "해당 이슈"
    score = score or 0
    complaint_count = complaint_count or 0

    related = [keyword for keyword in related_keywords if keyword]
    related_text = ", ".join(related[:3]) if related else "관련 민원"

    if trend_direction == "increasing":
        return (
            f"추후에 {issue_name} 관련 민원은 {related_text} 문제와 함께 "
            f"더 넓은 민원 이슈로 확산될 가능성이 있습니다. "
            f"최근 키워드 흐름이 증가하고 있으며, 징후 점수는 {score}점, "
            f"관련 민원 건수는 {complaint_count}건으로 확인됩니다. "
            f"이 흐름이 지속될 경우 단순 불편 제기를 넘어 신고, 단속 요구, "
            f"행정 대응 수요 증가로 이어질 수 있습니다."
        )

    if trend_direction == "decreasing":
        return (
            f"현재 {issue_name} 관련 키워드 흐름은 다소 완화되는 모습을 보이고 있습니다. "
            f"다만 추후에 {related_text} 문제가 반복될 경우 동일한 민원 유형이 "
            f"다시 확산될 가능성이 있습니다. "
            f"따라서 민원 건수와 연관 키워드 변화를 지속적으로 확인할 필요가 있습니다."
        )

    if trend_direction == "stable":
        return (
            f"추후에 {issue_name} 관련 민원은 {related_text}를 중심으로 "
            f"일정 수준 이상 지속될 가능성이 있습니다. "
            f"현재 급격한 증가는 아니지만, 징후 점수 {score}점과 "
            f"민원 건수 {complaint_count}건을 고려하면 반복적인 민원 흐름으로 "
            f"이어질 수 있어 지속적인 관찰이 필요합니다."
        )

    return (
        f"추후에 {issue_name} 관련 민원은 {related_text}와 연결되어 "
        f"추가 민원으로 확산될 가능성이 있습니다. "
        f"현재 키워드 트렌드 데이터가 충분하지 않으므로, 향후 민원 건수와 "
        f"연관 키워드 변화가 누적될 경우 확산 여부를 더 명확히 판단할 수 있습니다."
    )


@router.get("/dashboard", response_model=DashboardListResponse)
def get_dashboard(db: Session = Depends(get_db)):
    all_issues = db.query(Issue).all()

    total_issues = len(all_issues)
    high_risk_issues = len(
        [
            issue
            for issue in all_issues
            if issue.risk_level in ["high", "critical"]
        ]
    )

    score_values = [issue.score for issue in all_issues if issue.score is not None]
    average_score = round(sum(score_values) / len(score_values), 1) if score_values else 0.0

    issues = (
        db.query(Issue)
        .order_by(Issue.id.desc())
        .limit(10)
        .all()
    )

    result = []

    for issue in issues:
        summary_row = (
            db.query(IssueSummary)
            .filter(
                IssueSummary.issue_id == issue.id,
                IssueSummary.summary_type == "summary",
            )
            .first()
        )

        summary = summary_row.summary_text if summary_row else None

        issue_keywords = (
            db.query(IssueKeyword)
            .filter(IssueKeyword.issue_id == issue.id)
            .order_by(IssueKeyword.keyword_order.asc())
            .all()
        )

        category_tags = [
            k.keyword
            for k in issue_keywords
            if k.keyword_type == "category_tag"
        ]

        cluster_keywords = [
            k.keyword
            for k in issue_keywords
            if k.keyword_type == "cluster_keyword"
        ]

        result.append(
            {
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
                "category": issue.category,
                "category_tags": category_tags,
                "cluster_keywords": cluster_keywords,
                "batch_id": issue.batch_id,
                "summary": summary,
            }
        )

    return {
        "stats": {
            "total_issues": total_issues,
            "high_risk_issues": high_risk_issues,
            "average_score": average_score,
        },
        "issues": result,
    }


@router.get("/dashboard/map-data", response_model=DashboardMapDataResponse)
def get_dashboard_map_data(db: Session = Depends(get_db)):
    latest_snapshot = (
        db.query(DashboardExtraSnapshot)
        .order_by(
            DashboardExtraSnapshot.created_at.desc(),
            DashboardExtraSnapshot.id.desc(),
        )
        .first()
    )

    if not latest_snapshot:
        return {
            "id": None,
            "batch_id": None,
            "source": None,
            "target": None,
            "date_from": None,
            "date_to": None,
            "meta": {},
            "region_summary": {},
            "organization_summary": {},
            "region_rank": [],
            "organization_rank": [],
            "category_stats": [],
            "issues": [],
            "created_at": None,
        }

    payload = latest_snapshot.payload_json or {}

    return {
        "id": latest_snapshot.id,
        "batch_id": latest_snapshot.batch_id,
        "source": latest_snapshot.source,
        "target": latest_snapshot.target,
        "date_from": latest_snapshot.date_from,
        "date_to": latest_snapshot.date_to,
        "meta": payload.get("meta", {}),
        "region_summary": payload.get("region_summary", {}),
        "organization_summary": payload.get("organization_summary", {}),
        "region_rank": payload.get("region_rank", []),
        "organization_rank": payload.get("organization_rank", []),
        "category_stats": payload.get("category_stats", []),
        "issues": payload.get("issues", []),
        "created_at": latest_snapshot.created_at.isoformat() if latest_snapshot.created_at else None,
    }


@router.get("/dashboard/region-rankings")
def get_region_rankings(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    latest_row = (
        db.query(DashboardRegionRanking)
        .order_by(
            DashboardRegionRanking.created_at.desc(),
            DashboardRegionRanking.id.desc(),
        )
        .first()
    )

    if not latest_row:
        return {
            "batch_id": None,
            "source": None,
            "target": None,
            "date_from": None,
            "date_to": None,
            "count": 0,
            "region_rankings": [],
        }

    rankings = (
        db.query(DashboardRegionRanking)
        .filter(DashboardRegionRanking.batch_id == latest_row.batch_id)
        .order_by(DashboardRegionRanking.rank.asc())
        .limit(limit)
        .all()
    )

    return {
        "batch_id": latest_row.batch_id,
        "source": latest_row.source,
        "target": latest_row.target,
        "date_from": latest_row.date_from,
        "date_to": latest_row.date_to,
        "count": len(rankings),
        "region_rankings": [
            {
                "rank": row.rank,
                "region": row.region,
                "count": row.count,
                "ratio": row.ratio,
            }
            for row in rankings
        ],
    }


@router.get("/dashboard/categories")
def get_dashboard_categories(db: Session = Depends(get_db)):
    issues = (
        db.query(Issue)
        .order_by(Issue.id.desc())
        .all()
    )

    category_map = {}

    for issue in issues:
        category_name = issue.category or "미분류"

        if category_name not in category_map:
            category_map[category_name] = {
                "category": category_name,
                "issue_count": 0,
                "high_risk_count": 0,
                "score_values": [],
                "top_keywords": set(),
                "cluster_keywords": set(),
                "issues": [],
            }

        category_group = category_map[category_name]

        summary_row = (
            db.query(IssueSummary)
            .filter(
                IssueSummary.issue_id == issue.id,
                IssueSummary.summary_type == "summary",
            )
            .first()
        )

        summary = summary_row.summary_text if summary_row else None

        if issue.risk_level in ["high", "critical"]:
            category_group["high_risk_count"] += 1

        if issue.score is not None:
            category_group["score_values"].append(issue.score)

        if issue.top_keyword:
            category_group["top_keywords"].add(issue.top_keyword)

        cluster_rows = (
            db.query(IssueKeyword)
            .filter(
                IssueKeyword.issue_id == issue.id,
                IssueKeyword.keyword_type == "cluster_keyword",
            )
            .order_by(IssueKeyword.keyword_order.asc())
            .all()
        )

        for row in cluster_rows:
            if row.keyword:
                category_group["cluster_keywords"].add(row.keyword)

        category_group["issue_count"] += 1

        category_group["issues"].append(
            {
                "id": issue.id,
                "issue_key": issue.issue_key,
                "title": issue.title,
                "summary": summary,
                "risk_level": issue.risk_level,
                "score": issue.score,
                "complaint_count": issue.complaint_count,
                "top_keyword": issue.top_keyword,
                "category": category_name,
            }
        )

    categories = []

    for category_data in category_map.values():
        score_values = category_data.pop("score_values")

        average_score = (
            round(sum(score_values) / len(score_values), 1)
            if score_values
            else 0.0
        )

        categories.append(
            {
                "category": category_data["category"],
                "issue_count": category_data["issue_count"],
                "high_risk_count": category_data["high_risk_count"],
                "average_score": average_score,
                "top_keywords": list(category_data["top_keywords"])[:10],
                "cluster_keywords": list(category_data["cluster_keywords"])[:10],
                "issues": category_data["issues"],
            }
        )

    categories.sort(
        key=lambda item: (
            item["issue_count"],
            item["average_score"],
        ),
        reverse=True,
    )

    return {
        "count": len(categories),
        "categories": categories,
    }


@router.get("/dashboard/{issue_id}", response_model=DashboardDetailResponse)
def get_dashboard_detail(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    summary_row = (
        db.query(IssueSummary)
        .filter(
            IssueSummary.issue_id == issue.id,
            IssueSummary.summary_type == "summary",
        )
        .first()
    )
    summary = summary_row.summary_text if summary_row else None

    forecast_row = (
        db.query(IssueSummary)
        .filter(
            IssueSummary.issue_id == issue.id,
            IssueSummary.summary_type == "forecast",
        )
        .first()
    )
    forecast = forecast_row.summary_text if forecast_row else None

    issue_keywords = (
        db.query(IssueKeyword)
        .filter(IssueKeyword.issue_id == issue.id)
        .order_by(IssueKeyword.keyword_order.asc())
        .all()
    )

    keywords = [
        k.keyword
        for k in issue_keywords
        if k.keyword_type == "keyword"
    ]

    rising_keywords = [
        k.keyword
        for k in issue_keywords
        if k.keyword_type == "rising_keyword"
    ]

    related_keywords = [
        k.keyword
        for k in issue_keywords
        if k.keyword_type == "related_keyword"
    ]

    category_tags = [
        k.keyword
        for k in issue_keywords
        if k.keyword_type == "category_tag"
    ]

    cluster_keywords = [
        k.keyword
        for k in issue_keywords
        if k.keyword_type == "cluster_keyword"
    ]

    causes = [
        c.cause_text
        for c in db.query(IssueCause)
        .filter(IssueCause.issue_id == issue.id)
        .order_by(IssueCause.cause_order.asc())
    ]

    keyword_trends = [
        {
            "date": t.trend_date,
            "value": t.trend_value,
        }
        for t in db.query(IssueKeywordTrend)
        .filter(IssueKeywordTrend.issue_id == issue.id)
        .order_by(IssueKeywordTrend.trend_order.asc())
    ]

    trend_direction = get_trend_direction(keyword_trends)

    signal_status = get_signal_status(
        issue.risk_level,
        issue.score,
        issue.complaint_count,
        trend_direction,
    )

    signal_message = build_signal_message(
        issue.top_keyword,
        related_keywords,
        trend_direction,
        signal_status,
        issue.score,
        issue.complaint_count,
    )

    return {
        "id": issue.id,
        "issue_key": issue.issue_key,
        "title": issue.title,
        "summary": summary,
        "forecast": forecast,
        "risk_level": issue.risk_level,
        "score": issue.score,
        "complaint_count": issue.complaint_count,
        "top_keyword": issue.top_keyword,
        "category": issue.category,
        "signal_status": signal_status,
        "trend_direction": trend_direction,
        "signal_message": signal_message,
        "keywords": keywords,
        "rising_keywords": rising_keywords,
        "related_keywords": related_keywords,
        "category_tags": category_tags,
        "cluster_keywords": cluster_keywords,
        "causes": causes,
        "keyword_trends": keyword_trends,
    }
