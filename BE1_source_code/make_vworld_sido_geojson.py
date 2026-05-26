from pathlib import Path
import json
import os
import sys
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "cache" / "gis"
RAW_OUTPUT_FILE = OUTPUT_DIR / "vworld_lt_c_adsido_raw.json"
OUTPUT_FILE = OUTPUT_DIR / "korea-sido.geojson"
HANDOFF_FILE = OUTPUT_DIR / "frontend_handoff_note.txt"

VWORLD_WFS_URL = "https://api.vworld.kr/req/wfs"

EXPECTED_REGIONS = [
    "서울",
    "부산",
    "대구",
    "인천",
    "광주",
    "대전",
    "울산",
    "세종",
    "경기",
    "강원",
    "충북",
    "충남",
    "전북",
    "전남",
    "경북",
    "경남",
    "제주",
]

REGION_NORMALIZE_MAP = {
    "서울특별시": "서울",
    "부산광역시": "부산",
    "대구광역시": "대구",
    "인천광역시": "인천",
    "광주광역시": "광주",
    "대전광역시": "대전",
    "울산광역시": "울산",
    "세종특별자치시": "세종",
    "경기도": "경기",
    "강원도": "강원",
    "강원특별자치도": "강원",
    "충청북도": "충북",
    "충청남도": "충남",
    "전라북도": "전북",
    "전북특별자치도": "전북",
    "전라남도": "전남",
    "경상북도": "경북",
    "경상남도": "경남",
    "제주도": "제주",
    "제주특별자치도": "제주",
}

POSSIBLE_REGION_COLUMNS = [
    "ctp_kor_nm",
    "CTP_KOR_NM",
    "ctprvn_nm",
    "CTPRVN_NM",
    "sido_nm",
    "SIDO_NM",
    "sido_name",
    "SIDO_NAME",
    "adm_nm",
    "ADM_NM",
    "name",
    "NAME",
    "kor_nm",
    "KOR_NM",
]


