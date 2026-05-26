import os
import time
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv


load_dotenv()


SERVICE_KEY = os.getenv("PUBLIC_API_SERVICE_KEY")
TARGET = os.getenv("PUBLIC_API_TARGET", "pttn")

DATE_FROM = os.getenv("DATE_FROM", "20260328")
DATE_TO = os.getenv("DATE_TO", "20260513")

TIMEOUT = int(os.getenv("PUBLIC_API_TIMEOUT", "60"))

REGION_RANK_URL = os.getenv("PUBLIC_API_REGION_RANK_URL")
ORG_RANK_URL = os.getenv("PUBLIC_API_ORG_RANK_URL")
KEYWORD_AGE_URL = os.getenv("PUBLIC_API_KEYWORD_AGE_URL")

REGION_TOP_N = int(os.getenv("PUBLIC_API_REGION_TOP_N", "17"))
REGION_SORT_BY = os.getenv("PUBLIC_API_REGION_SORT_BY", "VALUE")
REGION_SORT_ORDER = os.getenv("PUBLIC_API_REGION_SORT_ORDER", "false")

ORG_TOP_N = int(os.getenv("PUBLIC_API_ORG_TOP_N", "10"))
ORG_SORT_BY = os.getenv("PUBLIC_API_ORG_SORT_BY", "VALUE")
ORG_SORT_ORDER = os.getenv("PUBLIC_API_ORG_SORT_ORDER", "false")

AGE_RESULT_COUNT = int(os.getenv("PUBLIC_API_AGE_RESULT_COUNT", "10"))


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _clean_keyword(keyword: str) -> str:
    if not keyword:
        return ""

    return str(keyword).strip().replace("_", " ")


def _extract_items(data: Any) -> List[Dict[str, Any]]:
    """
    공공데이터포털 응답이 이번 API에서는 리스트로 바로 오지만,
    혹시 다른 구조로 올 경우도 대비해서 items를 최대한 찾아준다.
    """

    if data is None:
        return []

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    if not isinstance(data, dict):
        return []

    candidate_paths = [
        ["response", "body", "items"],
        ["response", "body", "items", "item"],
        ["response", "body", "item"],
        ["body", "items"],
        ["body", "items", "item"],
        ["body", "item"],
        ["items"],
        ["items", "item"],
        ["item"],
        ["data"],
        ["result"],
        ["resultList"],
        ["list"],
    ]

    for path in candidate_paths:
        current = data

        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                current = None
                break

        if current is None:
            continue

        if isinstance(current, list):
            return [item for item in current if isinstance(item, dict)]

        if isinstance(current, dict):
            return [current]

    return []


def _request_public_api(name: str, url: Optional[str], params: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not SERVICE_KEY:
        print(f"[ERROR] {name}: PUBLIC_API_SERVICE_KEY가 없습니다.")
        return []

    if not url:
        print(f"[ERROR] {name}: URL이 .env에 없습니다.")
        return []

    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)

        if response.status_code != 200:
            print(f"[ERROR] {name}: status_code={response.status_code}")
            print(response.text[:1000])
            return []

        try:
            data = response.json()
        except Exception:
            print(f"[ERROR] {name}: JSON 파싱 실패")
            print(response.text[:1000])
            return []

        items = _extract_items(data)

        print(f"[OK] {name}: items={len(items)}")
        return items

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {name}: 요청 실패 - {e}")
        return []


def _normalize_rank_items(
    items: List[Dict[str, Any]],
    name_key: str,
) -> List[Dict[str, Any]]:
    """
    입력 예:
    {"hits": 557104, "label": "경기도"}

    출력 예:
    {"rank": 1, "region": "경기도", "value": 557104}
    """

    normalized = []

    for index, item in enumerate(items, start=1):
        label = str(item.get("label", "")).strip()
        value = _safe_int(item.get("hits", 0))

        if not label:
            continue

        normalized.append(
            {
                "rank": index,
                name_key: label,
                "value": value,
            }
        )

    return normalized


def _normalize_age_label(label: Any) -> str:
    value = str(label).strip()

    if not value:
        return "연령 미상"

    if value.upper() == "NONE":
        return "연령 미상"

    if value.isdigit():
        return f"{value}대"

    return value


