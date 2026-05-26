# backend1_project/services/auto_keyword_service.py

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from services.public_api_service import fetch_dataset_by_type
from services.source_normalizer import normalize_items

DISCOVERY_DATASETS = ["surge_keywords", "core_keywords"]

SOURCE_WEIGHTS = {
    "surge_keywords": 4.0,
    "core_keywords": 3.0,
}

BASE_DIR = Path(__file__).resolve().parents[1]   # backend1_project
CACHE_DIR = BASE_DIR / "cache" / "keyword_discovery"
RAW_DIR = CACHE_DIR / "raw"


def _score_item(item: Dict) -> float:
    dataset_type = item["dataset_type"]
    base = SOURCE_WEIGHTS.get(dataset_type, 1.0)

    rank = item.get("rank")
    value = item.get("value")

    if isinstance(value, str):
        try:
            value = float(value.replace(",", ""))
        except Exception:
            value = None

    rank_bonus = 0.0
    if isinstance(rank, int) and rank > 0:
        rank_bonus = max(0.0, 2.0 - (rank * 0.1))

    value_bonus = 0.0
    if isinstance(value, (int, float)):
        if value >= 100:
            value_bonus = 1.5
        elif value >= 50:
            value_bonus = 1.0
        elif value >= 10:
            value_bonus = 0.5

    return round(base + rank_bonus + value_bonus, 3)


def _merge_candidates(items: List[Dict]) -> List[Dict]:
    bucket = defaultdict(lambda: {
        "label": "",
        "total_score": 0.0,
        "sources": [],
        "ranks": [],
        "values": [],
        "raw_items": [],
    })

    for item in items:
        label = (item.get("label") or "").strip()
        if not label:
            continue

        key = label.lower()

        bucket[key]["label"] = label
        bucket[key]["total_score"] += item.get("score", 0.0)
        bucket[key]["sources"].append(item["dataset_type"])

        if item.get("rank") is not None:
            bucket[key]["ranks"].append(item["rank"])

        value = item.get("value")
        if isinstance(value, str):
            try:
                value = float(value.replace(",", ""))
            except Exception:
                value = None

        if value is not None and isinstance(value, (int, float)):
            bucket[key]["values"].append(value)

        bucket[key]["raw_items"].append(item)

    merged = []
    for _, value in bucket.items():
        merged.append({
            "label": value["label"],
            "total_score": round(value["total_score"], 3),
            "sources": sorted(list(set(value["sources"]))),
            "best_rank": min(value["ranks"]) if value["ranks"] else None,
            "max_value": max(value["values"]) if value["values"] else None,
            "raw_items": value["raw_items"],
        })

    merged.sort(
        key=lambda x: (
            x["total_score"],
            -(x["best_rank"] or 999),
            x["max_value"] or 0
        ),
        reverse=True
    )

    return merged


def _save_discovery_summary(date_from: str, date_to: str, merged: List[Dict], final_keywords: List[str]):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = CACHE_DIR / f"{ts}_discovery_result.json"

    payload = {
        "date_from": date_from,
        "date_to": date_to,
        "final_keywords": final_keywords,
        "merged_candidates": merged,
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def discover_keywords(date_from: str, date_to: str, limit: int = 5, result_count: int = 10) -> Tuple[List[str], List[Dict]]:
    all_items = []

    print("[1] 자동 키워드 수집 시작")
    print(f"    - 기간: {date_from} ~ {date_to}")
    print(f"    - 각 소스별 최대 수집 건수: {result_count}")

    for dataset_type in DISCOVERY_DATASETS:
        try:
            print(f"[2] {dataset_type} 호출 중...")
            raw_items = fetch_dataset_by_type(
                dataset_type=dataset_type,
                date_from=date_from,
                date_to=date_to,
                result_count=result_count,
            )

            print(f"[3] {dataset_type} 호출 성공: {len(raw_items)}건")

            normalized = normalize_items(dataset_type, raw_items)

            for item in normalized:
                item["score"] = _score_item(item)
                all_items.append(item)

        except Exception as e:
            print(f"[WARN] {dataset_type} 호출 실패: {e}")

    print(f"[4] 전체 정규화 대상 수: {len(all_items)}건")

    merged = _merge_candidates(all_items)
    final_keywords = [item["label"] for item in merged[:limit]]

    _save_discovery_summary(date_from, date_to, merged, final_keywords)

    print("[5] 자동 키워드 병합/점수화 완료")
    print(f"[6] 최종 키워드 수: {len(final_keywords)}건")

    return final_keywords, merged