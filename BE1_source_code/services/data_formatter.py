def format_complaint_data(raw_data, trend_data=None, related_keywords=None, complaint_count=None):
    keywords = []

    for index, item in enumerate(raw_data, start=1):
        keyword_info = {
            "rank": index,
            "label": item.get("label"),
            "value": item.get("value")
        }
        keywords.append(keyword_info)

    labels_only = [item["label"] for item in keywords if item.get("label")]

    formatted_data = {
        "keyword_count": complaint_count if complaint_count is not None else len(keywords),
        "keywords": keywords,
        "labels_only": labels_only,
        "trend_data": trend_data or [],
        "related_keywords": related_keywords or labels_only[:10],
    }

    return formatted_data