# backend1_project/services/gpt_service.py
import os
import json
from typing import Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()


class ComplaintAnalysisResult(BaseModel):
    title: str = Field(description="민원 이슈 제목")
    summary: str = Field(description="민원 이슈 핵심 요약")
    forecast: str = Field(description="향후 확산 가능성 또는 전망")
    causes: List[str] = Field(default_factory=list, description="원인 후보 리스트")
    keywords: List[str] = Field(default_factory=list, description="핵심 키워드 리스트")
    status: str = Field(description="watch / growing / stable / warning 중 하나")
    risk_level: str = Field(description="low / medium / high / critical 중 하나")
    score: int = Field(default=50, ge=0, le=100, description="0~100 점수")


SYSTEM_PROMPT = """
너는 공공 민원 집계 데이터를 기반으로
민원 흐름과 이슈 강도를 분석하는 AI다.

반드시 아래 원칙을 지켜라.
1. 제공된 데이터만 기반으로 판단한다.
2. 근거가 약하면 과장하지 말고 불확실성을 드러낸다.
3. 한국어로 답한다.
4. title, summary, forecast는 UI에서 바로 보여줄 수 있게 짧고 명확하게 작성한다.
5. causes는 1~4개, keywords는 3~8개 정도 작성한다.
6. risk_level은 low / medium / high / critical 중 하나다.
7. status는 watch / growing / stable / warning 중 하나다.
8. score는 0~100 정수다.
9. 각 필드는 [필드별 작성 지침]을 우선적으로 따른다.
10. 출력은 반드시 ComplaintAnalysisResult 스키마에 맞춘 구조화 결과여야 한다.
11. 제공되는 데이터는 실제 민원 원문이 아닌 집계/분석 데이터다.
12. 실제 민원 내용을 상상하거나 구체적인 사건을 단정하지 마라.
13. 분석은 키워드, 민원 건수, 트렌드, 연관어 기반으로만 수행한다.
""".strip()


FIELD_PROMPTS: Dict[str, str] = {
    "title": """
[title 작성 지침]
- 공공 민원 이슈를 한 문장형 제목으로 작성한다.
- 20자 내외로 짧게 작성한다.
- 가장 중심이 되는 키워드 또는 민원 주제를 포함한다.
- 위험도나 확산성을 과장하는 표현은 피한다.
""".strip(),
    "summary": """
[summary 작성 지침]
- 수집된 공공 민원 데이터에서 확인되는 핵심 내용을 1~2문장으로 요약한다.
- 반복적으로 나타나는 키워드와 민원 흐름을 포함한다.
- 데이터에 없는 원인이나 배경을 단정하지 않는다.
- UI 카드에 바로 노출될 수 있도록 간결하게 작성한다.
""".strip(),
    "forecast": """
[forecast 작성 지침]
- 향후 확산 가능성, 민원 증가 가능성, 관찰 필요성을 작성한다.
- keyword_count, keywords, labels_only, trend_data, related_keywords를 근거로 판단한다.
- trend_data가 있으면 최근 값의 증가/감소 흐름을 반영한다.
- 근거가 약하면 '추가 데이터 확인 필요', '지속 관찰 필요'처럼 불확실성을 표현한다.
- 단정적인 예측이나 재난성 표현은 피한다.
""".strip(),
    "causes": """
[causes 작성 지침]
- 민원의 원인 후보를 1~4개 리스트로 작성한다.
- 원인은 확정 원인이 아니라 '가능성' 또는 '후보'로 표현한다.
- 행정 처리 지연, 정보 부족, 이용 불편, 제도 인식 차이, 지역/시설 문제 등 데이터에서 추론 가능한 범위만 포함한다.
- 서로 중복되는 원인은 합친다.
- 명확한 근거가 없으면 일반적 행정 원인을 과도하게 생성하지 마라.
""".strip(),
    "keywords": """
[keywords 작성 지침]
- 핵심 키워드는 3~8개 리스트로 작성한다.
- labels_only와 keywords에 존재하는 표현을 우선 사용한다.
- 같은 의미의 키워드는 하나로 통합한다.
- 너무 일반적인 단어보다 민원 분석에 유용한 구체적 단어를 선택한다.
""".strip(),
    "risk_level": """
[risk_level 작성 지침]
- 반드시 low / medium / high / critical 중 하나로만 작성한다.
- low: 민원 수가 적거나 단발성으로 보이는 경우.
- medium: 반복 민원이 있으나 즉각적 위험 신호는 약한 경우.
- high: 민원 수, 키워드 반복, 부정적 이슈가 뚜렷해 대응 검토가 필요한 경우.
- critical: 안전, 대규모 확산, 긴급 대응 가능성이 강하게 드러나는 경우.
""".strip(),
    "status": """
[status 작성 지침]
- 반드시 watch / growing / stable / warning 중 하나로만 작성한다.
- watch: 현재 관찰이 필요한 초기 또는 일반 이슈.
- growing: 관련 민원이 증가 또는 확산되는 흐름으로 보이는 경우.
- stable: 반복은 있으나 확산 징후가 제한적인 경우.
- warning: 즉각적인 주의 또는 대응 검토가 필요한 경우.
""".strip(),
    "score": """
[score 작성 지침]
- 0~100 사이의 정수로 작성한다.
- risk_level과 일관되게 작성한다.
- low: 0~39, medium: 40~69, high: 70~89, critical: 90~100 범위를 기준으로 한다.
- 데이터 근거가 부족하면 중간값으로 보수적으로 산정한다.
""".strip(),
}

