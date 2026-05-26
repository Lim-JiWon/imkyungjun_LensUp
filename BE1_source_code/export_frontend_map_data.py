import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict


DASHBOARD_CACHE_DIR = Path("cache") / "dashboard_sync"


def find_latest_enriched_payload() -> Path:
    if not DASHBOARD_CACHE_DIR.exists():
        raise FileNotFoundError(f"폴더가 없습니다: {DASHBOARD_CACHE_DIR}")

    candidates = list(DASHBOARD_CACHE_DIR.glob("*_dashboard_payload_enriched.json"))

    if not candidates:
        raise FileNotFoundError(
            "cache/dashboard_sync 폴더에서 *_dashboard_payload_enriched.json 파일을 찾지 못했습니다."
        )

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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

    for category, item in category_map.items():
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


def build_frontend_issues(issues):
    frontend_issues = []

    for issue in issues:
        age_summary = issue.get("age_summary", {})

        frontend_issues.append(
            {
                "issue_key": issue.get("issue_key"),
                "title": issue.get("title"),
                "summary": issue.get("summary"),
                "forecast": issue.get("forecast"),
                "category": issue.get("category") or "기타",
                "category_tags": issue.get("category_tags", []),
                "cluster_keywords": issue.get("cluster_keywords", []),
                "status": issue.get("status"),
                "risk_level": issue.get("risk_level"),
                "score": issue.get("score"),
                "complaint_count": issue.get("complaint_count"),
                "top_keyword": issue.get("top_keyword"),
                "related_keywords": issue.get("related_keywords", [])[:5],
                "keyword_trends": issue.get("keyword_trends", []),
                "age_searchword": issue.get("age_searchword"),
                "known_age_distribution": issue.get("known_age_distribution", []),
                "age_summary": {
                    "dominant_age_group": age_summary.get("dominant_age_group"),
                    "dominant_value": age_summary.get("dominant_value"),
                    "dominant_ratio_in_known": age_summary.get("dominant_ratio_in_known"),
                    "unknown_ratio": age_summary.get("unknown_ratio"),
                    "known_total": age_summary.get("known_total"),
                    "total": age_summary.get("total"),
                },
                "age_analysis_message": issue.get("age_analysis_message"),
            }
        )

    frontend_issues.sort(
        key=lambda x: (
            safe_int(x.get("score", 0)),
            safe_int(x.get("complaint_count", 0)),
        ),
        reverse=True,
    )

    return frontend_issues


def build_region_summary(region_rank):
    if not region_rank:
        return {
            "top_region": None,
            "top_region_value": 0,
            "total_value": 0,
        }

    total_value = sum(safe_int(item.get("value", 0)) for item in region_rank)
    top = region_rank[0]

    return {
        "top_region": top.get("region"),
        "top_region_value": safe_int(top.get("value", 0)),
        "total_value": total_value,
    }


def build_organization_summary(organization_rank):
    if not organization_rank:
        return {
            "top_organization": None,
            "top_organization_value": 0,
        }

    top = organization_rank[0]

    return {
        "top_organization": top.get("organization"),
        "top_organization_value": safe_int(top.get("value", 0)),
    }


def save_json(data):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = DASHBOARD_CACHE_DIR / f"{now}_frontend_map_data.json"

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return save_path


def main():
    print("=" * 100)
    print("[START] 프론트 지도/카드 시각화용 JSON 생성")
    print("=" * 100)

    latest_path = find_latest_enriched_payload()
    print(f"[INFO] 최신 enriched payload: {latest_path}")

    payload = load_json(latest_path)

    issues = payload.get("issues", [])
    region_rank = payload.get("region_rank", [])
    organization_rank = payload.get("organization_rank", [])

    frontend_data = {
        "meta": {
            "batch_id": payload.get("batch_id"),
            "generated_at": payload.get("generated_at"),
            "source": payload.get("source"),
            "target": payload.get("target"),
            "date_from": payload.get("date_from"),
            "date_to": payload.get("date_to"),
            "extra_data_period": payload.get("extra_data_period", {}),
            "issue_count": len(issues),
            "region_count": len(region_rank),
            "organization_count": len(organization_rank),
        },
        "region_summary": build_region_summary(region_rank),
        "organization_summary": build_organization_summary(organization_rank),
        "region_rank": region_rank,
        "organization_rank": organization_rank,
        "category_stats": build_category_stats(issues),
        "issues": build_frontend_issues(issues),
    }

    save_path = save_json(frontend_data)

    print(f"[SAVE] 프론트용 JSON 저장 완료: {save_path}")

    print("\n[SUMMARY]")
    print(f"- 이슈 수: {len(frontend_data['issues'])}")
    print(f"- 지역 수: {len(frontend_data['region_rank'])}")
    print(f"- 기관/지자체 수: {len(frontend_data['organization_rank'])}")
    print(f"- 카테고리 수: {len(frontend_data['category_stats'])}")

    print("\n[지역 TOP 5]")
    for item in frontend_data["region_rank"][:5]:
        print(f"- {item.get('rank')}위 {item.get('region')} / {item.get('value')}건")

    print("\n[기관/지자체 TOP 5]")
    for item in frontend_data["organization_rank"][:5]:
        print(f"- {item.get('rank')}위 {item.get('organization')} / {item.get('value')}건")

    print("\n[카테고리 요약]")
    for item in frontend_data["category_stats"]:
        print(
            f"- {item['category']} / 이슈 {item['issue_count']}개 / "
            f"민원 {item['total_complaint_count']}건 / "
            f"강한징후 {item['critical_count']}개"
        )

    print("\n[DONE] 완료")


if __name__ == "__main__":
    main()