def _normalize_age_distribution(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    입력 예:
    {"hits": 2455, "label": "40"}

    출력 예:
    {"age_group": "40대", "value": 2455}
    """

    normalized = []

    for item in items:
        age_group = _normalize_age_label(item.get("label"))
        value = _safe_int(item.get("hits", 0))

        normalized.append(
            {
                "age_group": age_group,
                "value": value,
            }
        )

    return normalized


def _build_age_summary(age_distribution: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = sum(_safe_int(item.get("value", 0)) for item in age_distribution)

    known_items = [
        item
        for item in age_distribution
        if item.get("age_group") != "연령 미상"
    ]

    known_total = sum(_safe_int(item.get("value", 0)) for item in known_items)

    if known_items:
        dominant = max(known_items, key=lambda x: _safe_int(x.get("value", 0)))
        dominant_age_group = dominant.get("age_group")
        dominant_value = _safe_int(dominant.get("value", 0))
    else:
        dominant_age_group = None
        dominant_value = 0

    if total > 0:
        unknown_item = next(
            (item for item in age_distribution if item.get("age_group") == "연령 미상"),
            None,
        )
        unknown_value = _safe_int(unknown_item.get("value", 0)) if unknown_item else 0
        unknown_ratio = round((unknown_value / total) * 100, 2)
    else:
        unknown_value = 0
        unknown_ratio = 0.0

    if known_total > 0 and dominant_age_group:
        dominant_ratio_in_known = round((dominant_value / known_total) * 100, 2)
    else:
        dominant_ratio_in_known = 0.0

    return {
        "total": total,
        "known_total": known_total,
        "unknown_total": unknown_value,
        "unknown_ratio": unknown_ratio,
        "dominant_age_group": dominant_age_group,
        "dominant_value": dominant_value,
        "dominant_ratio_in_known": dominant_ratio_in_known,
    }


def fetch_region_rank() -> List[Dict[str, Any]]:
    params = {
        "serviceKey": SERVICE_KEY,
        "topN": REGION_TOP_N,
        "sortBy": REGION_SORT_BY,
        "sortOrder": REGION_SORT_ORDER,
        "dateFrom": DATE_FROM,
        "dateTo": DATE_TO,
        "target": TARGET,
        "dataType": "json",
    }

    items = _request_public_api(
        name="민원 발생 지역 순위",
        url=REGION_RANK_URL,
        params=params,
    )

    return _normalize_rank_items(items, name_key="region")


def fetch_organization_rank() -> List[Dict[str, Any]]:
    params = {
        "serviceKey": SERVICE_KEY,
        "topN": ORG_TOP_N,
        "sortBy": ORG_SORT_BY,
        "sortOrder": ORG_SORT_ORDER,
        "dateFrom": DATE_FROM,
        "dateTo": DATE_TO,
        "target": TARGET,
        "dataType": "json",
    }

    items = _request_public_api(
        name="민원 발생 기관 순위",
        url=ORG_RANK_URL,
        params=params,
    )

    return _normalize_rank_items(items, name_key="organization")


def fetch_keyword_age_distribution(keyword: str) -> Dict[str, Any]:
    clean_keyword = _clean_keyword(keyword)

    if not clean_keyword:
        return {
            "keyword": keyword,
            "searchword": clean_keyword,
            "age_distribution": [],
            "known_age_distribution": [],
            "age_summary": {
                "total": 0,
                "known_total": 0,
                "unknown_total": 0,
                "unknown_ratio": 0.0,
                "dominant_age_group": None,
                "dominant_value": 0,
                "dominant_ratio_in_known": 0.0,
            },
        }

    params = {
        "serviceKey": SERVICE_KEY,
        "searchword": clean_keyword,
        "dateFrom": DATE_FROM,
        "dateTo": DATE_TO,
        "resultCount": AGE_RESULT_COUNT,
        "target": TARGET,
        "dataType": "json",
    }

    items = _request_public_api(
        name=f"키워드 연령대 민원 현황 - {clean_keyword}",
        url=KEYWORD_AGE_URL,
        params=params,
    )

    age_distribution = _normalize_age_distribution(items)

    known_age_distribution = [
        item
        for item in age_distribution
        if item.get("age_group") != "연령 미상"
    ]

    age_summary = _build_age_summary(age_distribution)

    return {
        "keyword": keyword,
        "searchword": clean_keyword,
        "age_distribution": age_distribution,
        "known_age_distribution": known_age_distribution,
        "age_summary": age_summary,
    }


def collect_extra_datasets(keywords: List[str]) -> Dict[str, Any]:
    """
    지역/기관 순위는 전체 기간 기준으로 1회 수집.
    연령 정보는 키워드별로 반복 수집.
    """

    print("=" * 100)
    print("[START] 추가 데이터 수집 시작")
    print("=" * 100)

    region_rank = fetch_region_rank()
    organization_rank = fetch_organization_rank()

    keyword_age_map = {}

    unique_keywords = []

    for keyword in keywords:
        clean_keyword = _clean_keyword(keyword)

        if clean_keyword and clean_keyword not in unique_keywords:
            unique_keywords.append(clean_keyword)

    print(f"[INFO] 연령 정보 수집 대상 키워드: {unique_keywords}")

    for keyword in unique_keywords:
        age_result = fetch_keyword_age_distribution(keyword)
        keyword_age_map[keyword] = age_result

        # 공공 API에 너무 빠르게 연속 요청하지 않도록 짧게 대기
        time.sleep(0.2)

    result = {
        "period": {
            "date_from": DATE_FROM,
            "date_to": DATE_TO,
            "target": TARGET,
        },
        "region_rank": region_rank,
        "organization_rank": organization_rank,
        "keyword_age_map": keyword_age_map,
    }

    print("=" * 100)
    print("[DONE] 추가 데이터 수집 완료")
    print("=" * 100)
    print(f"[RESULT] region_rank={len(region_rank)}")
    print(f"[RESULT] organization_rank={len(organization_rank)}")
    print(f"[RESULT] keyword_age_map={len(keyword_age_map)}")

    return result


def pick_issue_keyword(issue: Dict[str, Any]) -> str:
    """
    dashboard payload의 issue에서 연령 정보 조회용 키워드를 하나 고른다.
    우선순위:
    1. top_keyword
    2. keywords 첫 번째
    3. title에서 '관련' 앞부분
    """

    top_keyword = issue.get("top_keyword")

    if top_keyword:
        return _clean_keyword(top_keyword)

    keywords = issue.get("keywords")

    if isinstance(keywords, list) and keywords:
        return _clean_keyword(str(keywords[0]))

    title = issue.get("title", "")

    if "관련" in title:
        return _clean_keyword(title.split("관련")[0])

    return _clean_keyword(title)


def enrich_dashboard_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    기존 dashboard payload에 새 데이터 3종을 추가한다.
    - 전체 payload 상단: region_rank, organization_rank
    - issue별: age_distribution, age_summary
    """

    issues = payload.get("issues", [])

    if not isinstance(issues, list):
        issues = []

    issue_keywords = []

    for issue in issues:
        if isinstance(issue, dict):
            keyword = pick_issue_keyword(issue)

            if keyword:
                issue_keywords.append(keyword)

    extra_data = collect_extra_datasets(issue_keywords)

    payload["extra_data_period"] = extra_data.get("period", {})
    payload["region_rank"] = extra_data.get("region_rank", [])
    payload["organization_rank"] = extra_data.get("organization_rank", [])

    keyword_age_map = extra_data.get("keyword_age_map", {})

    for issue in issues:
        if not isinstance(issue, dict):
            continue

        keyword = pick_issue_keyword(issue)
        clean_keyword = _clean_keyword(keyword)

        age_result = keyword_age_map.get(clean_keyword)

        if not age_result:
            issue["age_distribution"] = []
            issue["known_age_distribution"] = []
            issue["age_summary"] = {
                "total": 0,
                "known_total": 0,
                "unknown_total": 0,
                "unknown_ratio": 0.0,
                "dominant_age_group": None,
                "dominant_value": 0,
                "dominant_ratio_in_known": 0.0,
            }
            issue["age_analysis_message"] = "연령대별 민원 현황을 확인할 수 없습니다."
            continue

        issue["age_searchword"] = age_result.get("searchword")
        issue["age_distribution"] = age_result.get("age_distribution", [])
        issue["known_age_distribution"] = age_result.get("known_age_distribution", [])
        issue["age_summary"] = age_result.get("age_summary", {})

        age_summary = issue["age_summary"]
        dominant_age_group = age_summary.get("dominant_age_group")
        dominant_value = age_summary.get("dominant_value", 0)
        dominant_ratio = age_summary.get("dominant_ratio_in_known", 0.0)
        unknown_ratio = age_summary.get("unknown_ratio", 0.0)

        if dominant_age_group:
            issue["age_analysis_message"] = (
                f"연령 정보가 확인된 민원 기준으로 {dominant_age_group} 비중이 가장 높습니다. "
                f"{dominant_age_group} 민원은 {dominant_value}건이며, "
                f"확인된 연령대 중 {dominant_ratio}%를 차지합니다. "
                f"연령 미상 비율은 전체의 {unknown_ratio}%입니다."
            )
        else:
            issue["age_analysis_message"] = (
                f"연령 미상 데이터 비중이 높아 특정 연령대를 단정하기 어렵습니다. "
                f"연령 미상 비율은 전체의 {unknown_ratio}%입니다."
            )

    return payload