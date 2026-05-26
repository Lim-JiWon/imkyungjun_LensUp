from sqlalchemy.orm import Session

from models.issue import Issue
from models.issue_summary import IssueSummary
from models.issue_keyword import IssueKeyword
from models.issue_cause import IssueCause
from models.issue_keyword_trend import IssueKeywordTrend
from models.issue_search_alias import IssueSearchAlias
from models.dashboard_region_ranking import DashboardRegionRanking
from schemas.analysis_result import AnalysisBatchRequest


def build_search_aliases(item):
    aliases = []

    # 백엔드1이 명시적으로 준 검색 연관어
    aliases.extend(item.search_aliases or [])

    # 대표 키워드
    if item.top_keyword:
        aliases.append(item.top_keyword)

    # 핵심 검색 대상
    aliases.extend(item.keywords or [])
    aliases.extend(item.related_keywords or [])

    # 주의:
    # category_tags, cluster_keywords는 분야/묶음 표시용 데이터이므로
    # 검색 연관어에 자동 포함하지 않는다.
    # 포함하면 "자동차"처럼 넓은 단어 때문에 관련 없는 이슈가 검색될 수 있다.

    cleaned_aliases = []
    seen = set()

    for alias in aliases:
        if not alias:
            continue

        cleaned = alias.strip()

        if not cleaned:
            continue

        if cleaned in seen:
            continue

        seen.add(cleaned)
        cleaned_aliases.append(cleaned)

    return cleaned_aliases


def save_search_aliases(db: Session, issue_id: int, item):
    aliases = build_search_aliases(item)

    if not aliases:
        return

    existing_aliases = {
        row.alias
        for row in db.query(IssueSearchAlias)
        .filter(IssueSearchAlias.issue_id == issue_id)
        .all()
    }

    for idx, alias in enumerate(aliases):
        if alias in existing_aliases:
            continue

        alias_row = IssueSearchAlias(
            issue_id=issue_id,
            alias=alias,
            alias_order=idx,
        )
        db.add(alias_row)


def save_keyword_list(db: Session, issue_id: int, keywords, keyword_type: str):
    if not keywords:
        return

    existing_rows = (
        db.query(IssueKeyword)
        .filter(
            IssueKeyword.issue_id == issue_id,
            IssueKeyword.keyword_type == keyword_type,
        )
        .all()
    )

    existing_keywords = {row.keyword for row in existing_rows if row.keyword}

    max_order = -1
    for row in existing_rows:
        if row.keyword_order is not None and row.keyword_order > max_order:
            max_order = row.keyword_order

    next_order = max_order + 1

    for keyword in keywords:
        if not keyword:
            continue

        cleaned_keyword = keyword.strip()

        if not cleaned_keyword:
            continue

        if cleaned_keyword in existing_keywords:
            continue

        keyword_row = IssueKeyword(
            issue_id=issue_id,
            keyword=cleaned_keyword,
            keyword_type=keyword_type,
            keyword_order=next_order,
        )
        db.add(keyword_row)

        existing_keywords.add(cleaned_keyword)
        next_order += 1


def save_region_rankings(db: Session, payload: AnalysisBatchRequest):
    if not payload.dashboard_extras:
        return

    region_rankings = payload.dashboard_extras.region_rankings

    if not region_rankings:
        return

    db.query(DashboardRegionRanking).filter(
        DashboardRegionRanking.batch_id == payload.batch_id
    ).delete(synchronize_session=False)

    for item in region_rankings:
        ranking_row = DashboardRegionRanking(
            batch_id=payload.batch_id,
            source=payload.source,
            target=payload.target,
            date_from=payload.date_from,
            date_to=payload.date_to,
            rank=item.rank,
            region=item.region,
            count=item.count,
            ratio=item.ratio,
        )
        db.add(ranking_row)


def ingest_analysis_batch(db: Session, payload: AnalysisBatchRequest):
    saved_issue_count = 0
    skipped_issue_count = 0

    save_region_rankings(db, payload)

    for item in payload.issues:
        existing_issue = (
            db.query(Issue)
            .filter(Issue.issue_key == item.issue_key)
            .first()
        )

        if existing_issue:
            if item.category:
                existing_issue.category = item.category

            save_keyword_list(db, existing_issue.id, item.category_tags, "category_tag")
            save_keyword_list(db, existing_issue.id, item.cluster_keywords, "cluster_keyword")
            save_search_aliases(db, existing_issue.id, item)

            skipped_issue_count += 1
            continue

        new_issue = Issue(
            issue_key=item.issue_key,
            title=item.title,
            source=payload.source,
            target=payload.target,
            status=item.status,
            risk_level=item.risk_level,
            score=item.score,
            complaint_count=item.complaint_count,
            top_keyword=item.top_keyword,
            category=item.category,
            batch_id=payload.batch_id,
        )

        db.add(new_issue)
        db.flush()

        summary_row = IssueSummary(
            issue_id=new_issue.id,
            summary_type="summary",
            summary_text=item.summary,
        )
        db.add(summary_row)

        if item.forecast:
            forecast_row = IssueSummary(
                issue_id=new_issue.id,
                summary_type="forecast",
                summary_text=item.forecast,
            )
            db.add(forecast_row)

        save_keyword_list(db, new_issue.id, item.keywords, "keyword")
        save_keyword_list(db, new_issue.id, item.rising_keywords, "rising_keyword")
        save_keyword_list(db, new_issue.id, item.related_keywords, "related_keyword")
        save_keyword_list(db, new_issue.id, item.category_tags, "category_tag")
        save_keyword_list(db, new_issue.id, item.cluster_keywords, "cluster_keyword")

        save_search_aliases(db, new_issue.id, item)

        if item.causes:
            for idx, cause in enumerate(item.causes):
                if not cause:
                    continue

                cause_row = IssueCause(
                    issue_id=new_issue.id,
                    cause_text=cause,
                    cause_order=idx,
                )
                db.add(cause_row)

        if item.keyword_trends:
            for idx, trend in enumerate(item.keyword_trends):
                if not trend:
                    continue

                trend_row = IssueKeywordTrend(
                    issue_id=new_issue.id,
                    trend_date=trend.date,
                    trend_value=trend.value,
                    trend_order=idx,
                )
                db.add(trend_row)

        saved_issue_count += 1

    db.commit()

    return {
        "message": "analysis batch ingested successfully",
        "batch_id": payload.batch_id,
        "saved_issue_count": saved_issue_count,
        "skipped_issue_count": skipped_issue_count,
    }
