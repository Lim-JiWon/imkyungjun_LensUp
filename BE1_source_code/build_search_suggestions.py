import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DASHBOARD_SYNC_DIR = BASE_DIR / "cache" / "dashboard_sync"

SUGGESTION_FILE = DASHBOARD_SYNC_DIR / "search_suggestions.json"
SUGGESTION_DETAIL_FILE = DASHBOARD_SYNC_DIR / "search_suggestions_detail.json"


# 자동완성에 보여줄 가치가 높은 핵심 후보
IMPORTANT_KEYWORDS = {
    "불법 주정차",
    "불법주정차",
    "주정차 신고",
    "주정차",
    "불법 주차",
    "불법주차",
    "주차",
    "주차 신고",
    "주차방해",
    "친환경차 충전구역",
    "친환경차",
    "전기차",
    "전기차 충전",
    "전기차 충전소",
    "전기차 주차",
    "충전구역",
    "충전소",
    "충전 방해",
    "충전구역 불법주차",
    "국토교통부 자동차운영보험",
    "자동차운영보험",
    "자동차 보험",
    "차량 보험",
    "보험",
    "자동차",
    "국토교통부",
    "보건복지부 장애인권익지원",
    "장애인권익지원",
    "장애인",
    "장애인 주차",
    "장애인 전용구역",
    "장애인 복지",
    "장애인 지원",
    "보건복지부",
    "횡단보도",
    "안전지대",
    "소화전",
    "버스정류소",
    "과태료",
}


# 자동완성에서 제외할 일반어/노이즈
STOPWORDS = {
    "민원",
    "관련",
    "이슈",
    "자동",
    "수집",
    "결과",
    "기간",
    "추이",
    "정보",
    "확인",
    "중심",
    "주요",
    "연관어",
    "데이터",
    "분석",
    "신고",
    "불법",
    "차량",
    "운영",
    "지원",
    "권익",
    "복지",
    "도로",
    "교차",
    "처리",
    "여부",
    "지자체",
    "신고자",
    "자관법",
    "번호판",
    "백운로",
    "우회전",
    "황색실선",
    "경찰청",
    "위반사항",
    "전대구내",
    "후미등불량",
    "반사지훼손",
    "후부반사지",
    "후부반사지 훼손",
    "방해행위차량",
    "진입로이중주차",
    "고덕국제신도시다해브",
    "팜파스리조트내",
    "팜파스리조트내 친환경차",
    "지하1층",
    "경상남도",
    "부산광역시",
}


BLOCK_CONTAINS = [
    "경상남도",
    "부산광역시",
    "창원시",
    "기장군",
    "정관읍",
    "용지",
    "지하1층",
    "팜파스리조트",
    "고덕국제신도시",
    "기간 내",
    "자동 수집",
    "집계",
    "흐름",
    "가능성",
    "모니터링",
]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_key(value: Any) -> str:
    text = normalize_text(value)
    return text.lower().replace("_", "").replace(" ", "")


def prefer_display_text(old_text: str, new_text: str) -> str:
    old_text = normalize_text(old_text)
    new_text = normalize_text(new_text)

    if not old_text:
        return new_text

    old_has_space = " " in old_text
    new_has_space = " " in new_text

    old_has_underscore = "_" in old_text
    new_has_underscore = "_" in new_text

    if old_has_underscore and not new_has_underscore:
        return new_text
    if new_has_underscore and not old_has_underscore:
        return old_text

    if new_has_space and not old_has_space:
        return new_text
    if old_has_space and not new_has_space:
        return old_text

    if len(new_text) < len(old_text):
        return new_text

    return old_text


def is_bad_suggestion(text: str) -> bool:
    text = normalize_text(text)

    if not text:
        return True

    if text in STOPWORDS:
        return True

    if len(text) < 2:
        return True

    if len(text) > 20 and text not in IMPORTANT_KEYWORDS:
        return True

    if text.isdigit():
        return True

    for blocked in BLOCK_CONTAINS:
        if blocked in text:
            return True

    return False


def should_keep_suggestion(text: str, source: str) -> bool:
    text = normalize_text(text)

    if is_bad_suggestion(text):
        return False

    # 핵심 후보는 무조건 유지
    if text in IMPORTANT_KEYWORDS:
        return True

    compact = text.replace(" ", "").replace("_", "")
    important_compacts = {x.replace(" ", "").replace("_", "") for x in IMPORTANT_KEYWORDS}
    if compact in important_compacts:
        return True

    # 대표 키워드/keywords는 유지
    if source in {"top_keyword", "keywords"}:
        return True

    # related/search_aliases는 너무 많은 노이즈가 생기므로 핵심어만 유지
    if source in {"related_keywords", "related_keywords_token", "search_aliases"}:
        if text in IMPORTANT_KEYWORDS:
            return True
        if compact in important_compacts:
            return True
        return False

    return False


