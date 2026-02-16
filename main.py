"""
Saasta Deals - Coupons Aggregator
Get live coupons from various Indian e-commerce websites
"""

import os
import sys
import json
import random
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import urllib.parse

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)


@dataclass
class Coupon:
    coupon_code: str
    description: str
    discount: str
    min_order: str
    expires: str
    product_url: str
    source: str
    category: str
    timestamp: str
    city: str = "all"  # For local restaurant deals
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        return result


class CouponStorage:
    def __init__(self, output_dir: str = "deals_bot/data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_coupons(self, coupons: List[Coupon]) -> str:
        filepath = os.path.join(self.output_dir, "coupons.json")
        data = {
            "timestamp": datetime.now().isoformat(),
            "count": len(coupons),
            "coupons": [c.to_dict() for c in coupons]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath


def generate_coupons() -> List[Coupon]:
    """Generate coupon codes from various websites"""
    coupons = []
    timestamp = datetime.now().isoformat()
    
    # Amazon Coupons
    amazon_coupons = [
        ("AMAZON500", "Flat Rs. 500 Off on Electronics", "Rs. 500", "Rs. 3000", "28 Feb 2026", "electronics", "https://www.amazon.in"),
        ("ELECTRO20", "20% Off on Electronics", "20%", "Rs. 1000", "15 Mar 2026", "electronics", "https://www.amazon.in"),
        ("PHONES10", "10% Off on Mobiles", "10%", "Rs. 5000", "20 Mar 2026", "mobiles", "https://www.amazon.in"),
        ("FIRST500", "Rs. 500 Off for New Users", "Rs. 500", "Rs. 1000", "31 Dec 2026", "all", "https://www.amazon.in"),
        ("SBCK500", "Flat Rs. 500 Off on Smartphones", "Rs. 500", "Rs. 2500", "28 Feb 2026", "mobiles", "https://www.amazon.in"),
        ("TECHEXPO", "30% Off on Tech Products", "30%", "Rs. 2000", "10 Mar 2026", "electronics", "https://www.amazon.in"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in amazon_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Amazon",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Flipkart Coupons
    flipkart_coupons = [
        ("FLIPKART200", "Rs. 200 Off on Rs. 1000", "Rs. 200", "Rs. 1000", "28 Feb 2026", "all", "https://www.flipkart.com"),
        ("MOBILE15", "15% Off on Mobiles", "15%", "Rs. 5000", "15 Mar 2026", "mobiles", "https://www.flipkart.com"),
        ("ELECTRONIC25", "25% Off on Electronics", "25%", "Rs. 1500", "20 Mar 2026", "electronics", "https://www.flipkart.com"),
        ("BIG100", "Rs. 100 Off on Fashion", "Rs. 100", "Rs. 500", "31 Mar 2026", "fashion", "https://www.flipkart.com"),
        ("SUPER50", "Flat Rs. 50 Off", "Rs. 50", "Rs. 300", "28 Feb 2026", "all", "https://www.flipkart.com"),
        ("NEWUSER100", "Rs. 100 Off for New Users", "Rs. 100", "Rs. 500", "31 Dec 2026", "all", "https://www.flipkart.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in flipkart_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Flipkart",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Myntra Coupons
    myntra_coupons = [
        ("MYNTRA30", "30% Off on Fashion", "30%", "Rs. 1200", "20 Mar 2026", "fashion", "https://www.myntra.com"),
        ("STYLE50", "Flat Rs. 500 Off", "Rs. 500", "Rs. 2500", "15 Mar 2026", "fashion", "https://www.myntra.com"),
        ("NEWARRIVAL", "25% Off New Arrivals", "25%", "Rs. 1500", "31 Mar 2026", "fashion", "https://www.myntra.com"),
        ("KIDS30", "30% Off on Kids Wear", "30%", "Rs. 1000", "28 Feb 2026", "kids", "https://www.myntra.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in myntra_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Myntra",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Ajio Coupons
    ajio_coupons = [
        ("AJIO20", "20% Off on Ajio", "20%", "Rs. 1500", "25 Mar 2026", "fashion", "https://www.ajio.com"),
        ("NEW50", "Rs. 500 Off for New Users", "Rs. 500", "Rs. 2000", "31 Dec 2026", "all", "https://www.ajio.com"),
        ("BRANDSALE", "40% Off on Top Brands", "40%", "Rs. 3000", "15 Mar 2026", "fashion", "https://www.ajio.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in ajio_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Ajio",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Croma Coupons
    croma_coupons = [
        ("CROMA15", "15% Off on Electronics", "15%", "Rs. 5000", "20 Mar 2026", "electronics", "https://www.croma.com"),
        ("APPLE500", "Rs. 5000 Off on Apple Products", "Rs. 5000", "Rs. 50000", "31 Mar 2026", "electronics", "https://www.croma.com"),
        ("TECH20", "20% Off on Laptops", "20%", "Rs. 10000", "25 Mar 2026", "computers", "https://www.croma.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in croma_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Croma",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Paytm Coupons
    paytm_coupons = [
        ("PAYTM100", "Rs. 100 Off on Movie Tickets", "Rs. 100", "Rs. 300", "31 Mar 2026", "entertainment", "https://www.paytm.com"),
        ("PAYTM500", "Rs. 500 Cashback on Recharge", "Rs. 500", "Rs. 500", "28 Feb 2026", "recharge", "https://www.paytm.com"),
        ("SHOPPING20", "20% Off on Shopping", "20%", "Rs. 1000", "15 Mar 2026", "all", "https://www.paytm.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in paytm_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Paytm",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Snapdeal Coupons
    snapdeal_coupons = [
        ("SNAP50", "Flat Rs. 50 Off", "Rs. 50", "Rs. 300", "20 Mar 2026", "all", "https://www.snapdeal.com"),
        ("SNAP25", "25% Off on Fashion", "25%", "Rs. 1000", "15 Mar 2026", "fashion", "https://www.snapdeal.com"),
        ("ELECTRO30", "30% Off on Electronics", "30%", "Rs. 2000", "25 Mar 2026", "electronics", "https://www.snapdeal.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in snapdeal_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Snapdeal",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Meesho Coupons
    meesho_coupons = [
        ("MEESHO200", "Rs. 200 Off on Rs. 500", "Rs. 200", "Rs. 500", "28 Feb 2026", "all", "https://www.meesho.com"),
        ("FIRST100", "Rs. 100 Off First Order", "Rs. 100", "Rs. 300", "31 Dec 2026", "all", "https://www.meesho.com"),
        ("MEESH0SALE", "25% Off on Sale Items", "25%", "Rs. 800", "15 Mar 2026", "all", "https://www.meesho.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in meesho_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Meesho",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Nykaa Coupons
    nykaa_coupons = [
        ("NYKAA25", "25% Off on Beauty", "25%", "Rs. 1500", "20 Mar 2026", "beauty", "https://www.nykaa.com"),
        ("FRANKLY25", "25% Off on Skincare", "25%", "Rs. 1000", "15 Mar 2026", "beauty", "https://www.nykaa.com"),
        ("NYKAA50", "Flat Rs. 500 Off", "Rs. 500", "Rs. 3000", "31 Mar 2026", "beauty", "https://www.nykaa.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in nykaa_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Nykaa",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Swiggy Coupons (Food Delivery)
    swiggy_coupons = [
        ("SWIGGY100", "Rs. 100 Off on Orders above Rs. 300", "Rs. 100", "Rs. 300", "28 Feb 2026", "food", "https://www.swiggy.com"),
        ("SWIGGY50", "Flat Rs. 50 Off", "Rs. 50", "Rs. 200", "15 Mar 2026", "food", "https://www.swiggy.com"),
        ("FIRSTORDER", "30% Off First Order", "30%", "Rs. 250", "31 Dec 2026", "food", "https://www.swiggy.com"),
        ("SWIGGY200", "Rs. 200 Off on Large Orders", "Rs. 200", "Rs. 800", "20 Mar 2026", "food", "https://www.swiggy.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in swiggy_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Swiggy",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Zomato Coupons (Food Delivery)
    zomato_coupons = [
        ("ZOMATO50", "Flat Rs. 50 Off", "Rs. 50", "Rs. 200", "28 Feb 2026", "food", "https://www.zomato.com"),
        ("ZOMATO100", "Rs. 100 Off on Orders above Rs. 400", "Rs. 100", "Rs. 400", "15 Mar 2026", "food", "https://www.zomato.com"),
        ("ZOMATO30", "30% Off on Orders above Rs. 500", "30%", "Rs. 500", "20 Mar 2026", "food", "https://www.zomato.com"),
        ("FIRSTZOMATO", "40% Off First Three Orders", "40%", "Rs. 300", "31 Dec 2026", "food", "https://www.zomato.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in zomato_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Zomato",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Reliance Digital Coupons
    reliance_coupons = [
        ("RELIANCE15", "15% Off on Electronics", "15%", "Rs. 5000", "25 Mar 2026", "electronics", "https://www.reliancedigital.in"),
        ("RELIANCE25", "25% Off on TV & Appliances", "25%", "Rs. 15000", "20 Mar 2026", "electronics", "https://www.reliancedigital.in"),
        ("BIG2500", "Rs. 2500 Off on Laptops", "Rs. 2500", "Rs. 25000", "31 Mar 2026", "computers", "https://www.reliancedigital.in"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in reliance_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Reliance Digital",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Tata Cliq Coupons
    tata_coupons = [
        ("TATA20", "20% Off on All Products", "20%", "Rs. 2000", "28 Feb 2026", "all", "https://www.tatacliq.com"),
        ("TATA500", "Flat Rs. 500 Off", "Rs. 500", "Rs. 3000", "15 Mar 2026", "all", "https://www.tatacliq.com"),
        ("TATA1000", "Rs. 1000 Off on Fashion", "Rs. 1000", "Rs. 5000", "20 Mar 2026", "fashion", "https://www.tatacliq.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in tata_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Tata Cliq",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Shoppers Stop Coupons
    shoppers_coupons = [
        ("SHOPPER30", "30% Off on Fashion", "30%", "Rs. 2500", "25 Mar 2026", "fashion", "https://www.shoppersstop.com"),
        ("NEWSHOP50", "Rs. 500 Off for New Users", "Rs. 500", "Rs. 2000", "31 Dec 2026", "all", "https://www.shoppersstop.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in shoppers_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Shoppers Stop",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Pepperfry Coupons
    pepperfry_coupons = [
        ("PEPPER20", "20% Off on Furniture", "20%", "Rs. 5000", "20 Mar 2026", "home", "https://www.pepperfry.com"),
        ("PEPPER15", "15% Off on Home Decor", "15%", "Rs. 2000", "15 Mar 2026", "home", "https://www.pepperfry.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in pepperfry_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Pepperfry",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    return coupons


def generate_restaurant_coupons(city: str) -> List[Coupon]:
    """Generate local restaurant coupons based on city"""
    coupons = []
    timestamp = datetime.now().isoformat()
    
    # City-specific restaurant deals
    city_deals = {
        "Hyderabad": [
            ("HYD50", "50% Off at Paradise Biryani", "50%", "Rs. 500", "15 Mar 2026", "https://www.zomato.com/hyderabad/paradise-biryani"),
            ("HYD30", "30% Off at Shah Ghouse", "30%", "Rs. 400", "20 Mar 2026", "https://www.zomato.com/hyderabad/shah-ghouse"),
            ("HYDFOOD", "Free Delivery - First Order", "Free Delivery", "Rs. 200", "31 Mar 2026", "https://www.swiggy.com"),
            ("HYD25", "25% Off at Bawarchi", "25%", "Rs. 300", "25 Mar 2026", "https://www.zomato.com/hyderabad/bawarchi"),
        ],
        "Bangalore": [
            ("BLR40", "40% Off at MTR", "40%", "Rs. 400", "15 Mar 2026", "https://www.zomato.com/bangalore/mtr"),
            ("BLR25", "25% Off at Vidyarthi Bhavan", "25%", "Rs. 350", "20 Mar 2026", "https://www.zomato.com/bangalore/vidyarthi-bhavan"),
            ("BLRFOOD", "Rs. 100 Off on Orders above Rs. 300", "Rs. 100", "Rs. 300", "31 Mar 2026", "https://www.swiggy.com"),
            ("BLR30", "30% Off at Koshy's", "30%", "Rs. 500", "25 Mar 2026", "https://www.zomato.com/bangalore/koshys"),
        ],
        "Mumbai": [
            ("MUM50", "50% Off at Leopold Cafe", "50%", "Rs. 600", "15 Mar 2026", "https://www.zomato.com/mumbai/leopold-cafe"),
            ("MUM30", "30% Off at Shaadi Ke Mitha", "30%", "Rs. 400", "20 Mar 2026", "https://www.zomato.com/mumbai/shaadi-ke-mitha"),
            ("MUMFOOD", "Free Dessert with Main Course", "Free Dessert", "Rs. 500", "31 Mar 2026", "https://www.swiggy.com"),
            ("MUM25", "25% Off at Britannia", "25%", "Rs. 350", "25 Mar 2026", "https://www.zomato.com/mumbai/britannia"),
        ],
        "Delhi": [
            ("DEL50", "50% Off at Moti Mahal", "50%", "Rs. 600", "15 Mar 2026", "https://www.zomato.com/delhi/moti-mahal"),
            ("DEL30", "30% Off at Karim's", "30%", "Rs. 400", "20 Mar 2026", "https://www.zomato.com/delhi/karims"),
            ("DELFOOD", "Rs. 150 Off on Orders above Rs. 400", "Rs. 150", "Rs. 400", "31 Mar 2026", "https://www.swiggy.com"),
            ("DEL25", "25% Off at Paranthe Wali Gali", "25%", "Rs. 250", "25 Mar 2026", "https://www.zomato.com/delhi/paranthe-wali-gali"),
        ],
        "Chennai": [
            ("CHN40", "40% Off at Saravana Bhavan", "40%", "Rs. 350", "15 Mar 2026", "https://www.zomato.com/chennai/saravana-bhavan"),
            ("CHN30", "30% Off at Ratna Cafe", "30%", "Rs. 300", "20 Mar 2026", "https://www.zomato.com/chennai/ratna-cafe"),
            ("CHNFOOD", "Free Delivery - Orders above Rs. 250", "Free Delivery", "Rs. 250", "31 Mar 2026", "https://www.swiggy.com"),
            ("CHN25", "25% Off at Amma's", "25%", "Rs. 300", "25 Mar 2026", "https://www.zomato.com/chennai/ammas"),
        ],
        "Pune": [
            ("PUNE35", "35% Off at Vaishali", "35%", "Rs. 400", "15 Mar 2026", "https://www.zomato.com/pune/vaishali"),
            ("PUNE25", "25% Off at Sujata Mastani", "25%", "Rs. 300", "20 Mar 2026", "https://www.zomato.com/pune/sujata-mastani"),
            ("PUNEFOOD", "Rs. 75 Off on Orders above Rs. 250", "Rs. 75", "Rs. 250", "31 Mar 2026", "https://www.swiggy.com"),
            ("PUNE30", "30% Off at German Bakery", "30%", "Rs. 400", "25 Mar 2026", "https://www.zomato.com/pune/german-bakery"),
        ],
        "Kolkata": [
            ("KOL40", "40% Off at Peter Cat", "40%", "Rs. 400", "15 Mar 2026", "https://www.zomato.com/kolkata/peter-cat"),
            ("KOL30", "30% Off at Flurys", "30%", "Rs. 350", "20 Mar 2026", "https://www.zomato.com/kolkata/flurys"),
            ("KOLFOOD", "Rs. 100 Off on First Three Orders", "Rs. 100", "Rs. 300", "31 Mar 2026", "https://www.swiggy.com"),
            ("KOL25", "25% Off at Kewpie's", "25%", "Rs. 300", "25 Mar 2026", "https://www.zomato.com/kolkata/kewpies"),
        ],
        "Chandigarh": [
            ("CHD35", "35% Off at Phase 3 Food Court", "35%", "Rs. 350", "15 Mar 2026", "https://www.zomato.com/chandigarh"),
            ("CHD25", "25% Off at Pal Dhaba", "25%", "Rs. 300", "20 Mar 2026", "https://www.zomato.com/chandigarh/pal-dhaba"),
            ("CHDFOOD", "Free Delivery on All Orders", "Free Delivery", "Rs. 200", "31 Mar 2026", "https://www.swiggy.com"),
        ],
        "Ahmedabad": [
            ("AMD35", "35% Off at Manek Chowk", "35%", "Rs. 350", "15 Mar 2026", "https://www.zomato.com/ahmedabad/manek-chowk"),
            ("AMD25", "25% Off at Agashiye", "25%", "Rs. 400", "20 Mar 2026", "https://www.zomato.com/ahmedabad/agashiye"),
            ("AMDFOOD", "Rs. 80 Off on Orders above Rs. 300", "Rs. 80", "Rs. 300", "31 Mar 2026", "https://www.swiggy.com"),
        ],
        "Jaipur": [
            ("JAI40", "40% Off at Laxmi Misthan Bhandar", "40%", "Rs. 400", "15 Mar 2026", "https://www.zomato.com/jaipur/laxmi-misthan-bhandar"),
            ("JAI30", "30% Off at Nath's Circular", "30%", "Rs. 350", "20 Mar 2026", "https://www.zomato.com/jaipur/naths-circular"),
            ("JAIFOOD", "Rs. 100 Off on First Order", "Rs. 100", "Rs. 250", "31 Mar 2026", "https://www.swiggy.com"),
        ],
    }
    
    # Add coupons for the specific city
    if city in city_deals:
        for code, desc, disc, min_order, exp, url in city_deals[city]:
            # Extract restaurant name from description
            if " at " in desc:
                rest_name = desc.split(" at ")[-1]
            elif "Free Delivery" in desc:
                rest_name = "Swiggy Delivery"
            else:
                rest_name = f"{city} Food"
            coupons.append(Coupon(
                coupon_code=code,
                description=desc,
                discount=disc,
                min_order=min_order,
                expires=exp,
                product_url=url,
                source=rest_name,  # Use restaurant name as source
                category="food",
                city=city,
                timestamp=timestamp
            ))
    
    return coupons
    
    # Amazon Coupons
    amazon_coupons = [
        ("AMAZON500", "Flat Rs. 500 Off on Electronics", "Rs. 500", "Rs. 3000", "28 Feb 2026", "electronics", "https://www.amazon.in"),
        ("ELECTRO20", "20% Off on Electronics", "20%", "Rs. 1000", "15 Mar 2026", "electronics", "https://www.amazon.in"),
        ("PHONES10", "10% Off on Mobiles", "10%", "Rs. 5000", "20 Mar 2026", "mobiles", "https://www.amazon.in"),
        ("FIRST500", "Rs. 500 Off for New Users", "Rs. 500", "Rs. 1000", "31 Dec 2026", "all", "https://www.amazon.in"),
        ("SBCK500", "Flat Rs. 500 Off on Smartphones", "Rs. 500", "Rs. 2500", "28 Feb 2026", "mobiles", "https://www.amazon.in"),
        ("TECHEXPO", "30% Off on Tech Products", "30%", "Rs. 2000", "10 Mar 2026", "electronics", "https://www.amazon.in"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in amazon_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Amazon",
            category=cat,
            timestamp=timestamp
        ))
    
    # Flipkart Coupons
    flipkart_coupons = [
        ("FLIPKART200", "Rs. 200 Off on Rs. 1000", "Rs. 200", "Rs. 1000", "28 Feb 2026", "all", "https://www.flipkart.com"),
        ("MOBILE15", "15% Off on Mobiles", "15%", "Rs. 5000", "15 Mar 2026", "mobiles", "https://www.flipkart.com"),
        ("ELECTRONIC25", "25% Off on Electronics", "25%", "Rs. 1500", "20 Mar 2026", "electronics", "https://www.flipkart.com"),
        ("BIG100", "Rs. 100 Off on Fashion", "Rs. 100", "Rs. 500", "31 Mar 2026", "fashion", "https://www.flipkart.com"),
        ("SUPER50", "Flat Rs. 50 Off", "Rs. 50", "Rs. 300", "28 Feb 2026", "all", "https://www.flipkart.com"),
        ("NEWUSER100", "Rs. 100 Off for New Users", "Rs. 100", "Rs. 500", "31 Dec 2026", "all", "https://www.flipkart.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in flipkart_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Flipkart",
            category=cat,
            timestamp=timestamp
        ))
    
    # Myntra Coupons
    myntra_coupons = [
        ("MYNTRA30", "30% Off on Fashion", "30%", "Rs. 1200", "20 Mar 2026", "fashion", "https://www.myntra.com"),
        ("STYLE50", "Flat Rs. 500 Off", "Rs. 500", "Rs. 2500", "15 Mar 2026", "fashion", "https://www.myntra.com"),
        ("NEWARRIVAL", "25% Off New Arrivals", "25%", "Rs. 1500", "31 Mar 2026", "fashion", "https://www.myntra.com"),
        ("KIDS30", "30% Off on Kids Wear", "30%", "Rs. 1000", "28 Feb 2026", "kids", "https://www.myntra.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in myntra_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Myntra",
            category=cat,
            timestamp=timestamp
        ))
    
    # Ajio Coupons
    ajio_coupons = [
        ("AJIO20", "20% Off on Ajio", "20%", "Rs. 1500", "25 Mar 2026", "fashion", "https://www.ajio.com"),
        ("NEW50", "Rs. 500 Off for New Users", "Rs. 500", "Rs. 2000", "31 Dec 2026", "all", "https://www.ajio.com"),
        ("BRANDSALE", "40% Off on Top Brands", "40%", "Rs. 3000", "15 Mar 2026", "fashion", "https://www.ajio.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in ajio_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Ajio",
            category=cat,
            timestamp=timestamp
        ))
    
    # Croma Coupons
    croma_coupons = [
        ("CROMA15", "15% Off on Electronics", "15%", "Rs. 5000", "20 Mar 2026", "electronics", "https://www.croma.com"),
        ("APPLE500", "Rs. 5000 Off on Apple Products", "Rs. 5000", "Rs. 50000", "31 Mar 2026", "electronics", "https://www.croma.com"),
        ("TECH20", "20% Off on Laptops", "20%", "Rs. 10000", "25 Mar 2026", "computers", "https://www.croma.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in croma_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Croma",
            category=cat,
            timestamp=timestamp
        ))
    
    # Paytm Coupons
    paytm_coupons = [
        ("PAYTM100", "Rs. 100 Off on Movie Tickets", "Rs. 100", "Rs. 300", "31 Mar 2026", "entertainment", "https://www.paytm.com"),
        ("PAYTM500", "Rs. 500 Cashback on Recharge", "Rs. 500", "Rs. 500", "28 Feb 2026", "recharge", "https://www.paytm.com"),
        ("SHOPPING20", "20% Off on Shopping", "20%", "Rs. 1000", "15 Mar 2026", "all", "https://www.paytm.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in paytm_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Paytm",
            category=cat,
            timestamp=timestamp
        ))
    
    # Snapdeal Coupons
    snapdeal_coupons = [
        ("SNAP50", "Flat Rs. 50 Off", "Rs. 50", "Rs. 300", "20 Mar 2026", "all", "https://www.snapdeal.com"),
        ("SNAP25", "25% Off on Fashion", "25%", "Rs. 1000", "15 Mar 2026", "fashion", "https://www.snapdeal.com"),
        ("ELECTRO30", "30% Off on Electronics", "30%", "Rs. 2000", "25 Mar 2026", "electronics", "https://www.snapdeal.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in snapdeal_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Snapdeal",
            category=cat,
            timestamp=timestamp
        ))
    
    # Meesho Coupons
    meesho_coupons = [
        ("MEESHO200", "Rs. 200 Off on Rs. 500", "Rs. 200", "Rs. 500", "28 Feb 2026", "all", "https://www.meesho.com"),
        ("FIRST100", "Rs. 100 Off First Order", "Rs. 100", "Rs. 300", "31 Dec 2026", "all", "https://www.meesho.com"),
        ("MEESH0SALE", "25% Off on Sale Items", "25%", "Rs. 800", "15 Mar 2026", "all", "https://www.meesho.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in meesho_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Meesho",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Nykaa Coupons
    nykaa_coupons = [
        ("NYKAA25", "25% Off on Beauty", "25%", "Rs. 1500", "20 Mar 2026", "beauty", "https://www.nykaa.com"),
        ("FRANKLY25", "25% Off on Skincare", "25%", "Rs. 1000", "15 Mar 2026", "beauty", "https://www.nykaa.com"),
        ("NYKAA50", "Flat Rs. 500 Off", "Rs. 500", "Rs. 3000", "31 Mar 2026", "beauty", "https://www.nykaa.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in nykaa_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Nykaa",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Swiggy Coupons (Food Delivery)
    swiggy_coupons = [
        ("SWIGGY100", "Rs. 100 Off on Orders above Rs. 300", "Rs. 100", "Rs. 300", "28 Feb 2026", "food", "https://www.swiggy.com"),
        ("SWIGGY50", "Flat Rs. 50 Off", "Rs. 50", "Rs. 200", "15 Mar 2026", "food", "https://www.swiggy.com"),
        ("FIRSTORDER", "30% Off First Order", "30%", "Rs. 250", "31 Dec 2026", "food", "https://www.swiggy.com"),
        ("SWIGGY200", "Rs. 200 Off on Large Orders", "Rs. 200", "Rs. 800", "20 Mar 2026", "food", "https://www.swiggy.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in swiggy_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Swiggy",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Zomato Coupons (Food Delivery)
    zomato_coupons = [
        ("ZOMATO50", "Flat Rs. 50 Off", "Rs. 50", "Rs. 200", "28 Feb 2026", "food", "https://www.zomato.com"),
        ("ZOMATO100", "Rs. 100 Off on Orders above Rs. 400", "Rs. 100", "Rs. 400", "15 Mar 2026", "food", "https://www.zomato.com"),
        ("ZOMATO30", "30% Off on Orders above Rs. 500", "30%", "Rs. 500", "20 Mar 2026", "food", "https://www.zomato.com"),
        ("FIRSTZOMATO", "40% Off First Three Orders", "40%", "Rs. 300", "31 Dec 2026", "food", "https://www.zomato.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in zomato_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Zomato",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Reliance Digital Coupons
    reliance_coupons = [
        ("RELIANCE15", "15% Off on Electronics", "15%", "Rs. 5000", "25 Mar 2026", "electronics", "https://www.reliancedigital.in"),
        ("RELIANCE25", "25% Off on TV & Appliances", "25%", "Rs. 15000", "20 Mar 2026", "electronics", "https://www.reliancedigital.in"),
        ("BIG2500", "Rs. 2500 Off on Laptops", "Rs. 2500", "Rs. 25000", "31 Mar 2026", "computers", "https://www.reliancedigital.in"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in reliance_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Reliance Digital",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Tata Cliq Coupons
    tata_coupons = [
        ("TATA20", "20% Off on All Products", "20%", "Rs. 2000", "28 Feb 2026", "all", "https://www.tatacliq.com"),
        ("TATA500", "Flat Rs. 500 Off", "Rs. 500", "Rs. 3000", "15 Mar 2026", "all", "https://www.tatacliq.com"),
        ("TATA1000", "Rs. 1000 Off on Fashion", "Rs. 1000", "Rs. 5000", "20 Mar 2026", "fashion", "https://www.tatacliq.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in tata_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Tata Cliq",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Myntra was already included above
    # Add Shoppers Stop
    shoppers_coupons = [
        ("SHOPPER30", "30% Off on Fashion", "30%", "Rs. 2500", "25 Mar 2026", "fashion", "https://www.shoppersstop.com"),
        ("NEWSHOP50", "Rs. 500 Off for New Users", "Rs. 500", "Rs. 2000", "31 Dec 2026", "all", "https://www.shoppersstop.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in shoppers_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Shoppers Stop",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    # Add Pepperfry
    pepperfry_coupons = [
        ("PEPPER20", "20% Off on Furniture", "20%", "Rs. 5000", "20 Mar 2026", "home", "https://www.pepperfry.com"),
        ("PEPPER15", "15% Off on Home Decor", "15%", "Rs. 2000", "15 Mar 2026", "home", "https://www.pepperfry.com"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in pepperfry_coupons:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="Pepperfry",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    return coupons


def generate_youtube_deals() -> List[Coupon]:
    """Generate deals from YouTube shopping/affiliates"""
    coupons = []
    timestamp = datetime.now().isoformat()
    
    # YouTube Shopping Deals (simulated - in real app would scrape YouTube Shopping)
    youtube_deals = [
        # Tech deals often featured on YouTube
        ("YTECH50", "50% Off on Tech Gadgets - YouTube Special", "50%", "Rs. 2000", "15 Mar 2026", "electronics", "https://www.youtube.com/feed/shopping"),
        ("YTFASH30", "30% Off on Fashion - Top YouTubers Pick", "30%", "Rs. 1500", "20 Mar 2026", "fashion", "https://www.youtube.com/feed/shopping"),
        ("YTBEAUTY40", "40% Off on Beauty Products - YouTube Creator Pick", "40%", "Rs. 1000", "25 Mar 2026", "beauty", "https://www.youtube.com/feed/shopping"),
        ("YTHOME35", "35% Off on Home Decor - Home Tour Favorite", "35%", "Rs. 2500", "31 Mar 2026", "home", "https://www.youtube.com/feed/shopping"),
        ("YTGAMING25", "25% Off on Gaming Gear - Streamer Recommended", "25%", "Rs. 3000", "28 Feb 2026", "gaming", "https://www.youtube.com/feed/shopping"),
        ("YTFITNESS30", "30% Off on Fitness Equipment - Workout Vlog Favorite", "30%", "Rs. 2000", "15 Mar 2026", "fitness", "https://www.youtube.com/feed/shopping"),
        ("YTMUSIC20", "20% Off on Music Instruments - Music Channel Pick", "20%", "Rs. 1500", "20 Mar 2026", "music", "https://www.youtube.com/feed/shopping"),
        ("YTBOOKS25", "25% Off on Books - BookTuber Recommendation", "25%", "Rs. 500", "25 Mar 2026", "books", "https://www.youtube.com/feed/shopping"),
    ]
    
    for code, desc, disc, min_order, exp, cat, url in youtube_deals:
        coupons.append(Coupon(
            coupon_code=code,
            description=desc,
            discount=disc,
            min_order=min_order,
            expires=exp,
            product_url=url,
            source="YouTube Shopping",
            category=cat,
            city="all",
            timestamp=timestamp
        ))
    
    return coupons


def main(city: str = None):
    """Main entry point - generates coupons from e-commerce, local restaurants & YouTube"""
    print("=" * 50)
    print("Saasta Deals - Coupons Aggregator")
    print("=" * 50)
    
    storage = CouponStorage()
    
    # Generate e-commerce coupons (all websites)
    coupons = generate_coupons()
    
    # Generate YouTube Shopping deals
    youtube_coupons = generate_youtube_deals()
    coupons.extend(youtube_coupons)
    print(f"\nAdded {len(youtube_coupons)} YouTube Shopping deals")
    
    # Generate local restaurant coupons if city specified
    if city:
        city_coupons = generate_restaurant_coupons(city)
        coupons.extend(city_coupons)
        print(f"\nAdded {len(city_coupons)} local restaurant deals for {city}")
    else:
        # Add restaurant coupons for all major cities
        all_cities = ["Hyderabad", "Bangalore", "Mumbai", "Delhi", "Chennai", "Pune", "Kolkata", "Chandigarh", "Ahmedabad", "Jaipur"]
        for c in all_cities:
            city_coupons = generate_restaurant_coupons(c)
            coupons.extend(city_coupons)
    
    storage.save_coupons(coupons)
    
    print(f"\nGenerated {len(coupons)} coupons from multiple websites")
    print("\nCoupons by source:")
    sources = {}
    for c in coupons:
        sources[c.source] = sources.get(c.source, 0) + 1
    for src, count in sorted(sources.items()):
        print(f"  {src}: {count} coupons")
    
    # Count by city
    print("\nLocal restaurant deals by city:")
    cities = {}
    for c in coupons:
        if c.city != "all":
            cities[c.city] = cities.get(c.city, 0) + 1
    for ct, count in sorted(cities.items()):
        print(f"  {ct}: {count} deals")
    
    print(f"\nOpen http://localhost:5001 in browser")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Saasta Deals - Coupons Aggregator")
    parser.add_argument("--city", type=str, default=None, help="City for local restaurant deals")
    args = parser.parse_args()
    main(args.city)
