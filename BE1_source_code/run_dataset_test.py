from dotenv import load_dotenv
from services.public_api_service import fetch_dataset_by_type
from services.source_normalizer import normalize_items
import json

load_dotenv()

dataset_type = "keyword_complaint_count"
date_from = "20250301000000"
date_to = "20250305235959"
keyword = "불법 주정차"

raw_items = fetch_dataset_by_type(
    dataset_type=dataset_type,
    date_from=date_from,
    date_to=date_to,
    result_count=10,
    keyword=keyword,
)

print("[RAW COUNT]", len(raw_items))
print(json.dumps(raw_items[:3], ensure_ascii=False, indent=2))

normalized = normalize_items(dataset_type, raw_items)

print("[NORMALIZED COUNT]", len(normalized))
print(json.dumps(normalized[:3], ensure_ascii=False, indent=2))