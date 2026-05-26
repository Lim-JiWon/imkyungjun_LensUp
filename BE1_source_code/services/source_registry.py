SOURCE_REGISTRY = {
    "surge_keywords": {
        "display_name": "급등 키워드",
        "entity_type": "keyword",
        "stage": "discovery",
        "url_env_key": "PUBLIC_API_SURGE_URL",
        "request_type": "date_only",
    },
    "core_keywords": {
        "display_name": "핵심 키워드",
        "entity_type": "keyword",
        "stage": "discovery",
        "url_env_key": "PUBLIC_API_CORE_URL",
        "request_type": "date_range",
    },
    "today_issue": {
        "display_name": "오늘의 민원 이슈",
        "entity_type": "issue",
        "stage": "dashboard",
        "url_env_key": "PUBLIC_API_TODAY_ISSUE_URL",
        "request_type": "search_date_topn",
    },
    "keyword_trend": {
        "display_name": "키워드 트렌드 정보",
        "entity_type": "trend",
        "stage": "dashboard",
        "url_env_key": "PUBLIC_API_KEYWORD_TREND_URL",
        "request_type": "keyword_trend_custom",
    },
    "related_keywords": {
        "display_name": "연관어 분석 정보",
        "entity_type": "relation",
        "stage": "dashboard",
        "url_env_key": "PUBLIC_API_RELATED_KEYWORDS_URL",
        "request_type": "related_keywords_custom",
    },
    "keyword_complaint_count": {
        "display_name": "키워드 기반 민원 건수 정보",
        "entity_type": "count",
        "stage": "dashboard",
        "url_env_key": "PUBLIC_API_KEYWORD_COUNT_URL",
        "request_type": "keyword_count_custom",
    },
}