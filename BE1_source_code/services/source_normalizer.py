from typing import Any, Dict, List
from services.source_registry import SOURCE_REGISTRY


def _pick(item: Dict[str, Any], *keys, default=None):
    for key in keys:
        if key in item and item[key] not in [None, ""]:
            return item[key]
    return default


def _safe_int(value, default=None):
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default


def normalize_items(dataset_type: str, raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if dataset_type not in SOURCE_REGISTRY:
        raise ValueError(f"지원하지 않는 dataset_type: {dataset_type}")

    source = SOURCE_REGISTRY[dataset_type]
    normalized = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        # 1) 오늘의 민원 이슈 전용 처리
        if dataset_type == "today_issue":
            record = {
                "dataset_type": dataset_type,
                "dataset_label": source["display_name"],
                "entity_type": source["entity_type"],
                "label": _pick(item, "topic", "title", "issue", default=""),
                "value": _pick(item, "count", "cnt", default=0),
                "rank": _safe_int(_pick(item, "rank", "rnum", default=None)),
                "raw": item,
            }
            normalized.append(record)
            continue

        # 2) 키워드 트렌드 전용 처리
        if dataset_type == "keyword_trend":
            raw_label = _pick(item, "label", "date", "statDt", "baseDate", default="")

            record = {
                "dataset_type": dataset_type,
                "dataset_label": source["display_name"],
                "entity_type": source["entity_type"],
                "label": raw_label,
                "value": _pick(item, "hits", "count", "cnt", "df", default=0),
                "rank": _safe_int(_pick(item, "rank", "rnum", default=None)),
                "date": raw_label,
                "change_rate": _pick(item, "prebRatio", "prevRatio", default=None),
                "raw": item,
            }
            normalized.append(record)
            continue

        # 3) 연관어 분석 전용 처리
        if dataset_type == "related_keywords":
            record = {
                "dataset_type": dataset_type,
                "dataset_label": source["display_name"],
                "entity_type": source["entity_type"],
                "label": _pick(item, "label", "keyword", default=""),
                "related_label": _pick(item, "relatedKeyword", "relKeyword", "relationKeyword", default=""),
                "value": _pick(item, "value", "score", "weight", "count", default=0),
                "rank": _safe_int(_pick(item, "rank", "rnum", default=None)),
                "raw": item,
            }
            normalized.append(record)
            continue

        # 4) 키워드 기반 민원 건수 전용 처리
        if dataset_type == "keyword_complaint_count":
            raw_value = _pick(item, "value", "pttn", "complaintCount", "count", "cnt", "totalCnt", default=0)

            try:
                raw_value = int(raw_value)
            except Exception:
                pass

            record = {
                "dataset_type": dataset_type,
                "dataset_label": source["display_name"],
                "entity_type": source["entity_type"],
                "label": _pick(item, "label", "keyword", "name", default=""),
                "value": raw_value,
                "rank": _safe_int(_pick(item, "rank", "rnum", default=None)),
                "date": _pick(item, "date", "statDt", "baseDate", default=None),
                "raw": item,
            }
            normalized.append(record)
            continue

        # 5) 나머지 공통 처리 (surge_keywords, core_keywords 등)
        record = {
            "dataset_type": dataset_type,
            "dataset_label": source["display_name"],
            "entity_type": source["entity_type"],
            "label": _pick(
                item,
                "label", "keyword", "name", "term", "kwd", "wd", "srchwrd",
                default=""
            ),
            "value": _pick(
                item,
                "value", "count", "cnt", "score", "complaintCount", "totalCnt", "df",
                default=None
            ),
            "rank": _safe_int(
                _pick(item, "rank", "rnum", "no", "ranking", default=None)
            ),
            "raw": item,
        }

        # 급등 키워드처럼 날짜/변화율이 있는 경우 추가
        if dataset_type == "surge_keywords":
            record["date"] = _pick(item, "date", default=None)
            record["change_rate"] = _pick(item, "prevRatio", default=None)

        normalized.append(record)

    return normalized