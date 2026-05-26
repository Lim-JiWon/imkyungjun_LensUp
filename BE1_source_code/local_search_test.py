import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


BASE_DIR = Path(__file__).resolve().parent
PAYLOAD_DIR = BASE_DIR / "cache" / "dashboard_sync"

# 검색 매칭에 실제로 사용할 필드만 남김
# rising_keywords는 모든 이슈에 공통으로 들어가므로 검색 매칭에서 제외
SEARCH_FIELDS = [
    "title",
    "summary",
    "top_keyword",
    "keywords",
    "related_keywords",
    "search_aliases",
]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().lower().replace("_", " ").replace("  ", " ")


def compact_text(value: Any) -> str:
    return normalize_text(value).replace(" ", "")


def find_latest_dashboard_payload() -> Path:
    files = sorted(
        PAYLOAD_DIR.glob("*_dashboard_payload.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not files:
        raise FileNotFoundError(
            f"dashboard payload 파일을 찾지 못했습니다: {PAYLOAD_DIR}"
        )

    return files[0]


def load_payload(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def values_from_field(issue: Dict[str, Any], field: str) -> List[str]:
    value = issue.get(field)

    if value is None:
        return []

    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, dict):
                result.append(json.dumps(item, ensure_ascii=False))
            else:
                result.append(str(item))
        return result

    if isinstance(value, dict):
        return [json.dumps(value, ensure_ascii=False)]

    return [str(value)]


def match_issue(issue: Dict[str, Any], query: str) -> Tuple[int, List[str]]:
    query_norm = normalize_text(query)
    query_compact = compact_text(query)

    score = 0
    matched_reasons = []

    for field in SEARCH_FIELDS:
        values = values_from_field(issue, field)

        for value in values:
            value_norm = normalize_text(value)
            value_compact = compact_text(value)

            if not value_norm:
                continue

            # 1. 완전 일치
            if query_norm == value_norm or query_compact == value_compact:
                if field == "top_keyword":
                    score += 100
                elif field == "keywords":
                    score += 90
                elif field == "search_aliases":
                    score += 85
                elif field == "related_keywords":
                    score += 75
                elif field == "title":
                    score += 60
                elif field == "summary":
                    score += 40
                else:
                    score += 30

                matched_reasons.append(f"{field}:완전일치:{value}")
                continue

            # 2. 포함 검색
            if query_norm in value_norm or query_compact in value_compact:
                if field == "top_keyword":
                    score += 80
                elif field == "keywords":
                    score += 75
                elif field == "search_aliases":
                    score += 70
                elif field == "related_keywords":
                    score += 60
                elif field == "title":
                    score += 40
                elif field == "summary":
                    score += 20
                else:
                    score += 10

                matched_reasons.append(f"{field}:부분일치:{value}")
                continue

            # 3. 반대 방향 포함 검색
            # 예: query='불법주정차신고', value='불법 주정차'
            if value_compact in query_compact and len(value_compact) >= 3:
                score += 25
                matched_reasons.append(f"{field}:역부분일치:{value}")

    # 실제 매칭 이유가 없으면 검색 결과에서 제외
    if not matched_reasons:
        return 0, []

    return score, matched_reasons


def search_issues(payload: Dict[str, Any], query: str, limit: int = 10) -> List[Dict[str, Any]]:
    issues = payload.get("issues", [])
    results = []

    for issue in issues:
        match_score, matched_reasons = match_issue(issue, query)

        if match_score <= 0:
            continue

        results.append({
            "match_score": match_score,
            "matched_reasons": matched_reasons,
            "issue": issue,
        })

    results.sort(
        key=lambda x: (
            x["match_score"],
            x["issue"].get("score", 0),
            x["issue"].get("complaint_count", 0),
        ),
        reverse=True,
    )

    return results[:limit]


def print_result(query: str, payload_file: Path, payload: Dict[str, Any], results: List[Dict[str, Any]]):
    print("=" * 70)
    print("[LOCAL SEARCH TEST]")
    print(f"검색어: {query}")
    print(f"payload_file: {payload_file}")
    print(f"batch_id: {payload.get('batch_id')}")
    print(f"issue_count: {len(payload.get('issues', []))}")
    print(f"result_count: {len(results)}")
    print("=" * 70)

    if not results:
        print("[결과 없음]")
        print("검색어가 title, summary, keywords, related_keywords, search_aliases 등에 걸리지 않았습니다.")
        return

    for idx, item in enumerate(results, start=1):
        issue = item["issue"]
        matched_reasons = item["matched_reasons"]

        print(f"\n{idx}. {issue.get('title')}")
        print(f"   - match_score: {item['match_score']}")
        print(f"   - issue_key: {issue.get('issue_key')}")
        print(f"   - top_keyword: {issue.get('top_keyword')}")
        print(f"   - risk_level: {issue.get('risk_level')}")
        print(f"   - score: {issue.get('score')}")
        print(f"   - complaint_count: {issue.get('complaint_count')}")
        print(f"   - keywords: {issue.get('keywords', [])}")
        print(f"   - related_keywords: {issue.get('related_keywords', [])[:5]}")
        print(f"   - search_aliases: {issue.get('search_aliases', [])[:10]}")
        print("   - matched:")

        for reason in matched_reasons[:5]:
            print(f"     · {reason}")


def main():
    if len(sys.argv) >= 2:
        query = " ".join(sys.argv[1:]).strip()
    else:
        query = input("검색어를 입력하세요: ").strip()

    if not query:
        print("[ERROR] 검색어가 비어 있습니다.")
        return

    payload_file = find_latest_dashboard_payload()
    payload = load_payload(payload_file)

    results = search_issues(payload, query=query, limit=10)
    print_result(query, payload_file, payload, results)


if __name__ == "__main__":
    main()