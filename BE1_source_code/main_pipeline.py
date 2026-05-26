from services.public_api_service import fetch_complaint_data
from services.data_formatter import format_complaint_data
from services.prompt_builder import build_prompt_text
from services.payload_builder import build_payload
from services.backend2_sender import send_to_backend2
from services.gpt_service import analyze_with_gpt
from services.auto_keyword_service import discover_keywords

from dotenv import load_dotenv
import os
import json

load_dotenv()


def load_search_words(file_path="keywords.txt"):
    search_words = []

    if not os.path.exists(file_path):
        return search_words

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            keyword = line.strip()
            if keyword:
                search_words.append(keyword)

    return search_words


def get_processing_keywords():
    use_auto = os.getenv("USE_AUTO_KEYWORD_DISCOVERY", "true").lower() == "true"
    date_from = os.getenv("DATE_FROM", "20260301")
    date_to = os.getenv("DATE_TO", "20260331")
    limit = int(os.getenv("AUTO_KEYWORD_LIMIT", "5"))
    result_count = int(os.getenv("AUTO_KEYWORD_RESULT_COUNT", "10"))

    if use_auto:
        try:
            auto_keywords, merged = discover_keywords(
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                result_count=result_count
            )

            if auto_keywords:
                print("\n[자동 발견 키워드 사용]")
                for idx, item in enumerate(merged[:limit], start=1):
                    print(
                        f"{idx}. {item['label']} | "
                        f"score={item['total_score']} | "
                        f"sources={item['sources']}"
                    )
                return auto_keywords

            print("[WARN] 자동 발견 결과가 비어 있어서 keywords.txt fallback 사용")

        except Exception as e:
            print(f"[WARN] 자동 발견 실패 -> keywords.txt fallback 사용: {e}")

    manual_keywords = load_search_words("keywords.txt")
    print("\n[keywords.txt 사용]")
    print(f"[INFO] 불러온 키워드 개수: {len(manual_keywords)}")
    print(f"[INFO] 키워드 목록: {manual_keywords}")
    return manual_keywords


target = "pttn"
date_from = os.getenv("DATE_FROM", "20260301")
date_to = os.getenv("DATE_TO", "20260331")

search_words = get_processing_keywords()[:2]

print("[START] 자동 키워드 기반 다중 키워드 파이프라인 시작")
print(f"[INFO] 최종 처리 키워드 개수: {len(search_words)}")
print(f"[INFO] 최종 키워드 목록: {search_words}")

for index, search_word in enumerate(search_words, start=1):
    print("=" * 60)
    print(f"[{index}] 현재 키워드: {search_word}")

    try:
        print("[1] 국민권익위원회 민원빅데이터 API 호출 시작")
        raw_data = fetch_complaint_data(
            search_word=search_word,
            date_from=date_from,
            date_to=date_to,
            result_count=10
        )

        print("[2] 데이터 정리 시작")
        formatted_data = format_complaint_data(raw_data)

        print("[3] GPT 입력용 텍스트 생성")
        prompt_text = build_prompt_text(formatted_data)

        print("[4] GPT 분석 시작")
        gpt_result = analyze_with_gpt(
            prompt_text=prompt_text,
            formatted_data=formatted_data
        )

        print("[5] payload 생성 시작")
        payload = build_payload(
            formatted_data,
            gpt_result,
            target=target,
            date_from=date_from,
            date_to=date_to
        )

        payload["source"] = f"complaint_api_gpt_pipeline:{search_word}"

        print("[6] 최종 payload 출력")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

        print("[7] 백엔드2 전송 시작")
        success = send_to_backend2(payload)

        if success:
            print(f"[8] 키워드 '{search_word}' 파이프라인 성공")
        else:
            print(f"[8] 키워드 '{search_word}' 전송 실패")

    except Exception as e:
        print(f"[ERROR] 키워드 '{search_word}' 처리 중 오류 발생: {e}")

print("=" * 60)
print("[END] 자동 키워드 기반 다중 키워드 파이프라인 종료")