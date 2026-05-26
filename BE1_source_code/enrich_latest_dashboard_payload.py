import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from services.extra_dataset_service import enrich_dashboard_payload


load_dotenv()


DASHBOARD_CACHE_DIR = Path("cache") / "dashboard_sync"


def find_latest_dashboard_payload() -> Path:
    if not DASHBOARD_CACHE_DIR.exists():
        raise FileNotFoundError(f"대시보드 캐시 폴더가 없습니다: {DASHBOARD_CACHE_DIR}")

    candidates = []

    for path in DASHBOARD_CACHE_DIR.glob("*_dashboard_payload.json"):
        if "enriched" in path.name:
            continue

        if "search_suggestions" in path.name:
            continue

        candidates.append(path)

    if not candidates:
        raise FileNotFoundError(
            "cache/dashboard_sync 폴더에서 *_dashboard_payload.json 파일을 찾지 못했습니다."
        )

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return candidates[0]


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, source_path: Path) -> Path:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = DASHBOARD_CACHE_DIR / f"{now}_dashboard_payload_enriched.json"

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return save_path


def print_enriched_summary(payload):
    issues = payload.get("issues", [])

    region_rank = payload.get("region_rank", [])
    organization_rank = payload.get("organization_rank", [])

    print("\n" + "=" * 100)
    print("[SUMMARY] enriched payload 요약")
    print("=" * 100)

    print(f"[INFO] issue_count = {len(issues)}")
    print(f"[INFO] region_rank_count = {len(region_rank)}")
    print(f"[INFO] organization_rank_count = {len(organization_rank)}")

    print("\n[지역 순위 TOP 5]")
    for item in region_rank[:5]:
        print(f"- {item.get('rank')}위 {item.get('region')} / {item.get('value')}건")

    print("\n[기관 순위 TOP 5]")
    for item in organization_rank[:5]:
        print(f"- {item.get('rank')}위 {item.get('organization')} / {item.get('value')}건")

    print("\n[이슈별 연령 분석]")
    for issue in issues:
        title = issue.get("title", "제목 없음")
        searchword = issue.get("age_searchword")
        age_summary = issue.get("age_summary", {})
        dominant_age_group = age_summary.get("dominant_age_group")
        dominant_value = age_summary.get("dominant_value")
        unknown_ratio = age_summary.get("unknown_ratio")

        print(f"- {title}")
        print(f"  검색 키워드: {searchword}")
        print(f"  주요 연령대: {dominant_age_group} / {dominant_value}건")
        print(f"  연령 미상 비율: {unknown_ratio}%")


def main():
    print("=" * 100)
    print("[START] 최신 dashboard payload에 지역/기관/연령 데이터 붙이기")
    print("=" * 100)

    latest_path = find_latest_dashboard_payload()

    print(f"[INFO] 최신 payload 파일: {latest_path}")

    payload = load_json(latest_path)

    if not isinstance(payload, dict):
        raise ValueError("dashboard payload가 dict 형태가 아닙니다.")

    if "issues" not in payload:
        raise ValueError("dashboard payload 안에 issues 필드가 없습니다.")

    enriched_payload = enrich_dashboard_payload(payload)

    save_path = save_json(enriched_payload, latest_path)

    print(f"\n[SAVE] enriched payload 저장 완료: {save_path}")

    print_enriched_summary(enriched_payload)

    print("\n[DONE] 완료")


if __name__ == "__main__":
    main()