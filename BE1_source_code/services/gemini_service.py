import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


def parse_gemini_response(text_result):
    summary = ""
    main_issue = ""
    forecast = ""
    causes = []

    lines = text_result.splitlines()
    current_section = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("summary:"):
            summary = line.replace("summary:", "", 1).strip()
            current_section = "summary"

        elif line.startswith("main_issue:"):
            main_issue = line.replace("main_issue:", "", 1).strip()
            current_section = "main_issue"

        elif line.startswith("forecast:"):
            forecast = line.replace("forecast:", "", 1).strip()
            current_section = "forecast"

        elif line.startswith("causes:"):
            current_section = "causes"

        elif line.startswith("-") and current_section == "causes":
            causes.append(line.replace("-", "", 1).strip())

        else:
            if current_section == "summary":
                summary += " " + line
            elif current_section == "main_issue":
                main_issue += " " + line
            elif current_section == "forecast":
                forecast += " " + line

    return {
        "summary": summary.strip(),
        "main_issue": main_issue.strip(),
        "forecast": forecast.strip(),
        "causes": causes
    }


def run_gemini_analysis(prompt_text):
    full_prompt = f"""
너는 공공 민원 데이터 분석 도우미다.

아래 키워드 데이터를 보고 반드시 아래 형식 그대로 한국어로 작성해라.
다른 설명은 쓰지 말고 형식만 지켜라.

summary: 전체 요약 한두 문장
main_issue: 핵심 이슈 제목 한 문장
forecast: 앞으로의 가능성 한두 문장
causes:
- 원인 후보 1
- 원인 후보 2
- 원인 후보 3

키워드 데이터:
{prompt_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
    )

    text_result = response.text if response.text else ""
    parsed_result = parse_gemini_response(text_result)

    return parsed_result