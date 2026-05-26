import json
from pathlib import Path
from collections import defaultdict


DASHBOARD_CACHE_DIR = Path("cache") / "dashboard_sync"
FINAL_FILE_NAME = "frontend_map_data_final.json"


CATEGORY_OVERRIDES = {
    "공중 목욕탕": "도시/시설",
}


CATEGORY_TAG_OVERRIDES = {
    "공중 목욕탕": ["목욕탕", "공중 목욕탕", "시설", "생활시설"],
}


def find_latest_recategorized_file() -> Path:
    candidates = list(DASHBOARD_CACHE_DIR.glob("*_frontend_map_data_recategorized.json"))

    if not candidates:
        raise FileNotFoundError(
            "cache/dashboard_sync 폴더에서 *_frontend_map_data_recategorized.json 파일을 찾지 못했습니다."
        )

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def build_category_stats(issues):
    category_map = defaultdict(
        lambda: {
            "category": "",
            "issue_count": 0,
            "total_complaint_count": 0,
            "critical_count": 0,
            "warning_count": 0,
            "growing_count": 0,
            "watch_count": 0,
            "stable_count": 0,
            "top_issues": [],
        }
    )

    for issue in issues:
        category = issue.get("category") or "기타"
        status = issue.get("status") or "unknown"
        complaint_count = safe_int(issue.get("complaint_count", 0))
        score = float(issue.get("score", 0) or 0)

        item = category_map[category]
        item["category"] = category
        item["issue_count"] += 1
        item["total_complaint_count"] += complaint_count

        if status == "critical":
            item["critical_count"] += 1
        elif status == "warning":
            item["warning_count"] += 1
        elif status == "growing":
            item["growing_count"] += 1
        elif status == "watch":
            item["watch_count"] += 1
        elif status == "stable":
            item["stable_count"] += 1

        item["top_issues"].append(
            {
                "issue_key": issue.get("issue_key"),
                "title": issue.get("title"),
                "status": status,
                "risk_level": issue.get("risk_level"),
                "score": score,
                "complaint_count": complaint_count,
                "top_keyword": issue.get("top_keyword"),
                "dominant_age_group": issue.get("age_summary", {}).get("dominant_age_group"),
                "dominant_age_value": issue.get("age_summary", {}).get("dominant_value"),
                "unknown_age_ratio": issue.get("age_summary", {}).get("unknown_ratio"),
            }
        )

    result = []

    for _, item in category_map.items():
        item["top_issues"].sort(
            key=lambda x: (
                safe_int(x.get("score", 0)),
                safe_int(x.get("complaint_count", 0)),
            ),
            reverse=True,
        )
        item["top_issues"] = item["top_issues"][:5]
        result.append(item)

    result.sort(
        key=lambda x: (
            x["critical_count"],
            x["warning_count"],
            x["growing_count"],
            x["total_complaint_count"],
        ),
        reverse=True,
    )

    return result


def apply_overrides(data):
    issues = data.get("issues", [])

    changed_count = 0

    for issue in issues:
        top_keyword = issue.get("top_keyword")

        if top_keyword in CATEGORY_OVERRIDES:
            old_category = issue.get("category")
            new_category = CATEGORY_OVERRIDES[top_keyword]

            issue["category"] = new_category
            issue["category_tags"] = CATEGORY_TAG_OVERRIDES.get(top_keyword, [])

            if old_category != new_category:
                changed_count += 1

    data["category_stats"] = build_category_stats(issues)

    if "meta" not in data:
        data["meta"] = {}

    data["meta"]["finalized"] = True
    data["meta"]["final_category_override_count"] = changed_count

    return data


def print_summary(data):
    print("\n[카테고리 요약]")
    for item in data.get("category_stats", []):
        print(
            f"- {item['category']} / 이슈 {item['issue_count']}개 / "
            f"민원 {item['total_complaint_count']}건 / "
            f"강한징후 {item['critical_count']}개 / "
            f"주의징후 {item['warning_count']}개"
        )

    print("\n[이슈별 카테고리]")
    for issue in data.get("issues", []):
        print(f"- {issue.get('top_keyword')} : {issue.get('category')}")


def main():
    print("=" * 100)
    print("[START] 프론트 지도 데이터 최종 정리")
    print("=" * 100)

    source_path = find_latest_recategorized_file()
    print(f"[INFO] 최신 보정 파일: {source_path}")

    data = load_json(source_path)
    data = apply_overrides(data)

    final_path = DASHBOARD_CACHE_DIR / FINAL_FILE_NAME
    save_json(data, final_path)

    print(f"[SAVE] 최종 프론트용 JSON 저장 완료: {final_path}")

    print_summary(data)

    print("\n[DONE] 완료")


if __name__ == "__main__":
    main()