from datetime import datetime
import uuid


def build_payload(formatted_data, gpt_result, target, date_from, date_to):
    batch_id = f"batch-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    issue_key = f"issue-{uuid.uuid4().hex[:12]}"

    keywords = formatted_data.get("labels_only", [])
    keyword_count = formatted_data.get("keyword_count", 0)
    top_keyword = keywords[0] if keywords else ""

    title = gpt_result.get("title")
    if not title:
        if top_keyword:
            title = f"{top_keyword} 관련 민원 브리핑"
        else:
            title = "민원 이슈 브리핑"

    summary = gpt_result.get("summary") or ""
    forecast = gpt_result.get("forecast") or ""
    causes = gpt_result.get("causes") or []

    risk_level = gpt_result.get("risk_level") or "medium"

    score = gpt_result.get("score", 70.0)
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 70.0

    payload = {
        "batch_id": batch_id,
        "generated_at": datetime.now().isoformat(),
        "source": "complaint_api_gpt_pipeline",
        "target": target,
        "date_from": date_from,
        "date_to": date_to,
        "issues": [
            {
                "issue_key": issue_key,
                "issue_type": "keyword_trend",
                "title": title,
                "summary": summary,
                "forecast": forecast,
                "causes": causes,
                "keywords": keywords,
                "status": "detected",
                "risk_level": risk_level,
                "score": score,
                "complaint_count": keyword_count,
                "top_keyword": top_keyword,
            }
        ]
    }

    return payload