"""
Script to update expired BookMyShow and Snapdeal coupons with new expiry dates
"""
import json
from datetime import datetime, timedelta


def update_expired_coupons():
    # Load existing data
    with open("deals_bot/data/coupons.json", "r") as f:
        data = json.load(f)

    # Calculate new expiry dates (30 days from now)
    future_date = datetime.now() + timedelta(days=30)
    future_date_str = future_date.strftime("%d %b %Y")

    # Update BookMyShow and Snapdeal coupons with new expiry dates
    updated_count = 0
    for coupon in data["coupons"]:
        if coupon.get("source") in ["BookMyShow", "Snapdeal"]:
            # Update to future date
            coupon["expires"] = future_date_str
            coupon["timestamp"] = datetime.now().isoformat()
            updated_count += 1
            print(f"Updated: {coupon.get('coupon_code')} - {coupon.get('source')} -> expires {future_date_str}")

    # Save updated data
    with open("deals_bot/data/coupons.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nTotal coupons updated: {updated_count}")
    print(f"New expiry date: {future_date_str}")


if __name__ == "__main__":
    update_expired_coupons()
