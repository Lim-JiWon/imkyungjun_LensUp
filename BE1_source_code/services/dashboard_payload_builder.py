from datetime import datetime
from typing import Any, Dict, List
import hashlib


SEARCH_SYNONYMS = {
    "불법 주정차": [
        "주차",
        "주정차",
        "불법주차",
        "불법 주차",
        "주차 신고",
        "주정차 신고",
        "불법주정차 신고",
        "불법주차 신고",
        "도로 주차",
        "주차 민원",
    ],
    "주정차 신고": [
        "주차",
        "주정차",
        "불법 주정차",
        "불법주정차",
        "불법주차",
        "주차 민원",
    ],
    "친환경차 충전구역": [
        "전기차",
        "친환경차",
        "충전구역",
        "전기차 충전",
        "전기차 충전소",
        "충전소",
        "전기차 주차",
        "충전 방해",
    ],
    "국토교통부 자동차운영보험": [
        "자동차",
        "자동차 보험",
        "보험",
        "자동차 운영",
        "차량 보험",
        "자동차 민원",
    ],
    "보건복지부 장애인권익지원": [
        "장애인",
        "장애인 지원",
        "장애인 권익",
        "복지",
        "보건복지부",
        "장애인 복지",
        "권익 지원",
        "장애인 주차",
        "장애인 전용구역",
    ],
    "공원 조성": [
        "공원",
        "공원 조성",
        "도시공원",
        "후보지",
        "매립지",
        "폐석회 매립지",
        "녹지",
        "도시 시설",
    ],
    "재발 방지": [
        "재발",
        "재발 방지",
        "과태료",
        "행정처분",
        "행정조치",
        "안전조치",
        "사후조치",
    ],
    "조사 요청": [
        "조사",
        "조사 요청",
        "사실관계",
        "행정 조치",
        "행정조치",
        "민원 조사",
        "어린이 제품",
        "KC미인증",
    ],
    "한국교통안전공단 자동차": [
        "자동차",
        "교통안전",
        "교통안전공단",
        "한국교통안전공단",
        "안전기준",
        "위반사항",
        "제동등",
        "후부반사지",
    ],
    "한국도로공사 안전순찰원": [
        "도로공사",
        "한국도로공사",
        "안전순찰원",
        "도로 안전",
        "교통 안전",
        "위반사항",
    ],
}


