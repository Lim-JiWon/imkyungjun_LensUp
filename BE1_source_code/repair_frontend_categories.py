import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict


DASHBOARD_CACHE_DIR = Path("cache") / "dashboard_sync"


CATEGORY_RULES = {
    "도시/시설": [
        "데이터센터",
        "건립",
        "주거환경",
        "전자파",
        "과천시",
        "방송통신시설",
        "공원",
        "공원조성",
        "조성",
        "후보지",
        "매립지",
        "폐석회",
        "도시공원",
        "녹지",
        "시설",
        "주택",
        "주거",
        "목욕탕",
        "공중 목욕탕",
    ],
    "교통/자동차": [
        "자동차",
        "차량",
        "번호판",
        "도로",
        "교통",
        "주정차",
        "주차",
        "한국교통안전공단",
        "한국도로공사",
        "안전순찰원",
        "위반사항",
        "제동등",
        "후부반사지",
        "전기차",
        "충전",
        "충전구역",
    ],
    "행정/민원처리": [
        "조사",
        "조사요청",
        "요청",
        "재발",
        "재발방지",
        "방지",
        "사실관계",
        "행정",
        "행정조치",
        "행정처분",
        "과태료",
        "민원조사",
        "경찰청",
        "북부경찰청",
        "고소",
        "고발",
        "신고",
        "강제 집행",
        "강제집행",
        "강제체포",
        "강제수사",
        "수사",
        "압수",
        "압류",
        "몰수",
        "추징",
        "기소",
        "구치소",
        "교도소",
        "감금",
        "수감",
        "재물손괴",
        "공범",
    ],
    "복지/생활": [
        "장애인",
        "복지",
        "권익",
        "국가유공자",
        "어린이",
        "어린이제품",
        "KC미인증",
        "생활",
        "피부양자",
        "보건복지부",
    ],
    "금융/소비자": [
        "은행",
        "농협",
        "농협은행",
        "통장",
        "카드",
        "신용카드",
        "체크카드",
        "배송",
        "택배",
        "도착",
        "소비자",
    ],
    "환경/에너지": [
        "환경",
        "쓰레기",
        "무단투기",
        "폐기물",
        "에너지",
        "친환경",
        "전기차",
    ],
}


CATEGORY_PRIORITY = [
    "교통/자동차",
    "도시/시설",
    "행정/민원처리",
    "복지/생활",
    "금융/소비자",
    "환경/에너지",
]


def find_latest_frontend_map_data() -> Path:
    candidates = list(DASHBOARD_CACHE_DIR.glob("*_frontend_map_data.json"))

    if not candidates:
        raise FileNotFoundError(
            "cache/dashboard_sync 폴더에서 *_frontend_map_data.json 파일을 찾지 못했습니다."
        )

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data) -> Path:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = DASHBOARD_CACHE_DIR / f"{now}_frontend_map_data_recategorized.json"

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return save_path


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def normalize_text(value):
    if value is None:
        return ""

    return str(value).replace("_", " ").replace("/", " ").strip()


def collect_issue_text(issue):
    parts = []

    for key in [
        "title",
        "summary",
        "top_keyword",
        "category",
        "age_searchword",
    ]:
        parts.append(normalize_text(issue.get(key)))

    for list_key in [
        "category_tags",
        "cluster_keywords",
        "related_keywords",
    ]:
        values = issue.get(list_key, [])

        if isinstance(values, list):
            parts.extend(normalize_text(v) for v in values)

    return " ".join(parts)


def detect_category(issue):
    text = collect_issue_text(issue)

    scores = {}

    for category, keywords in CATEGORY_RULES.items():
        score = 0

        for keyword in keywords:
            if keyword in text:
                score += 1

        scores[category] = score

    # 핵심 키워드가 직접 들어간 경우 가중치 보정
    top_keyword = normalize_text(issue.get("top_keyword"))
    title = normalize_text(issue.get("title"))

    if "데이터센터" in top_keyword or "데이터센터" in title:
        scores["도시/시설"] += 5

    if "목욕탕" in top_keyword or "목욕탕" in title:
        scores["도시/시설"] += 4

    if "무단투기" in top_keyword or "무단투기" in title:
        scores["환경/에너지"] += 4

    if "은행" in top_keyword or "통장" in top_keyword or "배송" in top_keyword:
        scores["금융/소비자"] += 4

    if "국가유공자" in top_keyword:
        scores["복지/생활"] += 4

    if "자동차" in top_keyword or "차량" in top_keyword or "번호판" in top_keyword:
        scores["교통/자동차"] += 5

    if (
        "경찰청" in top_keyword
        or "강제" in top_keyword
        or "압수" in top_keyword
        or "압류" in top_keyword
        or "몰수" in top_keyword
        or "기소" in top_keyword
        or "감금" in top_keyword
        or "공범" in top_keyword
    ):
        scores["행정/민원처리"] += 5

    best_category = "기타"
    best_score = 0

    for category in CATEGORY_PRIORITY:
        score = scores.get(category, 0)

        if score > best_score:
            best_score = score
            best_category = category

    if best_score <= 0:
        return "기타", []

    matched_tags = []

    for keyword in CATEGORY_RULES.get(best_category, []):
        if keyword in text:
            matched_tags.append(keyword)

    # 너무 길어지지 않게 앞 8개만
    matched_tags = list(dict.fromkeys(matched_tags))[:8]

    return best_category, matched_tags


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


def main():
    print("=" * 100)
    print("[START] 프론트용 JSON 카테고리 보정")
    print("=" * 100)

    latest_path = find_latest_frontend_map_data()
    print(f"[INFO] 최신 frontend_map_data: {latest_path}")

    data = load_json(latest_path)

    issues = data.get("issues", [])

    if not isinstance(issues, list):
        raise ValueError("issues 필드가 list가 아닙니다.")

    changed_count = 0

    for issue in issues:
        old_category = issue.get("category") or "기타"
        new_category, new_tags = detect_category(issue)

        issue["original_category"] = old_category
        issue["category"] = new_category
        issue["category_tags"] = new_tags

        if old_category != new_category:
            changed_count += 1

    data["category_stats"] = build_category_stats(issues)

    data["meta"]["recategorized_at"] = datetime.now().isoformat()
    data["meta"]["category_changed_count"] = changed_count

    save_path = save_json(data)

    print(f"[SAVE] 보정된 프론트용 JSON 저장 완료: {save_path}")
    print(f"[RESULT] 변경된 카테고리 수: {changed_count}")

    print("\n[카테고리 요약]")
    for item in data["category_stats"]:
        print(
            f"- {item['category']} / 이슈 {item['issue_count']}개 / "
            f"민원 {item['total_complaint_count']}건 / "
            f"강한징후 {item['critical_count']}개 / "
            f"주의징후 {item['warning_count']}개"
        )

    print("\n[이슈별 카테고리]")
    for issue in issues:
        print(
            f"- {issue.get('top_keyword')} : "
            f"{issue.get('original_category')} → {issue.get('category')}"
        )

    print("\n[DONE] 완료")


if __name__ == "__main__":
    main()