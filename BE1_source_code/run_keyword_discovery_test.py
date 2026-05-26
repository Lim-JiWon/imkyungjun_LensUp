# run_keyword_discovery_test.py

import os
from dotenv import load_dotenv
from services.auto_keyword_service import discover_keywords

load_dotenv()


def main():
    date_from = os.getenv("DATE_FROM", "20260301")
    date_to = os.getenv("DATE_TO", "20260331")
    limit = int(os.getenv("AUTO_KEYWORD_LIMIT", "5"))
    result_count = int(os.getenv("AUTO_KEYWORD_RESULT_COUNT", "10"))

    print("=" * 70)
    print("[자동 키워드 발견 테스트 시작]")
    print(f"date_from={date_from}, date_to={date_to}, limit={limit}, result_count={result_count}")
    print("=" * 70)

    final_keywords, merged = discover_keywords(
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        result_count=result_count
    )

    print("\n[후보 키워드 점수표]")
    for idx, item in enumerate(merged, start=1):
        print(
            f"{idx}. {item['label']} | total_score={item['total_score']} "
            f"| best_rank={item['best_rank']} | max_value={item['max_value']} "
            f"| sources={item['sources']}"
        )

    print("\n[최종 처리 키워드]")
    for idx, keyword in enumerate(final_keywords, start=1):
        print(f"{idx}. {keyword}")

    if not final_keywords:
        print("\n[WARN] 최종 키워드가 비어 있습니다.")
        print("확인할 것:")
        print("1) .env의 PUBLIC_API_SURGE_URL / PUBLIC_API_CORE_URL")
        print("2) PUBLIC_API_SERVICE_KEY")
        print("3) dateFrom/dateTo 형식")
        print("4) backend1_project/cache/keyword_discovery/raw 안의 원본 JSON 구조")
    else:
        print("\n[OK] 자동 키워드 발견 테스트 성공")


if __name__ == "__main__":
    main()