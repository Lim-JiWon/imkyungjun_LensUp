from typing import List, Optional, Set

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import SessionLocal
from models.issue import Issue
from models.issue_keyword import IssueKeyword
from models.issue_search_alias import IssueSearchAlias
from routers.search import (
    build_search_results,
    normalize_text,
    is_search_term_allowed,
    MIN_MATCH_SCORE,
)


router = APIRouter(prefix="/chat", tags=["chat"])


TEST_SOURCES = {
    "backend1_integration_test",
    "test_search_alias_pipeline",
}


IGNORE_WORDS = {
    "관련",
    "민원",
    "찾아줘",
    "알려줘",
    "검색",
    "이슈",
    "문제",
    "문제가",
    "문제야",
    "때문에",
    "때문",
    "때문이야",
    "있어",
    "있나요",
    "보여줘",
    "추천",
    "최근",
    "요즘",
    "어떤",
    "무슨",
    "좀",
    "해줘",
    "불편",
    "불편해",
    "발생",
    "발생했어",
    "궁금해",
    "궁금해요",
    "궁금합니다",
    "관련해서",
}


class ChatSearchRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatTopicItem(BaseModel):
    id: int
    issue_key: Optional[str] = None
    title: str
    summary: Optional[str] = None
    source: Optional[str] = None
    risk_level: Optional[str] = None
    score: Optional[float] = None
    complaint_count: Optional[int] = None
    top_keyword: Optional[str] = None
    category: Optional[str] = None
    category_tags: List[str] = Field(default_factory=list)
    cluster_keywords: List[str] = Field(default_factory=list)
    matched_fields: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)
    matched_aliases: List[str] = Field(default_factory=list)
    match_score: int
    detail_api: str


class ChatSearchResponse(BaseModel):
    user_message: str
    assistant_message: str
    detected_keywords: List[str] = Field(default_factory=list)
    related_keywords: List[str] = Field(default_factory=list)
    topic_count: int
    topics: List[ChatTopicItem] = Field(default_factory=list)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_real_issues_query(db: Session):
    return db.query(Issue).filter(
        or_(
            Issue.source.is_(None),
            ~Issue.source.in_(TEST_SOURCES),
        )
    )


def extract_message_tokens(message: str) -> List[str]:
    cleaned = (
        message.replace(",", " ")
        .replace(".", " ")
        .replace("?", " ")
        .replace("!", " ")
        .replace("/", " ")
        .replace("_", " ")
        .replace("-", " ")
    )

    tokens = []

    for token in cleaned.split():
        token = token.strip()

        if not token:
            continue

        if token in IGNORE_WORDS:
            continue

        if not is_search_term_allowed(token):
            continue

        tokens.append(token)

    return tokens


def collect_server_keywords(db: Session) -> Set[str]:
    keywords = set()

    issues = get_real_issues_query(db).all()

    for issue in issues:
        if issue.top_keyword and is_search_term_allowed(issue.top_keyword):
            keywords.add(issue.top_keyword.strip())

    issue_ids = [issue.id for issue in issues]

    if not issue_ids:
        return keywords

    keyword_rows = (
        db.query(IssueKeyword)
        .filter(IssueKeyword.issue_id.in_(issue_ids))
        .all()
    )

    for row in keyword_rows:
        if not row.keyword:
            continue

        if row.keyword_type == "rising_keyword":
            continue

        if not is_search_term_allowed(row.keyword):
            continue

        keywords.add(row.keyword.strip())

    alias_rows = (
        db.query(IssueSearchAlias)
        .filter(IssueSearchAlias.issue_id.in_(issue_ids))
        .all()
    )

    for row in alias_rows:
        if not row.alias:
            continue

        if not is_search_term_allowed(row.alias):
            continue

        keywords.add(row.alias.strip())

    return {keyword for keyword in keywords if keyword}


def detect_keywords_from_message(db: Session, message: str) -> List[str]:
    server_keywords = collect_server_keywords(db)
    normalized_message = normalize_text(message)

    detected = []

    for keyword in server_keywords:
        normalized_keyword = normalize_text(keyword)

        if not normalized_keyword:
            continue

        if normalized_keyword in normalized_message:
            detected.append(keyword)

    if detected:
        detected.sort(key=lambda value: len(normalize_text(value)), reverse=True)

        unique_detected = []
        seen = set()

        for keyword in detected:
            key = normalize_text(keyword)

            if key in seen:
                continue

            seen.add(key)
            unique_detected.append(keyword)

        return unique_detected[:10]

    return extract_message_tokens(message)


