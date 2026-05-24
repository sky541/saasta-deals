"""One-off cleanup: remove expired coupons from local JSON files."""
import os
import json
from datetime import datetime


def is_expired(expires: str) -> bool:
    if not expires:
        return False
    try:
        exp_date = datetime.strptime(expires.strip(), "%d %b %Y")
        return exp_date.date() < datetime.now().date()
    except:
        return False


def cleanup_file(filepath: str) -> int:
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0

    # Determine coupon list key
    if "coupons" in data:
        key = "coupons"
    elif "deals" in data:
        key = "deals"
    else:
        return 0

    coupons = data.get(key, [])
    before = len(coupons)
    cleaned = [c for c in coupons if not is_expired(c.get("expires", ""))]
    removed = before - len(cleaned)
    if removed > 0:
        data[key] = cleaned
        data["count"] = len(cleaned)
        data["timestamp"] = datetime.now().isoformat()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    return removed


def main():
    paths = [
        "deals_bot/data/coupons.json",
        "data/coupons.json",
        "../deals_bot/data/coupons.json",
        "deals_bot/data/combined_deals.json",
        "data/combined_deals.json",
        "../deals_bot/data/combined_deals.json",
    ]
    total_removed = 0
    for p in paths:
        removed = cleanup_file(p)
        if removed:
            print(f"Removed {removed} expired coupons from {p}")
            total_removed += removed

    if total_removed == 0:
        print("No expired coupons found/removed.")
    else:
        print(f"Total expired coupons removed: {total_removed}")


if __name__ == "__main__":
    main()
