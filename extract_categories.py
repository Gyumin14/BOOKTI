import json
import re
from collections import defaultdict
from pathlib import Path

# ✅ 네 100권 파일명으로 바꿔줘
INPUT_JSON = "aladin_bestseller_100.json"
OUT_DIR = "by_major"

def safe_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    name = re.sub(r"\s+", "_", name)
    return name[:60] if name else "Unknown"

def get_major_category(category_name: str) -> str:
    """
    '국내도서>소설/시/희곡>한국소설>...' -> '소설/시/희곡' (대분류)
    """
    if not category_name:
        return "Unknown"

    parts = [p.strip() for p in category_name.split(">") if p.strip()]
    # parts[0] = '국내도서' 같은 최상위
    # parts[1] = 대분류
    return parts[1] if len(parts) >= 2 else parts[0]

def load_items(path: str):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "item" in data:
        return data["item"]
    if isinstance(data, list):
        return data
    raise ValueError("JSON 구조가 list 또는 dict(item) 형태가 아닙니다.")

def main():
    items = load_items(INPUT_JSON)

    grouped = defaultdict(list)

    for it in items:
        major = get_major_category(it.get("categoryName", ""))
        grouped[major].append(it)

    out_path = Path(OUT_DIR)
    out_path.mkdir(parents=True, exist_ok=True)

    # ✅ 대분류별 파일 저장
    for major, books in sorted(grouped.items(), key=lambda x: (-len(x[1]), x[0])):
        filename = out_path / f"major_{safe_filename(major)}_{len(books)}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        print(f"[OK] {major}: {len(books)}권 -> {filename}")

    # ✅ 전체 요약도 같이 저장(선택)
    summary = {major: len(books) for major, books in grouped.items()}
    with open(out_path / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("\n[OK] summary.json 저장 완료")

if __name__ == "__main__":
    main()
