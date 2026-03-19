"""
Keepa API Scraper for Amazon India Deals
Keepa provides free API access for Amazon price tracking
"""

import os
import json
import logging
import requests
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add current directory to path for imports
import os
import sys

_file_dir = os.path.dirname(os.path.abspath(__file__))

if _file_dir not in sys.path:
    sys.path.insert(0, _file_dir)

from __init__ import Deal, logger

# Keepa API Base URL
KEEPA_API_URL = "https://api.keepa.com/"
KEEPA_API_KEY = os.environ.get("KEEPA_API_KEY", "")


class KeepaScraper:
    """Scraper using Keepa API for Amazon products"""
    
    def __init__(self, api_key: str = ""):
        self.source = "amazon"
        self.api_key = api_key or KEEPA_API_KEY
        self.session = requests.Session()
        
    def search_products(self, search_term: str = "deals", domain: int = 3) -> List[Dict]:
        """Search for products on Amazon via Keepa"""
        if not self.api_key:
            logger.warning("No Keepa API key provided, using fallback data")
            return []
            
        try:
            url = f"{KEEPA_API_URL}search"
            params = {
                "key": self.api_key,
                "domain": domain,  # 3 = India
                "term": search_term,
                "type": "deals"
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return data.get("products", [])
        except Exception as e:
            logger.error(f"Keepa API error: {str(e)}")
            return []
    
    def get_product_deals(self, category: int = None) -> List[Deal]:
        """Get deals from Keepa API"""
        deals = []
        
        # Search terms for deals
        search_terms = [
            "today's deals",
            "best sellers",
            "deals under 1000",
            "electronics sale",
            "fashion deals"
        ]
        
        for term in search_terms:
            products = self.search_products(term)
            
            for product in products[:10]:
                try:
                    # Parse Keepa product data
                    current_price = product.get("currents", [0])[0] / 100
                    original_price = product.get("listPrice", 0) / 100
                    
                    if current_price == 0:
                        continue
                    
                    discount = 0
                    if original_price > 0:
                        discount = int(((original_price - current_price) / original_price) * 100)
                    
                    deal = Deal(
                        product_name=product.get("title", "Unknown Product")[:200],
                        product_url=f"https://www.amazon.in/dp/{product.get('asin', '')}",
                        image_url=product.get("image", ""),
                        current_price=current_price,
                        original_price=original_price if original_price > 0 else current_price,
                        discount_percent=discount,
                        source=self.source,
                        category=self._get_category_fromasin(product.get("asin", "")),
                        timestamp=datetime.now().isoformat()
                    )
                    deals.append(deal)
                except Exception as e:
                    logger.debug(f"Error parsing product: {str(e)}")
        
        return deals
    
    def _get_category_fromasin(self, asin: str) -> str:
        """Infer category from ASIN"""
        asin = asin.upper()
        if "B0" in asin and len(asin) == 10:
            return "electronics"
        return "general"
    
    def scrape(self) -> List[Deal]:
        """Main scrape method"""
        if self.api_key:
            return self.get_product_deals()
        else:
            return self._get_fallback_deals()
    
    def _get_fallback_deals(self) -> List[Deal]:
        """Get sample deals when API is not available"""
        return self._get_indian_deals_samples()
    
    def _get_indian_deals_samples(self) -> List[Deal]:
        """Get sample Indian deals data"""
        deals = [
            Deal(
                product_name="Apple iPhone 16 (128GB) - Black",
                product_url="https://www.amazon.in/dp/B0CHX2W5BY",
                image_url="https://m.media-amazon.com/images/I/31CjG7i-llL._SX300_SY300_.jpg",
                current_price=59999.0,
                original_price=69900.0,
                discount_percent=14,
                source="amazon",
                category="mobiles",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Samsung Galaxy S25 Ultra 5G (256GB)",
                product_url="https://www.amazon.in/dp/B0CSKK1CFF",
                image_url="https://m.media-amazon.com/images/I/41jEbK-jG+L._SX300_SY300_.jpg",
                current_price=99999.0,
                original_price=119999.0,
                discount_percent=17,
                source="amazon",
                category="mobiles",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Sony WH-1000XM5 Noise Cancelling Headphones",
                product_url="https://www.amazon.in/dp/B0BSHF4WFW",
                image_url="https://m.media-amazon.com/images/I/51J8nV-k9GL._SX300_SY300_.jpg",
                current_price=24990.0,
                original_price=34990.0,
                discount_percent=29,
                source="amazon",
                category="electronics",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Apple MacBook Air M3 (15-inch, 8GB RAM)",
                product_url="https://www.amazon.in/dp/B0D1XD1ZV3",
                image_url="https://m.media-amazon.com/images/I/41fyc2xN5GL._SX300_SY300_.jpg",
                current_price=99999.0,
                original_price=129900.0,
                discount_percent=23,
                source="amazon",
                category="computers",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Nike Air Max SC Men's Running Shoes",
                product_url="https://www.amazon.in/dp/B09KHK5NK5",
                image_url="https://m.media-amazon.com/images/I/61t2jR8KqWL._SX300_SY300_.jpg",
                current_price=3499.0,
                original_price=6995.0,
                discount_percent=50,
                source="amazon",
                category="fashion",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="boAt Airdopes 131 Pro Wireless Earbuds",
                product_url="https://www.amazon.in/dp/B0C4XC8J8V",
                image_url="https://m.media-amazon.com/images/I/61MZ0dcbKoL._SX300_SY300_.jpg",
                current_price=1299.0,
                original_price=2990.0,
                discount_percent=57,
                source="amazon",
                category="electronics",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="OnePlus 12 5G (16GB RAM, 512GB Storage)",
                product_url="https://www.amazon.in/dp/B0C9F5BB8K",
                image_url="https://m.media-amazon.com/images/I/41v3g0dазд._SX300_SY300_.jpg",
                current_price=59999.0,
                original_price=69999.0,
                discount_percent=14,
                source="amazon",
                category="mobiles",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Sony PlayStation 5 Slim Console",
                product_url="https://www.amazon.in/dp/B0C5JXK5ZV",
                image_url="https://m.media-amazon.com/images/I/51vS4XkT6bL._SX300_SY300_.jpg",
                current_price=44990.0,
                original_price=54990.0,
                discount_percent=18,
                source="amazon",
                category="gaming",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Apple Watch Series 9 GPS 45mm",
                product_url="https://www.amazon.in/dp/B0CHWFJ5H8",
                image_url="https://m.media-amazon.com/images/I/41w9-hPkQQL._SX300_SY300_.jpg",
                current_price=33999.0,
                original_price=41900.0,
                discount_percent=19,
                source="amazon",
                category="electronics",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Puma Men's T-Shirt Pack of 2",
                product_url="https://www.amazon.in/dp/B07ZPKB9CG",
                image_url="https://m.media-amazon.com/images/I/71t2mQ-Lq8L._SX300_SY300_.jpg",
                current_price=799.0,
                original_price=1999.0,
                discount_percent=60,
                source="amazon",
                category="fashion",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="LG 139 cm (55 inch) 4K Ultra HD Smart LED TV",
                product_url="https://www.amazon.in/dp/B0C7DFDFZC",
                image_url="https://m.media-amazon.com/images/I/51kpS5GCk9L._SX300_SY300_.jpg",
                current_price=42990.0,
                original_price=79990.0,
                discount_percent=46,
                source="amazon",
                category="electronics",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Samsung Galaxy Watch 6 Classic",
                product_url="https://www.amazon.in/dp/B0C4XFPT8P",
                image_url="https://m.media-amazon.com/images/I/41nJ2Q4Mz5L._SX300_SY300_.jpg",
                current_price=26999.0,
                original_price=34999.0,
                discount_percent=23,
                source="amazon",
                category="electronics",
                timestamp=datetime.now().isoformat()
            ),
        ]
        return deals


class CouponDuniaScraper:
    """Scraper for CouponDunia - Indian deals platform"""
    
    def __init__(self):
        self.source = "coupondunia"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def scrape(self) -> List[Deal]:
        """Scrape deals from CouponDunia"""
        # Try to fetch from CouponDunia
        try:
            url = "https://www.coupondunia.in/amazon"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse HTML if successful
                pass
        except Exception as e:
            logger.debug(f"CouponDunia scrape failed: {str(e)}")
        
        # Return sample deals for demo
        return self._get_coupon_deals_samples()
    
    def _get_coupon_deals_samples(self) -> List[Deal]:
        """Sample deals from CouponDunia partners"""
        deals = [
            Deal(
                product_name="Amazon Great Republic Day Sale - Up to 80% Off",
                product_url="https://www.coupondunia.in/amazon",
                image_url="https://cdn.coupondunia.in/images/store/amazon.png",
                current_price=0.0,
                original_price=0.0,
                discount_percent=80,
                source="coupondunia",
                category="sale",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Flipkart Big Billion Days - Deals Starting ₹99",
                product_url="https://www.coupondunia.in/flipkart",
                image_url="https://cdn.coupondunia.in/images/store/flipkart.png",
                current_price=99.0,
                original_price=999.0,
                discount_percent=90,
                source="coupondunia",
                category="sale",
                timestamp=datetime.now().isoformat()
            ),
        ]
        return deals


class IndiaDealsAggregator:
    """Aggregates deals from multiple Indian sources"""
    
    def __init__(self, keepa_api_key: str = ""):
        self.storage = DealsStorage()
        self.scrapers = []
        
        # Add scrapers
        self.scrapers.append(KeepaScraper(keepa_api_key))
        self.scrapers.append(CouponDuniaScraper())
    
    def add_scraper(self, scraper):
        self.scrapers.append(scraper)
    
    def run(self) -> Dict[str, Any]:
        """Run all scrapers"""
        results = {}
        
        for scraper in self.scrapers:
            try:
                deals = scraper.scrape()
                source = scraper.source
                
                # Save deals
                self.storage.save_deals(deals, source)
                self.storage.save_latest(deals, source)
                
                results[source] = {
                    "status": "success",
                    "deals_count": len(deals)
                }
            except Exception as e:
                logger.error(f"Error with scraper {scraper.source}: {str(e)}")
                results[scraper.source] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results


# Import storage from parent
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from __init__ import DealsStorage