def mask_key(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return value[:4] + "*" * (len(value) - 8) + value[-4:]


def normalize_region_name(value):
    if value is None:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    if text in REGION_NORMALIZE_MAP:
        return REGION_NORMALIZE_MAP[text]

    for full_name, short_name in REGION_NORMALIZE_MAP.items():
        if full_name in text:
            return short_name

    for short_name in EXPECTED_REGIONS:
        if short_name in text:
            return short_name

    return text


def get_region_name(properties):
    if not isinstance(properties, dict):
        return ""

    for column in POSSIBLE_REGION_COLUMNS:
        value = properties.get(column)
        if value:
            return normalize_region_name(value)

    for key, value in properties.items():
        key_text = str(key).lower()
        if any(token in key_text for token in ["kor", "name", "nm", "sido", "ctp"]):
            normalized = normalize_region_name(value)
            if normalized:
                return normalized

    return ""


def extract_features(data):
    if not isinstance(data, dict):
        return []

    if data.get("type") == "FeatureCollection" and isinstance(data.get("features"), list):
        return data["features"]

    if isinstance(data.get("features"), list):
        return data["features"]

    response = data.get("response")
    if isinstance(response, dict):
        result = response.get("result")
        if isinstance(result, dict):
            feature_collection = result.get("featureCollection")
            if isinstance(feature_collection, dict) and isinstance(feature_collection.get("features"), list):
                return feature_collection["features"]

            if isinstance(result.get("features"), list):
                return result["features"]

    return []


def make_request(api_key, domain):
    params = {
        "service": "WFS",
        "request": "GetFeature",
        "version": "1.1.0",
        "typename": "lt_c_adsido_info",
        "output": "application/json",
        "srsname": "EPSG:4326",
        "maxfeatures": "100",
        "key": api_key,
    }

    if domain:
        params["domain"] = domain

    safe_params = dict(params)
    safe_params["key"] = mask_key(api_key)

    print("[INFO] 브이월드 WFS 요청을 보냅니다.")
    print(f"[INFO] 요청 URL: {VWORLD_WFS_URL}?{urlencode(safe_params)}")

    response = requests.get(VWORLD_WFS_URL, params=params, timeout=30)

    print(f"[INFO] HTTP 상태 코드: {response.status_code}")

    if response.status_code != 200:
        raise RuntimeError(
            f"브이월드 WFS 요청 실패: HTTP {response.status_code}\n{response.text[:1000]}"
        )

    content_type = response.headers.get("Content-Type", "")
    print(f"[INFO] 응답 Content-Type: {content_type}")

    return response


def load_response_json(response):
    try:
        return response.json()
    except Exception:
        text = response.text
        error_file = OUTPUT_DIR / "vworld_error_response.txt"
        error_file.write_text(text, encoding="utf-8")

        raise RuntimeError(
            "응답을 JSON으로 읽지 못했습니다. "
            f"에러 응답을 저장했습니다: {error_file}\n"
            "브이월드 API 키, 활용 API 체크 여부, 도메인 설정을 확인해주세요."
        )


def build_clean_geojson(features):
    clean_features = []
    seen_regions = set()

    for index, feature in enumerate(features, start=1):
        if not isinstance(feature, dict):
            continue

        geometry = feature.get("geometry")
        properties = feature.get("properties") or {}

        if not geometry:
            print(f"[WARN] geometry가 없는 feature 건너뜀: {index}")
            continue

        region = get_region_name(properties)

        if not region:
            print(f"[WARN] 지역명을 찾지 못했습니다. feature {index} properties:")
            print(properties)
            region = f"unknown_{index}"

        clean_feature = {
            "type": "Feature",
            "properties": {
                "region": region,
                "name": region,
                "source": "vworld",
                "layer": "lt_c_adsido_info",
            },
            "geometry": geometry,
        }

        clean_features.append(clean_feature)
        seen_regions.add(region)

    clean_geojson = {
        "type": "FeatureCollection",
        "name": "korea_sido",
        "features": clean_features,
    }

    return clean_geojson, seen_regions


def write_handoff_note():
    text = """프론트 전달용 GIS 지도 파일 안내

1. 생성 파일
- cache/gis/korea-sido.geojson

2. 프론트 프로젝트에 넣을 위치
- public/data/korea-sido.geojson

3. 프론트에서 불러오는 경로
- fetch("/data/korea-sido.geojson")

4. 설명
- 브이월드 WFS API의 광역시도 경계 레이어 lt_c_adsido_info를 사용해 생성한 시도 단위 GeoJSON 파일입니다.
- 프론트에서는 이 GeoJSON과 백엔드2의 GET /dashboard/map-data 지역별 민원 수를 결합해 GIS 기반 지역별 민원 분포 지도를 구현하면 됩니다.
"""
    HANDOFF_FILE.write_text(text, encoding="utf-8")


def main():
    load_dotenv()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    api_key = os.getenv("VWORLD_API_KEY", "").strip()
    domain = os.getenv("VWORLD_DOMAIN", "").strip()

    if not api_key:
        print("[ERROR] .env에 VWORLD_API_KEY가 없습니다.")
        print("예: VWORLD_API_KEY=발급받은_브이월드_인증키")
        sys.exit(1)

    print("[INFO] VWORLD_API_KEY:", mask_key(api_key))
    print("[INFO] VWORLD_DOMAIN:", domain or "(없음)")

    response = make_request(api_key, domain)
    data = load_response_json(response)

    RAW_OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[INFO] 원본 응답 저장 완료: {RAW_OUTPUT_FILE}")

    features = extract_features(data)

    if not features:
        print("[ERROR] Feature 목록을 찾지 못했습니다.")
        print("[ERROR] 원본 응답 일부:")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        sys.exit(1)

    print(f"[INFO] 가져온 feature 수: {len(features)}")

    first_properties = features[0].get("properties", {})
    print("[INFO] 첫 번째 feature properties 컬럼:")
    print(list(first_properties.keys()))

    clean_geojson, seen_regions = build_clean_geojson(features)

    OUTPUT_FILE.write_text(
        json.dumps(clean_geojson, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    write_handoff_note()

    print(f"[DONE] 시도 GeoJSON 생성 완료: {OUTPUT_FILE}")
    print(f"[DONE] 프론트 전달 메모 생성 완료: {HANDOFF_FILE}")

    print("\n[INFO] 추출된 지역:")
    for region in sorted(seen_regions):
        print("-", region)

    missing = [region for region in EXPECTED_REGIONS if region not in seen_regions]

    if missing:
        print("\n[WARN] 예상 지역 중 누락된 지역이 있습니다:")
        for region in missing:
            print("-", region)
        print("\n원본 컬럼명이 예상과 다를 수 있으니 위 properties 컬럼을 확인해야 합니다.")
    else:
        print("\n[SUCCESS] 17개 시도 지역이 모두 확인되었습니다.")


if __name__ == "__main__":
    main()