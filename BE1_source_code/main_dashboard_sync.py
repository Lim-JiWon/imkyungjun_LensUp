import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

from services.auto_keyword_service import discover_keywords
from services.public_api_service import fetch_dataset_by_type
from services.source_normalizer import normalize_items
from services.dashboard_payload_builder import build_dashboard_payload
from services.backend2_sender import send_to_backend2

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "cache" / "dashboard_sync"


def save_dashboard_snapshot(payload: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = OUTPUT_DIR / f"{ts}_dashboard_snapshot.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[SAVE] dashboard snapshot saved: {file_path}")


def save_dashboard_payload(payload: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = OUTPUT_DIR / f"{ts}_dashboard_payload.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[SAVE] dashboard payload saved: {file_path}")


def fetch_and_normalize(dataset_type, date_from, date_to, result_count=10, keyword=None):
    raw_items = fetch_dataset_by_type(
        dataset_type=dataset_type,
        date_from=date_from,
        date_to=date_to,
        result_count=result_count,
        keyword=keyword,
    )
    normalized = normalize_items(dataset_type, raw_items)
    return {
        "raw_count": len(raw_items),
        "normalized_count": len(normalized),
        "items": normalized,
    }


def ensure_date8(value: str) -> str:
    value = str(value).strip()
    return value[:8]


def ensure_datetime_start(value: str) -> str:
    value = str(value).strip()
    if len(value) >= 14:
        return value[:14]
    if len(value) == 8:
        return value + "000000"
    return value


def ensure_datetime_end(value: str) -> str:
    value = str(value).strip()
    if len(value) >= 14:
        return value[:14]
    if len(value) == 8:
        return value + "235959"
    return value


def main():
    raw_date_from = os.getenv("DATE_FROM", "20250301")
    raw_date_to = os.getenv("DATE_TO", "20250305")

    date_from_8 = ensure_date8(raw_date_from)
    date_to_8 = ensure_date8(raw_date_to)

    trend_date_from = ensure_datetime_start(raw_date_from)
    trend_date_to = ensure_datetime_end(raw_date_to)

    keyword_limit = int(os.getenv("AUTO_KEYWORD_LIMIT", "5"))
    result_count = int(os.getenv("AUTO_KEYWORD_RESULT_COUNT", "5"))

    print("=" * 70)
    print("[START] dashboard sync pipeline")
    print(f"date_from={date_from_8}, date_to={date_to_8}")
    print("=" * 70)

    # 1. 자동 키워드 발견
    final_keywords, merged = discover_keywords(
        date_from=date_from_8,
        date_to=date_to_8,
        limit=keyword_limit,
        result_count=result_count,
    )

    print(f"[INFO] discovered keywords count = {len(final_keywords)}")
    print(f"[INFO] discovered keywords = {final_keywords}")

    # 2. 오늘의 민원 이슈 수집
    print("[STEP] fetch today_issue")
    today_issue_result = fetch_and_normalize(
        dataset_type="today_issue",
        date_from=date_from_8,
        date_to=date_to_8,
        result_count=10,
    )

    # 3. 키워드별 상세 데이터 수집
    keyword_details = []

    for keyword in final_keywords:
        print("-" * 60)
        print(f"[KEYWORD] {keyword}")

        search_keyword = keyword.replace("_", " ")

        print("[STEP] fetch keyword_trend")
        trend_result = fetch_and_normalize(
            dataset_type="keyword_trend",
            date_from=trend_date_from,
            date_to=trend_date_to,
            result_count=10,
            keyword=search_keyword,
        )

        print("[STEP] fetch related_keywords")
        related_result = fetch_and_normalize(
            dataset_type="related_keywords",
            date_from=date_from_8,
            date_to=date_to_8,
            result_count=10,
            keyword=search_keyword,
        )

        print("[STEP] fetch keyword_complaint_count")
        count_result = fetch_and_normalize(
            dataset_type="keyword_complaint_count",
            date_from=date_from_8,
            date_to=date_to_8,
            result_count=10,
            keyword=search_keyword,
        )

        keyword_details.append({
            "keyword": keyword,
            "search_keyword": search_keyword,
            "trend": trend_result,
            "related_keywords": related_result,
            "complaint_count": count_result,
        })

    # 4. 스냅샷 생성
    dashboard_snapshot = {
        "synced_at": datetime.now().isoformat(),
        "date_from": date_from_8,
        "date_to": date_to_8,
        "today_issue": today_issue_result,
        "discovered_keywords": final_keywords,
        "merged_keyword_candidates": merged,
        "keyword_details": keyword_details,
    }

    # 5. snapshot 저장
    save_dashboard_snapshot(dashboard_snapshot)

    # 6. backend2 전송용 payload 생성
    dashboard_payload = build_dashboard_payload(dashboard_snapshot)

    # 7. payload 미리보기
    print("[PAYLOAD PREVIEW]")
    print(json.dumps(dashboard_payload, ensure_ascii=False, indent=2)[:5000])

    # 8. payload 저장
    save_dashboard_payload(dashboard_payload)

    # 9. backend2 전송
    success = send_to_backend2(dashboard_payload)
    print("[BACKEND2 SEND]", success)

    print("=" * 70)
    print("[END] dashboard sync pipeline complete")
    print("=" * 70)


def run_pipeline():
    print("\n=== 자동 실행 시작 ===")
    try:
        main()
    except Exception as e:
        print(f"[SCHEDULER ERROR] {e}")


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # 프로그램 시작 시 1회 즉시 실행
    run_pipeline()

    # 이후 10분마다 실행
    scheduler.add_job(
        run_pipeline,
        trigger="interval",
        minutes=10,
        id="dashboard_sync_job",
        replace_existing=True,
    )

    print("[START] scheduler running... (every 10 minutes)")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[STOP] scheduler stopped")