import json
from pathlib import Path
from collections import Counter
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import SessionLocal
from models.issue import Issue
from models.issue_summary import IssueSummary
from models.issue_keyword import IssueKeyword
from models.issue_search_alias import IssueSearchAlias

router = APIRouter(tags=["search"])


TEST_SOURCES = {
    "backend1_integration_test",
    "test_search_alias_pipeline",
}

MIN_MATCH_SCORE = 60

# 결과 포함을 허용하는 강한 매칭 필드
STRONG_INCLUDE_FIELDS = {
    "title_core",
    "top_keyword",
    "keywords",
    "search_aliases",
}

# related_keywords, cluster_keywords, category, category_tags, summary는 보조 점수만 부여
WEAK_MATCH_FIELDS = {
    "title",
    "summary",
    "related_keywords",
    "cluster_keywords",
    "category",
    "category_tags",
}

GENERIC_SEARCH_TERMS = {
    "자동",
    "처리",
    "신청",
    "추가",
    "자료",
    "사건",
    "관련",
    "중심",
    "민원",
    "문제",
    "요청",
    "확인",
    "등록",
    "문의",
    "내용",
    "발생",
    "일반",
    "기타",
    "안내",
    "상담",
}

# 검색어별 의미상 가까운 표현
# 단, 이 유사어 매칭은 top_keyword / keywords / title_core 같은 핵심 필드에서만 강하게 인정한다.
SEARCH_EQUIVALENTS = {
    "주차": [
        "주차",
        "주정차",
        "불법주정차",
        "불법주차",
        "주차방해",
        "주차구역",
        "전용구역",
        "인도불법",
    ],
    "주정차": [
        "주정차",
        "주차",
        "불법주정차",
        "불법주차",
        "주정차신고",
    ],
    "불법주차": [
        "불법주차",
        "불법주정차",
        "주정차",
        "주차",
    ],
    "자동차": [
        "자동차",
        "차량",
        "자동차안전기준",
        "교통안전공단",
        "한국교통안전공단",
        "도로공사",
        "한국도로공사",
        "안전순찰원",
        "번호판",
        "기아자동차",
        "쏘렌토",
    ],
    "배송": [
        "배송",
        "배송도착",
        "택배",
    ],
    "청정원": [
        "청정원",
        "청정원마요네즈",
        "마요네즈",
    ],
    "목욕탕": [
        "목욕탕",
        "공중목욕탕",
    ],
    "무단투기": [
        "무단투기",
        "노래방무단투기",
    ],
}

