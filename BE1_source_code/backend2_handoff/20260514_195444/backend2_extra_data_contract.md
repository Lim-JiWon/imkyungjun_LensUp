# 백엔드2 인수인계 문서

## 1. 목적

백엔드1에서 기존 민원 이슈 수집/가공 데이터에 추가로 아래 3가지 데이터를 수집했다.

1. 민원 발생 지역 순위
2. 민원 발생 기관/지자체 순위
3. 키워드 기반 연령대 민원 현황

이 문서는 백엔드2가 해당 데이터를 서버 DB/API 응답에 붙일 수 있도록 전달하는 인수인계 자료다.

---

## 2. 생성 정보

- batch_id: `dashboard-batch-20260513162720`
- generated_at: `2026-05-13T16:27:20.627750`
- source: `complaint_dashboard_sync_pipeline`
- target: `pttn`
- date_from: `20260428`
- date_to: `20260513`
- issue_count: `20`
- region_count: `17`
- organization_count: `10`

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
$key = (Get-Content .env | Where-Object { $_ -match '^\s*PIPELINE_API_KEY\s*=' } | Select-Object -First 1) -replace '^\s*PIPELINE_API_KEY\s*=\s*',''
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
  {
    "rank": 1,
    "region": "경기도",
    "value": 557104
  }
]
```

현재 1위 지역:

```text
경기도 / 557104건
```

---

## 7. organization_rank 구조

기관/지자체별 민원 발생량이다.

예시:

```json
[
  {
    "rank": 1,
    "organization": "경기도 수원시",
    "value": 49689
  }
]
```

현재 1위 기관/지자체:

```text
경기도 수원시 / 49689건
```

---

## 8. category_stats 구조

카테고리별 이슈 요약이다.

예시:

```json
[
  {
    "category": "도시/시설",
    "issue_count": 2,
    "total_complaint_count": 640,
    "critical_count": 1,
    "warning_count": 1,
    "top_issues": []
  }
]
```

현재 카테고리 요약:

- 도시/시설: 이슈 2개, 민원 640건, 강한징후 1개, 주의징후 1개
- 행정/민원처리: 이슈 12개, 민원 5470건, 강한징후 0개, 주의징후 0개
- 금융/소비자: 이슈 2개, 민원 1118건, 강한징후 0개, 주의징후 0개
- 교통/자동차: 이슈 3개, 민원 1118건, 강한징후 0개, 주의징후 0개
- 환경/에너지: 이슈 1개, 민원 56건, 강한징후 0개, 주의징후 0개

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
  {
    "age_group": "30대",
    "value": 144
  },
  {
    "age_group": "40대",
    "value": 135
  }
]
```

### age_summary

연령대 분석 요약값이다.

```json
{
  "dominant_age_group": "30대",
  "dominant_value": 144,
  "dominant_ratio_in_known": 41.62,
  "unknown_ratio": 76.24,
  "known_total": 346,
  "total": 1456
}
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
