import requests


BASE_URL = "http://211.188.50.216:8000/search"


TEST_CASES = [
    {
        "query": "자동차",
        "must_include_any": [
            "자동차",
            "차량",
            "번호판",
            "한국교통안전공단",
            "한국도로공사",
        ],
        "must_exclude": [
            "농협은행 통장",
            "배송 도착",
            "데이터센터 건립",
            "청정원 마요네즈",
            "노래방 무단투기",
        ],
    },
    {
        "query": "농협은행",
        "must_include_any": [
            "농협은행 통장",
        ],
        "must_exclude": [
            "자동차",
            "배송 도착",
            "데이터센터",
            "노래방 무단투기",
        ],
    },
    {
        "query": "배송",
        "must_include_any": [
            "배송 도착",
        ],
        "must_exclude": [
            "자동차",
            "농협은행 통장",
            "데이터센터 건립",
        ],
    },
    {
        "query": "청정원",
        "must_include_any": [
            "청정원 마요네즈",
        ],
        "must_exclude": [
            "노래방 무단투기",
            "공중 목욕탕",
            "내란죄우두머리수괴 종물",
        ],
    },
    {
        "query": "목욕탕",
        "must_include_any": [
            "공중 목욕탕",
        ],
        "must_exclude": [
            "몰수추징청구 기소전",
            "노래장 집단",
            "내란죄우두머리수괴 종물",
        ],
    },
    {
        "query": "무단투기",
        "must_include_any": [
            "노래방 무단투기",
        ],
        "must_exclude": [
            "공중 목욕탕",
            "노래장 집단",
            "몰수추징청구 기소전",
            "내란죄우두머리수괴 종물",
        ],
    },
    {
        "query": "데이터센터",
        "must_include_any": [
            "데이터센터 건립",
        ],
        "must_exclude": [
            "농협은행 통장",
            "배송 도착",
            "노래방 무단투기",
            "청정원 마요네즈",
        ],
    },
]


def fetch_search(query: str):
    response = requests.get(BASE_URL, params={"query": query}, timeout=30)
    print(f"\n[QUERY] {query}")
    print(f"[STATUS] {response.status_code}")

    if response.status_code != 200:
        print("[FAIL] 요청 실패")
        print(response.text[:1000])
        return []

    data = response.json()
    results = data.get("results", [])

    print(f"[COUNT] {data.get('count')}")
    print(f"[TOTAL BEFORE DEDUP] {data.get('total_count_before_dedup')}")

    for index, item in enumerate(results, start=1):
        title = item.get("title", "")
        category = item.get("category", "")
        top_keyword = item.get("top_keyword", "")
        matched_fields = item.get("matched_fields", [])
        match_score = item.get("match_score", 0)

        print(f"  {index}. {title}")
        print(f"     top_keyword={top_keyword}")
        print(f"     category={category}")
        print(f"     match_score={match_score}")
        print(f"     matched_fields={matched_fields}")

    return results


def contains_text(item, text: str) -> bool:
    fields = [
        item.get("title", ""),
        item.get("top_keyword", ""),
        item.get("summary", ""),
        item.get("category", ""),
    ]

    for field in fields:
        if text in str(field):
            return True

    return False


def check_case(case):
    query = case["query"]
    results = fetch_search(query)

    titles = [item.get("title", "") for item in results]

    passed = True

    include_ok = False
    for expected in case["must_include_any"]:
        for item in results:
            if contains_text(item, expected):
                include_ok = True
                break

    if include_ok:
        print("[OK] 기대 결과 포함")
    else:
        print(f"[FAIL] 기대 결과 없음: {case['must_include_any']}")
        passed = False

    for banned in case["must_exclude"]:
        for item in results:
            if contains_text(item, banned):
                print(f"[FAIL] 제외되어야 할 결과 포함: {banned}")
                passed = False

    if passed:
        print("[PASS] 검색 노이즈 검수 통과")
    else:
        print("[WARN] 검색 노이즈 검수 실패")

    return passed


def main():
    print("=" * 100)
    print("[START] 검색 노이즈 자동 검수")
    print("=" * 100)

    total = len(TEST_CASES)
    passed_count = 0

    for case in TEST_CASES:
        if check_case(case):
            passed_count += 1

    print("\n" + "=" * 100)
    print("[FINAL RESULT]")
    print("=" * 100)
    print(f"통과: {passed_count}/{total}")

    if passed_count == total:
        print("[SUCCESS] 검색 노이즈 수정 검수 통과")
    else:
        print("[WARN] 일부 검색어에서 관계없는 결과가 남아 있습니다.")
        print("위 FAIL 항목을 백엔드2 담당자에게 전달하세요.")


if __name__ == "__main__":
    main()