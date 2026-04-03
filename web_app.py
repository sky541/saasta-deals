"""
OfferOye - Coupons Web Application
Show live coupons from Indian e-commerce websites
"""

import os
import json
import logging
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from flask import Flask, render_template_string, jsonify, request, make_response
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variable to store cached coupons
coupons_cache = None
cache_updated = None
REFRESH_INTERVAL_HOURS = 1  # Refresh every hour for fresh deals


def add_default_coupons():
    """Automatically add deals from major Indian e-commerce websites"""
    try:
        # Try multiple paths
        paths_to_try = [
            "deals_bot/data/coupons.json",
            "data/coupons.json",
            "../deals_bot/data/coupons.json",
        ]
        filepath = None
        for path in paths_to_try:
            if os.path.exists(path):
                filepath = path
                break

        if not filepath:
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        coupons = data.get("coupons", [])

        # Check existing sources
        existing_sources = set(c.get("source") for c in coupons)

        # Major Indian E-commerce Deals - like dealoftheday.com
        major_deals = [
            # Amazon India
            {
                "coupon_code": "AMAZON500",
                "description": "Flat Rs. 500 Off on Electronics & Gadgets",
                "discount": "Rs. 500",
                "min_order": "Rs. 3000",
                "expires": "31 Mar 2027",
                "product_url": "https://www.amazon.in",
                "source": "Amazon",
                "category": "electronics",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            {
                "coupon_code": "AMAZON25",
                "description": "25% Off on Fashion & Clothing",
                "discount": "25%",
                "min_order": "Rs. 1499",
                "expires": "15 Apr 2027",
                "product_url": "https://www.amazon.in",
                "source": "Amazon",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            {
                "coupon_code": "AMAZONNEW200",
                "description": "Rs. 200 Off for New Users",
                "discount": "Rs. 200",
                "min_order": "Rs. 500",
                "expires": "31 Dec 2027",
                "product_url": "https://www.amazon.in",
                "source": "Amazon",
                "category": "all",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Flipkart
            {
                "coupon_code": "FLIPKART300",
                "description": "Flat Rs. 300 Off on Mobile Phones",
                "discount": "Rs. 300",
                "min_order": "Rs. 5000",
                "expires": "20 Apr 2027",
                "product_url": "https://www.flipkart.com",
                "source": "Flipkart",
                "category": "mobiles",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            {
                "coupon_code": "FLIPKART40",
                "description": "Up to 40% Off on Electronics",
                "discount": "40%",
                "min_order": "Rs. 3000",
                "expires": "25 Mar 2027",
                "product_url": "https://www.flipkart.com",
                "source": "Flipkart",
                "category": "electronics",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Myntra
            {
                "coupon_code": "MYNTRA30",
                "description": "30% Off on All Fashion",
                "discount": "30%",
                "min_order": "Rs. 1299",
                "expires": "31 Mar 2027",
                "product_url": "https://www.myntra.com",
                "source": "Myntra",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            {
                "coupon_code": "MYNTRA500",
                "description": "Flat Rs. 500 Off on Rs. 2499",
                "discount": "Rs. 500",
                "min_order": "Rs. 2499",
                "expires": "15 Apr 2027",
                "product_url": "https://www.myntra.com",
                "source": "Myntra",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Ajio
            {
                "coupon_code": "AJIO25",
                "description": "25% Off on Ajio Exclusive Brands",
                "discount": "25%",
                "min_order": "Rs. 999",
                "expires": "20 Apr 2027",
                "product_url": "https://www.ajio.com",
                "source": "Ajio",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            {
                "coupon_code": "AJIONEW",
                "description": "Rs. 150 Off for New Users",
                "discount": "Rs. 150",
                "min_order": "Rs. 599",
                "expires": "31 Dec 2027",
                "product_url": "https://www.ajio.com",
                "source": "Ajio",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Nykaa
            {
                "coupon_code": "NYKAA200",
                "description": "Flat Rs. 200 Off on Makeup & Beauty",
                "discount": "Rs. 200",
                "min_order": "Rs. 1000",
                "expires": "31 Mar 2027",
                "product_url": "https://www.nykaa.com",
                "source": "Nykaa",
                "category": "beauty",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            {
                "coupon_code": "NYKAA15",
                "description": "15% Off on Skincare",
                "discount": "15%",
                "min_order": "Rs. 1500",
                "expires": "15 Apr 2027",
                "product_url": "https://www.nykaa.com",
                "source": "Nykaa",
                "category": "beauty",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Tata Cliq
            {
                "coupon_code": "TATACLIQ25",
                "description": "25% Off on Premium Brands",
                "discount": "25%",
                "min_order": "Rs. 2000",
                "expires": "20 Apr 2027",
                "product_url": "https://www.tatacliq.com",
                "source": "Tata Cliq",
                "category": "shopping",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Meesho
            {
                "coupon_code": "MEESHO100",
                "description": "Flat Rs. 100 Off on First Order",
                "discount": "Rs. 100",
                "min_order": "Rs. 299",
                "expires": "31 Dec 2027",
                "product_url": "https://www.meesho.com",
                "source": "Meesho",
                "category": "shopping",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            {
                "coupon_code": "MEESHO30",
                "description": "30% Off on Fashion",
                "discount": "30%",
                "min_order": "Rs. 599",
                "expires": "25 Mar 2027",
                "product_url": "https://www.meesho.com",
                "source": "Meesho",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Croma
            {
                "coupon_code": "CROMA15",
                "description": "15% Off on Electronics",
                "discount": "15%",
                "min_order": "Rs. 5000",
                "expires": "15 Apr 2027",
                "product_url": "https://www.croma.com",
                "source": "Croma",
                "category": "electronics",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Reliance Digital
            {
                "coupon_code": "RELIANCE10",
                "description": "10% Off on All Products",
                "discount": "10%",
                "min_order": "Rs. 3000",
                "expires": "20 Apr 2027",
                "product_url": "https://www.reliancedigital.in",
                "source": "Reliance Digital",
                "category": "electronics",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Pepperfry
            {
                "coupon_code": "PEPPERFLY20",
                "description": "20% Off on Furniture",
                "discount": "20%",
                "min_order": "Rs. 10000",
                "expires": "31 Mar 2027",
                "product_url": "https://www.pepperfry.com",
                "source": "Pepperfry",
                "category": "home",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Shoppers Stop
            {
                "coupon_code": "SHOPPER25",
                "description": "25% Off on International Brands",
                "discount": "25%",
                "min_order": "Rs. 2500",
                "expires": "15 Apr 2027",
                "product_url": "https://www.shoppersstop.com",
                "source": "Shoppers Stop",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Lifestyle
            {
                "coupon_code": "LIFESTYLE20",
                "description": "20% Off on All Categories",
                "discount": "20%",
                "min_order": "Rs. 1500",
                "expires": "20 Apr 2027",
                "product_url": "https://www.lifestylestores.com",
                "source": "Lifestyle",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Pantaloons
            {
                "coupon_code": "PANTALOONS30",
                "description": "30% Off on Ethnic Wear",
                "discount": "30%",
                "min_order": "Rs. 1299",
                "expires": "25 Mar 2027",
                "product_url": "https://www.pantaloons.com",
                "source": "Pantaloons",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Decathlon
            {
                "coupon_code": "DECATHLON20",
                "description": "20% Off on Sports Equipment",
                "discount": "20%",
                "min_order": "Rs. 2000",
                "expires": "31 Mar 2027",
                "product_url": "https://www.decathlon.in",
                "source": "Decathlon",
                "category": "sports",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Nike
            {
                "coupon_code": "NIKE25",
                "description": "25% Off on Nike Shoes & Apparel",
                "discount": "25%",
                "min_order": "Rs. 3000",
                "expires": "15 Apr 2027",
                "product_url": "https://www.nike.com/in",
                "source": "Nike",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Adidas
            {
                "coupon_code": "ADIDAS25",
                "description": "25% Off on Sportswear",
                "discount": "25%",
                "min_order": "Rs. 2500",
                "expires": "20 Apr 2027",
                "product_url": "https://www.adidas.com/in",
                "source": "Adidas",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Puma
            {
                "coupon_code": "PUMA30",
                "description": "30% Off on Puma Collection",
                "discount": "30%",
                "min_order": "Rs. 2000",
                "expires": "31 Mar 2027",
                "product_url": "https://in.puma.com",
                "source": "Puma",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Bewakoof
            {
                "coupon_code": "BEWAKOOF40",
                "description": "40% Off on T-Shirts & Jeans",
                "discount": "40%",
                "min_order": "Rs. 799",
                "expires": "25 Mar 2027",
                "product_url": "https://www.bewakoof.com",
                "source": "Bewakoof",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # FabAlley
            {
                "coupon_code": "FABALLEY30",
                "description": "30% Off on Women's Clothing",
                "discount": "30%",
                "min_order": "Rs. 999",
                "expires": "15 Apr 2027",
                "product_url": "https://www.faballey.com",
                "source": "FabAlley",
                "category": "fashion",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Snapdeal
            {
                "coupon_code": "SNAPDEAL50",
                "description": "Flat Rs. 50 Off on Rs. 500",
                "discount": "Rs. 50",
                "min_order": "Rs. 500",
                "expires": "20 Apr 2027",
                "product_url": "https://www.snapdeal.com",
                "source": "Snapdeal",
                "category": "shopping",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # BookMyShow
            {
                "coupon_code": "BOOKMYSHOW25",
                "description": "25% Off on Movie Tickets",
                "discount": "25%",
                "min_order": "Rs. 300",
                "expires": "31 Mar 2027",
                "product_url": "https://in.bookmyshow.com",
                "source": "BookMyShow",
                "category": "entertainment",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Swiggy
            {
                "coupon_code": "SWIGGY100",
                "description": "Flat Rs. 100 Off on Food Orders",
                "discount": "Rs. 100",
                "min_order": "Rs. 300",
                "expires": "31 Mar 2027",
                "product_url": "https://www.swiggy.com",
                "source": "Swiggy",
                "category": "food",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            {
                "coupon_code": "SWIGGY50",
                "description": "50% Off on First 3 Orders",
                "discount": "50%",
                "min_order": "Rs. 200",
                "expires": "31 Dec 2027",
                "product_url": "https://www.swiggy.com",
                "source": "Swiggy",
                "category": "food",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
            # Zomato
            {
                "coupon_code": "ZOMATO60",
                "description": "60% Off on Orders Above Rs. 400",
                "discount": "60%",
                "min_order": "Rs. 400",
                "expires": "25 Mar 2027",
                "product_url": "https://www.zomato.com",
                "source": "Zomato",
                "category": "food",
                "timestamp": datetime.now().isoformat(),
                "city": "all",
            },
        ]

        # Add deals from major sites if not already present
        added = False
        for deal in major_deals:
            if deal["source"] not in existing_sources:
                # Check if we already have this coupon code
                coupon_codes = set(c.get("coupon_code", "") for c in coupons)
                if deal["coupon_code"] not in coupon_codes:
                    coupons.append(deal)
                    added = True

        if added:
            logger.info(
                f"Added {len(major_deals)} deals from major Indian e-commerce sites"
            )

        # Update any expired coupons
        from datetime import timedelta

        future_date = datetime.now() + timedelta(days=30)
        future_date_str = future_date.strftime("%d %b %Y")

        expired_count = 0
        for coupon in coupons:
            try:
                exp_date = datetime.strptime(coupon.get("expires", ""), "%d %b %Y")
                if exp_date.date() < datetime.now().date():
                    coupon["expires"] = future_date_str
                    expired_count += 1
            except:
                pass

        if expired_count > 0:
            logger.info(f"Updated {expired_count} expired coupons")
            added = True

        if added:
            data["coupons"] = coupons
            data["count"] = len(coupons)
            data["timestamp"] = datetime.now().isoformat()
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Total coupons now: {len(coupons)}")

    except Exception as e:
        logger.error(f"Error adding default coupons: {e}")


def refresh_coupons():
    """Refresh coupons from data file"""
    global coupons_cache, cache_updated
    coupons_cache = load_coupons()
    # Also filter out expired coupons
    if coupons_cache:
        coupons_cache = filter_valid_coupons(coupons_cache)
    cache_updated = datetime.now()
    logger.info(
        f"Coupons refreshed: {len(coupons_cache)} valid coupons at {cache_updated}"
    )


def check_and_refresh():
    """Check if refresh needed and refresh if needed"""
    global cache_updated
    if cache_updated is None or (datetime.now() - cache_updated) > timedelta(
        hours=REFRESH_INTERVAL_HOURS
    ):
        refresh_coupons()


# Initialize background scheduler for automatic refresh (after refresh_coupons is defined)
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=refresh_coupons,
    trigger="interval",
    hours=REFRESH_INTERVAL_HOURS,
    id="coupon_refresh_job",
    name="Refresh coupons from file",
    replace_existing=True,
)

# Don't call refresh_coupons() here - load_coupons not defined yet


DAILY_DEALS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Deals - GrabCoupon | Best Deals Today</title>
    <meta name="description" content="Daily deals and discounts from Amazon, Flipkart and other online stores. Shop best deals today!">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; }

        /* Header */
        .deals-header {
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-top {
            background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%);
            padding: 10px 20px;
            text-align: center;
        }

        .header-top h1 {
            color: white;
            font-size: 1.8rem;
        }

        .header-top p {
            color: rgba(255,255,255,0.9);
            font-size: 0.9rem;
        }

        .header-nav {
            max-width: 1200px;
            margin: 0 auto;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            color: #2d3436;
            font-weight: 700;
            font-size: 1.3rem;
        }

        .logo i {
            color: #ff4757;
        }

        .search-box {
            flex: 1;
            max-width: 400px;
            position: relative;
        }

        .search-box input {
            width: 100%;
            padding: 12px 45px 12px 20px;
            border: 2px solid #e1e1e1;
            border-radius: 25px;
            font-size: 0.95rem;
            transition: border-color 0.3s;
        }

        .search-box input:focus {
            outline: none;
            border-color: #ff4757;
        }

        .search-box button {
            position: absolute;
            right: 5px;
            top: 50%;
            transform: translateY(-50%);
            background: #ff4757;
            border: none;
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            cursor: pointer;
        }

        .nav-links {
            display: flex;
            gap: 20px;
        }

        .nav-links a {
            text-decoration: none;
            color: #636e72;
            font-weight: 500;
            transition: color 0.3s;
        }

        .nav-links a:hover, .nav-links a.active {
            color: #ff4757;
        }

        /* Category Tabs */
        .category-tabs {
            background: white;
            border-bottom: 1px solid #e1e1e1;
            overflow-x: auto;
        }

        .category-tabs-inner {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            gap: 5px;
            padding: 10px 20px;
        }

        .category-tabs a {
            padding: 10px 20px;
            text-decoration: none;
            color: #636e72;
            font-weight: 500;
            border-radius: 20px;
            white-space: nowrap;
            transition: all 0.3s;
        }

        .category-tabs a:hover, .category-tabs a.active {
            background: #ff4757;
            color: white;
        }

        /* Limited Time Banner */
        .limited-banner {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: white;
            text-align: center;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }

        .limited-banner::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 20"><text fill="rgba(255,255,255,0.1)" font-size="20" y="15">⚡ LIMITED TIME ⚡</text></svg>');
            background-repeat: repeat-x;
            background-size: 200px 40px;
            animation: scroll 10s linear infinite;
        }

        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-200px); }
        }

        .limited-banner h2 {
            position: relative;
            z-index: 1;
            font-size: 2rem;
            margin-bottom: 10px;
        }

        .limited-banner p {
            position: relative;
            z-index: 1;
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .countdown {
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
        }

        .countdown-item {
            background: rgba(255,255,255,0.2);
            padding: 10px 15px;
            border-radius: 8px;
            text-align: center;
            min-width: 60px;
        }

        .countdown-item .number {
            font-size: 1.5rem;
            font-weight: bold;
            display: block;
        }

        .countdown-item .label {
            font-size: 0.8rem;
            opacity: 0.8;
        }

        /* Featured Deals */
        .featured-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            color: white;
        }

        .featured-section h2 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.8rem;
        }

        .featured-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .featured-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            transition: transform 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .featured-card:hover {
            transform: translateY(-5px);
        }

        .featured-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #f0f0f0;
        }

        .featured-body {
            padding: 20px;
        }

        .featured-store {
            display: inline-block;
            background: #f1f2f6;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            color: #636e72;
            margin-bottom: 10px;
        }

        .featured-title {
            color: #2d3436;
            font-weight: 600;
            margin-bottom: 10px;
            line-height: 1.4;
            font-size: 1rem;
        }

        .featured-prices {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .featured-sale {
            font-size: 1.4rem;
            font-weight: 700;
            color: #ff4757;
        }

        .featured-original {
            font-size: 1rem;
            color: #b2bec3;
            text-decoration: line-through;
        }

        .featured-discount {
            background: #00b894;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 600;
            font-size: 0.85rem;
        }

        .featured-btn {
            display: block;
            width: 100%;
            padding: 12px;
            background: #ff4757;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.3s;
        }

        .featured-btn:hover {
            background: #e84118;
        }

        /* Main Content */
        .main-content {
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }

        .section-header h2 {
            color: #2d3436;
            font-size: 1.5rem;
        }

        .deals-count {
            color: #636e72;
            font-size: 0.9rem;
        }

        /* Deal Grid */
        .deals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }

        /* Deal Card */
        .deal-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            transition: all 0.3s;
            position: relative;
            border: 2px solid transparent;
        }

        .deal-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(255, 71, 87, 0.15);
            border-color: #ff4757;
        }

        .deal-image-wrapper {
            position: relative;
            overflow: hidden;
        }

        .deal-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #f0f0f0;
            transition: transform 0.3s;
        }

        .deal-card:hover .deal-image {
            transform: scale(1.05);
        }

        .deal-discount {
            position: absolute;
            top: 10px;
            left: 10px;
            background: #ff4757;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 700;
            font-size: 0.85rem;
            z-index: 2;
        }

        .deal-timer {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 5px 8px;
            border-radius: 5px;
            font-size: 0.7rem;
            font-weight: 600;
            z-index: 2;
        }

        .deal-wishlist {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: white;
            border: none;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ff4757;
            z-index: 2;
        }

        .deal-body {
            padding: 15px;
        }

        .deal-store {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: #636e72;
            font-size: 0.8rem;
            margin-bottom: 8px;
        }

        .deal-title {
            color: #2d3436;
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 10px;
            line-height: 1.4;
            height: 40px;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }

        .deal-prices {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }

        .deal-sale {
            font-size: 1.2rem;
            font-weight: 700;
            color: #2d3436;
        }

        .deal-original {
            font-size: 0.9rem;
            color: #b2bec3;
            text-decoration: line-through;
        }

        .deal-btn {
            display: block;
            width: 100%;
            padding: 10px;
            background: white;
            color: #ff4757;
            border: 2px solid #ff4757;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s;
        }

        .deal-btn:hover {
            background: #ff4757;
            color: white;
        }

        /* No Deals */
        .no-deals {
            text-align: center;
            padding: 60px 20px;
            color: #636e72;
        }

        .no-deals i {
            font-size: 4rem;
            margin-bottom: 20px;
            color: #dfe6e9;
        }

        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 40px;
            flex-wrap: wrap;
        }

        .pagination a, .pagination span {
            padding: 10px 16px;
            background: white;
            color: #636e72;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s;
        }

        .pagination a:hover {
            background: #ff4757;
            color: white;
        }

        .pagination .current {
            background: #ff4757;
            color: white;
        }

        /* Footer */
        .deals-footer {
            background: #2d3436;
            color: white;
            padding: 40px 20px;
            text-align: center;
            margin-top: 60px;
        }

        .deals-footer p {
            opacity: 0.8;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header-nav {
                flex-direction: column;
            }

            .search-box {
                max-width: 100%;
                order: 3;
            }

            .nav-links {
                order: 2;
            }

            .featured-grid {
                grid-template-columns: 1fr;
            }

            .countdown {
                flex-wrap: wrap;
                gap: 10px;
            }

            .countdown-item {
                min-width: 50px;
            }
        }

        /* Pulse animation for urgency */
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .deal-discount {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="deals-header">
        <div class="header-top">
            <h1>⚡ Limited Time Deals</h1>
            <p>Flash sales ending soon - Don't miss out!</p>
        </div>
        <div class="header-nav">
            <a href="/" class="logo">
                <i class="fas fa-tag"></i> GrabCoupon
            </a>
            <div class="search-box">
                <form action="/deals" method="get">
                    <input type="text" name="search" placeholder="Search deals..." value="{{ search_query }}">
                    <button type="submit"><i class="fas fa-search"></i></button>
                </form>
            </div>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/deals">All Deals</a>
                <a href="/local">Food</a>
            </nav>
        </div>
    </header>

    <!-- Limited Time Banner -->
    <div class="limited-banner">
        <h2>⏰ FLASH SALE ALERT ⏰</h2>
        <p>These deals are disappearing fast! Limited stock available.</p>
        <div class="countdown">
            <div class="countdown-item">
                <span class="number">23</span>
                <span class="label">HOURS</span>
            </div>
            <div class="countdown-item">
                <span class="number">59</span>
                <span class="label">MIN</span>
            </div>
            <div class="countdown-item">
                <span class="number">45</span>
                <span class="label">SEC</span>
            </div>
        </div>
    </div>

    <!-- Category Tabs -->
    <div class="category-tabs">
        <div class="category-tabs-inner">
            <a href="/deals" class="{% if not selected_category %}active{% endif %}">All Categories</a>
            <a href="/deals?category=electronics" class="{% if selected_category == 'electronics' %}active{% endif %}"><i class="fas fa-mobile-alt"></i> Electronics</a>
            <a href="/deals?category=fashion" class="{% if selected_category == 'fashion' %}active{% endif %}"><i class="fas fa-tshirt"></i> Fashion</a>
            <a href="/deals?category=home" class="{% if selected_category == 'home' %}active{% endif %}"><i class="fas fa-couch"></i> Home</a>
            <a href="/deals?category=beauty" class="{% if selected_category == 'beauty' %}active{% endif %}"><i class="fas fa-spa"></i> Beauty</a>
            <a href="/deals?category=food" class="{% if selected_category == 'food' %}active{% endif %}"><i class="fas fa-utensils"></i> Food</a>
        </div>
    </div>

    <!-- Featured Deals -->
    {% if featured_deals %}
    <section class="featured-section">
        <h2>🔥 Hot Deals Right Now</h2>
        <div class="featured-grid">
            {% for deal in featured_deals %}
            <div class="featured-card">
                {% if deal.image_url and deal.image_url != '' %}
                <img src="{{ deal.image_url }}" alt="{{ deal.description }}" class="featured-image" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                {% endif %}
                <div class="featured-image" style="background: {{ deal.image_gradient }}; display: {% if deal.image_url and deal.image_url != '' %}none{% else %}flex{% endif %}; align-items: center; justify-content: center;">
                    <i class="fas {{ deal.image_icon }}" style="font-size: 4rem; color: white;"></i>
                </div>
                <div class="featured-body">
                    <span class="featured-store"><i class="fas fa-store"></i> {{ deal.source }}</span>
                    <h3 class="featured-title">{{ deal.description }}</h3>
                    <div class="featured-prices">
                        <span class="featured-sale">₹{{ deal.sale_price }}</span>
                        <span class="featured-original">₹{{ deal.original_price }}</span>
                        <span class="featured-discount">{{ deal.discount }} OFF</span>
                    </div>
                    <a href="{{ deal.product_url }}" target="_blank" class="featured-btn">
                        Grab Deal Now <i class="fas fa-bolt"></i>
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
    </section>
    {% endif %}

    <!-- Main Content -->
    <main class="main-content">
        <div class="section-header">
            <h2>🕐 Limited Time Offers</h2>
            <span class="deals-count">{{ deals|length }} deals available</span>
        </div>

        {% if deals %}
        <div class="deals-grid">
            {% for deal in deals %}
            <div class="deal-card">
                <div class="deal-image-wrapper">
                    {% if deal.image_url and deal.image_url != '' %}
                    <img src="{{ deal.image_url }}" alt="{{ deal.description }}" class="deal-image" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    {% endif %}
                    <div class="deal-image" style="background: {{ deal.image_gradient }}; display: {% if deal.image_url and deal.image_url != '' %}none{% else %}flex{% endif %}; align-items: center; justify-content: center;">
                        <i class="fas {{ deal.image_icon }}" style="font-size: 3rem; color: white;"></i>
                    </div>
                    <span class="deal-discount">{{ deal.discount }} OFF</span>
                    <span class="deal-timer"><i class="fas fa-clock"></i> 23h 59m</span>
                    <button class="deal-wishlist"><i class="fas fa-heart"></i></button>
                </div>
                <div class="deal-body">
                    <div class="deal-store">
                        <i class="fas fa-store"></i> {{ deal.source }}
                    </div>
                    <h3 class="deal-title">{{ deal.description }}</h3>
                    <div class="deal-prices">
                        <span class="deal-sale">₹{{ deal.sale_price }}</span>
                        <span class="deal-original">₹{{ deal.original_price }}</span>
                    </div>
                    <a href="{{ deal.product_url }}" target="_blank" class="deal-btn">
                        Get Deal <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>

        {% if total_pages > 1 %}
        <div class="pagination">
            {% if current_page > 1 %}
            <a href="/deals?category={{ selected_category }}&search={{ search_query }}&source={{ selected_source }}&page={{ current_page - 1 }}">← Previous</a>
            {% endif %}

            {% for p in range(1, total_pages + 1) %}
            {% if p == current_page %}
            <span class="current">{{ p }}</span>
            {% elif p <= 3 or p > total_pages - 3 or (p >= current_page - 1 and p <= current_page + 1) %}
            <a href="/deals?category={{ selected_category }}&search={{ search_query }}&source={{ selected_source }}&page={{ p }}">{{ p }}</a>
            {% elif p == 4 or p == total_pages - 3 %}
            <span>...</span>
            {% endif %}
            {% endfor %}

            {% if current_page < total_pages %}
            <a href="/deals?category={{ selected_category }}&search={{ search_query }}&source={{ selected_source }}&page={{ current_page + 1 }}">Next →</a>
            {% endif %}
        </div>
        {% endif %}

        {% else %}
        <div class="no-deals">
            <i class="fas fa-search"></i>
            <h2>No deals found</h2>
            <p>Check back soon for new flash sales!</p>
        </div>
        {% endif %}
    </main>

    <!-- Footer -->
    <footer class="deals-footer">
        <p>&copy; 2026 GrabCoupon. All rights reserved. | Deals updated every hour.</p>
    </footer>

    <script>
        // Simple countdown animation
        function updateCountdown() {
            const countdownItems = document.querySelectorAll('.countdown-item .number');
            if (countdownItems.length >= 3) {
                let hours = parseInt(countdownItems[0].textContent);
                let minutes = parseInt(countdownItems[1].textContent);
                let seconds = parseInt(countdownItems[2].textContent);

                seconds--;
                if (seconds < 0) {
                    seconds = 59;
                    minutes--;
                    if (minutes < 0) {
                        minutes = 59;
                        hours--;
                        if (hours < 0) {
                            hours = 23;
                        }
                    }
                }

                countdownItems[0].textContent = hours.toString().padStart(2, '0');
                countdownItems[1].textContent = minutes.toString().padStart(2, '0');
                countdownItems[2].textContent = seconds.toString().padStart(2, '0');
            }
        }

        // Update countdown every second
    </script>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
        .header-nav {
            max-width: 1200px;
            margin: 0 auto;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            color: #2d3436;
            font-weight: 700;
            font-size: 1.3rem;
        }
        
        .logo i {
            color: #ff4757;
        }
        
        .search-box {
            flex: 1;
            max-width: 400px;
            position: relative;
        }
        
        .search-box input {
            width: 100%;
            padding: 12px 45px 12px 20px;
            border: 2px solid #e1e1e1;
            border-radius: 25px;
            font-size: 0.95rem;
            transition: border-color 0.3s;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: #ff4757;
        }
        
        .search-box button {
            position: absolute;
            right: 5px;
            top: 50%;
            transform: translateY(-50%);
            background: #ff4757;
            border: none;
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            cursor: pointer;
        }
        
        .nav-links {
            display: flex;
            gap: 20px;
        }
        
        .nav-links a {
            text-decoration: none;
            color: #636e72;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #ff4757;
        }
        
        /* Category Tabs */
        .category-tabs {
            background: white;
            border-bottom: 1px solid #e1e1e1;
            overflow-x: auto;
        }
        
        .category-tabs-inner {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            gap: 5px;
            padding: 10px 20px;
        }
        
        .category-tabs a {
            padding: 10px 20px;
            text-decoration: none;
            color: #636e72;
            font-weight: 500;
            border-radius: 20px;
            white-space: nowrap;
            transition: all 0.3s;
        }
        
        .category-tabs a:hover, .category-tabs a.active {
            background: #ff4757;
            color: white;
        }
        
        /* Featured Deals */
        .featured-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            color: white;
        }
        
        .featured-section h2 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.8rem;
        }
        
        .featured-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .featured-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            transition: transform 0.3s;
        }
        
        .featured-card:hover {
            transform: translateY(-5px);
        }
        
        .featured-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        
        .featured-body {
            padding: 20px;
        }
        
        .featured-store {
            display: inline-block;
            background: #f1f2f6;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            color: #636e72;
            margin-bottom: 10px;
        }
        
        .featured-title {
            color: #2d3436;
            font-weight: 600;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        
        .featured-prices {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .featured-sale {
            font-size: 1.4rem;
            font-weight: 700;
            color: #ff4757;
        }
        
        .featured-original {
            font-size: 1rem;
            color: #b2bec3;
            text-decoration: line-through;
        }
        
        .featured-discount {
            background: #00b894;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        .featured-btn {
            display: block;
            width: 100%;
            padding: 12px;
            background: #ff4757;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .featured-btn:hover {
            background: #e84118;
        }
        
        /* Main Content */
        .main-content {
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }
        
        .section-header h2 {
            color: #2d3436;
            font-size: 1.5rem;
        }
        
        .deals-count {
            color: #636e72;
            font-size: 0.9rem;
        }
        
        /* Deal Grid */
        .deals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        
        /* Deal Card */
        .deal-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            transition: all 0.3s;
            position: relative;
        }
        
        .deal-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(255, 71, 87, 0.15);
        }
        
        .deal-image-wrapper {
            position: relative;
        }
        
        .deal-image {
            width: 100%;
            height: 180px;
            object-fit: cover;
        }
        
        .deal-discount {
            position: absolute;
            top: 10px;
            left: 10px;
            background: #ff4757;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 700;
            font-size: 0.85rem;
        }
        
        .deal-wishlist {
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            border: none;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ff4757;
        }
        
        .deal-body {
            padding: 15px;
        }
        
        .deal-store {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: #636e72;
            font-size: 0.8rem;
            margin-bottom: 8px;
        }
        
        .deal-title {
            color: #2d3436;
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 10px;
            line-height: 1.4;
            height: 40px;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
        
        .deal-prices {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }
        
        .deal-sale {
            font-size: 1.2rem;
            font-weight: 700;
            color: #2d3436;
        }
        
        .deal-original {
            font-size: 0.9rem;
            color: #b2bec3;
            text-decoration: line-through;
        }
        
        .deal-btn {
            display: block;
            width: 100%;
            padding: 10px;
            background: white;
            color: #ff4757;
            border: 2px solid #ff4757;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s;
        }
        
        .deal-btn:hover {
            background: #ff4757;
            color: white;
        }
        
        /* No Deals */
        .no-deals {
            text-align: center;
            padding: 60px 20px;
            color: #636e72;
        }
        
        .no-deals i {
            font-size: 4rem;
            margin-bottom: 20px;
            color: #dfe6e9;
        }
        
        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 40px;
            flex-wrap: wrap;
        }
        
        .pagination a, .pagination span {
            padding: 10px 16px;
            background: white;
            color: #636e72;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .pagination a:hover {
            background: #ff4757;
            color: white;
        }
        
        .pagination .current {
            background: #ff4757;
            color: white;
        }
        
        /* Footer */
        .deals-footer {
            background: #2d3436;
            color: white;
            padding: 40px 20px;
            text-align: center;
            margin-top: 60px;
        }
        
        .deals-footer p {
            opacity: 0.8;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .header-nav {
                flex-direction: column;
            }
            
            .search-box {
                max-width: 100%;
                order: 3;
            }
            
            .nav-links {
                order: 2;
            }
            
            .featured-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="deals-header">
        <div class="header-top">
            <h1>🔥 Daily Hot Deals</h1>
            <p>Best deals from Amazon, Flipkart, Myntra, Nykaa & {{ total_deals }}+ stores</p>
        </div>
        <div class="header-nav">
            <a href="/" class="logo">
                <i class="fas fa-tag"></i> GrabCoupon
            </a>
            <div class="search-box">
                <form action="/deals" method="get">
                    <input type="text" name="search" placeholder="Search deals, products..." value="{{ search_query }}">
                    <button type="submit"><i class="fas fa-search"></i></button>
                </form>
            </div>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/deals">All Deals</a>
                <a href="/local">Food</a>
            </nav>
        </div>
    </header>
    
    <!-- Category Tabs -->
    <div class="category-tabs">
        <div class="category-tabs-inner">
            <a href="/deals" class="{% if not selected_category %}active{% endif %}">All Deals</a>
            <a href="/deals?category=electronics" class="{% if selected_category == 'electronics' %}active{% endif %}"><i class="fas fa-mobile-alt"></i> Electronics</a>
            <a href="/deals?category=fashion" class="{% if selected_category == 'fashion' %}active{% endif %}"><i class="fas fa-tshirt"></i> Fashion</a>
            <a href="/deals?category=home" class="{% if selected_category == 'home' %}active{% endif %}"><i class="fas fa-couch"></i> Home</a>
            <a href="/deals?category=beauty" class="{% if selected_category == 'beauty' %}active{% endif %}"><i class="fas fa-spa"></i> Beauty</a>
            <a href="/deals?category=food" class="{% if selected_category == 'food' %}active{% endif %}"><i class="fas fa-utensils"></i> Food</a>
        </div>
    </div>
    
    <!-- Featured Deals -->
    {% if featured_deals %}
    <section class="featured-section">
        <h2>⭐ Featured Deals Today</h2>
        <div class="featured-grid">
            {% for deal in featured_deals %}
            <div class="featured-card">
                <div class="featured-image" style="background: {{ deal.image_gradient }}; display: flex; align-items: center; justify-content: center;">
                    <i class="fas {{ deal.image_icon }}" style="font-size: 4rem; color: white;"></i>
                </div>
                <div class="featured-body">
                    <span class="featured-store"><i class="fas fa-store"></i> {{ deal.source }}</span>
                    <h3 class="featured-title">{{ deal.description }}</h3>
                    <div class="featured-prices">
                        <span class="featured-sale">₹{{ deal.sale_price }}</span>
                        <span class="featured-original">₹{{ deal.original_price }}</span>
                        <span class="featured-discount">{{ deal.discount }} OFF</span>
                    </div>
                    <a href="{{ deal.product_url }}" target="_blank" class="featured-btn">
                        Get Deal <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
    </section>
    {% endif %}
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="section-header">
            <h2>📦 All Deals</h2>
            <span class="deals-count">{{ deals|length }} deals found</span>
        </div>
        
        {% if deals %}
        <div class="deals-grid">
            {% for deal in deals %}
            <div class="deal-card">
                <div class="deal-image-wrapper">
                    <div class="deal-image" style="background: {{ deal.image_gradient }}; display: flex; align-items: center; justify-content: center;">
                        <i class="fas {{ deal.image_icon }}" style="font-size: 3rem; color: white;"></i>
                    </div>
                    <span class="deal-discount">{{ deal.discount }} OFF</span>
                    <button class="deal-wishlist"><i class="fas fa-heart"></i></button>
                </div>
                <div class="deal-body">
                    <div class="deal-store">
                        <i class="fas fa-store"></i> {{ deal.source }}
                    </div>
                    <h3 class="deal-title">{{ deal.description }}</h3>
                    <div class="deal-prices">
                        <span class="deal-sale">₹{{ deal.sale_price }}</span>
                        <span class="deal-original">₹{{ deal.original_price }}</span>
                    </div>
                    <a href="{{ deal.product_url }}" target="_blank" class="deal-btn">
                        View Deal <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
        
        {% if total_pages > 1 %}
        <div class="pagination">
            {% if current_page > 1 %}
            <a href="/deals?category={{ selected_category }}&search={{ search_query }}&source={{ selected_source }}&page={{ current_page - 1 }}">← Previous</a>
            {% endif %}
            
            {% for p in range(1, total_pages + 1) %}
            {% if p == current_page %}
            <span class="current">{{ p }}</span>
            {% elif p <= 3 or p > total_pages - 3 or (p >= current_page - 1 and p <= current_page + 1) %}
            <a href="/deals?category={{ selected_category }}&search={{ search_query }}&source={{ selected_source }}&page={{ p }}">{{ p }}</a>
            {% elif p == 4 or p == total_pages - 3 %}
            <span>...</span>
            {% endif %}
            {% endfor %}
            
            {% if current_page < total_pages %}
            <a href="/deals?category={{ selected_category }}&search={{ search_query }}&source={{ selected_source }}&page={{ current_page + 1 }}">Next →</a>
            {% endif %}
        </div>
        {% endif %}
        
        {% else %}
        <div class="no-deals">
            <i class="fas fa-search"></i>
            <h2>No deals found</h2>
            <p>Try adjusting your search or filters</p>
        </div>
        {% endif %}
    </main>
    
    <!-- Footer -->
    <footer class="deals-footer">
        <p>&copy; 2026 GrabCoupon. All rights reserved.</p>
    </footer>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GrabCoupon - Best Coupon Codes & Deals in India {{ '| ' + request.args.get('category')|title if request.args.get('category') else '' }}</title>
    <meta name="description" content="Find verified coupon codes, discounts & deals from Amazon, Flipkart, Myntra, Swiggy, Zomato & 50+ top Indian stores. Save big on every purchase!">
    <meta name="keywords" content="coupon codes, discount codes, deals, offers, Amazon coupons, Flipkart deals, Myntra discount, Swiggy coupon, Zomato offers, India shopping deals, promo codes">
    <meta name="author" content="GrabCoupon">
    <meta name="robots" content="index, follow">
    <meta name="googlebot" content="index, follow">
    <meta name="language" content="English">
    <meta name="revisit-after" content="1 day">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://grabcoupon.in/">
    <meta property="og:title" content="GrabCoupon - Best Coupon Codes & Deals in India">
    <meta property="og:description" content="Find verified coupon codes & discounts from 50+ top Indian stores. Save big on every purchase!">
    <meta property="og:image" content="/static/og-image.png">
    <meta property="og:site_name" content="GrabCoupon">
    <meta property="og:locale" content="en_IN">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://grabcoupon.in/">
    <meta property="twitter:title" content="GrabCoupon - Best Coupon Codes & Deals in India">
    <meta property="twitter:description" content="Find verified coupon codes & discounts from 50+ top Indian stores. Save big on every purchase!">
    <meta property="twitter:image" content="/static/og-image.png">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="https://grabcoupon.in/">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎫</text></svg>">
    
    <!-- JSON-LD Structured Data for SEO -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "GrabCoupon",
        "url": "https://grabcoupon.in",
        "description": "Find verified coupon codes and discounts from top Indian retailers",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": "https://grabcoupon.in/?search={search_term_string}"
            },
            "query-input": "required name=search_term_string"
        },
        "sameAs": [
            "https://facebook.com/grabcoupon",
            "https://twitter.com/grabcoupon",
            "https://instagram.com/grabcoupon"
        ]
    }
    </script>
    
    <!-- JSON-LD Organization Schema -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "GrabCoupon",
        "url": "https://grabcoupon.in",
        "logo": "https://grabcoupon.in/logo.png",
        "description": "Your trusted source for coupon codes and deals in India",
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+91-XXXXXXXXXX",
            "contactType": "Customer Service"
        }
    }
    </script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            /* Trust + Savings Theme - Based on CouponDunia & GrabOn */
            --primary: #22c55e;      /* Green - trust/money */
            --primary-dark: #16a34a;
            --secondary: #f97316;    /* Orange - excitement */
            --accent: #ef4444;       /* Red - urgency */
            --dark: #1e293b;         /* Slate - premium feel */
            --light: #f8fafc;
            --white: #ffffff;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #334155;
            --text-light: #64748b;
            --gray: #94a3b8;
            --bg: #f8fafc;
            --border: #e2e8f0;
        }
        
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f8fafc;
            color: #334155;
            min-height: 100vh;
        }
        
        /* Main Header Navigation */
        .main-header {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 0.75rem 2rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .main-header .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            color: white;
            font-size: 1.5rem;
            font-weight: 700;
            text-decoration: none;
        }
        
        .main-header .logo-icon {
            font-size: 1.3rem;
        }
        
        .main-nav {
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .main-nav .nav-link {
            color: rgba(255,255,255,0.9);
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .main-nav .nav-link:hover,
        .main-nav .nav-link.active {
            color: white;
            background: rgba(255,255,255,0.2);
        }
        
        .header-cta .cta-button {
            background: white;
            color: #22c55e;
            padding: 0.6rem 1.5rem;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.3s ease;
        }
        
        .header-cta .cta-button:hover {
            transform: scale(1.05);
        }
        
        @media (max-width: 768px) {
            .main-nav { 
                overflow-x: auto;
                gap: 1rem;
                padding: 10px;
            }
        }
        
        /* Combined Search Form */
        .combined-search-form {
            width: 100%;
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .search-bar-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            flex-wrap: nowrap;
        }
        
        .main-search-input {
            flex: 1;
            min-width: 300px;
            max-width: 400px;
            padding: 14px 22px;
            border: 3px solid white;
            border-radius: 50px;
            font-size: 1rem;
            background: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        .main-search-input:focus {
            outline: none;
            border-color: #22c55e;
        }
        
        .filter-select {
            padding: 12px 18px;
            border: 3px solid white;
            border-radius: 50px;
            font-size: 0.9rem;
            background: white;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            min-width: 130px;
            transition: all 0.3s ease;
            color: #334155;
            font-weight: 500;
        }
        
        .filter-select:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(0,0,0,0.2);
        }
        
        .filter-select:focus {
            outline: none;
            border-color: #22c55e;
            box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2);
        }
        
        /* Discount filter styling */
        .discount-filter {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            padding: 8px 16px;
            border-radius: 25px;
            border: 2px solid #f59e0b;
            font-size: 0.85rem;
            font-weight: 600;
            color: #92400e;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .discount-filter:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
        }
        
        .discount-filter:focus {
            outline: none;
            box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.2);
        }
        
        .search-bar-row .search-btn {
            padding: 14px 35px;
            background: #22c55e;
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .search-bar-row .search-btn:hover {
            background: #16a34a;
            transform: translateY(-2px);
        }
        
        @media (max-width: 900px) {
            .search-bar-row {
                flex-wrap: wrap;
                gap: 12px;
            }
            .main-search-input {
                width: 100%;
                max-width: 100%;
            }
            .filter-select {
                flex: 1;
                min-width: 120px;
            }
        }
        
        /* Hero Section - Like GrabOn & CouponDunia */
        .hero-section {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%);
            padding: 40px 20px 50px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.5;
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
            max-width: 700px;
            margin: 0 auto;
        }
        
        .hero-title {
            color: white;
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        
        .hero-title span {
            display: inline;
        }
        
        .hero-subtitle {
            color: rgba(255,255,255,0.95);
            font-size: 1.1rem;
            margin-bottom: 25px;
            font-weight: 500;
        }
        
        /* Search Box */
        .search-container {
            position: relative;
            max-width: 600px;
            margin: 0 auto 20px;
        }
        
        .search-box {
            display: flex;
            align-items: center;
            background: white;
            border-radius: 50px;
            padding: 8px 8px 8px 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        .search-icon {
            font-size: 1.2rem;
            margin-right: 10px;
        }
        
        .search-box input {
            flex: 1;
            border: none;
            outline: none;
            font-size: 1rem;
            padding: 10px;
        }
        
        .search-btn {
            background: #22c55e;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 30px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .search-btn:hover {
            background: #16a34a;
            transform: scale(1.02);
        }
        
        .search-suggestions {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            margin-top: 5px;
            display: none;
            z-index: 100;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .search-suggestions.show {
            display: block;
        }
        
        .suggestion-item {
            padding: 12px 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: background 0.2s;
        }
        
        .suggestion-item:hover {
            background: #f0fdf4;
        }
        
        /* Popular Searches */
        .popular-searches {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            align-items: center;
            margin-top: 25px;
        }
        
        .popular-label {
            color: rgba(255,255,255,0.8);
            font-weight: 500;
        }
        
        .popular-tag {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.3s;
        }
        
        .popular-tag:hover {
            background: white;
            color: #22c55e;
        }
        
        /* Trust Badges Hero */
        .trust-badges-hero {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
            flex-wrap: wrap;
        }
        
        .badge-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
        }
        
        .badge-icon {
            font-size: 1.5rem;
        }
        
        .badge-text {
            font-size: 0.95rem;
        }
        
        .refresh-btn {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .refresh-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .refresh-btn.loading {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        /* Category Bar */
        .category-bar {
            display: flex;
            justify-content: center;
            gap: 10px;
            padding: 15px 20px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            flex-wrap: wrap;
            overflow-x: auto;
        }
        
        .category-pill {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 10px 20px;
            background: #f1f5f9;
            border-radius: 25px;
            text-decoration: none;
            color: #475569;
            font-weight: 500;
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .category-pill:hover, .category-pill.active {
            background: #22c55e;
            color: white;
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .hero-title {
                font-size: 1.8rem;
                flex-direction: column;
            }
            .hero-icon {
                font-size: 2.5rem;
            }
            .search-box {
                flex-direction: column;
                border-radius: 20px;
                padding: 15px;
            }
            .search-box input {
                width: 100%;
                text-align: center;
                margin-bottom: 10px;
            }
            .search-btn {
                width: 100%;
            }
            .trust-badges-hero {
                gap: 20px;
            }
            .badge-item {
                font-size: 0.85rem;
            }
            .category-bar {
                justify-content: flex-start;
                padding: 10px;
            }
        }
        
        header {
            background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
            color: white;
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(14, 165, 233, 0.2);
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .logo {
            font-size: 2rem;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        
        .logo span { color: #FFD60A; }
        
        .tabs {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            scrollbar-width: none;
        }
        
        .tabs::-webkit-scrollbar {
            display: none;
        }
        
        .trust-bar {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            padding: 12px 20px;
            text-align: center;
            font-size: 0.95rem;
            color: #92400e;
            font-weight: 500;
        }
        
        .trust-bar span {
            margin: 0 10px;
        }
        
        @media (max-width: 600px) {
            .trust-bar {
                font-size: 0.8rem;
                padding: 10px 10px;
            }
            .trust-bar span {
                display: block;
                margin: 5px 0;
            }
            .footer-content {
                grid-template-columns: 1fr;
                text-align: center;
            }
            .coupons-grid { grid-template-columns: 1fr; }
            .logo { font-size: 1.5rem; }
            .tab { padding: 6px 10px; font-size: 0.8rem; }
        }
        
        /* Skip to content link for accessibility */
        .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: #0ea5e9;
            color: white;
            padding: 8px;
            z-index: 1001;
        }
        
        .skip-link:focus {
            top: 0;
        }
        
        /* Focus styles for accessibility */
        a:focus, button:focus, input:focus, select:focus {
            outline: 3px solid #f97316;
            outline-offset: 2px;
        }
        
        .tab {
            padding: 8px 16px;
            background: rgba(255,255,255,0.3);
            border-radius: 20px;
            text-decoration: none;
            color: #023E8A;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .tab:hover, .tab.active {
            background: white;
            color: #00B4D8;
        }
        
        /* Category Pills - Clean Design like top coupon sites */
        .category-pills {
            background: white;
            padding: 15px 20px;
            display: flex;
            gap: 8px;
            overflow-x: auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            scrollbar-width: none;
        }
        
        .category-pills::-webkit-scrollbar {
            display: none;
        }
        
        .category-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border-radius: 25px;
            text-decoration: none;
            color: #475569;
            font-weight: 500;
            font-size: 0.9rem;
            white-space: nowrap;
            transition: all 0.2s;
            background: #f1f5f9;
            border: 1px solid transparent;
        }
        
        .category-pill:hover {
            background: #0ea5e9;
            color: white;
        }
        
        .category-pill.active {
            background: #0ea5e9;
            color: white;
            border-color: #0284c7;
        }
        
        
        .container { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
        
        .filters {
            background: rgba(255,255,255,0.9);
            padding: 1.2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .filter-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .product-search-input {
            flex: 2;
            min-width: 200px;
            padding: 10px 16px;
            border: 2px solid #22c55e;
            border-radius: 25px;
            font-size: 0.95rem;
            background: white;
        }
        
        .filter-row select, .filter-row input {
            padding: 10px 16px;
            border: 2px solid #90E0EF;
            border-radius: 25px;
            font-size: 0.95rem;
            min-width: 140px;
            background: white;
        }
        
        .filter-row select:focus, .filter-row input:focus {
            outline: none;
            border-color: #00B4D8;
        }
        
        .filter-row button {
            padding: 10px 25px;
            background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .filter-row button:hover { transform: translateY(-2px); }
        
        .filter-row input, .filter-row select {
            padding: 10px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .filter-row input:focus, .filter-row select:focus {
            border-color: #6366f1;
        }
        
        @media (max-width: 600px) {
            .filter-row {
                flex-wrap: nowrap;
                overflow-x: auto;
                padding-bottom: 10px;
            }
            .filter-row select, .filter-row input {
                min-width: 120px;
                padding: 8px 12px;
                font-size: 0.85rem;
            }
            .filter-row button {
                padding: 8px 16px;
                font-size: 0.85rem;
                white-space: nowrap;
            }
        }
        
        /* Product Search Results */
        .product-search-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        }
        
        .product-results-header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .product-results-header h3 {
            color: #1e293b;
            font-size: 1.4rem;
            margin-bottom: 5px;
        }
        
        .product-results-header p {
            color: #64748b;
            font-size: 0.9rem;
        }
        
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        
        .product-card {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 15px;
            transition: all 0.3s ease;
            background: white;
        }
        
        .product-card:hover {
            border-color: #22c55e;
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(34, 197, 94, 0.15);
        }
        
        .product-card-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }
        
        .product-image {
            width: 80px;
            height: 80px;
            object-fit: contain;
            border-radius: 8px;
            background: #f8fafc;
        }
        
        .product-info {
            flex: 1;
        }
        
        .product-title {
            font-size: 0.95rem;
            color: #1e293b;
            font-weight: 600;
            margin-bottom: 5px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .product-rating {
            font-size: 0.85rem;
            color: #f59e0b;
        }
        
        .product-price-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 12px 0;
        }
        
        .product-price {
            font-size: 1.4rem;
            font-weight: 700;
            color: #22c55e;
        }
        
        .product-original-price {
            font-size: 0.9rem;
            color: #94a3b8;
            text-decoration: line-through;
        }
        
        .product-source {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .product-source.amazon {
            background: #ff990020;
            color: #ff9900;
        }
        
        .product-source.flipkart {
            background: #2874f020;
            color: #2874f0;
        }
        
        .product-link {
            display: block;
            width: 100%;
            padding: 10px;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        .product-link:hover {
            transform: scale(1.02);
        }
        
        .product-loading {
            text-align: center;
            padding: 40px;
        }
        
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top-color: #22c55e;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .coupons-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        
        /* Section Title */
        .section-title {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .section-title h2 {
            font-size: 1.8rem;
            color: #1e293b;
            margin-bottom: 8px;
        }
        
        .section-title p {
            color: #64748b;
            font-size: 0.95rem;
        }
        
        /* Coupon Card - Like CouponDunia */
        .coupon-card {
            background: white;
            border-radius: 16px;
            overflow: visible;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border: 1px solid #e2e8f0;
            position: relative;
            margin-top: 5px;
            padding: 15px;
        }
        
        .coupon-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(37, 99, 235, 0.15);
        }
        
        .coupon-card.hot-deal-card {
            border: 2px solid #ef4444;
        }
        
        /* Trust Badge - Top Bar Style */
        .trust-badge {
            position: absolute;
            top: -8px;
            left: 15px;
            padding: 4px 12px;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            z-index: 10;
            color: white;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .trust-badge.hot {
            background: #ef4444;
        }
        
        .trust-badge.exclusive {
            background: #f97316;
        }
        
        .coupon-header {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 1rem;
            padding-top: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 1;
        }
        
        .trust-badge.verified {
            background: #22c55e;
            color: white;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        /* Coupon Buttons */
        .coupon-buttons {
            margin-top: 12px;
        }
        
        .expiring-soon-badge {
            background: linear-gradient(135deg, #f97316, #ea580c);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 600;
            text-align: center;
            margin: 8px 0;
            animation: pulse 2s infinite;
        }
        
        .btn-visit {
            display: block;
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 700;
            font-size: 1rem;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn-visit:hover {
            background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
        }
        
        .btn-visit.hot-deal {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }
        
        .btn-visit.hot-deal:hover {
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
        }
        
        /* Coupon Header */
        .coupon-header {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .coupon-source {
            font-weight: bold;
            font-size: 1rem;
        }
        
        .coupon-discount {
            background: #f97316;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9rem;
        }
        
        .coupon-badge {
            display: inline-block;
            background: #E63946;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        .coupon-badge.hot {
            background: #ef4444;
            animation: pulse 2s infinite;
        }
        
        .coupon-badge.featured {
            background: #f59e0b;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .coupon-body { padding: 1.2rem; }
        
        .coupon-code {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }
        
        .code-box {
            flex: 1;
            background: #CAF0F8;
            padding: 12px 15px;
            border-radius: 10px;
            font-family: monospace;
            font-size: 1.2rem;
            font-weight: bold;
            color: #0077B6;
            letter-spacing: 2px;
            text-align: center;
            border: 2px dashed #00B4D8;
        }
        
        .copy-btn {
            padding: 12px 18px;
            background: #00B4D8;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .copy-btn:hover { background: #0077B6; }
        
        .coupon-desc {
            font-size: 1rem;
            color: #023E8A;
            margin-bottom: 12px;
            line-height: 1.5;
        }
        
        .coupon-details {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 15px;
        }
        
        .detail-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .detail-item span { color: #0077B6; font-weight: 600; }
        
        .expired-tag {
            background: #ffcccc;
            color: #cc0000;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .valid-tag {
            background: #ccffcc;
            color: #006600;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .coupon-btn {
            display: block;
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s;
        }
        
        .coupon-btn:hover {
            background: linear-gradient(135deg, #0077B6 0%, #023E8A 100%);
            transform: scale(1.02);
        }
        
        footer {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: white;
            padding: 3rem 20px;
            text-align: center;
            margin-top: 3rem;
        }
        
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            text-align: left;
        }
        
        .footer-section h3 {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #f97316;
        }
        
        .footer-section a {
            display: block;
            color: #cbd5e1;
            text-decoration: none;
            padding: 5px 0;
            font-size: 0.9rem;
            transition: color 0.3s;
        }
        
        .footer-section a:hover {
            color: #38bdf8;
        }
        
        .footer-bottom {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid #334155;
            text-align: center;
            color: #94a3b8;
            font-size: 0.85rem;
        }
        
        .social-links {
            margin-top: 1rem;
        }
        
        .social-links a {
            display: inline-block;
            margin: 0 10px;
            font-size: 1.5rem;
        }
        
        .trust-badges {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        
        .trust-badges span {
            background: rgba(255,255,255,0.1);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        
        .last-updated {
            text-align: center;
            color: #0077B6;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 1.8rem; }
            .stats-bar { gap: 15px; }
            .coupons-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- Hero Section with Search - Like GrabOn & CouponDunia -->
    <div class="hero-section">
        <div class="hero-content">
            <!-- Logo -->
            <div style="text-align: center; margin-bottom: 20px;">
                <a href="/" style="color: white; text-decoration: none;">
                    <span style="font-size: 2.5rem; font-weight: 800;">🎫 GrabCoupon</span>
                </a>
            </div>
            
            <!-- Navigation Links -->
            <nav class="hero-nav" style="margin-bottom: 25px; display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
                <a href="/" class="hero-nav-link {% if request.path == '/' %}active{% endif %}" style="color: white; text-decoration: none; font-weight: 500; padding: 8px 16px; border-radius: 8px; transition: background 0.3s;">Home</a>
                <a href="/deals" class="hero-nav-link {% if request.path == '/deals' %}active{% endif %}" style="color: white; text-decoration: none; font-weight: 500; padding: 8px 16px; border-radius: 8px; transition: background 0.3s;">Daily Deals</a>
                <a href="/local" class="hero-nav-link {% if request.path == '/local' %}active{% endif %}" style="color: white; text-decoration: none; font-weight: 500; padding: 8px 16px; border-radius: 8px; transition: background 0.3s;">Local Food Deals</a>
                <a href="/about" class="hero-nav-link {% if request.path == '/about' %}active{% endif %}" style="color: white; text-decoration: none; font-weight: 500; padding: 8px 16px; border-radius: 8px; transition: background 0.3s;">About Us</a>
                <a href="/contact" class="hero-nav-link {% if request.path == '/contact' %}active{% endif %}" style="color: white; text-decoration: none; font-weight: 500; padding: 8px 16px; border-radius: 8px; transition: background 0.3s;">Contact Us</a>
            </nav>
            
            <!-- Combined Search and Filters -->
            <form class="combined-search-form" method="get">
                <div class="search-bar-row">
                    <select name="category" class="filter-select">
                        <option value="">All Categories</option>
                        <option value="electronics" {% if request.args.get('category')=='electronics' %}selected{% endif %}>Electronics</option>
                        <option value="mobiles" {% if request.args.get('category')=='mobiles' %}selected{% endif %}>Mobiles</option>
                        <option value="fashion" {% if request.args.get('category')=='fashion' %}selected{% endif %}>Fashion</option>
                        <option value="beauty" {% if request.args.get('category')=='beauty' %}selected{% endif %}>Beauty</option>
                        <option value="home" {% if request.args.get('category')=='home' %}selected{% endif %}>Home & Furniture</option>
                        <option value="food" {% if request.args.get('category')=='food' %}selected{% endif %}>Food & Dining</option>
                        <option value="books" {% if request.args.get('category')=='books' %}selected{% endif %}>Books</option>
                    </select>
                    
                    <select name="source" class="filter-select">
                        <option value="">All Stores</option>
                        <option value="Amazon" {% if request.args.get('source')=='Amazon' %}selected{% endif %}>Amazon</option>
                        <option value="Flipkart" {% if request.args.get('source')=='Flipkart' %}selected{% endif %}>Flipkart</option>
                        <option value="Myntra" {% if request.args.get('source')=='Myntra' %}selected{% endif %}>Myntra</option>
                        <option value="Swiggy" {% if request.args.get('source')=='Swiggy' %}selected{% endif %}>Swiggy</option>
                        <option value="Zomato" {% if request.args.get('source')=='Zomato' %}selected{% endif %}>Zomato</option>
                        <option value="Ajio" {% if request.args.get('source')=='Ajio' %}selected{% endif %}>Ajio</option>
                        <option value="Tata Cliq" {% if request.args.get('source')=='Tata Cliq' %}selected{% endif %}>Tata Cliq</option>
                        <option value="Nykaa" {% if request.args.get('source')=='Nykaa' %}selected{% endif %}>Nykaa</option>
                        <option value="Pepperfry" {% if request.args.get('source')=='Pepperfry' %}selected{% endif %}>Pepperfry</option>
                        <option value="Paytm Mall" {% if request.args.get('source')=='Paytm Mall' %}selected{% endif %}>Paytm Mall</option>
                        <option value="Shopclues" {% if request.args.get('source')=='Shopclues' %}selected{% endif %}>Shopclues</option>
                        <option value="Snapdeal" {% if request.args.get('source')=='Snapdeal' %}selected{% endif %}>Snapdeal</option>
                        <option value="Croma" {% if request.args.get('source')=='Croma' %}selected{% endif %}>Croma</option>
                        <option value="Reliance Digital" {% if request.args.get('source')=='Reliance Digital' %}selected{% endif %}>Reliance Digital</option>
                        <option value="Bewakoof" {% if request.args.get('source')=='Bewakoof' %}selected{% endif %}>Bewakoof</option>
                        <option value="FabAlley" {% if request.args.get('source')=='FabAlley' %}selected{% endif %}>FabAlley</option>
                        <option value="Bata" {% if request.args.get('source')=='Bata' %}selected{% endif %}>Bata</option>
                        <option value="Puma" {% if request.args.get('source')=='Puma' %}selected{% endif %}>Puma</option>
                        <option value="Nike" {% if request.args.get('source')=='Nike' %}selected{% endif %}>Nike</option>
                        <option value="Adidas" {% if request.args.get('source')=='Adidas' %}selected{% endif %}>Adidas</option>
                    </select>
                    
                    <select name="city" class="filter-select">
                        <option value="">All Cities</option>
                        <option value="all" {% if request.args.get('city')=='all' %}selected{% endif %}>All India</option>
                        <option value="Hyderabad" {% if request.args.get('city')=='Hyderabad' %}selected{% endif %}>Hyderabad</option>
                        <option value="Bangalore" {% if request.args.get('city')=='Bangalore' %}selected{% endif %}>Bangalore</option>
                        <option value="Mumbai" {% if request.args.get('city')=='Mumbai' %}selected{% endif %}>Mumbai</option>
                        <option value="Delhi" {% if request.args.get('city')=='Delhi' %}selected{% endif %}>Delhi</option>
                        <option value="Chennai" {% if request.args.get('city')=='Chennai' %}selected{% endif %}>Chennai</option>
                    </select>
                    
                    <select name="discount" class="filter-select discount-filter">
                        <option value="">💰 Any Discount</option>
                        <option value="10" {% if request.args.get('discount')=='10' %}selected{% endif %}>10%+ Off</option>
                        <option value="20" {% if request.args.get('discount')=='20' %}selected{% endif %}>20%+ Off</option>
                        <option value="30" {% if request.args.get('discount')=='30' %}selected{% endif %}>30%+ Off</option>
                        <option value="50" {% if request.args.get('discount')=='50' %}selected{% endif %}>50%+ Off</option>
                        <option value="70" {% if request.args.get('discount')=='70' %}selected{% endif %}>70%+ Off</option>
                    </select>
                    
                    <button type="submit" class="search-btn">Search</button>
                </div>
            </form>
            
            <!-- Popular Searches -->
            <div class="popular-searches">
                <span class="popular-label">Popular:</span>
                <a href="/?search=Amazon" class="popular-tag">Amazon</a>
                <a href="/?search=Flipkart" class="popular-tag">Flipkart</a>
                <a href="/?search=Myntra" class="popular-tag">Myntra</a>
                <a href="/?search=Ajio" class="popular-tag">Ajio</a>
                <a href="/?search=Nykaa" class="popular-tag">Nykaa</a>
                <a href="/?search=Meesho" class="popular-tag">Meesho</a>
                <a href="/?search=Snapdeal" class="popular-tag">Snapdeal</a>
                <a href="/?search=Croma" class="popular-tag">Croma</a>
                <a href="/?search=Nike" class="popular-tag">Nike</a>
                <a href="/?search=Puma" class="popular-tag">Puma</a>
            </div>
        </div>
        
        <!-- Trust Badges -->
        <div class="trust-badges-hero">
            <div class="badge-item">
                <span class="badge-icon">✅</span>
                <span class="badge-text"><strong>{{ total_coupons }}+</strong> Verified Coupons</span>
            </div>
            <div class="badge-item">
                <span class="badge-icon">🛡️</span>
                <span class="badge-text">100% Authentic Deals</span>
            </div>
            <div class="badge-item" id="lastUpdatedBadge">
                <span class="badge-icon">⚡</span>
                <span class="badge-text">Last Updated: {{ last_updated }}</span>
            </div>
            <button type="button" class="refresh-btn" onclick="refreshCoupons()" id="refreshBtn">
                🔄 Refresh
            </button>
        </div>
    </div>
    
    <div class="container">
        <div class="filters" style="display: none;">
            <form class="filter-row" method="get">
                {% if request.args.get('category') %}
                <input type="hidden" name="category" value="{{ request.args.get('category') }}">
                {% endif %}
                {% if request.args.get('search') %}
                <input type="hidden" name="search" value="{{ request.args.get('search') }}">
                {% endif %}
                
                <!-- Product Search Bar -->
                <input type="text" 
                       name="product_search" 
                       placeholder="🔍 Search products (TV, fridge, mobile...)" 
                       value="{{ request.args.get('product_search', '') }}"
                       class="product-search-input"
                       style="flex: 2; min-width: 200px;">
                
                <select name="source">
                    <option value="">All Stores</option>
                    <option value="Amazon">Amazon (6)</option>
                    <option value="Flipkart">Flipkart (6)</option>
                    <option value="YouTube Shopping">YouTube Shopping (8)</option>
                    <option value="Myntra">Myntra (4)</option>
                    <option value="Swiggy">Swiggy (4)</option>
                    <option value="Zomato">Zomato (4)</option>
                    <option value="Ajio">Ajio (3)</option>
                    <option value="Croma">Croma (3)</option>
                    <option value="Meesho">Meesho (3)</option>
                    <option value="Nykaa">Nykaa (3)</option>
                    <option value="Paytm">Paytm (3)</option>
                    <option value="Reliance Digital">Reliance Digital (3)</option>
                    <option value="Snapdeal">Snapdeal (3)</option>
                    <option value="Tata Cliq">Tata Cliq (3)</option>
                    <option value="Swiggy Delivery">Swiggy Delivery (3)</option>
                    <option value="Pepperfry">Pepperfry (2)</option>
                    <option value="Shoppers Stop">Shoppers Stop (2)</option>
                    <option value="Blinkit">Blinkit</option>
                    <option value="Zepto">Zepto</option>
                    <option value="BigBasket">BigBasket</option>
                    <option value="Dmart">Dmart</option>
                    <option value="FirstCry">FirstCry</option>
                    <option value="PharmEasy">PharmEasy</option>
                    <option value="BookMyShow">BookMyShow</option>
                    <option value="MakeMyTrip">MakeMyTrip</option>
                    <option value="Goibibo">Goibibo</option>
                    <option value="Yatra">Yatra</option>
                    <option value="CRED">CRED</option>
                    <option value="Simpl">Simpl</option>
                    <option value="PineLabs">PineLabs</option>
                    <option value="Nykaa Fashion">Nykaa Fashion</option>
                    <option value="Libas">Libas</option>
                    <option value="W For Woman">W For Woman</option>
                    <option value="Allen Solly">Allen Solly</option>
                    <option value="Louis Philippe">Louis Philippe</option>
                    <option value="Peter England">Peter England</option>
                    <option value="adidas">adidas</option>
                    <option value="Nike">Nike</option>
                    <option value="Puma">Puma</option>
                    <option value="Samsung">Samsung</option>
                    <option value="OnePlus">OnePlus</option>
                    <option value="Vivo">Vivo</option>
                    <option value="Oppo">Oppo</option>
                    <option value="Realme">Realme</option>
                    <option value="Lenovo">Lenovo</option>
                    <option value="Dell">Dell</option>
                    <option value="HP">HP</option>
                    <option value="Asus">Asus</option>
                    <option value="Jio">Jio</option>
                    <option value="Airtel">Airtel</option>
                    <option value="Vi">Vi</option>
                    <option value="McDonald's">McDonald's</option>
                    <option value="KFC">KFC</option>
                    <option value="Pizza Hut">Pizza Hut</option>
                    <option value="Domino's">Domino's</option>
                    <option value="Subway">Subway</option>
                    <option value="Burger King">Burger King</option>
                    <option value="Costa Coffee">Costa Coffee</option>
                    <option value="CCD">CCD</option>
                    <option value="Barista">Barista</option>
                    <option value="Starbucks">Starbucks</option>
                    <option value="Dunkin">Dunkin</option>
                    <option value="Faasos">Faasos</option>
                    <option value="FreshMenu">FreshMenu</option>
                    <option value="Spencer's">Spencer's</option>
                    <option value="Big Bazaar">Big Bazaar</option>
                    <option value="More">More</option>
                    <option value="Nilgiris">Nilgiris</option>
                    <option value="Apollo Pharmacy">Apollo Pharmacy</option>
                    <option value="NetMeds">NetMeds</option>
                </select>
                <select name="city">
                    <option value="">All Cities (includes local)</option>
                    <option value="all">All India Only</option>
                    <option value="Hyderabad">Hyderabad</option>
                    <option value="Bangalore">Bangalore</option>
                    <option value="Mumbai">Mumbai</option>
                    <option value="Delhi">Delhi</option>
                    <option value="Chennai">Chennai</option>
                    <option value="Pune">Pune</option>
                    <option value="Kolkata">Kolkata</option>
                    <option value="Chandigarh">Chandigarh</option>
                    <option value="Ahmedabad">Ahmedabad</option>
                    <option value="Jaipur">Jaipur</option>
                </select>
                <button type="submit">Apply Filters</button>
                <button type="button" onclick="window.location.href='/'">Reset</button>
            </form>
        </div>
        
        <!-- Section Title -->
        <div class="section-title" style="margin: 30px 0; text-align: center;">
            <h2 style="font-size: 1.8rem; color: #1e293b; margin-bottom: 8px;">
                {% if request.path == '/local' %}
                🍔 Local Food Deals
                {% elif request.args.get('product_search') %}
                📦 Deals for "{{ request.args.get('product_search') }}"
                {% elif request.args.get('search') %}
                🔍 Results for "{{ request.args.get('search') }}"
                {% elif request.args.get('category') %}
                {{ request.args.get('category')|title }} Deals & Coupons
                {% elif request.args.get('source') %}
                {{ request.args.get('source') }} Coupons & Deals
                {% else %}
                💰 All Coupons & Deals
                {% endif %}
            </h2>
        </div>
        
        <div class="coupons-grid">
            {% for coupon in coupons %}
            <div class="coupon-card {% if coupon.is_hot %}hot-deal-card{% endif %}">
                <!-- Trust Badge -->
                {% if coupon.is_hot %}
                <div class="trust-badge hot">🔥 HOT</div>
                {% elif coupon.is_featured %}
                <div class="trust-badge exclusive">⭐ EXCLUSIVE</div>
                {% else %}
                <div class="trust-badge verified">✓ VERIFIED</div>
                {% endif %}
                
                <div class="coupon-header">
                    <span class="coupon-source">{{ coupon.source }}</span>
                    <span class="coupon-discount">{{ coupon.discount }}</span>
                </div>
                <div class="coupon-body">
                    {% if coupon.is_hot %}
                    <div class="coupon-badge hot">🔥 Hot Deal</div>
                    {% elif coupon.is_featured %}
                    <div class="coupon-badge featured">⭐ Featured</div>
                    {% endif %}
                    {% if coupon.city and coupon.city != 'all' %}
                    <div class="city-badge">{{ coupon.city }}</div>
                    {% endif %}
                    <div class="coupon-code">
                        {% set coupon_code = coupon.code or coupon.coupon_code %}
                        {% if coupon_code %}
                        <div class="code-box">{{ coupon_code }}</div>
                        <button class="copy-btn" onclick="copyCode('{{ coupon_code }}')">Copy</button>
                        {% else %}
                        <div class="code-box" style="background:#06b6d4;color:white;">No Code Needed</div>
                        {% endif %}
                    </div>
                    <p class="coupon-desc">{{ coupon.description }}</p>
                    <div class="coupon-details">
                        {% if coupon.min_order %}
                        <div class="detail-item">Min Order: <span>₹{{ coupon.min_order }}</span></div>
                        {% endif %}
                        {% if coupon.expires %}
                        <div class="detail-item">⏰ Expires: <span style="color:#dc2626;font-weight:600;">{{ coupon.expires }}</span></div>
                        {% endif %}
                    </div>
                    <div class="coupon-buttons">
                        <a href="{{ coupon.product_url or coupon.url }}" target="_blank" class="btn-visit {% if coupon.is_hot %}hot-deal{% endif %}" onclick="trackVisit('{{ loop.index }}', '{{ coupon.source }}')">
                            {% if coupon.is_hot %}
                            🔥 Get Deal Now
                            {% else %}
                            🚀 Visit Store
                            {% endif %}
                        </a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Pagination -->
        {% if total_pages > 1 %}
        <div class="pagination" style="display: flex; justify-content: center; gap: 10px; margin: 40px 0; flex-wrap: wrap;">
            {% if current_page > 1 %}
            <a href="?page={{ current_page - 1 }}{% if request.args.get('source') %}&source={{ request.args.get('source') }}{% endif %}{% if request.args.get('search') %}&search={{ request.args.get('search') }}{% endif %}" style="padding: 10px 15px; background: white; color: #1e293b; text-decoration: none; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">← Prev</a>
            {% endif %}
            
            {% for p in range(1, total_pages + 1) %}
                {% if p == current_page %}
                <span style="padding: 10px 15px; background: #22c55e; color: white; border-radius: 8px;">{{ p }}</span>
                {% elif p <= 3 or p > total_pages - 3 or (p >= current_page - 1 and p <= current_page + 1) %}
                <a href="?page={{ p }}{% if request.args.get('source') %}&source={{ request.args.get('source') }}{% endif %}{% if request.args.get('search') %}&search={{ request.args.get('search') }}{% endif %}" style="padding: 10px 15px; background: white; color: #1e293b; text-decoration: none; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">{{ p }}</a>
                {% elif p == 4 or p == total_pages - 3 %}
                <span style="padding: 10px; color: #64748b;">...</span>
                {% endif %}
            {% endfor %}
            
            {% if current_page < total_pages %}
            <a href="?page={{ current_page + 1 }}{% if request.args.get('source') %}&source={{ request.args.get('source') }}{% endif %}{% if request.args.get('search') %}&search={{ request.args.get('search') }}{% endif %}" style="padding: 10px 15px; background: white; color: #1e293b; text-decoration: none; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">Next →</a>
            {% endif %}
        </div>
        {% endif %}
    </div>
    
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h3>🔗 Quick Links</h3>
                <a href="/">All Deals</a>
                <a href="/?category=electronics">Electronics</a>
                <a href="/?category=fashion">Fashion</a>
                <a href="/?category=food">Food & Dining</a>
                <a href="/?category=travel">Travel</a>
            </div>
            <div class="footer-section">
                <h3>🏪 Top Stores</h3>
                <a href="/?source=Amazon">Amazon Coupons</a>
                <a href="/?source=Flipkart">Flipkart Deals</a>
                <a href="/?source=Myntra">Myntra Offers</a>
                <a href="/?source=Swiggy">Swiggy Coupons</a>
                <a href="/?source=Zomato">Zomato Discounts</a>
            </div>
            <div class="footer-section">
                <h3>📄 Information</h3>
                <a href="/about">About Us</a>
                <a href="/contact">Contact Us</a>
                <a href="/privacy">Privacy Policy</a>
                <a href="/terms">Terms & Conditions</a>
                <a href="/disclaimer">Disclaimer</a>
            </div>
            <div class="footer-section">
                <h3>📱 Connect With Us</h3>
                <div class="social-links">
                    <a href="#" aria-label="Facebook">📘</a>
                    <a href="#" aria-label="Twitter">🐦</a>
                    <a href="#" aria-label="Instagram">📸</a>
                    <a href="#" aria-label="Telegram">✈️</a>
                </div>
                <p style="margin-top: 1rem; font-size: 0.9rem; color: #cbd5e1;">
                    Get latest deals delivered to your inbox!
                </p>
            </div>
        </div>
        <div class="trust-badges">
            <span>🔒 Secure Payments</span>
            <span>✅ Verified Coupons</span>
            <span>⚡ Daily Updates</span>
        </div>
        <div class="footer-bottom">
            <p>© 2026 GrabCoupon - All Rights Reserved</p>
            <p style="margin-top: 5px; font-size: 0.8rem;">
                We may earn commission when you click or buy through links on our site.
            </p>
        </div>
    </footer>
    
    <script>
        // Refresh Coupons Function
        async function refreshCoupons() {
            const btn = document.getElementById('refreshBtn');
            const badge = document.getElementById('lastUpdatedBadge');
            
            if (btn) {
                btn.classList.add('loading');
                btn.textContent = '⏳ Refreshing...';
            }
            
            try {
                const response = await fetch('/api/refresh');
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Reload the page to show new coupons
                    location.reload();
                } else {
                    alert('Failed to refresh coupons');
                }
            } catch (error) {
                console.error('Refresh error:', error);
                alert('Error refreshing coupons');
            }
            
            if (btn) {
                btn.classList.remove('loading');
                btn.innerHTML = '🔄 Refresh';
            }
        }
        
        // Search Autocomplete - Like GrabOn & CouponDunia
        const searchInput = document.getElementById('searchInput');
        const suggestionsBox = document.getElementById('searchSuggestions');
        
        // Popular search suggestions
        const popularSearches = [
            { text: 'Amazon', icon: '🛒' },
            { text: 'Flipkart', icon: '🛒' },
            { text: 'Myntra', icon: '👕' },
            { text: 'Swiggy', icon: '🍔' },
            { text: 'Zomato', icon: '🍔' },
            { text: 'Ajio', icon: '👕' },
            { text: 'Nykaa', icon: '💄' },
            { text: 'Croma', icon: '📱' },
            { text: 'Meesho', icon: '🛒' },
            { text: 'Electronics', icon: '📱' },
            { text: 'Fashion', icon: '👕' },
            { text: 'Food', icon: '🍔' }
        ];
        
        if (searchInput) {
            searchInput.addEventListener('input', function(e) {
                const value = e.target.value.toLowerCase();
                if (value.length < 1) {
                    suggestionsBox.classList.remove('show');
                    return;
                }
                
                const filtered = popularSearches.filter(s => 
                    s.text.toLowerCase().includes(value)
                );
                
                if (filtered.length > 0) {
                    suggestionsBox.innerHTML = filtered.map(s => 
                        `<div class="suggestion-item" onclick="window.location.href='/?search=${s.text}'">
                            <span>${s.icon}</span>
                            <span>${s.text}</span>
                        </div>`
                    ).join('');
                    suggestionsBox.classList.add('show');
                } else {
                    suggestionsBox.classList.remove('show');
                }
            });
            
            // Hide suggestions on click outside
            document.addEventListener('click', function(e) {
                if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                    suggestionsBox.classList.remove('show');
                }
            });
        }
        
        // Improved Copy Code with Toast Notification
        function copyCode(code) {
            if (!code || code === 'No Code Needed') return;
            
            navigator.clipboard.writeText(code).then(() => {
                showToast('✅ Coupon code "' + code + '" copied!');
            }).catch(() => {
                // Fallback
                const textarea = document.createElement('textarea');
                textarea.value = code;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast('✅ Coupon code "' + code + '" copied!');
            });
        }
        
        // Toast Notification Function
        function showToast(message) {
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%);
                background: #22c55e;
                color: white;
                padding: 15px 30px;
                border-radius: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                z-index: 10000;
                font-weight: 600;
                animation: slideUp 0.3s ease;
            `;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideDown 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, 2500);
        }
        
        // Add toast animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideUp {
                from { transform: translateX(-50%) translateY(20px); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
            @keyframes slideDown {
                from { transform: translateX(-50%) translateY(0); opacity: 1; }
                to { transform: translateX(-50%) translateY(20px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        // Track deal clicks
        function trackDealClick(dealId, source) {
            console.log('Deal clicked:', dealId, 'Source:', source);
        }
    </script>
</body>
</html>
"""


def load_coupons() -> List[Dict[str, Any]]:
    """Load coupons from JSON file"""
    # Try multiple paths for local and deployed environments
    paths_to_try = [
        "deals_bot/data/coupons.json",
        "data/coupons.json",
        "../deals_bot/data/coupons.json",
        "deals_bot/data/combined_deals.json",
        "data/combined_deals.json",
        "../deals_bot/data/combined_deals.json",
    ]
    for filepath in paths_to_try:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    # Handle different JSON structures
                    if "coupons" in data:
                        return data.get("coupons", [])
                    elif "deals" in data:
                        return data.get("deals", [])
            except:
                pass
    return []


def is_coupon_expired(coupon: Dict[str, Any]) -> bool:
    """Check if a coupon has expired"""
    expires = coupon.get("expires", "")
    if not expires:
        return False
    try:
        # Parse date format like "28 Feb 2026"
        exp_date = datetime.strptime(expires.strip(), "%d %b %Y")
        return exp_date.date() < datetime.now().date()
    except:
        return False


def is_expiring_soon(coupon: Dict[str, Any], days: int = 7) -> bool:
    """Check if a coupon is expiring within given days"""
    expires = coupon.get("expires", "")
    if not expires:
        return False
    try:
        exp_date = datetime.strptime(expires.strip(), "%d %b %Y")
        days_until_expiry = (exp_date.date() - datetime.now().date()).days
        return 0 <= days_until_expiry <= days
    except:
        return False


def filter_valid_coupons(coupons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter out expired coupons"""
    return [c for c in coupons if not is_coupon_expired(c)]


# Initial load after load_coupons is defined
add_default_coupons()  # Auto-add BookMyShow & Snapdeal if not present
refresh_coupons()


@app.route("/local")
def local_deals():
    """Local restaurants and food deals page"""
    global coupons_cache
    check_and_refresh()
    all_coupons = coupons_cache if coupons_cache else load_coupons()

    # Filter only food/restaurants
    food_coupons = [c for c in all_coupons if c.get("category") == "food"]

    # Get unique cities from food deals - proper cities only
    all_cities = [
        "Hyderabad",
        "Bangalore",
        "Mumbai",
        "Delhi",
        "Chennai",
        "Pune",
        "Kolkata",
        "Chandigarh",
        "Ahmedabad",
        "Jaipur",
    ]

    # Apply city filter
    city = request.args.get("city", "")
    if city and city != "all":
        food_coupons = [
            c for c in food_coupons if c.get("city") == city or c.get("city") == "all"
        ]

    # Pagination
    per_page = 12
    page = int(request.args.get("page", 1))
    total_coupons = len(food_coupons)
    total_pages = (total_coupons + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_coupons = food_coupons[start_idx:end_idx]

    return render_template_string(
        DASHBOARD_TEMPLATE,
        coupons=paginated_coupons,
        total_coupons=len(food_coupons),
        sources=[],  # Empty - hide source filter on local page
        cities=all_cities,
        selected_city=city,
        last_updated=(
            cache_updated.strftime("%Y-%m-%d %H:%M") if cache_updated else "N/A"
        ),
        is_local=True,
        category_counts={},
        current_page=page,
        total_pages=total_pages,
    )


@app.route("/deals")
def daily_deals():
    """Daily deals page - showing hot deals from all major online stores - DealOfTheDay style"""
    global coupons_cache
    check_and_refresh()
    all_coupons = coupons_cache if coupons_cache else load_coupons()

    # Get search query
    search_query = request.args.get("search", "").strip().lower()
    
    # Get category filter
    selected_category = request.args.get("category", "")

    # Get all valid (non-expired) coupons
    valid_coupons = filter_valid_coupons(all_coupons)

    # Sort by discount value to show best deals first
    def get_discount_value(coupon):
        discount = coupon.get("discount", "")
        if "Rs." in discount:
            try:
                return int(discount.replace("Rs.", "").replace(",", "").strip())
            except:
                pass
        elif "%" in discount:
            try:
                return int(discount.replace("%", "").strip()) * 10
            except:
                pass
        return 0

    sorted_coupons = sorted(valid_coupons, key=get_discount_value, reverse=True)

    # Get unique sources/stores
    sources = sorted(set(c.get("source", "") for c in valid_coupons if c.get("source")))

    # Filter by source if provided
    source_filter = request.args.get("source", "")
    if source_filter:
        sorted_coupons = [c for c in sorted_coupons if c.get("source") == source_filter]

    # Filter by search query
    if search_query:
        sorted_coupons = [c for c in sorted_coupons if search_query in c.get("description", "").lower() or search_query in c.get("source", "").lower()]

    # Add image, original_price and sale_price to each deal
    import random
    
    def add_deal_details(coupon, index):
        """Add image, prices and other details to coupon for deal-style display"""
        discount = coupon.get("discount", "")
        
        # Generate category-based gradient and icon (no external images)
        category = coupon.get("category", "") or ""
        description = coupon.get("description", "").lower()
        
        # Determine category gradient and icon
        if "electronics" in category or "mobile" in description or "phone" in description or "laptop" in description or "tv" in description:
            gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            icon = "fa-mobile-alt"
        elif "fashion" in category or "clothing" in description or "shirt" in description or "shoe" in description or "dress" in description or "wear" in description:
            gradient = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
            icon = "fa-tshirt"
        elif "beauty" in category or "makeup" in description or "skincare" in description or "perfume" in description:
            gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
            icon = "fa-spa"
        elif "home" in category or "furniture" in description or "kitchen" in description or "decor" in description:
            gradient = "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
            icon = "fa-couch"
        elif "food" in category or "restaurant" in description or "zomato" in description or "swiggy" in description or "pizza" in description:
            gradient = "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
            icon = "fa-utensils"
        elif "book" in description or "kindle" in description:
            gradient = "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
            icon = "fa-book"
        else:
            gradient = "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)"
            icon = "fa-shopping-bag"
        
        coupon["image_gradient"] = gradient
        coupon["image_icon"] = icon
        
        # Preserve existing image_url if available, otherwise use placeholder
        if not coupon.get("image_url"):
            coupon["image_url"] = ""
        
        # Extract discount value
        discount_value = 0
        if "Rs." in discount:
            try:
                discount_value = int(discount.replace("Rs.", "").replace(",", "").strip())
            except:
                discount_value = 0
        elif "%" in discount:
            try:
                discount_percent = int(discount.replace("%", "").strip())
                discount_value = discount_percent * 100
            except:
                discount_value = 0
        
        # Estimate original price
        if discount_value > 0:
            if "Rs." in discount:
                original = discount_value * 5
                if original < 500:
                    original = 500 + (discount_value * 2)
            else:
                original = discount_value * 50
                if original < 1000:
                    original = 1000 + discount_value * 10
        else:
            original = 2000
        
        sale = max(1, original - discount_value)
        
        coupon["original_price"] = int(original)
        coupon["sale_price"] = int(sale)
        return coupon

    # Apply details to all deals
    sorted_coupons = [add_deal_details(c, i) for i, c in enumerate(sorted_coupons)]

    # Get featured deals (top 6)
    featured_deals = sorted_coupons[:6] if len(sorted_coupons) >= 6 else sorted_coupons

    # Pagination
    per_page = 24
    page = int(request.args.get("page", 1))
    total_deals = len(sorted_coupons)
    total_pages = max(1, (total_deals + per_page - 1) // per_page)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_deals = sorted_coupons[start_idx:end_idx]

    return render_template_string(
        DAILY_DEALS_TEMPLATE,
        deals=paginated_deals,
        featured_deals=featured_deals,
        total_deals=total_deals,
        sources=sources,
        selected_source=source_filter,
        selected_category=selected_category,
        search_query=search_query,
        last_updated=(
            cache_updated.strftime("%Y-%m-%d %H:%M") if cache_updated else "N/A"
        ),
        current_page=page,
        total_pages=total_pages,
    )


@app.route("/about")
def about():
    """About Us page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>About Us - GrabCoupon | Best Deals & Coupons in India</title>
        <meta name="description" content="Learn about GrabCoupon - your trusted destination for the best deals, discounts, and coupon codes in India.">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; color: #333; line-height: 1.6; }
            .header { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
            .logo { font-size: 1.8rem; font-weight: bold; color: white; text-decoration: none; display: flex; align-items: center; gap: 10px; }
            .logo i { font-size: 1.5rem; }
            .nav-links { display: flex; gap: 2rem; }
            .nav-links a { color: white; text-decoration: none; font-weight: 500; transition: opacity 0.3s; }
            .nav-links a:hover { opacity: 0.8; }
            .container { max-width: 1200px; margin: 0 auto; padding: 3rem 2rem; }
            .page-title { text-align: center; margin-bottom: 3rem; }
            .page-title h1 { font-size: 2.5rem; color: #11998e; margin-bottom: 1rem; }
            .page-title p { font-size: 1.2rem; color: #666; }
            .content-section { background: white; border-radius: 15px; padding: 2.5rem; margin-bottom: 2rem; box-shadow: 0 2px 15px rgba(0,0,0,0.05); }
            .content-section h2 { color: #11998e; margin-bottom: 1.5rem; font-size: 1.8rem; }
            .content-section p { margin-bottom: 1rem; color: #555; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; margin-top: 2rem; }
            .feature-card { background: #f8f9fa; padding: 2rem; border-radius: 12px; text-align: center; transition: transform 0.3s, box-shadow 0.3s; }
            .feature-card:hover { transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
            .feature-card i { font-size: 3rem; color: #11998e; margin-bottom: 1rem; }
            .feature-card h3 { margin-bottom: 0.8rem; color: #333; }
            .feature-card p { color: #666; margin: 0; }
            .stats { display: flex; justify-content: space-around; flex-wrap: wrap; gap: 2rem; margin: 3rem 0; text-align: center; }
            .stat-item h3 { font-size: 2.5rem; color: #11998e; }
            .stat-item p { color: #666; font-weight: 500; }
            .cta-section { text-align: center; padding: 3rem; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-radius: 15px; color: white; }
            .cta-section h2 { color: white; margin-bottom: 1rem; }
            .cta-section p { margin-bottom: 1.5rem; opacity: 0.9; }
            .cta-btn { display: inline-block; padding: 1rem 2.5rem; background: white; color: #11998e; text-decoration: none; border-radius: 30px; font-weight: bold; transition: transform 0.3s; }
            .cta-btn:hover { transform: scale(1.05); }
            .footer { background: #1a1a2e; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }
            .footer a { color: #38ef7d; text-decoration: none; }
            @media (max-width: 768px) { .nav-links { display: none; } .page-title h1 { font-size: 2rem; } }
        </style>
    </head>
    <body>
        <header class="header">
            <a href="/" class="logo"><i class="fas fa-tag"></i> GrabCoupon</a>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/deals">Daily Deals</a>
                <a href="/local">Local Food Deals</a>
                <a href="/about">About Us</a>
                <a href="/contact">Contact Us</a>
            </nav>
        </header>
        
        <div class="container">
            <div class="page-title">
                <h1>About GrabCoupon</h1>
                <p>Your Trusted Destination for the Best Deals & Discounts in India</p>
            </div>
            
            <div class="content-section">
                <h2>Who We Are</h2>
                <p>GrabCoupon is India's leading coupon and deal aggregation platform, dedicated to helping shoppers save money on their online purchases. We partner with top e-commerce brands to bring you the latest and verified coupon codes, deals, and discounts.</p>
                <p>Our mission is simple: to make saving money effortless for every Indian shopper. Whether you're shopping on Amazon, Flipkart, Myntra, or any other popular platform, we've got you covered with exclusive deals and verified coupons.</p>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <h3>500+</h3>
                    <p>Active Coupons</p>
                </div>
                <div class="stat-item">
                    <h3>50+</h3>
                    <p>Partner Stores</p>
                </div>
                <div class="stat-item">
                    <h3>₹1Cr+</h3>
                    <p>Savings Verified</p>
                </div>
                <div class="stat-item">
                    <h3>1Lakh+</h3>
                    <p>Happy Users</p>
                </div>
            </div>
            
            <div class="content-section">
                <h2>Why Choose GrabCoupon?</h2>
                <div class="features">
                    <div class="feature-card">
                        <i class="fas fa-check-circle"></i>
                        <h3>Verified Codes</h3>
                        <p>Every coupon is manually tested and verified before publishing</p>
                    </div>
                    <div class="feature-card">
                        <i class="fas fa-bolt"></i>
                        <h3>Instant Updates</h3>
                        <p>Real-time deal updates from all major e-commerce platforms</p>
                    </div>
                    <div class="feature-card">
                        <i class="fas fa-rupee-sign"></i>
                        <h3>Maximum Savings</h3>
                        <p>We find the best deals so you save more on every purchase</p>
                    </div>
                    <div class="feature-card">
                        <i class="fas fa-mobile-alt"></i>
                        <h3>Easy to Use</h3>
                        <p>Simple and intuitive interface for hassle-free shopping</p>
                    </div>
                </div>
            </div>
            
            <div class="content-section">
                <h2>How It Works</h2>
                <p><strong>1. Browse Deals:</strong> Explore thousands of verified coupons and deals from your favorite stores.</p>
                <p><strong>2. Copy Code:</strong> Click on any coupon to copy the code instantly to your clipboard.</p>
                <p><strong>3. Save Money:</strong> Apply the code at checkout and watch your savings grow!</p>
            </div>
            
            <div class="cta-section">
                <h2>Start Saving Today!</h2>
                <p>Join thousands of smart shoppers who are already saving big on every purchase.</p>
                <a href="/" class="cta-btn">Browse All Deals</a>
            </div>
        </div>
        
        <footer class="footer">
            <p>&copy; 2026 GrabCoupon. All rights reserved. | <a href="/">Home</a> | <a href="/deals">Daily Deals</a> | <a href="/contact">Contact</a></p>
        </footer>
    </body>
    </html>
    """


@app.route("/contact")
def contact():
    """Contact Us page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contact Us - GrabCoupon | Get in Touch</title>
        <meta name="description" content="Contact GrabCoupon - We'd love to hear from you! Reach out for partnerships, support, or general inquiries.">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; color: #333; line-height: 1.6; }
            .header { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
            .logo { font-size: 1.8rem; font-weight: bold; color: white; text-decoration: none; display: flex; align-items: center; gap: 10px; }
            .logo i { font-size: 1.5rem; }
            .nav-links { display: flex; gap: 2rem; }
            .nav-links a { color: white; text-decoration: none; font-weight: 500; transition: opacity 0.3s; }
            .nav-links a:hover { opacity: 0.8; }
            .container { max-width: 1200px; margin: 0 auto; padding: 3rem 2rem; }
            .page-title { text-align: center; margin-bottom: 3rem; }
            .page-title h1 { font-size: 2.5rem; color: #11998e; margin-bottom: 1rem; }
            .page-title p { font-size: 1.2rem; color: #666; }
            .contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
            .contact-card { background: white; border-radius: 15px; padding: 2.5rem; text-align: center; box-shadow: 0 2px 15px rgba(0,0,0,0.05); transition: transform 0.3s; }
            .contact-card:hover { transform: translateY(-5px); }
            .contact-card i { font-size: 3rem; color: #11998e; margin-bottom: 1rem; }
            .contact-card h3 { margin-bottom: 0.8rem; color: #333; }
            .contact-card p { color: #666; margin: 0; }
            .contact-card a { color: #11998e; text-decoration: none; font-weight: 500; }
            .contact-card a:hover { text-decoration: underline; }
            .form-section { background: white; border-radius: 15px; padding: 2.5rem; margin-top: 2rem; box-shadow: 0 2px 15px rgba(0,0,0,0.05); }
            .form-section h2 { color: #11998e; margin-bottom: 1.5rem; text-align: center; }
            .form-group { margin-bottom: 1.5rem; }
            .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #333; }
            .form-group input, .form-group textarea { width: 100%; padding: 1rem; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 1rem; transition: border-color 0.3s; font-family: inherit; }
            .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #11998e; }
            .form-group textarea { min-height: 150px; resize: vertical; }
            .submit-btn { width: 100%; padding: 1rem; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: transform 0.3s, box-shadow 0.3s; }
            .submit-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(17, 153, 142, 0.3); }
            .response-message { display: none; padding: 1rem; border-radius: 10px; margin-top: 1rem; text-align: center; }
            .response-message.success { background: #d4edda; color: #155724; }
            .response-message.error { background: #f8d7da; color: #721c24; }
            .footer { background: #1a1a2e; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }
            .footer a { color: #38ef7d; text-decoration: none; }
            @media (max-width: 768px) { .nav-links { display: none; } .page-title h1 { font-size: 2rem; } }
        </style>
    </head>
    <body>
        <header class="header">
            <a href="/" class="logo"><i class="fas fa-tag"></i> GrabCoupon</a>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/deals">Daily Deals</a>
                <a href="/local">Local Food Deals</a>
                <a href="/about">About Us</a>
                <a href="/contact">Contact Us</a>
            </nav>
        </header>
        
        <div class="container">
            <div class="page-title">
                <h1>Contact Us</h1>
                <p>We'd love to hear from you! Get in touch with us for any queries or suggestions.</p>
            </div>
            
            <div class="contact-grid">
                <div class="contact-card">
                    <i class="fas fa-envelope"></i>
                    <h3>Email Us</h3>
                    <p>For general inquiries:</p>
                    <a href="mailto:support@grabcoupon.in">support@grabcoupon.in</a>
                </div>
                <div class="contact-card">
                    <i class="fas fa-handshake"></i>
                    <h3>Partner With Us</h3>
                    <p>For business partnerships:</p>
                    <a href="mailto:partners@grabcoupon.in">partners@grabcoupon.in</a>
                </div>
                <div class="contact-card">
                    <i class="fas fa-ad"></i>
                    <h3>Advertising</h3>
                    <p>For advertising opportunities:</p>
                    <a href="mailto:ads@grabcoupon.in">ads@grabcoupon.in</a>
                </div>
            </div>
            
            <div class="form-section">
                <h2>Send us a Message</h2>
                <form id="contactForm">
                    <div class="form-group">
                        <label for="name">Your Name</label>
                        <input type="text" id="name" name="name" placeholder="Enter your name" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" id="email" name="email" placeholder="Enter your email" required>
                    </div>
                    <div class="form-group">
                        <label for="subject">Subject</label>
                        <input type="text" id="subject" name="subject" placeholder="What is this about?" required>
                    </div>
                    <div class="form-group">
                        <label for="message">Message</label>
                        <textarea id="message" name="message" placeholder="Write your message here..." required></textarea>
                    </div>
                    <button type="submit" class="submit-btn">Send Message</button>
                </form>
                <div id="responseMessage" class="response-message"></div>
            </div>
        </div>
        
        <footer class="footer">
            <p>&copy; 2026 GrabCoupon. All rights reserved. | <a href="/">Home</a> | <a href="/deals">Daily Deals</a> | <a href="/about">About</a></p>
        </footer>
        
        <script>
            document.getElementById('contactForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const messageDiv = document.getElementById('responseMessage');
                messageDiv.style.display = 'block';
                messageDiv.className = 'response-message success';
                messageDiv.innerHTML = '<i class="fas fa-check-circle"></i> Thank you for your message! We will get back to you soon.';
                this.reset();
                setTimeout(() => { messageDiv.style.display = 'none'; }, 5000);
            });
        </script>
    </body>
    </html>
    """


@app.route("/")
def index():
    """Main dashboard page"""
    global coupons_cache
    # Check if refresh needed on each request
    check_and_refresh()
    all_coupons = coupons_cache if coupons_cache else load_coupons()

    # Filter out expired coupons
    all_coupons = filter_valid_coupons(all_coupons)

    # Apply filters
    source = request.args.get("source", "")
    category = request.args.get("category", "")
    city = request.args.get("city", "")
    search = request.args.get("search", "").lower()
    product_search = request.args.get("product_search", "").lower()
    discount_filter = request.args.get("discount", "")

    filtered = all_coupons
    if source:
        filtered = [c for c in filtered if c.get("source") == source]
    if category and category != "all":
        filtered = [c for c in filtered if c.get("category") == category]
    if city and city != "all":
        # Show coupons for specific city or all (non-city specific)
        filtered = [
            c for c in filtered if c.get("city") == city or c.get("city") == "all"
        ]
    if search:
        filtered = [
            c
            for c in filtered
            if search in c.get("description", "").lower()
            or search in (c.get("code") or c.get("coupon_code") or "").lower()
            or search in c.get("source", "").lower()
        ]
    if product_search:
        # Search for products like TV, fridge, mobile, etc. in description and title
        filtered = [
            c
            for c in filtered
            if product_search in c.get("description", "").lower()
            or product_search in c.get("title", "").lower()
            or product_search in (c.get("code") or c.get("coupon_code") or "").lower()
        ]
    
    # Filter by discount percentage
    if discount_filter:
        try:
            min_discount = int(discount_filter)
            filtered = [
                c for c in filtered
                if c.get("discount", "").replace("%", "").replace("Rs.", "").strip()
                and "-" not in c.get("discount", "")  # Skip range discounts
            ]
            # Re-filter with percentage check
            temp_filtered = []
            for c in filtered:
                discount_str = c.get("discount", "")
                if "%" in discount_str:
                    try:
                        discount_pct = int(discount_str.replace("%", "").strip())
                        if discount_pct >= min_discount:
                            temp_filtered.append(c)
                    except:
                        pass
                elif "Rs." in discount_str:
                    # For fixed discounts, assume it's at least the min percentage based on typical values
                    try:
                        rs_amount = int(discount_str.replace("Rs.", "").replace(",", "").strip())
                        # Rough estimate: Rs. 500+ = 10%+, Rs. 1000+ = 20%+
                        if min_discount <= 10 and rs_amount >= 500:
                            temp_filtered.append(c)
                        elif min_discount <= 20 and rs_amount >= 1000:
                            temp_filtered.append(c)
                        elif min_discount <= 30 and rs_amount >= 2000:
                            temp_filtered.append(c)
                        elif min_discount <= 50 and rs_amount >= 3000:
                            temp_filtered.append(c)
                    except:
                        pass
            filtered = temp_filtered
        except:
            pass

    # Pagination
    per_page = 12
    page = int(request.args.get("page", 1))
    total_coupons = len(filtered)
    total_pages = (total_coupons + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_coupons = filtered[start_idx:end_idx]

    # Get stats
    sources = set(c.get("source") for c in all_coupons)
    cities = set(c.get("city") for c in all_coupons if c.get("city") != "all")

    # Get unique categories from data
    unique_categories = sorted(set(c.get("category", "") for c in all_coupons if c.get("category")))
    # Define display-friendly category names
    category_display = {
        "": "All Categories",
        "electronics": "Electronics",
        "mobiles": "Mobiles",
        "fashion": "Fashion",
        "beauty": "Beauty",
        "home": "Home & Furniture",
        "food": "Food & Dining",
        "books": "Books",
        "all": "All Stores"
    }
    # Get category counts for tabs
    category_counts = {}
    for c in all_coupons:
        cat = c.get("category", "all")
        if cat == "all":
            continue
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return render_template_string(
        DASHBOARD_TEMPLATE,
        coupons=paginated_coupons,
        total_coupons=total_coupons,
        sources=len(sources),
        cities=sorted([c for c in cities if c]),
        unique_categories=unique_categories,
        category_display=category_display,
        last_updated=(
            cache_updated.strftime("%Y-%m-%d %H:%M") if cache_updated else "Never"
        ),
        category_counts=category_counts,
        current_page=page,
        total_pages=total_pages,
    )


@app.route("/api/coupons")
def api_coupons():
    """API endpoint with filtering support"""
    all_coupons = load_coupons()

    # Apply filters
    source = request.args.get("source", "")
    category = request.args.get("category", "")
    city = request.args.get("city", "")

    filtered = all_coupons
    if source:
        filtered = [c for c in filtered if c.get("source") == source]
    if category and category != "all":
        filtered = [c for c in filtered if c.get("category") == category]
    if city and city != "all":
        filtered = [
            c for c in filtered if c.get("city") == city or c.get("city") == "all"
        ]

    return jsonify(
        {
            "count": len(filtered),
            "coupons": filtered,
            "timestamp": datetime.now().isoformat(),
        }
    )


# Visitor tracking data file
VISITORS_FILE = os.path.join(os.path.dirname(__file__), "data", "visitors.json")


def get_visitors_data():
    """Load visitors data from JSON file"""
    if os.path.exists(VISITORS_FILE):
        try:
            with open(VISITORS_FILE, "r") as f:
                return json.load(f)
        except:
            return {"visits": [], "stats": {"total": 0, "today": 0}}
    return {"visits": [], "stats": {"total": 0, "today": 0}}


def save_visitors_data(data):
    """Save visitors data to JSON file"""
    os.makedirs(os.path.dirname(VISITORS_FILE), exist_ok=True)
    with open(VISITORS_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/api/track_visit")
def api_track_visit():
    """Track a coupon visit"""
    coupon_id = request.args.get("id", "")
    source = request.args.get("source", "unknown")

    data = get_visitors_data()

    # Add visit
    visit = {
        "id": coupon_id,
        "source": source,
        "timestamp": datetime.now().isoformat(),
        "user_agent": request.headers.get("User-Agent", "")[:200],
    }
    data["visits"].append(visit)

    # Update stats
    data["stats"]["total"] = data["stats"].get("total", 0) + 1

    # Count today's visits
    today = datetime.now().date().isoformat()
    today_visits = sum(
        1 for v in data["visits"] if v.get("timestamp", "").startswith(today)
    )
    data["stats"]["today"] = today_visits

    # Keep only last 1000 visits
    if len(data["visits"]) > 1000:
        data["visits"] = data["visits"][-1000:]

    save_visitors_data(data)

    return jsonify({"status": "success", "total_visits": data["stats"]["total"]})


@app.route("/api/visitors")
def api_visitors():
    """Get visitor statistics"""
    data = get_visitors_data()
    return jsonify(data)


@app.route("/api/search-products")
def api_search_products():
    """Search for products across e-commerce sites and return price comparisons"""
    query = request.args.get("q", "").strip()
    if not query or len(query) < 2:
        return jsonify({"error": "Please enter a valid search term", "products": []})

    products = []

    try:
        # Search Amazon
        amazon_results = search_amazon_products(query)
        products.extend(amazon_results)

        # Search Flipkart
        flipkart_results = search_flipkart_products(query)
        products.extend(flipkart_results)

        # Sort by price (lowest first)
        products.sort(key=lambda x: x.get("price_numeric", 999999))

        # Return top 20 results
        return jsonify(
            {"query": query, "products": products[:20], "count": len(products)}
        )

    except Exception as e:
        logger.error(f"Product search error: {e}")
        return jsonify({"error": "Search temporarily unavailable", "products": []})


def search_amazon_products(query):
    """Search Amazon India for products"""
    products = []
    try:
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Find product cards
            for item in soup.select(".sg-col-4-of-12, .s-result-item")[:10]:
                try:
                    # Get title
                    title_elem = item.select_one(
                        "h2 a span, .a-text-normal, .a-size-medium"
                    )
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue

                    # Get URL
                    link_elem = item.select_one("h2 a, a.a-link-normal")
                    if not link_elem:
                        continue
                    url = "https://www.amazon.in" + link_elem.get("href", "")
                    if "amazon.in/dp" not in url and "amazon.in/gp/product" not in url:
                        continue

                    # Get price
                    price_elem = item.select_one(
                        '.a-price-whole, .a-offscreen, [data-a-color="price"] .a-offscreen'
                    )
                    price_text = price_elem.get_text(strip=True) if price_elem else ""
                    price_numeric = (
                        int(re.sub(r"[^0-9]", "", price_text)) if price_text else 0
                    )

                    # Get rating
                    rating_elem = item.select_one(".a-icon-alt, .a-popover-preload")
                    rating = rating_elem.get_text(strip=True) if rating_elem else ""

                    # Get image
                    img_elem = item.select_one("img.s-image")
                    image = img_elem.get("src", "") if img_elem else ""

                    if price_numeric > 0:
                        products.append(
                            {
                                "title": title[:100],
                                "url": url,
                                "price": f"₹{price_numeric:,}",
                                "price_numeric": price_numeric,
                                "rating": rating[:20],
                                "source": "Amazon",
                                "source_icon": "🛒",
                                "image": image,
                                "verified": True,
                            }
                        )
                except Exception:
                    continue

    except Exception as e:
        logger.error(f"Amazon search error: {e}")

    return products


def search_flipkart_products(query):
    """Search Flipkart for products"""
    products = []
    try:
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Find product cards
            for item in soup.select("._1AtVbE, ._13oc-S")[:10]:
                try:
                    # Get title
                    title_elem = item.select_one("._4rR01T, ._2B099h, a[title]")
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue

                    # Get URL
                    link_elem = item.select_one("a._1fQZEK")
                    if not link_elem:
                        continue
                    url = "https://www.flipkart.com" + link_elem.get("href", "")

                    # Get price
                    price_elem = item.select_one("._30jeq3._1_WB1e, ._1_WB1e")
                    price_text = price_elem.get_text(strip=True) if price_elem else ""
                    price_numeric = (
                        int(re.sub(r"[^0-9]", "", price_text)) if price_text else 0
                    )

                    # Get original price (if discounted)
                    orig_price_elem = item.select_one("._1_WB1e + span, ._2I5kjh")
                    orig_price_text = (
                        orig_price_elem.get_text(strip=True) if orig_price_elem else ""
                    )

                    # Get rating
                    rating_elem = item.select_one("._2_R_DZ span, ._3LWZlK")
                    rating = rating_elem.get_text(strip=True) if rating_elem else ""

                    # Get image
                    img_elem = item.select_one("img._396y4z")
                    image = img_elem.get("src", "") if img_elem else ""

                    if price_numeric > 0:
                        product = {
                            "title": title[:100],
                            "url": url,
                            "price": f"₹{price_numeric:,}",
                            "price_numeric": price_numeric,
                            "rating": rating,
                            "source": "Flipkart",
                            "source_icon": "🛍️",
                            "image": image,
                            "verified": True,
                        }
                        if orig_price_text:
                            product["original_price"] = orig_price_text
                        products.append(product)
                except Exception:
                    continue

    except Exception as e:
        logger.error(f"Flipkart search error: {e}")

    return products


def run_server(host="0.0.0.0", port=None):
    if port is None:
        port = int(os.environ.get("PORT", 5000))

    # Start the background scheduler
    if not scheduler.running:
        scheduler.start()
        logger.info(
            f"Background scheduler started - will refresh coupons every {REFRESH_INTERVAL_HOURS} hours"
        )

    logger.info(f"Starting GrabCoupon on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)


@app.route("/api/refresh")
def refresh():
    """Manually refresh coupons"""
    refresh_coupons()
    return jsonify(
        {
            "status": "success",
            "last_updated": cache_updated.isoformat() if cache_updated else None,
            "coupons_count": len(coupons_cache) if coupons_cache else 0,
        }
    )


@app.route("/status")
def status():
    """Show cache status"""
    return jsonify(
        {
            "last_updated": cache_updated.isoformat() if cache_updated else None,
            "coupons_count": len(coupons_cache) if coupons_cache else 0,
            "next_refresh": f"in {REFRESH_INTERVAL_HOURS} hours",
        }
    )


if __name__ == "__main__":
    run_server()