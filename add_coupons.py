"""
Script to add BookMyShow and Snapdeal coupons to the coupons.json file
Run this script to update the deals data
"""
import json
from datetime import datetime


def add_coupons():
    # Load existing data
    with open("data/coupons.json", "r") as f:
        data = json.load(f)

    # New BookMyShow coupons
    bookmyshow_coupons = [
        {
            "coupon_code": "BMSFLAT300",
            "description": "Flat Rs. 300 Off on Movie Tickets",
            "discount": "Rs. 300",
            "min_order": "Rs. 600",
            "expires": "31 Mar 2026",
            "product_url": "https://in.bookmyshow.com/",
            "source": "BookMyShow",
            "category": "entertainment",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
        {
            "coupon_code": "BMSEVENT25",
            "description": "25% Off on Event Tickets",
            "discount": "25%",
            "min_order": "Rs. 500",
            "expires": "15 Apr 2026",
            "product_url": "https://in.bookmyshow.com/",
            "source": "BookMyShow",
            "category": "entertainment",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
        {
            "coupon_code": "BMSNEWUSER",
            "description": "Rs. 200 Off for New Users",
            "discount": "Rs. 200",
            "min_order": "Rs. 400",
            "expires": "31 Dec 2026",
            "product_url": "https://in.bookmyshow.com/",
            "source": "BookMyShow",
            "category": "entertainment",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
        {
            "coupon_code": "BMSSPORTS50",
            "description": "50% Off on Sports Events",
            "discount": "50%",
            "min_order": "Rs. 1000",
            "expires": "20 Mar 2026",
            "product_url": "https://in.bookmyshow.com/",
            "source": "BookMyShow",
            "category": "sports",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
        {
            "coupon_code": "BMSSTRAMUSIC",
            "description": "Flat Rs. 150 Off on Concert Tickets",
            "discount": "Rs. 150",
            "min_order": "Rs. 750",
            "expires": "10 Apr 2026",
            "product_url": "https://in.bookmyshow.com/",
            "source": "BookMyShow",
            "category": "entertainment",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
    ]

    # New Snapdeal coupons
    snapdeal_coupons = [
        {
            "coupon_code": "SNAP100OFF",
            "description": "Flat Rs. 100 Off on Rs. 500",
            "discount": "Rs. 100",
            "min_order": "Rs. 500",
            "expires": "31 Mar 2026",
            "product_url": "https://www.snapdeal.com/",
            "source": "Snapdeal",
            "category": "shopping",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
        {
            "coupon_code": "SNAPELECTRO15",
            "description": "15% Off on Electronics",
            "discount": "15%",
            "min_order": "Rs. 2000",
            "expires": "20 Apr 2026",
            "product_url": "https://www.snapdeal.com/",
            "source": "Snapdeal",
            "category": "electronics",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
        {
            "coupon_code": "SNAPFASHION25",
            "description": "25% Off on Fashion",
            "discount": "25%",
            "min_order": "Rs. 999",
            "expires": "15 Apr 2026",
            "product_url": "https://www.snapdeal.com/",
            "source": "Snapdeal",
            "category": "fashion",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
        {
            "coupon_code": "SNAPHOME30",
            "description": "30% Off on Home & Kitchen",
            "discount": "30%",
            "min_order": "Rs. 1500",
            "expires": "25 Mar 2026",
            "product_url": "https://www.snapdeal.com/",
            "source": "Snapdeal",
            "category": "home",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
        {
            "coupon_code": "SNAPFREE100",
            "description": "Free Rs. 100 Gift Card on Rs. 2000",
            "discount": "Rs. 100",
            "min_order": "Rs. 2000",
            "expires": "30 Apr 2026",
            "product_url": "https://www.snapdeal.com/",
            "source": "Snapdeal",
            "category": "shopping",
            "timestamp": datetime.now().isoformat(),
            "city": "all",
        },
    ]

    # Add new coupons
    data["coupons"].extend(bookmyshow_coupons)
    data["coupons"].extend(snapdeal_coupons)
    data["count"] = len(data["coupons"])
    data["timestamp"] = datetime.now().isoformat()

    # Save updated data
    with open("data/coupons.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"Added {len(bookmyshow_coupons)} BookMyShow coupons")
    print(f"Added {len(snapdeal_coupons)} Snapdeal coupons")
    print(f"Total coupons now: {data['count']}")


if __name__ == "__main__":
    add_coupons()
