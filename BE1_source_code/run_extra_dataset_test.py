import os
import json
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()


# =========================================================
# 기본 환경변수
# =========================================================

SERVICE_KEY = os.getenv("PUBLIC_API_SERVICE_KEY")
TARGET = os.getenv("PUBLIC_API_TARGET", "pttn")

DATE_FROM = os.getenv("DATE_FROM", "20260305")
DATE_TO = os.getenv("DATE_TO", "20260514")

TIMEOUT = int(os.getenv("PUBLIC_API_TIMEOUT", "60"))


# =========================================================
# 새로 추가한 API URL
# =========================================================

REGION_RANK_URL = os.getenv("PUBLIC_API_REGION_RANK_URL")
ORG_RANK_URL = os.getenv("PUBLIC_API_ORG_RANK_URL")
KEYWORD_AGE_URL = os.getenv("PUBLIC_API_KEYWORD_AGE_URL")


# =========================================================
# 지역 순위 설정
# =========================================================

REGION_TOP_N = int(os.getenv("PUBLIC_API_REGION_TOP_N", "17"))
REGION_SORT_BY = os.getenv("PUBLIC_API_REGION_SORT_BY", "VALUE")
REGION_SORT_ORDER = os.getenv("PUBLIC_API_REGION_SORT_ORDER", "false")


# =========================================================
# 기관 순위 설정
# =========================================================

ORG_TOP_N = int(os.getenv("PUBLIC_API_ORG_TOP_N", "10"))
ORG_SORT_BY = os.getenv("PUBLIC_API_ORG_SORT_BY", "VALUE")
ORG_SORT_ORDER = os.getenv("PUBLIC_API_ORG_SORT_ORDER", "false")


# =========================================================
# 키워드 연령 정보 설정
# =========================================================
# 연령 정보 API가 키워드 기반이면 searchword/searchWord/keyword 중 하나를 쓸 가능성이 큼.
# 일단 공원_조성 또는 공원을 기본 테스트 키워드로 사용.
# .env에 PUBLIC_API_AGE_TEST_KEYWORD=공원 이런 식으로 넣으면 그 값을 사용함.

AGE_TEST_KEYWORD = os.getenv("PUBLIC_API_AGE_TEST_KEYWORD", "공원")
AGE_RESULT_COUNT = int(os.getenv("PUBLIC_API_AGE_RESULT_COUNT", "10"))


# =========================================================
# 저장 경로
# =========================================================

CACHE_DIR = Path("cache") / "extra_dataset_tests"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def mask_key(value: str) -> str:
    if not value:
        return "None"

    if len(value) <= 10:
        return "****"

    return value[:5] + "****" + value[-5:]


def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def save_result(name: str, result):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = name.replace(" ", "_").replace("/", "_")
    save_path = CACHE_DIR / f"{now}_{safe_name}.json"

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[SAVE] 응답 저장 완료: {save_path}")


def extract_items(data):
    """
    공공데이터포털 응답 구조가 API마다 조금씩 달라서
    자주 나오는 위치를 최대한 찾아봄.
    """

    if data is None:
        return []

    if isinstance(data, list):
        return data

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
            return current

        if isinstance(current, dict):
            return [current]

    return []


def request_api(name: str, url: str, params: dict):
    print("\n" + "=" * 100)
    print(f"[TEST] {name}")
    print("=" * 100)

    if not url:
        print(f"[ERROR] {name} URL이 .env에 없습니다.")
        return {
            "name": name,
            "ok": False,
            "error": "URL missing",
            "url": url,
            "params": params,
        }

    safe_params = dict(params)

    if "serviceKey" in safe_params:
        safe_params["serviceKey"] = mask_key(str(safe_params["serviceKey"]))

    print("[INFO] 요청 URL")
    print(url)

    print("[INFO] 요청 파라미터")
    print_json(safe_params)

    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)

        print(f"[INFO] status_code = {response.status_code}")
        print(f"[INFO] content_type = {response.headers.get('Content-Type')}")

        final_url = response.url

        if SERVICE_KEY:
            final_url = final_url.replace(SERVICE_KEY, mask_key(SERVICE_KEY))

        print("[INFO] 최종 요청 URL")
        print(final_url)

        text = response.text.strip()

        print("[INFO] 응답 앞부분")
        print(text[:1500])

        result = {
            "name": name,
            "ok": response.status_code == 200,
            "status_code": response.status_code,
            "url": url,
            "final_url": final_url,
            "params": safe_params,
            "content_type": response.headers.get("Content-Type"),
            "raw_text_preview": text[:3000],
        }

        try:
            data = response.json()
            items = extract_items(data)

            result["json"] = data
            result["items_count"] = len(items)
            result["items_preview"] = items[:5]

            print("[RESULT] JSON 파싱 성공")
            print(f"[RESULT] 추출된 items 개수 = {len(items)}")

            if items:
                print("[RESULT] items 앞 5개")
                print_json(items[:5])
            else:
                print("[WARN] JSON은 파싱됐지만 items를 자동으로 찾지 못했습니다.")
                print("[ACTION] 아래 저장된 JSON 파일을 보고 실제 필드 위치를 확인해야 합니다.")

        except Exception as e:
            result["ok"] = False
            result["json_parse_error"] = str(e)

            print("[WARN] JSON 파싱 실패")
            print("[WARN] XML 또는 일반 텍스트 응답일 수 있습니다.")

        save_result(name, result)
        return result

    except requests.exceptions.RequestException as e:
        print("[ERROR] 요청 실패")
        print(e)

        result = {
            "name": name,
            "ok": False,
            "error": str(e),
            "url": url,
            "params": safe_params,
        }

        save_result(name, result)
        return result


