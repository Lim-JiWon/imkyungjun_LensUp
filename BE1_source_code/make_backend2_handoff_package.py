import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


DASHBOARD_CACHE_DIR = Path("cache") / "dashboard_sync"
HANDOFF_ROOT_DIR = Path("backend2_handoff")


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Dict[str, Any], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_text(text: str, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def find_latest_file(pattern: str) -> Optional[Path]:
    candidates = list(DASHBOARD_CACHE_DIR.glob(pattern))

    if not candidates:
        return None

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def get_final_map_data_path() -> Path:
    path = DASHBOARD_CACHE_DIR / "frontend_map_data_final.json"

    if not path.exists():
        raise FileNotFoundError(
            "frontend_map_data_final.json 파일이 없습니다. "
            "먼저 finalize_frontend_map_data.py를 실행해야 합니다."
        )

    return path


def safe_get_meta_value(final_map_data: Dict[str, Any], enriched_payload: Dict[str, Any], key: str):
    meta = final_map_data.get("meta", {})

    if isinstance(meta, dict) and meta.get(key) is not None:
        return meta.get(key)

    if enriched_payload.get(key) is not None:
        return enriched_payload.get(key)

    return None


def build_sample_extra_payload(final_map_data: Dict[str, Any], enriched_payload: Dict[str, Any]) -> Dict[str, Any]:
    issues = final_map_data.get("issues", [])
    region_rank = final_map_data.get("region_rank", [])
    organization_rank = final_map_data.get("organization_rank", [])
    category_stats = final_map_data.get("category_stats", [])

    sample_issue = issues[0] if issues else {}

    return {
        "purpose": "백엔드1에서 추가 수집한 민원 지역/기관/연령 데이터 백엔드2 연동용 샘플",
        "recommended_backend2_endpoint": "GET /dashboard/map-data",
        "recommended_admin_endpoint": "POST /admin/pipeline/map-data",
        "meta": final_map_data.get("meta", {}),
        "data_shape": {
            "top_level_fields": [
                "meta",
                "region_summary",
                "organization_summary",
                "region_rank",
                "organization_rank",
                "category_stats",
                "issues",
            ],
            "issue_extra_fields": [
                "age_searchword",
                "known_age_distribution",
                "age_summary",
                "age_analysis_message",
            ],
        },
        "region_rank_sample": region_rank[:5],
        "organization_rank_sample": organization_rank[:5],
        "category_stats_sample": category_stats,
        "issue_sample": sample_issue,
        "original_batch_id": safe_get_meta_value(final_map_data, enriched_payload, "batch_id"),
        "original_generated_at": safe_get_meta_value(final_map_data, enriched_payload, "generated_at"),
        "original_date_from": safe_get_meta_value(final_map_data, enriched_payload, "date_from"),
        "original_date_to": safe_get_meta_value(final_map_data, enriched_payload, "date_to"),
        "original_target": safe_get_meta_value(final_map_data, enriched_payload, "target"),
        "original_source": safe_get_meta_value(final_map_data, enriched_payload, "source"),
    }


def build_backend2_contract_md(final_map_data: Dict[str, Any], enriched_payload: Dict[str, Any]) -> str:
    meta = final_map_data.get("meta", {})
    region_rank = final_map_data.get("region_rank", [])
    organization_rank = final_map_data.get("organization_rank", [])
    category_stats = final_map_data.get("category_stats", [])
    issues = final_map_data.get("issues", [])

    batch_id = safe_get_meta_value(final_map_data, enriched_payload, "batch_id")
    generated_at = safe_get_meta_value(final_map_data, enriched_payload, "generated_at")
    source = safe_get_meta_value(final_map_data, enriched_payload, "source")
    target = safe_get_meta_value(final_map_data, enriched_payload, "target")
    date_from = safe_get_meta_value(final_map_data, enriched_payload, "date_from")
    date_to = safe_get_meta_value(final_map_data, enriched_payload, "date_to")

    top_region = region_rank[0] if region_rank else {}
    top_org = organization_rank[0] if organization_rank else {}

    category_lines = []

    for item in category_stats:
        category_lines.append(
            f"- {item.get('category')}: "
            f"이슈 {item.get('issue_count')}개, "
            f"민원 {item.get('total_complaint_count')}건, "
            f"강한징후 {item.get('critical_count')}개, "
            f"주의징후 {item.get('warning_count')}개"
        )

    category_text = "\n".join(category_lines) if category_lines else "- 카테고리 데이터 없음"

    return f"""# 백엔드2 인수인계 문서

## 1. 목적

백엔드1에서 기존 민원 이슈 수집/가공 데이터에 추가로 아래 3가지 데이터를 수집했다.

1. 민원 발생 지역 순위
2. 민원 발생 기관/지자체 순위
3. 키워드 기반 연령대 민원 현황

이 문서는 백엔드2가 해당 데이터를 서버 DB/API 응답에 붙일 수 있도록 전달하는 인수인계 자료다.

---

## 2. 생성 정보

- batch_id: `{batch_id}`
- generated_at: `{generated_at}`
- source: `{source}`
- target: `{target}`
- date_from: `{date_from}`
- date_to: `{date_to}`
- issue_count: `{len(issues)}`
- region_count: `{len(region_rank)}`
- organization_count: `{len(organization_rank)}`

---

## 3. 백엔드1에서 생성한 최종 파일

```text
cache/dashboard_sync/frontend_map_data_final.json
```

백엔드2에는 위 JSON 파일 전체를 전송하면 된다.

---

## 4. 전송 API

백엔드2 관리자 API:

```text
POST /admin/pipeline/map-data
```

전체 URL:

```text
http://211.188.50.216:8000/admin/pipeline/map-data
```

필수 헤더:

```text
Content-Type: application/json
x-api-key: PIPELINE_API_KEY
```

PowerShell 예시:

```powershell
$key = (Get-Content .env | Where-Object {{ $_ -match '^\\s*PIPELINE_API_KEY\\s*=' }} | Select-Object -First 1) -replace '^\\s*PIPELINE_API_KEY\\s*=\\s*',''
$key = $key.Trim().Trim('"').Trim("'")
curl.exe -X POST "http://211.188.50.216:8000/admin/pipeline/map-data" -H "Content-Type: application/json" -H "x-api-key: $key" --data-binary "@cache/dashboard_sync/frontend_map_data_final.json"
```

---

## 5. 조회 API

백엔드2 조회 API:

```text
GET /dashboard/map-data
```

전체 URL:

```text
http://211.188.50.216:8000/dashboard/map-data
```

정상 응답에는 아래 필드가 들어 있어야 한다.

```text
meta
region_summary
organization_summary
region_rank
organization_rank
category_stats
issues
```

---

## 6. region_rank 구조

지역별 민원 발생량이다.

예시:

```json
[
  {{
    "rank": 1,
    "region": "경기도",
    "value": 557104
  }}
]
```

현재 1위 지역:

```text
{top_region.get("region")} / {top_region.get("value")}건
```

---

## 7. organization_rank 구조

기관/지자체별 민원 발생량이다.

예시:

```json
[
  {{
    "rank": 1,
    "organization": "경기도 수원시",
    "value": 49689
  }}
]
```

현재 1위 기관/지자체:

```text
{top_org.get("organization")} / {top_org.get("value")}건
```

---

## 8. category_stats 구조

카테고리별 이슈 요약이다.

예시:

```json
[
  {{
    "category": "도시/시설",
    "issue_count": 2,
    "total_complaint_count": 640,
    "critical_count": 1,
    "warning_count": 1,
    "top_issues": []
  }}
]
```

현재 카테고리 요약:

{category_text}

---

## 9. issues 안의 연령 정보 구조

각 이슈에는 연령대 분석 정보가 추가된다.

### age_searchword

연령대 분석 API 호출에 사용한 키워드다.

```json
"age_searchword": "데이터센터 건립"
```

### known_age_distribution

연령 미상 값을 제외한 연령대별 민원 건수다.

```json
[
  {{
    "age_group": "30대",
    "value": 144
  }},
  {{
    "age_group": "40대",
    "value": 135
  }}
]
```

### age_summary

연령대 분석 요약값이다.

```json
{{
  "dominant_age_group": "30대",
  "dominant_value": 144,
  "dominant_ratio_in_known": 41.62,
  "unknown_ratio": 76.24,
  "known_total": 346,
  "total": 1456
}}
```

### age_analysis_message

프론트나 상세 응답에서 그대로 보여줄 수 있는 문장이다.

```text
연령 정보가 확인된 민원 기준으로 30대 비중이 가장 높습니다...
```

---

## 10. 백엔드2 저장 방식 제안

PostgreSQL을 사용하므로 JSONB 스냅샷 방식이 가장 안전하다.

예시 테이블:

```text
dashboard_extra_snapshots

- id
- batch_id
- source
- target
- date_from
- date_to
- payload_json JSONB
- created_at
```

---

## 11. 백엔드1 완료 범위

백엔드1에서 완료한 것:

1. 민원 발생 지역 순위 API 추가 수집
2. 민원 발생 기관/지자체 순위 API 추가 수집
3. 키워드 기반 연령대 민원 현황 API 추가 수집
4. label/hits 응답 구조 정규화
5. region_rank 생성
6. organization_rank 생성
7. issue별 age_distribution / age_summary 생성
8. 연령 미상/NONE 처리
9. 카테고리 보정
10. 최종 JSON 생성
11. 백엔드2 POST 전송 가능 상태 구성

---

## 12. 백엔드2 검수 기준

```text
GET /dashboard/map-data
```

정상 기준:

```text
region_rank_count = 17
organization_rank_count = 10
category_stats_count = 5
issues_count = 20
```

대표값:

```text
region_rank[0].region = 경기도
organization_rank[0].organization = 경기도 수원시
```
"""


def build_backend2_prompt_md() -> str:
    return """# 백엔드2에게 보낼 요청 프롬프트

백엔드1에서 공공데이터포털 국민권익위원회 민원빅데이터 분석정보 API를 이용해 기존 이슈 데이터 외에 아래 3가지 데이터를 추가 수집했습니다.

1. 민원 발생 지역 순위
2. 민원 발생 기관/지자체 순위
3. 키워드 기반 연령대 민원 현황

백엔드1 최종 파일은 다음입니다.

```text
cache/dashboard_sync/frontend_map_data_final.json
```

백엔드2에 원하는 작업은 다음입니다.

## 1. 저장 API

```text
POST /admin/pipeline/map-data
```

이 API는 관리자용이므로 반드시 `x-api-key`를 확인해야 합니다.

백엔드1에서 전송하는 명령어 예시:

```powershell
$key = (Get-Content .env | Where-Object { $_ -match '^\\s*PIPELINE_API_KEY\\s*=' } | Select-Object -First 1) -replace '^\\s*PIPELINE_API_KEY\\s*=\\s*',''
$key = $key.Trim().Trim('"').Trim("'")
curl.exe -X POST "http://211.188.50.216:8000/admin/pipeline/map-data" -H "Content-Type: application/json" -H "x-api-key: $key" --data-binary "@cache/dashboard_sync/frontend_map_data_final.json"
```

## 2. 조회 API

```text
GET /dashboard/map-data
```

응답 구조:

```json
{
  "meta": {},
  "region_summary": {},
  "organization_summary": {},
  "region_rank": [],
  "organization_rank": [],
  "category_stats": [],
  "issues": []
}
```

## 3. 저장 방식

빠르게 구현하려면 PostgreSQL에 JSONB 스냅샷 테이블 하나를 만들어도 됩니다.

예시 테이블:

```text
dashboard_extra_snapshots

- id
- batch_id
- source
- target
- date_from
- date_to
- payload_json JSONB
- created_at
```

## 4. 주의

기존 `/dashboard`, `/search`, `/admin/pipeline/ingest`가 이미 동작하고 있으므로,
기존 스키마를 크게 깨지 않는 별도 map-data API 방식이 안전합니다.

이후 안정화되면 `/dashboard`와 `/dashboard/{id}` 응답에 region_rank, organization_rank, age_summary 등을 통합하면 됩니다.
"""


def make_handoff_package() -> Dict[str, Any]:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    handoff_dir = HANDOFF_ROOT_DIR / now
    handoff_dir.mkdir(parents=True, exist_ok=True)

    final_map_data_path = get_final_map_data_path()
    enriched_payload_path = find_latest_file("*_dashboard_payload_enriched.json")

    final_map_data = load_json(final_map_data_path)

    if enriched_payload_path and enriched_payload_path.exists():
        enriched_payload = load_json(enriched_payload_path)
    else:
        enriched_payload = {}

    final_map_copy_path = handoff_dir / "backend2_frontend_map_data_final.json"
    sample_path = handoff_dir / "backend2_extra_data_sample.json"
    contract_path = handoff_dir / "backend2_extra_data_contract.md"
    prompt_path = handoff_dir / "backend2_request_prompt.md"

    shutil.copy2(final_map_data_path, final_map_copy_path)

    enriched_copy_path = None
    if enriched_payload_path and enriched_payload_path.exists():
        enriched_copy_path = handoff_dir / "backend2_dashboard_payload_enriched.json"
        shutil.copy2(enriched_payload_path, enriched_copy_path)

    sample_payload = build_sample_extra_payload(final_map_data, enriched_payload)
    save_json(sample_payload, sample_path)

    contract_md = build_backend2_contract_md(final_map_data, enriched_payload)
    save_text(contract_md, contract_path)

    prompt_md = build_backend2_prompt_md()
    save_text(prompt_md, prompt_path)

    return {
        "handoff_dir": handoff_dir,
        "final_map_copy_path": final_map_copy_path,
        "enriched_copy_path": enriched_copy_path,
        "sample_path": sample_path,
        "contract_path": contract_path,
        "prompt_path": prompt_path,
        "final_map_data": final_map_data,
    }


def print_summary(result: Dict[str, Any]) -> None:
    final_map_data = result["final_map_data"]

    meta = final_map_data.get("meta", {})
    region_rank = final_map_data.get("region_rank", [])
    organization_rank = final_map_data.get("organization_rank", [])
    category_stats = final_map_data.get("category_stats", [])
    issues = final_map_data.get("issues", [])

    print("\n" + "=" * 100)
    print("[SUMMARY] 백엔드2 인수인계 패키지 생성 완료")
    print("=" * 100)

    print(f"[DIR] {result['handoff_dir']}")
    print(f"[FILE] {result['final_map_copy_path']}")

    if result.get("enriched_copy_path"):
        print(f"[FILE] {result['enriched_copy_path']}")

    print(f"[FILE] {result['sample_path']}")
    print(f"[FILE] {result['contract_path']}")
    print(f"[FILE] {result['prompt_path']}")

    print("\n[DATA]")
    print(f"- batch_id: {meta.get('batch_id')}")
    print(f"- source: {meta.get('source')}")
    print(f"- target: {meta.get('target')}")
    print(f"- date_from: {meta.get('date_from')}")
    print(f"- date_to: {meta.get('date_to')}")
    print(f"- issue_count: {len(issues)}")
    print(f"- region_rank_count: {len(region_rank)}")
    print(f"- organization_rank_count: {len(organization_rank)}")
    print(f"- category_count: {len(category_stats)}")

    print("\n[지역 TOP 5]")
    for item in region_rank[:5]:
        print(f"- {item.get('rank')}위 {item.get('region')} / {item.get('value')}건")

    print("\n[기관/지자체 TOP 5]")
    for item in organization_rank[:5]:
        print(f"- {item.get('rank')}위 {item.get('organization')} / {item.get('value')}건")

    print("\n[카테고리 요약]")
    for item in category_stats:
        print(
            f"- {item.get('category')} / "
            f"이슈 {item.get('issue_count')}개 / "
            f"민원 {item.get('total_complaint_count')}건 / "
            f"강한징후 {item.get('critical_count')}개 / "
            f"주의징후 {item.get('warning_count')}개"
        )

    print("\n[NEXT]")
    print("백엔드2 담당자에게 아래 파일들을 전달하면 됩니다.")
    print("1. backend2_frontend_map_data_final.json")
    print("2. backend2_extra_data_sample.json")
    print("3. backend2_extra_data_contract.md")
    print("4. backend2_request_prompt.md")


def main() -> None:
    print("=" * 100)
    print("[START] 백엔드2 인수인계 패키지 생성")
    print("=" * 100)

    result = make_handoff_package()
    print_summary(result)

    print("\n[DONE] 완료")


if __name__ == "__main__":
    main()