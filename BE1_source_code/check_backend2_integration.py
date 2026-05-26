import os
import json
from datetime import datetime
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()


BACKEND2_URL = os.getenv("BACKEND2_URL", "").strip()
API_KEY = os.getenv("BACKEND2_API_KEY") or os.getenv("PIPELINE_API_KEY")


def get_base_url() -> str:
    if not BACKEND2_URL:
        raise ValueError("BACKEND2_URL이 .env에 없습니다.")

    parsed = urlparse(BACKEND2_URL)
    return f"{parsed.scheme}://{parsed.netloc}"


def print_section(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_response(name: str, response: requests.Response):
    print(f"[{name}] status={response.status_code}")
    text = response.text or ""
    print(text[:1000])


def check_openapi(base_url: str):
    print_section("[1] OpenAPI 확인")

    url = f"{base_url}/openapi.json"

    try:
        response = requests.get(url, timeout=10)
        print(f"[GET] {url}")
        print(f"[STATUS] {response.status_code}")

        if response.status_code != 200:
            print("[WARN] openapi.json 접근 실패")
            print(response.text[:1000])
            return

        data = response.json()
        paths = data.get("paths", {})

        print("[OK] openapi.json 접근 성공")
        print("[ROUTES]")
        for path in sorted(paths.keys()):
            print(f"  - {path}")

        expected_routes = [
            "/admin/pipeline/ingest",
            "/dashboard",
            "/issues",
            "/issues/{issue_id}",
            "/issues/search",
        ]

        print("\n[ROUTE CHECK]")
        for route in expected_routes:
            if route in paths:
                print(f"  [OK] {route}")
            else:
                print(f"  [MISSING] {route}")

    except Exception as e:
        print(f"[ERROR] OpenAPI 확인 실패: {e}")


def check_docs(base_url: str):
    print_section("[2] /docs 확인")

    url = f"{base_url}/docs"

    try:
        response = requests.get(url, timeout=10)
        print(f"[GET] {url}")
        print(f"[STATUS] {response.status_code}")

        if response.status_code == 200:
            print("[OK] Swagger docs 접근 가능")
        else:
            print("[WARN] Swagger docs 접근 실패")
            print(response.text[:500])

    except Exception as e:
        print(f"[ERROR] /docs 확인 실패: {e}")


def build_test_payload():
    now = datetime.now().strftime("%Y%m%d%H%M%S")

    return {
        "batch_id": f"integration-test-batch-{now}",
        "generated_at": datetime.now().isoformat(),
        "source": "backend1_integration_test",
        "target": "pttn",
        "date_from": "20250301",
        "date_to": "20250305",
        "issues": [
            {
                "issue_key": f"integration-test-search-{now}",
                "issue_type": "dashboard_keyword_issue",
                "title": "검색 연동 테스트용 불법 주정차 이슈",
                "summary": "백엔드1과 백엔드2 검색 연동을 확인하기 위한 테스트 이슈입니다.",
                "forecast": "테스트 데이터이므로 실제 예측에는 사용하지 않습니다.",
                "causes": [
                    "검색 연동 테스트"
                ],
                "keywords": [
                    "불법 주정차"
                ],
                "rising_keywords": [
                    "불법_주정차"
                ],
                "related_keywords": [
                    "주차",
                    "주정차",
                    "불법주차"
                ],
                "keyword_trends": [
                    {
                        "date": "20250301",
                        "value": 100
                    },
                    {
                        "date": "20250302",
                        "value": 120
                    }
                ],
                "search_aliases": [
                    "주차",
                    "주정차",
                    "불법주차",
                    "불법 주차",
                    "주차 신고",
                    "주정차 신고"
                ],
                "status": "detected",
                "risk_level": "low",
                "score": 45.0,
                "complaint_count": 100,
                "top_keyword": "불법 주정차"
            }
        ]
    }


def check_ingest():
    print_section("[3] /admin/pipeline/ingest POST 확인")

    if not BACKEND2_URL:
        print("[ERROR] BACKEND2_URL이 없습니다.")
        return False

    if not API_KEY:
        print("[ERROR] BACKEND2_API_KEY 또는 PIPELINE_API_KEY가 없습니다.")
        return False

    payload = build_test_payload()

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY,
    }

    print(f"[POST] {BACKEND2_URL}")
    print(f"[batch_id] {payload['batch_id']}")
    print(f"[issue_key] {payload['issues'][0]['issue_key']}")

    try:
        response = requests.post(
            BACKEND2_URL,
            json=payload,
            headers=headers,
            timeout=60,
        )

        print(f"[STATUS] {response.status_code}")
        print("[BODY]")
        print(response.text[:2000])

        if response.status_code == 200:
            print("[OK] ingest 성공")
            return True

        print("[FAIL] ingest 실패")
        return False

    except requests.exceptions.Timeout:
        print("[TIMEOUT] 백엔드2가 60초 안에 응답하지 않았습니다.")
        print("가능성: ingest 내부 DB 저장 지연, search_aliases 저장 처리 문제, 서버/DB lock")
        return False

    except Exception as e:
        print(f"[ERROR] ingest 요청 실패: {e}")
        return False