def build_related_keywords(db: Session, detected_keywords: List[str]) -> List[str]:
    if not detected_keywords:
        return []

    related = set()

    issues = get_real_issues_query(db).all()
    issue_ids = [issue.id for issue in issues]

    if not issue_ids:
        return []

    keyword_rows = (
        db.query(IssueKeyword)
        .filter(IssueKeyword.issue_id.in_(issue_ids))
        .all()
    )

    alias_rows = (
        db.query(IssueSearchAlias)
        .filter(IssueSearchAlias.issue_id.in_(issue_ids))
        .all()
    )

    for detected in detected_keywords:
        detected_normalized = normalize_text(detected)

        for row in keyword_rows:
            if not row.keyword:
                continue

            if row.keyword_type == "rising_keyword":
                continue

            if not is_search_term_allowed(row.keyword):
                continue

            row_normalized = normalize_text(row.keyword)

            if detected_normalized in row_normalized or row_normalized in detected_normalized:
                related.add(row.keyword.strip())

        for row in alias_rows:
            if not row.alias:
                continue

            if not is_search_term_allowed(row.alias):
                continue

            alias_normalized = normalize_text(row.alias)

            if detected_normalized in alias_normalized or alias_normalized in detected_normalized:
                related.add(row.alias.strip())

    for detected in detected_keywords:
        related.discard(detected)

    related_list = sorted(
        list(related),
        key=lambda value: len(normalize_text(value)),
        reverse=True,
    )

    return related_list[:12]


def search_topics_with_detected_keywords(
    db: Session,
    detected_keywords: List[str],
    topic_limit: int = 5,
    min_match_score: int = MIN_MATCH_SCORE,
):
    if not detected_keywords:
        return []

    merged_topics = {}
    seen_topic_ids = set()

    for keyword in detected_keywords:
        if not is_search_term_allowed(keyword):
            continue

        search_result = build_search_results(
            db=db,
            query=keyword,
            limit=topic_limit,
            include_test=False,
            min_match_score=min_match_score,
        )

        for item in search_result.get("results", []):
            issue_id = item["id"]

            if issue_id in seen_topic_ids:
                continue

            seen_topic_ids.add(issue_id)

            topic = {
                **item,
                "detail_api": f"/dashboard/{issue_id}",
            }

            merged_topics[issue_id] = topic

    topics = list(merged_topics.values())

    topics.sort(
        key=lambda item: (
            item["match_score"],
            item["score"] or 0,
            item["complaint_count"] or 0,
            item["id"],
        ),
        reverse=True,
    )

    return topics[:topic_limit]


@router.post("/search-assistant", response_model=ChatSearchResponse)
def search_assistant(
    request: ChatSearchRequest,
    db: Session = Depends(get_db),
):
    user_message = request.message.strip()

    detected_keywords = detect_keywords_from_message(db, user_message)
    related_keywords = build_related_keywords(db, detected_keywords)

    topics = search_topics_with_detected_keywords(
        db=db,
        detected_keywords=detected_keywords,
        topic_limit=5,
        min_match_score=MIN_MATCH_SCORE,
    )

    if topics:
        assistant_message = (
            "입력한 내용과 관련된 키워드와 민원 주제를 찾았습니다. "
            "아래 주제를 선택하면 해당 민원 상세 페이지로 이동할 수 있습니다."
        )
    elif detected_keywords:
        assistant_message = (
            "관련 키워드는 찾았지만, 기준 점수 이상의 민원 주제는 없습니다. "
            "다른 표현이나 더 구체적인 키워드로 다시 입력해보세요."
        )
    else:
        assistant_message = (
            "입력한 문장에서 검색 가능한 키워드를 찾지 못했습니다. "
            "예: 주차 문제, 전기차 충전, 보험 민원처럼 입력해보세요."
        )

    return {
        "user_message": user_message,
        "assistant_message": assistant_message,
        "detected_keywords": detected_keywords,
        "related_keywords": related_keywords,
        "topic_count": len(topics),
        "topics": topics,
    }
