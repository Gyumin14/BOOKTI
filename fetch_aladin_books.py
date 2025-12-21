import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
TTB_KEY = os.getenv("ALADIN_TTB_KEY")

URL = "https://www.aladin.co.kr/ttb/api/ItemList.aspx"

def fetch_page(page: int, max_results: int = 50):
    params = {
        "ttbkey": TTB_KEY,
        "QueryType": "Bestseller",
        "SearchTarget": "Book",
        "MaxResults": max_results,
        "start": page,           # ✅ page 번호 (1,2,3...)
        "Output": "js",
        "Version": "20131101",
    }
    r = requests.get(URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get("item", [])

# ✅ 600권 = 50개 * 12페이지
items = []
for page in range(1, 13):   # 1~12
    items.extend(fetch_page(page, 50))

# (선택) isbn13 기준 중복 제거
dedup = {}
for it in items:
    key = it.get("isbn13") or it.get("isbn")
    if key:
        dedup[key] = it
items = list(dedup.values())

# ✅ 모든 필드 그대로 저장
with open("aladin_bestseller_600_raw.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print("저장 완료:", len(items))