ISSUE_CATEGORY_RULES = {
    "교통/자동차": [
        "자동차",
        "차량",
        "번호판",
        "도로",
        "교통",
        "주정차",
        "주차",
        "안전기준",
        "제동등",
        "후부반사지",
        "반사지",
        "한국교통안전공단",
        "한국도로공사",
        "안전순찰원",
        "도로공사",
        "교통안전",
        "전기차",
        "충전구역",
        "충전소",
    ],
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
        "폐석회매립지",
        "도시공원",
        "녹지",
        "시설",
        "도시",
        "목욕탕",
        "공중목욕탕",
        "주택",
        "주거",
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
        "강제",
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
        "내란죄",
        "청구취지",
    ],
    "복지/생활": [
        "장애인",
        "복지",
        "권익",
        "장애인권익지원",
        "보건복지부",
        "전용구역",
        "어린이",
        "어린이제품",
        "KC미인증",
        "생활",
        "국가유공자",
        "피부양자",
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
        "이체",
    ],
    "환경/에너지": [
        "환경",
        "쓰레기",
        "무단투기",
        "폐기물",
        "전기차",
        "친환경차",
        "충전",
        "충전구역",
        "충전소",
        "충전방해",
        "방해행위",
        "에너지",
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


ALIAS_STOPWORDS = {
    "자동",
    "처리",
    "신청",
    "추가",
    "자료",
    "사건",
    "관련",
    "중심",
    "민원",
    "키워드",
    "분석",
    "결과",
    "기간",
    "전체",
    "변화율",
    "정보",
    "확인",
    "요청",
    "발생",
    "사용",
    "해당",
    "이슈",
    "점수",
    "건수",
    "주요",
    "연관어",
    "추이",
    "평균",
    "최근",
    "전날",
    "대비",
    "필요",
    "관찰",
    "안정",
    "주의",
    "강한",
    "증가",
}


SAFE_SHORT_ALIASES = {
    "공원",
    "주차",
    "도로",
    "교통",
    "조사",
    "재발",
    "행정",
    "복지",
    "장애",
    "전기",
    "충전",
    "은행",
    "통장",
    "배송",
    "택배",
    "압수",
    "압류",
    "기소",
    "공범",
    "감금",
    "수감",
    "차량",
}


TRAFFIC_TERMS = {
    "자동차",
    "차량",
    "기아자동차",
    "쏘렌토",
    "번호판",
    "도로",
    "교통",
    "주정차",
    "주차",
    "제동등",
    "후부반사지",
    "한국교통안전공단",
    "한국도로공사",
    "도로공사",
    "안전순찰원",
}


FINANCE_TERMS = {
    "은행",
    "농협",
    "농협은행",
    "통장",
    "카드",
    "신용카드",
    "체크카드",
    "이체",
    "배송",
    "택배",
    "도착",
}


ADMIN_TERMS = {
    "경찰청",
    "북부경찰청",
    "강제",
    "강제집행",
    "강제체포",
    "강제수사",
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
    "내란죄",
    "청구취지",
}


FACILITY_TERMS = {
    "데이터센터",
    "건립",
    "주거환경",
    "전자파",
    "과천시",
    "방송통신시설",
    "공원",
    "목욕탕",
    "공중목욕탕",
    "시설",
    "주거",
}


ENV_TERMS = {
    "쓰레기",
    "무단투기",
    "폐기물",
    "환경",
}


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _normalize_keyword_text(text: Any) -> str:
    if not text:
        return ""
    return str(text).strip()


def _compact_text(text: Any) -> str:
    return _normalize_keyword_text(text).replace("_", "").replace(" ", "")


def _build_issue_key(keyword: str, date_from: str, date_to: str) -> str:
    base = _normalize_keyword_text(keyword).replace(" ", "_")
    if not base:
        base = "unknown_keyword"

    raw_key = f"{base}|{date_from}|{date_to}"
    stable_hash = hashlib.md5(raw_key.encode("utf-8")).hexdigest()[:12]

    return f"dashboard-{base}-{stable_hash}"


def _contains_any(text: str, terms: set) -> bool:
    compact = _compact_text(text)

    for term in terms:
        if _compact_text(term) in compact:
            return True

    return False


def _tokenize(text: str) -> List[str]:
    text = _normalize_keyword_text(text).replace("_", " ")
    return [token.strip() for token in text.split() if token.strip()]


def _extract_complaint_count(detail: Dict[str, Any]) -> int:
    items = detail.get("complaint_count", {}).get("items", [])
    if not items:
        return 0

    first = items[0]
    return _safe_int(first.get("value"), 0)


def _extract_related_keywords(detail: Dict[str, Any], limit: int = 10) -> List[str]:
    items = detail.get("related_keywords", {}).get("items", [])
    result = []

    for item in items[:limit]:
        label = _normalize_keyword_text(item.get("label"))
        if label:
            result.append(label)

    return result


def _detect_primary_category_from_keyword(search_keyword: str) -> str:
    keyword = _normalize_keyword_text(search_keyword)

    if _contains_any(keyword, {"자동차", "차량", "번호판", "한국교통안전공단", "한국도로공사", "도로공사", "안전순찰원"}):
        return "교통/자동차"

    if _contains_any(keyword, {"데이터센터", "공원", "목욕탕", "공중목욕탕", "주거환경", "시설"}):
        return "도시/시설"

    if _contains_any(keyword, {"농협", "농협은행", "은행", "통장", "배송", "택배", "도착", "카드", "이체"}):
        return "금융/소비자"

    if _contains_any(keyword, {"무단투기", "쓰레기", "폐기물", "환경"}):
        return "환경/에너지"

    if _contains_any(keyword, {"국가유공자", "장애인", "복지", "어린이", "KC미인증"}):
        return "복지/생활"

    if _contains_any(keyword, ADMIN_TERMS):
        return "행정/민원처리"

    return "기타"


def _is_conflicting_related_keyword(primary_category: str, related_word: str) -> bool:
    """
    공공 API 연관어에 엉뚱한 단어가 섞일 수 있어서,
    이슈의 핵심 카테고리와 충돌하는 연관어는 검색/카테고리/클러스터에서 제외한다.

    예:
    농협은행 통장 이슈에 '기아자동차 쏘렌토 차량'이 섞이면 자동차 검색에 잡히므로 제외.
    """

    if primary_category == "기타":
        return False

    if primary_category != "교통/자동차" and _contains_any(related_word, TRAFFIC_TERMS):
        return True

    if primary_category != "금융/소비자" and _contains_any(related_word, FINANCE_TERMS):
        return True

    if primary_category != "도시/시설" and _contains_any(related_word, FACILITY_TERMS):
        return True

    if primary_category != "환경/에너지" and _contains_any(related_word, ENV_TERMS):
        return True

    return False


def _filter_related_keywords(search_keyword: str, related_keywords: List[str], limit: int = 10) -> List[str]:
    primary_category = _detect_primary_category_from_keyword(search_keyword)

    filtered = []
    seen = set()

    for word in related_keywords:
        word = _normalize_keyword_text(word)

        if not word:
            continue

        if _is_conflicting_related_keyword(primary_category, word):
            continue

        key = _compact_text(word)
        if key in seen:
            continue

        seen.add(key)
        filtered.append(word)

        if len(filtered) >= limit:
            break

    return filtered


def _extract_keyword_trends(detail: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = detail.get("trend", {}).get("items", [])
    result = []

    for item in items:
        date_value = item.get("date") or item.get("label") or ""
        value = _safe_int(item.get("value"), 0)

        if date_value:
            result.append({
                "date": str(date_value),
                "value": value,
            })

    return result


def _extract_rising_keywords(snapshot: Dict[str, Any], limit: int = 5) -> List[str]:
    keywords = snapshot.get("discovered_keywords", [])
    result = []

    for keyword in keywords[:limit]:
        text = _normalize_keyword_text(keyword)
        if text:
            result.append(text)

    return result


def _is_rising_keyword(keyword: str, search_keyword: str, rising_keywords: List[str]) -> bool:
    keyword_compact = _compact_text(keyword)
    search_keyword_compact = _compact_text(search_keyword)

    for rising in rising_keywords:
        rising_compact = _compact_text(rising)

        if not rising_compact:
            continue

        if (
            rising_compact == keyword_compact
            or rising_compact == search_keyword_compact
            or rising_compact in keyword_compact
            or keyword_compact in rising_compact
            or rising_compact in search_keyword_compact
            or search_keyword_compact in rising_compact
        ):
            return True

    return False


def _percent_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


def _analyze_trend(keyword_trends: List[Dict[str, Any]]) -> Dict[str, Any]:
    values = []

    for item in keyword_trends:
        value = _safe_float(item.get("value"), 0.0)
        values.append(value)

    if not values:
        return {
            "has_trend": False,
            "first_value": 0.0,
            "last_value": 0.0,
            "previous_value": 0.0,
            "average_value": 0.0,
            "change_value": 0.0,
            "overall_change_rate": 0.0,
            "day_change_rate": 0.0,
            "recent_average": 0.0,
            "previous_average": 0.0,
            "recent_average_change_rate": 0.0,
            "last_vs_average_rate": 0.0,
            "direction": "unknown",
            "signal": "insufficient",
        }

    first_value = values[0]
    last_value = values[-1]
    previous_value = values[-2] if len(values) >= 2 else values[0]
    average_value = sum(values) / len(values)

    change_value = last_value - first_value
    overall_change_rate = _percent_change(last_value, first_value)
    day_change_rate = _percent_change(last_value, previous_value)

    if len(values) >= 4:
        recent_values = values[-2:]
        previous_values = values[:-2]
        recent_average = sum(recent_values) / len(recent_values)
        previous_average = sum(previous_values) / len(previous_values) if previous_values else 0.0
    elif len(values) >= 2:
        recent_average = values[-1]
        previous_average = values[0]
    else:
        recent_average = values[-1]
        previous_average = values[0]

    recent_average_change_rate = _percent_change(recent_average, previous_average)
    last_vs_average_rate = _percent_change(last_value, average_value)

    if overall_change_rate >= 15 and recent_average_change_rate >= 5:
        direction = "rising"
        signal = "strong_rise"
    elif overall_change_rate >= 5 or recent_average_change_rate >= 10:
        direction = "slightly_rising"
        signal = "rise"
    elif day_change_rate >= 50 and last_vs_average_rate >= 10:
        direction = "rebound"
        signal = "rebound"
    elif overall_change_rate <= -15 and recent_average_change_rate <= -10:
        direction = "falling"
        signal = "fall"
    else:
        direction = "stable"
        signal = "stable"

    return {
        "has_trend": True,
        "first_value": round(first_value, 2),
        "last_value": round(last_value, 2),
        "previous_value": round(previous_value, 2),
        "average_value": round(average_value, 2),
        "change_value": round(change_value, 2),
        "overall_change_rate": round(overall_change_rate, 2),
        "day_change_rate": round(day_change_rate, 2),
        "recent_average": round(recent_average, 2),
        "previous_average": round(previous_average, 2),
        "recent_average_change_rate": round(recent_average_change_rate, 2),
        "last_vs_average_rate": round(last_vs_average_rate, 2),
        "direction": direction,
        "signal": signal,
    }


def _calculate_detection_score(
    complaint_count: int,
    keyword_trends: List[Dict[str, Any]],
    related_keywords: List[str],
    is_rising_keyword: bool,
) -> Dict[str, Any]:
    trend = _analyze_trend(keyword_trends)

    score = 20.0
    reasons = []

    if complaint_count >= 50000:
        score += 30
        reasons.append("민원 건수가 매우 높음")
    elif complaint_count >= 10000:
        score += 25
        reasons.append("민원 건수가 높음")
    elif complaint_count >= 5000:
        score += 20
        reasons.append("민원 건수가 많은 편")
    elif complaint_count >= 1000:
        score += 15
        reasons.append("민원 건수가 관찰 기준 이상")
    elif complaint_count >= 500:
        score += 10
        reasons.append("민원 건수가 일정 수준 이상")
    elif complaint_count >= 100:
        score += 5
        reasons.append("민원 건수가 최소 관찰 기준 이상")

    if trend["has_trend"]:
        overall_change_rate = trend["overall_change_rate"]
        day_change_rate = trend["day_change_rate"]
        recent_average_change_rate = trend["recent_average_change_rate"]
        last_vs_average_rate = trend["last_vs_average_rate"]

        if overall_change_rate >= 15:
            score += 15
            reasons.append(f"기간 전체 변화율이 {overall_change_rate}% 증가")
        elif overall_change_rate >= 5:
            score += 8
            reasons.append(f"기간 전체 변화율이 {overall_change_rate}% 소폭 증가")

        if recent_average_change_rate >= 15:
            score += 15
            reasons.append(f"최근 2일 평균이 이전 기간 평균보다 {recent_average_change_rate}% 증가")
        elif recent_average_change_rate >= 5:
            score += 8
            reasons.append(f"최근 2일 평균이 이전 기간 평균보다 {recent_average_change_rate}% 소폭 증가")

        if day_change_rate >= 100:
            if overall_change_rate > 0 or recent_average_change_rate > 0:
                score += 10
                reasons.append(f"전날 대비 마지막 값이 {day_change_rate}% 급증")
            else:
                score += 3
                reasons.append(f"전날 대비 마지막 값은 {day_change_rate}% 반등했지만 전체 흐름은 감소")
        elif day_change_rate >= 30:
            if overall_change_rate > 0 or recent_average_change_rate > 0:
                score += 6
                reasons.append(f"전날 대비 마지막 값이 {day_change_rate}% 증가")
            else:
                score += 2
                reasons.append(f"전날 대비 마지막 값은 {day_change_rate}% 반등했지만 전체 흐름은 감소")

        if last_vs_average_rate >= 20:
            if overall_change_rate > 0 or recent_average_change_rate > 0:
                score += 8
                reasons.append(f"마지막 값이 전체 평균보다 {last_vs_average_rate}% 높음")
            else:
                score += 3
                reasons.append(f"마지막 값은 평균보다 {last_vs_average_rate}% 높지만 전체 추세는 감소")
        elif last_vs_average_rate >= 10:
            if overall_change_rate > 0 or recent_average_change_rate > 0:
                score += 4
                reasons.append(f"마지막 값이 전체 평균보다 {last_vs_average_rate}% 소폭 높음")
            else:
                score += 1
                reasons.append(f"마지막 값은 평균보다 {last_vs_average_rate}% 높지만 증가 추세는 제한적")

    if is_rising_keyword:
        score += 10
        reasons.append("자동 발견된 급등 키워드에 포함됨")

    if len(related_keywords) >= 7:
        score += 5
        reasons.append("연관 키워드가 충분히 수집됨")
    elif len(related_keywords) >= 4:
        score += 3
        reasons.append("연관 키워드가 일부 수집됨")

    if trend["has_trend"]:
        if trend["overall_change_rate"] < 0 and trend["recent_average_change_rate"] < 0:
            score = min(score, 55.0)

    score = round(min(score, 100.0), 1)

    return {
        "score": score,
        "trend": trend,
        "reasons": reasons,
    }


def _calculate_risk_level(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 65:
        return "high"
    if score >= 50:
        return "medium"
    return "low"


def _calculate_status(score: float, trend: Dict[str, Any]) -> str:
    signal = trend.get("signal", "stable")
    overall_change_rate = trend.get("overall_change_rate", 0.0)
    recent_average_change_rate = trend.get("recent_average_change_rate", 0.0)
    day_change_rate = trend.get("day_change_rate", 0.0)
    last_vs_average_rate = trend.get("last_vs_average_rate", 0.0)

    has_overall_growth = overall_change_rate > 0
    has_recent_average_growth = recent_average_change_rate > 0

    if overall_change_rate < 0 and recent_average_change_rate < 0:
        if score >= 35:
            return "watch"
        return "stable"

    if score >= 80 and (has_overall_growth or has_recent_average_growth):
        return "critical"

    if score >= 65 and (has_overall_growth or has_recent_average_growth):
        return "warning"

    if signal in {"strong_rise", "rise"} and score >= 50:
        return "growing"

    if day_change_rate >= 50 and last_vs_average_rate >= 10:
        return "watch"

    if score >= 35:
        return "watch"

    return "stable"


def _build_summary(
    keyword: str,
    complaint_count: int,
    related_keywords: List[str],
    keyword_trends: List[Dict[str, Any]],
    detection: Dict[str, Any],
) -> str:
    related_part = ", ".join(related_keywords[:3]) if related_keywords else "연관어 정보 없음"
    trend = detection["trend"]
    score = detection["score"]

    if trend["has_trend"]:
        trend_part = (
            f"기간 내 추이 값은 {int(trend['first_value'])} → {int(trend['last_value'])}이며, "
            f"기간 전체 변화율은 {trend['overall_change_rate']}%입니다. "
            f"전날 대비 변화율은 {trend['day_change_rate']}%, "
            f"최근 2일 평균 변화율은 {trend['recent_average_change_rate']}%입니다."
        )
    else:
        trend_part = "기간 내 추이 정보는 확인되지 않았습니다."

    return (
        f"{keyword} 관련 민원/키워드 동향을 분석한 결과, "
        f"민원 건수는 {complaint_count}건이고 징후 점수는 {score}점입니다. "
        f"주요 연관어는 {related_part}입니다. "
        f"{trend_part}"
    )


def _build_forecast(
    keyword: str,
    keyword_trends: List[Dict[str, Any]],
    detection: Dict[str, Any],
    risk_level: str,
    status: str,
) -> str:
    trend = detection["trend"]
    reasons = detection.get("reasons", [])

    if not keyword_trends or not trend["has_trend"]:
        return "추세 데이터가 충분하지 않아 향후 흐름은 추가 수집 후 판단이 필요합니다."

    if status in {"critical", "warning"}:
        reason_text = reasons[0] if reasons else "민원 집중 신호가 확인됨"
        return (
            f"{keyword} 이슈는 {reason_text}으로 인해 확산 가능성이 높은 편입니다. "
            f"단기적으로 관련 민원 변화를 우선 모니터링할 필요가 있습니다."
        )

    if status == "growing":
        if trend["signal"] == "rebound":
            return (
                f"{keyword} 이슈는 전체 기간 기준으로는 강한 상승세가 제한적이지만, "
                f"마지막 날 전날 대비 반등이 확인되어 단기 모니터링이 필요합니다."
            )

        return (
            f"{keyword} 이슈는 최근 증가 징후가 확인되어 당분간 관심이 확대될 가능성이 있습니다. "
            f"추가 데이터 수집을 통해 상승 흐름 지속 여부를 확인해야 합니다."
        )

    if trend["direction"] == "falling":
        return (
            f"{keyword} 이슈는 기간 전체 기준으로 완화 흐름이 일부 확인됩니다. "
            f"다만 재확산 가능성을 고려해 지속적인 관찰이 필요합니다."
        )

    if status == "watch":
        return (
            f"{keyword} 이슈는 현재 관찰이 필요한 수준입니다. "
            f"민원 건수, 전날 대비 변화율, 최근 평균 변화율을 주기적으로 확인할 필요가 있습니다."
        )

    return (
        f"{keyword} 이슈는 현재 큰 급등 신호는 제한적입니다. "
        f"다만 추가 수집 데이터에 따라 상태가 바뀔 수 있습니다."
    )


def _build_causes(related_keywords: List[str], detection: Dict[str, Any]) -> List[str]:
    result = []

    for word in related_keywords[:3]:
        result.append(f"{word} 관련 민원 연관성이 확인됨")

    for reason in detection.get("reasons", [])[:2]:
        result.append(reason)

    if not result:
        return ["연관 키워드와 추세 데이터가 부족하여 원인 후보는 추가 데이터 수집이 필요합니다."]

    deduped = []
    seen = set()

    for item in result:
        key = item.strip()
        if key and key not in seen:
            seen.add(key)
            deduped.append(key)

    return deduped[:5]


def _build_title(keyword: str, related_keywords: List[str], status: str) -> str:
    status_label = {
        "critical": "강한 징후",
        "warning": "주의 징후",
        "growing": "증가 징후",
        "watch": "관찰 필요",
        "stable": "안정 관찰",
    }.get(status, "관찰 필요")

    if related_keywords:
        return f"{keyword} 관련 민원 이슈 - {related_keywords[0]} 중심 [{status_label}]"

    return f"{keyword} 관련 민원 이슈 [{status_label}]"


def _is_safe_alias(alias: str) -> bool:
    alias = _normalize_keyword_text(alias)

    if not alias:
        return False

    compact = _compact_text(alias)

    if not compact:
        return False

    if alias in ALIAS_STOPWORDS or compact in {_compact_text(word) for word in ALIAS_STOPWORDS}:
        return False

    if len(compact) <= 1:
        return False

    if len(compact) == 2 and alias not in SAFE_SHORT_ALIASES and compact not in {_compact_text(word) for word in SAFE_SHORT_ALIASES}:
        return False

    return True


def _add_alias_variants(alias_set: set, text: str, add_tokens: bool = False):
    text = _normalize_keyword_text(text)

    if not text:
        return

    candidates = [
        text,
        text.replace("_", " "),
        text.replace(" ", "_"),
        text.replace("_", ""),
        text.replace(" ", ""),
    ]

    if add_tokens:
        for token in _tokenize(text):
            candidates.append(token)

    for candidate in candidates:
        candidate = _normalize_keyword_text(candidate)

        if _is_safe_alias(candidate):
            alias_set.add(candidate)


def _build_search_aliases(
    keyword: str,
    search_keyword: str,
    related_keywords: List[str],
    rising_keywords: List[str],
    limit: int = 30,
) -> List[str]:
    alias_set = set()

    # 핵심 키워드만 토큰 분리 허용
    # related_keywords는 공공 API 노이즈가 많아서 토큰 분리하지 않음
    _add_alias_variants(alias_set, keyword, add_tokens=True)
    _add_alias_variants(alias_set, search_keyword, add_tokens=True)

    # 연관어는 검색 보조용으로만 풀 문장/붙인 문장 형태만 추가
    # 예: "자동 이체 떼"에서 "자동"만 따로 alias로 들어가는 문제 방지
    for word in related_keywords[:5]:
        _add_alias_variants(alias_set, word, add_tokens=False)

    check_targets = [
        keyword,
        search_keyword,
        keyword.replace("_", " "),
        search_keyword.replace("_", " "),
        keyword.replace("_", ""),
        search_keyword.replace(" ", ""),
    ]

    for target in check_targets:
        target = _normalize_keyword_text(target)
        if not target:
            continue

        for base_keyword, synonyms in SEARCH_SYNONYMS.items():
            base_compact = base_keyword.replace(" ", "").replace("_", "")
            target_compact = target.replace(" ", "").replace("_", "")

            if (
                base_keyword in target
                or target in base_keyword
                or base_compact in target_compact
                or target_compact in base_compact
            ):
                for synonym in synonyms:
                    _add_alias_variants(alias_set, synonym, add_tokens=False)

    aliases = []
    seen = set()

    for item in alias_set:
        item = _normalize_keyword_text(item)
        if not _is_safe_alias(item):
            continue

        key = item.lower()
        if key in seen:
            continue

        seen.add(key)
        aliases.append(item)

    aliases.sort(key=lambda x: (len(x), x))

    return aliases[:limit]


def _build_issue_category(
    search_keyword: str,
    title: str,
    related_keywords: List[str],
    search_aliases: List[str],
) -> Dict[str, Any]:
    keyword_text = _normalize_keyword_text(search_keyword)
    title_text = _normalize_keyword_text(title)
    keyword_title_text = f"{keyword_text} {title_text}"

    # 핵심 키워드 기반 강제 보정
    if _contains_any(keyword_title_text, {"자동차", "차량", "번호판", "한국교통안전공단", "한국도로공사", "도로공사", "안전순찰원"}):
        return {
            "category": "교통/자동차",
            "category_tags": _matched_category_tags("교통/자동차", keyword_title_text, related_keywords),
        }

    if _contains_any(keyword_title_text, {"데이터센터", "공원", "목욕탕", "공중목욕탕", "주거환경", "전자파", "방송통신시설"}):
        return {
            "category": "도시/시설",
            "category_tags": _matched_category_tags("도시/시설", keyword_title_text, related_keywords),
        }

    if _contains_any(keyword_title_text, {"농협", "농협은행", "은행", "통장", "배송", "택배", "도착", "카드", "이체"}):
        return {
            "category": "금융/소비자",
            "category_tags": _matched_category_tags("금융/소비자", keyword_title_text, related_keywords),
        }

    if _contains_any(keyword_title_text, {"무단투기", "쓰레기", "폐기물", "환경"}):
        return {
            "category": "환경/에너지",
            "category_tags": _matched_category_tags("환경/에너지", keyword_title_text, related_keywords),
        }

    if _contains_any(keyword_title_text, {"국가유공자", "장애인", "복지", "어린이", "KC미인증"}):
        return {
            "category": "복지/생활",
            "category_tags": _matched_category_tags("복지/생활", keyword_title_text, related_keywords),
        }

    if _contains_any(keyword_title_text, ADMIN_TERMS):
        return {
            "category": "행정/민원처리",
            "category_tags": _matched_category_tags("행정/민원처리", keyword_title_text, related_keywords),
        }

    # 점수 기반 보정
    category_scores = {}

    for category, rule_keywords in ISSUE_CATEGORY_RULES.items():
        score = 0
        matched_tags = []

        for rule in rule_keywords:
            rule_compact = _compact_text(rule)

            if not rule_compact:
                continue

            # 핵심 키워드/제목 매칭은 가중치 높게
            if rule_compact in _compact_text(keyword_title_text):
                score += 5
                matched_tags.append(rule)
                continue

            # 연관어 매칭은 가중치 낮게
            for related in related_keywords:
                if rule_compact in _compact_text(related):
                    score += 1
                    matched_tags.append(rule)
                    break

        if score > 0:
            category_scores[category] = {
                "score": score,
                "matched_tags": matched_tags,
            }

    if not category_scores:
        return {
            "category": "기타",
            "category_tags": [],
        }

    sorted_categories = sorted(
        category_scores.items(),
        key=lambda x: (x[1]["score"], len(x[1]["matched_tags"])),
        reverse=True,
    )

    best_category = sorted_categories[0][0]
    matched_tags = sorted_categories[0][1]["matched_tags"]

    deduped_tags = []
    seen = set()

    for tag in matched_tags:
        tag = _normalize_keyword_text(tag)
        if tag and tag not in seen:
            seen.add(tag)
            deduped_tags.append(tag)

    return {
        "category": best_category,
        "category_tags": deduped_tags[:8],
    }


def _matched_category_tags(category: str, keyword_title_text: str, related_keywords: List[str]) -> List[str]:
    tags = []
    seen = set()

    text_parts = [keyword_title_text] + related_keywords
    compact_text = _compact_text(" ".join(text_parts))

    for rule in ISSUE_CATEGORY_RULES.get(category, []):
        rule_compact = _compact_text(rule)
        if rule_compact and rule_compact in compact_text:
            if rule not in seen:
                seen.add(rule)
                tags.append(rule)

    return tags[:8]


def _build_cluster_keywords(
    search_keyword: str,
    related_keywords: List[str],
    category_tags: List[str],
    limit: int = 10,
) -> List[str]:
    candidates = []

    if search_keyword:
        candidates.append(search_keyword)

    candidates.extend(related_keywords[:5])
    candidates.extend(category_tags[:5])

    result = []
    seen = set()

    for item in candidates:
        item = _normalize_keyword_text(item)
        if not item:
            continue

        key = _compact_text(item)
        if key in seen:
            continue

        seen.add(key)
        result.append(item)

    return result[:limit]


def build_dashboard_payload(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    synced_at = snapshot.get("synced_at") or datetime.now().isoformat()
    date_from = snapshot.get("date_from", "")
    date_to = snapshot.get("date_to", "")
    keyword_details = snapshot.get("keyword_details", [])

    rising_keywords = _extract_rising_keywords(snapshot, limit=5)

    issues = []

    for detail in keyword_details:
        keyword = _normalize_keyword_text(detail.get("keyword"))
        search_keyword = _normalize_keyword_text(detail.get("search_keyword")) or keyword

        complaint_count = _extract_complaint_count(detail)

        raw_related_keywords = _extract_related_keywords(detail, limit=10)
        related_keywords = _filter_related_keywords(
            search_keyword=search_keyword,
            related_keywords=raw_related_keywords,
            limit=10,
        )

        keyword_trends = _extract_keyword_trends(detail)

        is_rising = _is_rising_keyword(
            keyword=keyword,
            search_keyword=search_keyword,
            rising_keywords=rising_keywords,
        )

        detection = _calculate_detection_score(
            complaint_count=complaint_count,
            keyword_trends=keyword_trends,
            related_keywords=related_keywords,
            is_rising_keyword=is_rising,
        )

        score = detection["score"]
        risk_level = _calculate_risk_level(score)
        status = _calculate_status(score, detection["trend"])

        search_aliases = _build_search_aliases(
            keyword=keyword,
            search_keyword=search_keyword,
            related_keywords=related_keywords,
            rising_keywords=[],
        )

        title = _build_title(search_keyword, related_keywords, status)

        category_info = _build_issue_category(
            search_keyword=search_keyword,
            title=title,
            related_keywords=related_keywords,
            search_aliases=search_aliases,
        )

        category = category_info["category"]
        category_tags = category_info["category_tags"]

        cluster_keywords = _build_cluster_keywords(
            search_keyword=search_keyword,
            related_keywords=related_keywords,
            category_tags=category_tags,
        )

        issue = {
            "issue_key": _build_issue_key(keyword, date_from, date_to),
            "issue_type": "dashboard_keyword_issue",
            "title": title,
            "summary": _build_summary(search_keyword, complaint_count, related_keywords, keyword_trends, detection),
            "forecast": _build_forecast(search_keyword, keyword_trends, detection, risk_level, status),
            "causes": _build_causes(related_keywords, detection),
            "keywords": [search_keyword] if search_keyword else [],
            "rising_keywords": rising_keywords,
            "related_keywords": related_keywords,
            "keyword_trends": keyword_trends,
            "search_aliases": search_aliases,
            "category": category,
            "category_tags": category_tags,
            "cluster_keywords": cluster_keywords,
            "status": status,
            "risk_level": risk_level,
            "score": score,
            "complaint_count": complaint_count,
            "top_keyword": search_keyword,
        }

        issues.append(issue)

    payload = {
        "batch_id": f"dashboard-batch-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "generated_at": synced_at,
        "source": "complaint_dashboard_sync_pipeline",
        "target": "pttn",
        "date_from": date_from,
        "date_to": date_to,
        "issues": issues,
    }

    return payload