ALLOWED_STATUS = {"watch", "growing", "stable", "warning"}
ALLOWED_RISK_LEVEL = {"low", "medium", "high", "critical"}


def _get_client():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def _safe_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default


def _derive_top_keyword(formatted_data: dict) -> str:
    labels_only = formatted_data.get("labels_only", [])
    if labels_only and isinstance(labels_only, list):
        return str(labels_only[0]).strip()

    keywords = formatted_data.get("keywords", [])
    if keywords and isinstance(keywords, list):
        first = keywords[0]
        if isinstance(first, dict):
            return str(first.get("label", "")).strip()

    return "미확인 키워드"


def _derive_keyword_candidates(formatted_data: dict, limit: int = 8):
    results = []

    labels_only = formatted_data.get("labels_only", [])
    if isinstance(labels_only, list):
        for item in labels_only:
            item = str(item).strip()
            if item:
                results.append(item)

    keywords = formatted_data.get("keywords", [])
    if isinstance(keywords, list):
        for item in keywords:
            if isinstance(item, dict):
                label = str(item.get("label", "")).strip()
                if label:
                    results.append(label)

    deduped = []
    seen = set()
    for item in results:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped[:limit]


def _derive_complaint_count(formatted_data: dict) -> int:
    return _safe_int(formatted_data.get("keyword_count", 0), default=0)