SUGGESTION_FILE_PATHS = [
    Path("/root/cache/dashboard_sync/search_suggestions.json"),
    Path("/root/cache/dashboard_sync/search_suggestions_detail.json"),
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""

    text = value.lower()
    text = text.replace("_", " ")
    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = text.replace(".", " ")
    text = text.replace(",", " ")
    text = text.replace("(", " ")
    text = text.replace(")", " ")
    text = text.replace("[", " ")
    text = text.replace("]", " ")
    text = "".join(text.split())

    return text


def get_equivalent_terms(query: str) -> List[str]:
    normalized_query = normalize_text(query)

    terms = [normalized_query]

    if normalized_query in SEARCH_EQUIVALENTS:
        terms.extend([normalize_text(item) for item in SEARCH_EQUIVALENTS[normalized_query]])

    unique_terms = []
    seen = set()

    for term in terms:
        if not term:
            continue

        if term in seen:
            continue

        seen.add(term)
        unique_terms.append(term)

    return unique_terms


def is_search_term_allowed(value: Optional[str]) -> bool:
    normalized = normalize_text(value)

    if not normalized:
        return False

    if len(normalized) < 2:
        return False

    generic_terms = {normalize_text(term) for term in GENERIC_SEARCH_TERMS}

    if normalized in generic_terms:
        return False

    return True


def exact_match(query: str, value: Optional[str]) -> bool:
    if not query or not value:
        return False

    return normalize_text(query) == normalize_text(value)


def contains_match(query: str, value: Optional[str]) -> bool:
    if not query or not value:
        return False

    normalized_query = normalize_text(query)
    normalized_value = normalize_text(value)

    if not normalized_query or not normalized_value:
        return False

    return normalized_query in normalized_value


def semantic_core_match(query: str, value: Optional[str]) -> bool:
    """
    top_keyword, keywords, title_core 같은 핵심 필드용 매칭.
    예:
    - query=주차, value=불법 주정차 → 허용
    - query=자동차, value=한국도로공사 안전순찰원 → 허용
    - query=배송, value=배송 도착 → 허용
    """
    if not query or not value:
        return False

    normalized_query = normalize_text(query)
    normalized_value = normalize_text(value)

    if not normalized_query or not normalized_value:
        return False

    if not is_search_term_allowed(query):
        return False

    if normalized_query == normalized_value:
        return True

    if normalized_query in normalized_value:
        return True

    equivalent_terms = get_equivalent_terms(query)

    for term in equivalent_terms:
        if not term:
            continue

        if len(term) < 2:
            continue

        if term in normalized_value:
            return True

    return False


def get_title_core(title: Optional[str]) -> str:
    """
    title에서 핵심 이슈명만 추출한다.

    예:
    '청정원 마요네즈 관련 민원 이슈 - 배송 도착 확인 중심'
    → '청정원 마요네즈'

    '공중 목욕탕 관련 민원 이슈 - 신청 중심'
    → '공중 목욕탕'
    """
    if not title:
        return ""

    core = title.strip()

    split_patterns = [
        " 관련 민원 이슈",
        " 관련 민원/키워드",
        " 관련 민원",
        " - ",
        "[",
    ]

    for pattern in split_patterns:
        if pattern in core:
            core = core.split(pattern)[0].strip()

    return core


def get_summary_text(db: Session, issue_id: int) -> Optional[str]:
    summary_row = (
        db.query(IssueSummary)
        .filter(
            IssueSummary.issue_id == issue_id,
            IssueSummary.summary_type == "summary",
        )
        .first()
    )

    return summary_row.summary_text if summary_row else None


def get_keywords_by_type(db: Session, issue_id: int, keyword_type: str) -> List[str]:
    rows = (
        db.query(IssueKeyword)
        .filter(
            IssueKeyword.issue_id == issue_id,
            IssueKeyword.keyword_type == keyword_type,
        )
        .order_by(IssueKeyword.keyword_order.asc())
        .all()
    )

    return [row.keyword for row in rows if row.keyword]


def get_issue_group_key(issue: Issue) -> str:
    if issue.top_keyword:
        return f"top_keyword:{normalize_text(issue.top_keyword)}"

    if issue.issue_key:
        return f"issue_key:{issue.issue_key.rsplit('-', 1)[0]}"

    return f"id:{issue.id}"


def get_real_issues_query(db: Session, include_test: bool = False):
    issues_query = db.query(Issue)

    if not include_test:
        issues_query = issues_query.filter(
            or_(
                Issue.source.is_(None),
                ~Issue.source.in_(TEST_SOURCES),
            )
        )

    return issues_query


def get_match_bonus(query: str, value: Optional[str]) -> int:
    if exact_match(query, value):
        return 20

    return 0


def is_alias_reliable_for_issue(
    query: str,
    alias: str,
    title_core: str,
    top_keyword: Optional[str],
    issue_keyword_values: List[str],
) -> bool:
    """
    search_aliases는 정확 일치만 허용한다.
    단, 기존 DB에 related_keywords에서 파생된 alias가 들어가 있을 수 있으므로,
    alias가 정확히 일치하더라도 이슈 핵심 맥락(title_core/top_keyword/keywords)과 맞지 않으면 제외한다.

    예:
    - query=청정원, alias=청정원, title_core=청정원 마요네즈 → 허용
    - query=청정원, alias=청정원, title_core=노래방 무단투기 → 제외
    - query=자동차, alias=자동 → 정확 일치 아님 → 제외
    """
    if not alias:
        return False

    if not is_search_term_allowed(alias):
        return False

    if not exact_match(query, alias):
        return False

    if semantic_core_match(query, title_core):
        return True

    if semantic_core_match(query, top_keyword):
        return True

    for keyword in issue_keyword_values:
        if semantic_core_match(query, keyword):
            return True

    return False


def build_search_results(
    db: Session,
    query: str,
    limit: int = 20,
    include_test: bool = False,
    min_match_score: int = MIN_MATCH_SCORE,
) -> Dict[str, Any]:
    normalized_query = normalize_text(query)

    if not normalized_query:
        return {
            "query": query,
            "normalized_query": normalized_query,
            "count": 0,
            "total_count_before_dedup": 0,
            "min_match_score": min_match_score,
            "results": [],
        }

    issues = (
        get_real_issues_query(db, include_test=include_test)
        .order_by(Issue.id.desc())
        .all()
    )

    candidates = []

    for issue in issues:
        matched_fields = set()
        matched_keywords = set()
        matched_aliases = set()
        match_score = 0
        match_priority = 0

        summary_text = get_summary_text(db, issue.id)
        title_core = get_title_core(issue.title)

        issue_keywords = (
            db.query(IssueKeyword)
            .filter(IssueKeyword.issue_id == issue.id)
            .all()
        )

        issue_keyword_values = [
            row.keyword
            for row in issue_keywords
            if row.keyword and row.keyword_type == "keyword"
        ]

        alias_rows = (
            db.query(IssueSearchAlias)
            .filter(IssueSearchAlias.issue_id == issue.id)
            .all()
        )

        # 1. title의 핵심 키워드 부분만 강한 매칭
        if semantic_core_match(query, title_core):
            matched_fields.add("title_core")
            match_score += 110
            match_score += get_match_bonus(query, title_core)
            match_priority = max(match_priority, 4)

        # 2. top_keyword 강한 매칭
        if semantic_core_match(query, issue.top_keyword):
            matched_fields.add("top_keyword")

            if issue.top_keyword:
                matched_keywords.add(issue.top_keyword)

            match_score += 130
            match_score += get_match_bonus(query, issue.top_keyword)
            match_priority = max(match_priority, 4)

        # 3. keywords 강한 매칭 / related, cluster, category_tags는 보조만
        for keyword_row in issue_keywords:
            if not keyword_row.keyword:
                continue

            if keyword_row.keyword_type == "rising_keyword":
                continue

            # keywords는 결과 포함 허용
            if keyword_row.keyword_type == "keyword":
                if semantic_core_match(query, keyword_row.keyword):
                    matched_fields.add("keywords")
                    matched_keywords.add(keyword_row.keyword)
                    match_score += 120
                    match_score += get_match_bonus(query, keyword_row.keyword)
                    match_priority = max(match_priority, 4)

            # related_keywords는 보조 점수만
            elif keyword_row.keyword_type == "related_keyword":
                if semantic_core_match(query, keyword_row.keyword):
                    matched_fields.add("related_keywords")
                    matched_keywords.add(keyword_row.keyword)
                    match_score += 20
                    match_priority = max(match_priority, 1)

            # cluster_keywords는 보조 점수만
            elif keyword_row.keyword_type == "cluster_keyword":
                if semantic_core_match(query, keyword_row.keyword):
                    matched_fields.add("cluster_keywords")
                    matched_keywords.add(keyword_row.keyword)
                    match_score += 15
                    match_priority = max(match_priority, 1)

            # category_tags는 보조 점수만
            elif keyword_row.keyword_type == "category_tag":
                if semantic_core_match(query, keyword_row.keyword):
                    matched_fields.add("category_tags")
                    matched_keywords.add(keyword_row.keyword)
                    match_score += 5
                    match_priority = max(match_priority, 1)

        # 4. search_aliases는 정확 일치 + 이슈 핵심 맥락 일치일 때만 강한 매칭
        for alias_row in alias_rows:
            if not alias_row.alias:
                continue

            alias = alias_row.alias.strip()

            if is_alias_reliable_for_issue(
                query=query,
                alias=alias,
                title_core=title_core,
                top_keyword=issue.top_keyword,
                issue_keyword_values=issue_keyword_values,
            ):
                matched_fields.add("search_aliases")
                matched_aliases.add(alias)
                match_score += 100
                match_score += get_match_bonus(query, alias)
                match_priority = max(match_priority, 3)

        # 5. title 전체는 약한 보조 점수만
        # "- 배송 도착 확인 중심" 같은 부분만 맞으면 결과 포함 금지
        if contains_match(query, issue.title):
            matched_fields.add("title")
            match_score += 5

        # 6. category는 약한 보조 점수만
        if contains_match(query, issue.category):
            matched_fields.add("category")
            match_score += 5

        # 7. summary는 약한 보조 점수만
        if contains_match(query, summary_text):
            matched_fields.add("summary")
            match_score += 5

        if match_score < min_match_score:
            continue

        if not matched_fields:
            continue

        # 결과 포함 허용 필드가 하나도 없으면 제외
        # 즉 related_keywords, cluster_keywords, category, category_tags, summary, title만 맞으면 제외
        if not matched_fields.intersection(STRONG_INCLUDE_FIELDS):
            continue

        category_tags = get_keywords_by_type(db, issue.id, "category_tag")
        cluster_keywords = get_keywords_by_type(db, issue.id, "cluster_keyword")

        candidates.append(
            {
                "id": issue.id,
                "issue_key": issue.issue_key,
                "title": issue.title,
                "summary": summary_text,
                "source": issue.source,
                "risk_level": issue.risk_level,
                "score": issue.score,
                "complaint_count": issue.complaint_count,
                "top_keyword": issue.top_keyword,
                "category": issue.category,
                "category_tags": category_tags,
                "cluster_keywords": cluster_keywords,
                "matched_fields": sorted(list(matched_fields)),
                "matched_keywords": sorted(list(matched_keywords)),
                "matched_aliases": sorted(list(matched_aliases)),
                "match_score": match_score,
                "_match_priority": match_priority,
                "_group_key": get_issue_group_key(issue),
            }
        )

    # 같은 top_keyword 계열은 최신 id 1개만 남긴다.
    latest_by_group = {}

    for item in sorted(candidates, key=lambda candidate: candidate["id"], reverse=True):
        group_key = item["_group_key"]

        if group_key not in latest_by_group:
            latest_by_group[group_key] = item

    deduplicated_candidates = list(latest_by_group.values())

    # 정렬 우선순위:
    # 1순위: top_keyword / keywords / title_core 직접 매칭
    # 2순위: search_aliases 정확 매칭
    # 3순위: 보조 점수
    deduplicated_candidates.sort(
        key=lambda item: (
            item["_match_priority"],
            item["match_score"],
            item["score"] or 0,
            item["complaint_count"] or 0,
            item["id"],
        ),
        reverse=True,
    )

    results = []

    for item in deduplicated_candidates[:limit]:
        item.pop("_group_key", None)
        item.pop("_match_priority", None)
        results.append(item)

    return {
        "query": query,
        "normalized_query": normalized_query,
        "count": len(results),
        "total_count_before_dedup": len(candidates),
        "min_match_score": min_match_score,
        "results": results,
    }


@router.get("/search")
def search_issues(
    query: str = Query(..., min_length=1, description="검색어"),
    limit: int = Query(20, ge=1, le=50, description="검색 결과 개수"),
    include_test: bool = Query(False, description="테스트 데이터 포함 여부"),
    min_match_score: int = Query(MIN_MATCH_SCORE, ge=0, le=300, description="검색 최소 점수"),
    db: Session = Depends(get_db),
):
    return build_search_results(
        db=db,
        query=query,
        limit=limit,
        include_test=include_test,
        min_match_score=min_match_score,
    )


@router.get("/search/popular-keywords")
def get_popular_keywords(
    limit: int = Query(10, ge=1, le=30, description="추천 검색어 개수"),
    db: Session = Depends(get_db),
):
    issues = (
        get_real_issues_query(db, include_test=False)
        .order_by(Issue.id.desc())
        .all()
    )

    if not issues:
        return {
            "count": 0,
            "keywords": [],
        }

    issue_ids = [issue.id for issue in issues]

    keyword_counter = Counter()
    display_name_map = {}

    def add_keyword(keyword: Optional[str]):
        if not keyword:
            return

        cleaned = keyword.strip()

        if not cleaned:
            return

        if not is_search_term_allowed(cleaned):
            return

        normalized = normalize_text(cleaned)

        keyword_counter[normalized] += 1

        if normalized not in display_name_map:
            display_name_map[normalized] = cleaned.replace("_", " ")

    for issue in issues:
        add_keyword(issue.top_keyword)

    keyword_rows = (
        db.query(IssueKeyword)
        .filter(IssueKeyword.issue_id.in_(issue_ids))
        .all()
    )

    for row in keyword_rows:
        if row.keyword_type == "rising_keyword":
            continue

        add_keyword(row.keyword)

    alias_rows = (
        db.query(IssueSearchAlias)
        .filter(IssueSearchAlias.issue_id.in_(issue_ids))
        .all()
    )

    for row in alias_rows:
        add_keyword(row.alias)

    popular_keywords = []

    for normalized_keyword, count in keyword_counter.most_common(limit):
        popular_keywords.append(
            {
                "keyword": display_name_map.get(normalized_keyword, normalized_keyword),
                "count": count,
            }
        )

    return {
        "count": len(popular_keywords),
        "keywords": popular_keywords,
    }


def clean_suggestion_keyword(value: str) -> str:
    if not value:
        return ""

    cleaned = value.strip().replace("_", " ")
    cleaned = " ".join(cleaned.split())

    return cleaned


def extract_suggestion_value(item):
    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        for key in ["keyword", "suggestion", "term", "label", "query", "text", "value"]:
            if key in item and item[key]:
                return str(item[key])

    return ""


def load_file_suggestions() -> List[str]:
    suggestions = []

    for path in SUGGESTION_FILE_PATHS:
        if not path.exists():
            continue

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        if isinstance(data, list):
            for item in data:
                value = extract_suggestion_value(item)
                if value:
                    suggestions.append(value)

        elif isinstance(data, dict):
            raw_items = data.get("suggestions") or data.get("items") or data.get("data") or []

            if isinstance(raw_items, list):
                for item in raw_items:
                    value = extract_suggestion_value(item)
                    if value:
                        suggestions.append(value)

    return suggestions


def collect_db_suggestions(db: Session) -> List[str]:
    suggestions = []

    issues = get_real_issues_query(db, include_test=False).all()
    issue_ids = [issue.id for issue in issues]

    for issue in issues:
        if issue.top_keyword:
            suggestions.append(issue.top_keyword)

    if issue_ids:
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

            suggestions.append(row.keyword)

        alias_rows = (
            db.query(IssueSearchAlias)
            .filter(IssueSearchAlias.issue_id.in_(issue_ids))
            .all()
        )

        for row in alias_rows:
            if row.alias:
                suggestions.append(row.alias)

    return suggestions


@router.get("/search/suggestions")
def get_search_suggestions(
    query: Optional[str] = Query(None, description="자동완성 검색어"),
    limit: int = Query(15, ge=1, le=50, description="자동완성 개수"),
    db: Session = Depends(get_db),
):
    raw_suggestions = []

    raw_suggestions.extend(load_file_suggestions())
    raw_suggestions.extend(collect_db_suggestions(db))

    suggestion_map = {}

    for item in raw_suggestions:
        cleaned = clean_suggestion_keyword(item)

        if not cleaned:
            continue

        if not is_search_term_allowed(cleaned):
            continue

        normalized = normalize_text(cleaned)

        if normalized not in suggestion_map:
            suggestion_map[normalized] = cleaned

    suggestions = list(suggestion_map.values())

    if query:
        normalized_query = normalize_text(query)

        suggestions = [
            suggestion
            for suggestion in suggestions
            if normalized_query in normalize_text(suggestion)
        ]

    suggestions = suggestions[:limit]

    return {
        "query": query,
        "count": len(suggestions),
        "suggestions": suggestions,
    }