def build_region_params():
    return {
        "serviceKey": SERVICE_KEY,
        "topN": REGION_TOP_N,
        "sortBy": REGION_SORT_BY,
        "sortOrder": REGION_SORT_ORDER,
        "dateFrom": DATE_FROM,
        "dateTo": DATE_TO,
        "target": TARGET,
        "dataType": "json",
    }


def build_org_params():
    return {
        "serviceKey": SERVICE_KEY,
        "topN": ORG_TOP_N,
        "sortBy": ORG_SORT_BY,
        "sortOrder": ORG_SORT_ORDER,
        "dateFrom": DATE_FROM,
        "dateTo": DATE_TO,
        "target": TARGET,
        "dataType": "json",
    }


def build_keyword_age_params():
    """
    키워드 연령 정보 API는 문서에 따라 파라미터명이 다를 수 있음.
    우선 가장 가능성 높은 searchword를 사용.
    만약 400/500/파라미터 오류가 뜨면 searchWord 또는 keyword로 바꿔서 다시 테스트하면 됨.
    """

    return {
        "serviceKey": SERVICE_KEY,
        "searchword": AGE_TEST_KEYWORD,
        "dateFrom": DATE_FROM,
        "dateTo": DATE_TO,
        "resultCount": AGE_RESULT_COUNT,
        "target": TARGET,
        "dataType": "json",
    }


def print_summary(results):
    print("\n" + "=" * 100)
    print("[SUMMARY] 새로 추가한 API 테스트 결과")
    print("=" * 100)

    for result in results:
        name = result.get("name")
        ok = result.get("ok")
        status_code = result.get("status_code")
        items_count = result.get("items_count", 0)

        if ok:
            print(f"[OK] {name} / status={status_code} / items={items_count}")
        else:
            print(f"[FAIL] {name} / status={status_code} / error={result.get('error') or result.get('json_parse_error')}")

    print("\n[CHECK] 다음 단계 판단 기준")
    print("- 셋 다 status_code=200이면 source_registry.py에 정식 등록")
    print("- items_count가 1개 이상이면 source_normalizer.py에서 필드명 매핑")
    print("- 키워드 연령 정보만 실패하면 searchword 파라미터명을 searchWord 또는 keyword로 바꿔서 재테스트")


def main():
    print("=" * 100)
    print("[START] 지역 순위 / 기관 순위 / 키워드 연령 정보 API 통합 테스트")
    print("=" * 100)

    if not SERVICE_KEY:
        print("[ERROR] PUBLIC_API_SERVICE_KEY가 .env에 없습니다.")
        return

    print("[INFO] 기본 설정")
    print_json(
        {
            "PUBLIC_API_SERVICE_KEY": mask_key(SERVICE_KEY),
            "PUBLIC_API_TARGET": TARGET,
            "DATE_FROM": DATE_FROM,
            "DATE_TO": DATE_TO,
            "PUBLIC_API_REGION_RANK_URL": REGION_RANK_URL,
            "PUBLIC_API_ORG_RANK_URL": ORG_RANK_URL,
            "PUBLIC_API_KEYWORD_AGE_URL": KEYWORD_AGE_URL,
            "PUBLIC_API_AGE_TEST_KEYWORD": AGE_TEST_KEYWORD,
        }
    )

    results = []

    results.append(
        request_api(
            name="민원 발생 지역 순위",
            url=REGION_RANK_URL,
            params=build_region_params(),
        )
    )

    results.append(
        request_api(
            name="민원 발생 기관 순위",
            url=ORG_RANK_URL,
            params=build_org_params(),
        )
    )

    results.append(
        request_api(
            name="키워드 연령대 민원 현황",
            url=KEYWORD_AGE_URL,
            params=build_keyword_age_params(),
        )
    )

    print_summary(results)


if __name__ == "__main__":
    main()