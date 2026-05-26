def build_prompt_text(formatted_data):
    keyword_count = formatted_data.get("keyword_count", 0)
    keywords = formatted_data.get("keywords", [])

    lines = []
    lines.append(f"분석 기간 동안 추출된 주요 키워드는 총 {keyword_count}개입니다.")
    lines.append("아래는 상위 키워드 목록입니다.")

    for item in keywords:
        rank = item.get("rank")
        label = item.get("label")
        value = item.get("value")
        lines.append(f"{rank}위 키워드는 '{label}'이며 값은 {value}입니다.")

    prompt_text = "\n".join(lines)
    return prompt_text