import os
import json
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from services.source_registry import SOURCE_REGISTRY

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_CACHE_DIR = BASE_DIR / "cache" / "keyword_discovery" / "raw"


def fetch_complaint_data(search_word, date_from, date_to, result_count=10):
    service_key = os.getenv("PUBLIC_API_SERVICE_KEY")
    if not service_key:
        raise ValueError("PUBLIC_API_SERVICE_KEY가 .env에 없습니다.")

    url = "https://apis.data.go.kr/1140100/minAnalsInfoView5/minWdcloudInfo5"

    params = {
        "serviceKey": service_key,
        "searchword": search_word,
        "resultCount": result_count,
        "target": "pttn",
        "dateFrom": date_from,
        "dateTo": date_to,
    }

    response = requests.get(url, params=params, timeout=60)

    print("[DEBUG] fetch_complaint_data final_url =", response.url)
    print("[DEBUG] fetch_complaint_data status_code =", response.status_code)

    response.raise_for_status()
    return response.json()


def _extract_items_from_response(data):
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    # 1) returnObject
    return_object = data.get("returnObject")
    if isinstance(return_object, list):
        return return_object
    if isinstance(return_object, dict):
        return [return_object]

    # 2) response > body > items > item
    response = data.get("response")
    if isinstance(response, dict):
        body = response.get("body")
        if isinstance(body, dict):
            items = body.get("items")
            if isinstance(items, dict):
                item = items.get("item")
                if isinstance(item, list):
                    return item
                if isinstance(item, dict):
                    return [item]
            if isinstance(items, list):
                return items

    # 3) body > items > item
    body = data.get("body")
    if isinstance(body, dict):
        items = body.get("items")
        if isinstance(items, dict):
            item = items.get("item")
            if isinstance(item, list):
                return item
            if isinstance(item, dict):
                return [item]
        if isinstance(items, list):
            return items

    # 4) items
    items = data.get("items")
    if isinstance(items, list):
        return items
    if isinstance(items, dict):
        item = items.get("item")
        if isinstance(item, list):
            return item
        if isinstance(item, dict):
            return [item]

    # 5) result
    result = data.get("result")
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return [result]

    return []

def _save_raw_discovery_response(dataset_type: str, payload: dict):
    debug_save = os.getenv("AUTO_KEYWORD_DEBUG_SAVE", "true").lower() == "true"
    if not debug_save:
        return

    RAW_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = RAW_CACHE_DIR / f"{ts}_{dataset_type}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def build_params_by_request_type(
    request_type: str,
    service_key: str,
    date_from: str,
    date_to: str,
    result_count: int,
    target: str = "pttn",
    keyword: str = None,
):
    
    if request_type == "keyword_trend_custom":
        return {
            "serviceKey": service_key,
            "period": "DAILY",
            "sortBy": "VALUE",
            "sortOrder": "FALSE",
            "target": target,
            "dateFrom": date_from,
            "dateTo": date_to,
            "searchword": keyword,
            "dataType": "json",
        }
    
    if request_type == "search_date_topn":
        return {
            "serviceKey": service_key,
            "searchDate": date_to,
            "todayTopicTopN": result_count,
            "target": target,
        }
    
    if request_type == "related_keywords_custom":
        return {
            "serviceKey": service_key,
            "target": target,
            "dateFrom": date_from,
            "dateTo": date_to,
            "searchword": keyword,
            "dataType": "json",
        }
    
    if request_type == "keyword_count_custom":
        return {
            "serviceKey": service_key,
            "target": target,
            "dateFrom": date_from,
            "dateTo": date_to,
            "searchword": keyword,
            "dataType": "json",
        }
    
    if request_type == "date_only":
        return {
            "serviceKey": service_key,
            "analysisTime": date_to,
            "maxResult": result_count,
            "target": target,
        }

    if request_type == "date_range":
        return {
            "serviceKey": service_key,
            "target": target,
            "dateFrom": date_from,
            "dateTo": date_to,
            "resultCount": result_count,
        }

    if request_type == "keyword_date_range":
        return {
            "serviceKey": service_key,
            "searchword": keyword,
            "target": target,
            "dateFrom": date_from,
            "dateTo": date_to,
            "resultCount": result_count,
        }
    

    raise ValueError(f"지원하지 않는 request_type: {request_type}")

def fetch_dataset_by_type(dataset_type: str, date_from: str, date_to: str, result_count: int = 10, keyword: str = None):
    if dataset_type not in SOURCE_REGISTRY:
        raise ValueError(f"지원하지 않는 dataset_type: {dataset_type}")

    service_key = os.getenv("PUBLIC_API_SERVICE_KEY")
    if not service_key:
        raise ValueError("PUBLIC_API_SERVICE_KEY가 .env에 없습니다.")

    url_env_key = SOURCE_REGISTRY[dataset_type]["url_env_key"]
    request_url = os.getenv(url_env_key)

    if not request_url:
        raise ValueError(f"{url_env_key}가 .env에 없습니다.")

    timeout_seconds = int(os.getenv("PUBLIC_API_TIMEOUT", "60"))
    target = os.getenv("PUBLIC_API_TARGET", "pttn")
    debug_mode = os.getenv("PUBLIC_API_DEBUG", "false").lower() == "true"

    request_type = SOURCE_REGISTRY[dataset_type]["request_type"]

    params = build_params_by_request_type(
        request_type=request_type,
        service_key=service_key,
        date_from=date_from,
        date_to=date_to,
        result_count=result_count,
        target=target,
        keyword=keyword,
    )

    if debug_mode:
        print(f"[DEBUG] dataset_type={dataset_type}")
        print(f"[DEBUG] request_url={request_url}")
        print(f"[DEBUG] params={params}")
        print(f"[DEBUG] timeout={timeout_seconds}")

    response = requests.get(request_url, params=params, timeout=timeout_seconds)

    if debug_mode:
        print(f"[DEBUG] final_url={response.url}")
        print(f"[DEBUG] status_code={response.status_code}")

    response.raise_for_status()

    try:
        data = response.json()
    except Exception:
        if debug_mode:
            print("[DEBUG] JSON 파싱 실패, 응답 원문 일부 출력:")
            print(response.text[:1000])
        raise ValueError("응답이 JSON 형식이 아닙니다.")

    _save_raw_discovery_response(dataset_type, data)

    items = _extract_items_from_response(data)

    if debug_mode:
        print(f"[DEBUG] extracted_items_count={len(items)}")
        if not items:
            print("[DEBUG] 응답 JSON 일부:")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])

    return items