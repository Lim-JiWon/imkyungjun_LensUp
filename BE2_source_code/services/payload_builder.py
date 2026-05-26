import os
from datetime import datetime


def build_payload(analysis_result, keyword, formatted_data):
    title = analysis_result.get("title")
    if not title:
        title = f"{keyword} 관련 민원 이슈"

    causes = analysis_result.get("causes", [])
    if not isinstance(causes, list):
        causes = [str(causes)] if causes else []

    keywords = analysis_result.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = [str(keywords)] if keywords else []

    score = analysis_result.get("score", 0)
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0

    complaint_count = analysis_result.get("complaint_count", 0)
    try:
        complaint_count = int(complaint_count)
    except (TypeError, ValueError):
        complaint_count = 0

    issue_key = analysis_result.get("issue_key")
    if not issue_key:
        issue_key = f"issue-{abs(hash(keyword)) % (10 ** 12)}"

    issue_type = analysis_result.get("issue_type") or "keyword_trend"
    summary = analysis_result.get("summary") or ""
    forecast = analysis_result.get("forecast") or ""
    status = analysis_result.get("status") or "detected"
    risk_level = analysis_result.get("risk_level") or "medium"
    top_keyword = analysis_result.get("top_keyword") or keyword

    payload = {
        "batch_id": f"batch-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now().isoformat(),
        "source": f"complaint_api_gpt_pipeline:{keyword}",
        "target": os.getenv("PUBLIC_API_TARGET", "pttn"),
        "date_from": os.getenv("DATE_FROM", ""),
        "date_to": os.getenv("DATE_TO", ""),
        "issues": [
            {
                "issue_key": issue_key,
                "issue_type": issue_type,
                "title": title,
                "summary": summary,
                "forecast": forecast,
                "causes": causes,
                "keywords": keywords,
                "status": status,
                "risk_level": risk_level,
                "score": score,
                "complaint_count": complaint_count,
                "top_keyword": top_keyword,
            }
        ],
    }

    return payload