def add_suggestion(
    bucket: Dict[str, Dict[str, Any]],
    text: str,
    source: str,
    score: int,
    issue_title: str = "",
):
    text = normalize_text(text)

    if not should_keep_suggestion(text, source):
        return

    key = normalize_key(text)
    if not key:
        return

    if key not in bucket:
        bucket[key] = {
            "keyword": text,
            "score": 0,
            "sources": set(),
            "issue_titles": set(),
            "count": 0,
        }

    bucket[key]["keyword"] = prefer_display_text(bucket[key]["keyword"], text)
    bucket[key]["score"] += score
    bucket[key]["sources"].add(source)
    bucket[key]["count"] += 1

    if issue_title:
        bucket[key]["issue_titles"].add(issue_title)


def find_latest_dashboard_payload() -> Path:
    files = sorted(
        DASHBOARD_SYNC_DIR.glob("*_dashboard_payload.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not files:
        raise FileNotFoundError(
            f"dashboard payload 파일을 찾지 못했습니다: {DASHBOARD_SYNC_DIR}"
        )

    return files[0]


def load_payload(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def keyword_variants_for_suggestion(text: str) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []

    variants = set()

    variants.add(text)

    if "_" in text:
        variants.add(text.replace("_", " "))

    compact = text.replace("_", "").replace(" ", "")
    if compact:
        variants.add(compact)

    tokens = text.replace("_", " ").split()
    for token in tokens:
        token = token.strip()
        if token in IMPORTANT_KEYWORDS:
            variants.add(token)

    return list(variants)


def build_search_suggestions(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    bucket: Dict[str, Dict[str, Any]] = {}

    issues = payload.get("issues", [])

    for issue in issues:
        issue_title = normalize_text(issue.get("title"))
        top_keyword = normalize_text(issue.get("top_keyword"))

        # 1. 대표 키워드
        for item in keyword_variants_for_suggestion(top_keyword):
            add_suggestion(
                bucket=bucket,
                text=item,
                source="top_keyword",
                score=120,
                issue_title=issue_title,
            )

        # 2. keywords
        for keyword in issue.get("keywords", []):
            for item in keyword_variants_for_suggestion(keyword):
                add_suggestion(
                    bucket=bucket,
                    text=item,
                    source="keywords",
                    score=100,
                    issue_title=issue_title,
                )

        # 3. related_keywords
        for related in issue.get("related_keywords", []):
            related = normalize_text(related)

            add_suggestion(
                bucket=bucket,
                text=related,
                source="related_keywords",
                score=60,
                issue_title=issue_title,
            )

            for token in related.replace("_", " ").split():
                token = token.strip()
                add_suggestion(
                    bucket=bucket,
                    text=token,
                    source="related_keywords_token",
                    score=40,
                    issue_title=issue_title,
                )

        # 4. search_aliases
        for alias in issue.get("search_aliases", []):
            alias = normalize_text(alias).replace("_", " ")
            add_suggestion(
                bucket=bucket,
                text=alias,
                source="search_aliases",
                score=50,
                issue_title=issue_title,
            )

    result = []

    for item in bucket.values():
        result.append({
            "keyword": item["keyword"],
            "score": item["score"],
            "count": item["count"],
            "sources": sorted(list(item["sources"])),
            "issue_titles": sorted(list(item["issue_titles"])),
        })

    result.sort(
        key=lambda x: (
            x["score"],
            x["count"],
            -len(x["keyword"]),
        ),
        reverse=True,
    )

    return result


def save_suggestions(suggestions: List[Dict[str, Any]]):
    DASHBOARD_SYNC_DIR.mkdir(parents=True, exist_ok=True)

    simple_keywords = [item["keyword"] for item in suggestions]

    with open(SUGGESTION_FILE, "w", encoding="utf-8") as f:
        json.dump(simple_keywords, f, ensure_ascii=False, indent=2)

    with open(SUGGESTION_DETAIL_FILE, "w", encoding="utf-8") as f:
        json.dump(suggestions, f, ensure_ascii=False, indent=2)

    print(f"[SAVE] search suggestions saved: {SUGGESTION_FILE}")
    print(f"[SAVE] search suggestions detail saved: {SUGGESTION_DETAIL_FILE}")


def main():
    payload_file = find_latest_dashboard_payload()
    payload = load_payload(payload_file)

    print("=" * 70)
    print("[BUILD SEARCH SUGGESTIONS]")
    print(f"payload_file: {payload_file}")
    print(f"batch_id: {payload.get('batch_id')}")
    print(f"issue_count: {len(payload.get('issues', []))}")
    print("=" * 70)

    suggestions = build_search_suggestions(payload)
    save_suggestions(suggestions)

    print(f"[RESULT] suggestion_count={len(suggestions)}")
    print("\n[TOP 30 SUGGESTIONS]")

    for idx, item in enumerate(suggestions[:30], start=1):
        print(
            f"{idx}. {item['keyword']} "
            f"| score={item['score']} "
            f"| count={item['count']} "
            f"| sources={item['sources']}"
        )


if __name__ == "__main__":
    main()