def _merge_field_prompts(custom_field_prompts: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    기본 필드별 프롬프트에 사용자가 전달한 커스텀 프롬프트를 덮어쓴다.
    예: {"summary": "summary는 3문장 이내로 작성"}
    """
    merged = dict(FIELD_PROMPTS)

    if isinstance(custom_field_prompts, dict):
        for key, value in custom_field_prompts.items():
            if key in merged and str(value).strip():
                merged[key] = str(value).strip()

    return merged


def _format_field_prompts(field_prompts: Dict[str, str]) -> str:
    ordered_keys = [
        "title",
        "summary",
        "forecast",
        "causes",
        "keywords",
        "risk_level",
        "status",
        "score",
    ]

    return "\n\n".join(
        field_prompts[key]
        for key in ordered_keys
        if key in field_prompts and str(field_prompts[key]).strip()
    )


def _build_user_input(
    prompt_text: str,
    formatted_data: dict,
    field_prompts: Optional[Dict[str, str]] = None,
) -> str:
    compact_payload = {
    "keyword_count": formatted_data.get("keyword_count", 0),
    "labels_only": formatted_data.get("labels_only", [])[:10],
    "keywords": formatted_data.get("keywords", [])[:10],
    "trend_data": formatted_data.get("trend_data", [])[:10],
    "related_keywords": formatted_data.get("related_keywords", [])[:10],
}

    merged_field_prompts = _merge_field_prompts(field_prompts)
    field_prompt_text = _format_field_prompts(merged_field_prompts)

    return f"""
아래는 공공 민원 데이터의 정리 결과다.

[사용자 입력 프롬프트]
{prompt_text}

[구조화 데이터(JSON)]
{json.dumps(compact_payload, ensure_ascii=False, indent=2)}

[필드별 작성 지침]
{field_prompt_text}

[최종 작업]
위 사용자 입력 프롬프트와 구조화 데이터를 바탕으로 다음 필드를 각각의 작성 지침에 따라 생성하라.
- title
- summary
- forecast
- causes
- keywords
- status
- risk_level
- score

[주의]
- 제공된 데이터에 없는 내용을 사실처럼 추가하지 마라.
- status와 risk_level은 허용된 값 중 하나만 사용하라.
- causes와 keywords는 리스트로 작성하라.
""".strip()


def _mock_analysis(prompt_text: str, formatted_data: dict, reason: str = "") -> dict:
    top_keyword = _derive_top_keyword(formatted_data)
    keyword_candidates = _derive_keyword_candidates(formatted_data)
    complaint_count = _derive_complaint_count(formatted_data)

    return {
        "title": f"{top_keyword} 관련 민원 브리핑",
        "summary": f"{top_keyword} 관련 민원이 수집되었으며 현재 주요 관심 이슈로 판단됩니다.",
        "forecast": f"추가 수집 데이터가 누적되면 {top_keyword} 관련 민원이 더 확대될 가능성을 계속 관찰할 필요가 있습니다.",
        "causes": [
            f"{top_keyword} 관련 불편 누적 가능성",
            "행정 처리 또는 제도 인식 차이 가능성",
        ],
        "keywords": keyword_candidates[:5] if keyword_candidates else [top_keyword],
        "status": "watch",
        "risk_level": "medium",
        "score": 50,
        "complaint_count": complaint_count,
        "top_keyword": top_keyword,
        "_meta": {
            "provider": "openai",
            "mode": "mock",
            "reason": reason,
        },
    }


def _normalize_analysis_result(result: dict, formatted_data: dict) -> dict:
    top_keyword = _derive_top_keyword(formatted_data)
    complaint_count = _derive_complaint_count(formatted_data)

    result["causes"] = [
        str(x).strip()
        for x in result.get("causes", [])
        if str(x).strip()
    ][:4]

    result["keywords"] = [
        str(x).strip()
        for x in result.get("keywords", [])
        if str(x).strip()
    ][:8]

    if not result["keywords"]:
        result["keywords"] = _derive_keyword_candidates(formatted_data)[:5] or [top_keyword]

    status = str(result.get("status", "watch")).strip().lower()
    if status not in ALLOWED_STATUS:
        status = "watch"
    result["status"] = status

    risk_level = str(result.get("risk_level", "medium")).strip().lower()
    if risk_level not in ALLOWED_RISK_LEVEL:
        risk_level = "medium"
    result["risk_level"] = risk_level

    result["score"] = max(0, min(100, _safe_int(result.get("score", 50), default=50)))
    result["complaint_count"] = complaint_count
    result["top_keyword"] = top_keyword

    return result


def analyze_with_gpt(
    prompt_text: str,
    formatted_data: dict,
    field_prompts: Optional[Dict[str, str]] = None,
) -> dict:
    """
    공공 민원 데이터를 GPT로 분석한다.

    Parameters
    ----------
    prompt_text:
        사용자가 입력한 전체 분석 요청/프롬프트.
    formatted_data:
        keyword_count, labels_only, keywords 등을 포함한 구조화 데이터.
    field_prompts:
        title, summary, forecast, causes, keywords, risk_level, status, score별
        세부 작성 지침을 외부에서 덮어쓰기 위한 선택 인자.
    """
    enabled = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
    use_mock_fallback = os.getenv("OPENAI_USE_MOCK_FALLBACK", "true").lower() == "true"
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

    top_keyword = _derive_top_keyword(formatted_data)

    if not enabled:
        print("[INFO] OPENAI_ENABLED=false -> mock 응답 사용")
        return _mock_analysis(prompt_text, formatted_data, reason="OPENAI_ENABLED=false")

    client = _get_client()
    if client is None:
        print("[WARN] OPENAI_API_KEY 없음 -> mock 응답 사용")
        return _mock_analysis(prompt_text, formatted_data, reason="OPENAI_API_KEY missing")

    try:
        print("[4] GPT 분석 시작")
        print(f"    - model: {model}")
        print(f"    - top_keyword: {top_keyword}")

        response = client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _build_user_input(
                        prompt_text=prompt_text,
                        formatted_data=formatted_data,
                        field_prompts=field_prompts,
                    ),
                },
            ],
            text_format=ComplaintAnalysisResult,
        )

        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("response.output_parsed is None")

        result = parsed.model_dump()
        result = _normalize_analysis_result(result, formatted_data)
        result["_meta"] = {
            "provider": "openai",
            "mode": "live",
            "model": model,
            "field_prompt_keys": list(_merge_field_prompts(field_prompts).keys()),
        }

        print("[5] GPT 분석 완료")
        print(f"    - title: {result['title']}")
        print(f"    - status: {result['status']}")
        print(f"    - risk_level: {result['risk_level']}")
        print(f"    - score: {result['score']}")

        return result

    except Exception as e:
        print(f"[WARN] GPT 분석 실패: {e}")

        if use_mock_fallback:
            print("[INFO] mock fallback 응답 사용")
            return _mock_analysis(prompt_text, formatted_data, reason=str(e))

        raise
