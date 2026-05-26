import requests
import time
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BACKEND2_URL = os.getenv("BACKEND2_URL")

# .env에서 BACKEND2_API_KEY를 우선 사용하고,
# 혹시 기존 이름인 PIPELINE_API_KEY를 쓰고 있었다면 fallback으로 사용
API_KEY = os.getenv("BACKEND2_API_KEY") or os.getenv("PIPELINE_API_KEY")

BASE_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = BASE_DIR / "cache"
FAILED_PAYLOAD_DIR = BASE_DIR / "failed_payloads"
SENT_BATCH_FILE = CACHE_DIR / "sent_batches.json"


def load_sent_batches():
    if not SENT_BATCH_FILE.exists():
        return set()

    try:
        with open(SENT_BATCH_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_sent_batches(sent_batches):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    with open(SENT_BATCH_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent_batches), f, ensure_ascii=False, indent=2)


def save_failed_payload(payload: dict, reason: str = ""):
    FAILED_PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)

    batch_id = payload.get("batch_id") or "unknown_batch"
    file_path = FAILED_PAYLOAD_DIR / f"{batch_id}.json"

    failed_data = {
        "reason": reason,
        "payload": payload,
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(failed_data, f, ensure_ascii=False, indent=2)

    print(f"[SAVE] failed payload saved: {file_path}")


def send_to_backend2(payload: dict, max_retries: int = 3, timeout: int = 60):
    batch_id = payload.get("batch_id")

    if not BACKEND2_URL:
        print("[ERROR] BACKEND2_URL이 .env에 없습니다.")
        save_failed_payload(payload, reason="BACKEND2_URL missing")
        return False

    if not API_KEY:
        print("[ERROR] BACKEND2_API_KEY 또는 PIPELINE_API_KEY가 .env에 없습니다.")
        save_failed_payload(payload, reason="API_KEY missing")
        return False

    sent_batches = load_sent_batches()

    # 같은 프로그램 실행 중 같은 batch_id 재전송 방지
    # 단, batch_id는 실행마다 바뀌므로 최종 중복 방지는 backend2의 issue_key 기준으로 처리해야 함
    if batch_id in sent_batches:
        print(f"[SKIP] 이미 전송된 batch_id={batch_id}")
        return True

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY,
    }

    print("[SEND] Backend2 전송 시작")
    print(f"[SEND] url={BACKEND2_URL}")
    print(f"[SEND] batch_id={batch_id}")
    print(f"[SEND] issue_count={len(payload.get('issues', []))}")
    print(f"[SEND] timeout={timeout}s")

    last_error = ""

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                BACKEND2_URL,
                json=payload,
                headers=headers,
                timeout=timeout,
            )

            print(f"[RESPONSE] attempt={attempt}, status={response.status_code}")

            if response.status_code == 200:
                print("[SUCCESS] Backend2 전송 성공")

                try:
                    print("[RESPONSE BODY]")
                    print(response.text[:1000])
                except Exception:
                    pass

                sent_batches.add(batch_id)
                save_sent_batches(sent_batches)

                return True

            else:
                last_error = f"status={response.status_code}, body={response.text[:1000]}"
                print(f"[FAIL] {last_error}")

        except requests.exceptions.Timeout:
            last_error = f"timeout after {timeout}s"
            print(f"[TIMEOUT] attempt={attempt}, {last_error}")

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f"[ERROR] attempt={attempt}, error={last_error}")

        if attempt < max_retries:
            sleep_time = 2 ** attempt
            print(f"[RETRY] {sleep_time}초 후 재시도...")
            time.sleep(sleep_time)

    print("[FINAL FAIL] Backend2 전송 실패")
    save_failed_payload(payload, reason=last_error)
    return False