def check_get_endpoint(base_url: str, path: str):
    print_section(f"[4] GET {path} 확인")

    url = f"{base_url}{path}"

    try:
        response = requests.get(url, timeout=15)
        print(f"[GET] {url}")
        print(f"[STATUS] {response.status_code}")

        if response.status_code == 200:
            print("[OK] 조회 성공")
            print(response.text[:2000])
        else:
            print("[WARN] 조회 실패")
            print(response.text[:1000])

    except Exception as e:
        print(f"[ERROR] GET {path} 실패: {e}")


def check_search_api(base_url: str):
    print_section("[5] 검색 API 확인")

    candidate_urls = [
        f"{base_url}/issues/search?q=주차",
        f"{base_url}/issues/search?query=주차",
        f"{base_url}/search/issues?q=주차",
        f"{base_url}/search?q=주차",
    ]

    for url in candidate_urls:
        try:
            response = requests.get(url, timeout=15)
            print(f"\n[GET] {url}")
            print(f"[STATUS] {response.status_code}")

            if response.status_code == 200:
                print("[OK] 검색 API 응답 성공")
                print(response.text[:2000])
                return

            print(response.text[:500])

        except Exception as e:
            print(f"[ERROR] {url} 실패: {e}")

    print("\n[INFO] 검색 API는 아직 없거나 경로가 다를 수 있습니다.")


def main():
    print_section("[BACKEND2 INTEGRATION CHECK]")

    if not BACKEND2_URL:
        print("[ERROR] .env에 BACKEND2_URL이 없습니다.")
        return

    base_url = get_base_url()

    print(f"BACKEND2_URL={BACKEND2_URL}")
    print(f"BASE_URL={base_url}")
    print(f"API_KEY 설정 여부={bool(API_KEY)}")

    check_openapi(base_url)
    check_docs(base_url)

    ingest_success = check_ingest()

    check_get_endpoint(base_url, "/dashboard")
    check_get_endpoint(base_url, "/issues")

    check_search_api(base_url)

    print_section("[RESULT SUMMARY]")

    if ingest_success:
        print("[OK] 백엔드2 ingest 연동은 성공했습니다.")
        print("다음 확인: /dashboard 또는 /issues에서 방금 보낸 테스트 이슈가 내려오는지 확인하세요.")
    else:
        print("[FAIL] 백엔드2 ingest 연동이 아직 실패했습니다.")
        print("다음 확인: 백엔드2 서버 로그에서 /admin/pipeline/ingest 처리 중 멈추는 지점을 확인해야 합니다.")


if __name__ == "__main__":
    main()