# 백엔드2에게 보낼 요청 프롬프트

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
$key = (Get-Content .env | Where-Object { $_ -match '^\s*PIPELINE_API_KEY\s*=' } | Select-Object -First 1) -replace '^\s*PIPELINE_API_KEY\s*=\s*',''
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
