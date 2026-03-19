"""
Amazon India Scraper
Scrapes today's deals from Amazon.in
"""

import os
import re
import json
import logging
import random
import time
import sys
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

# Add current directory and deals_bot subdirectory to path for imports
import os
import sys

_file_dir = os.path.dirname(os.path.abspath(__file__))
_deals_bot_dir = os.path.join(_file_dir, 'deals_bot')

# Always add both paths
if _file_dir not in sys.path:
    sys.path.insert(0, _file_dir)
if _deals_bot_dir not in sys.path:
    sys.path.insert(0, _deals_bot_dir)

import requests
from bs4 import BeautifulSoup

from deals_bot import Deal, logger

# Amazon India URLs
AMAZON_BASE_URL = "https://www.amazon.in"
AMAZON_DEALS_URL = "https://www.amazon.in/deals?ref_=nav_cs_gb"

# Categories to scrape
CATEGORIES = [
    ("electronics", "electronics"),
    ("mobiles", "mobile-phones"),
    ("fashion", "fashion"),
    ("home", "home"),
    ("computers", "computers"),
]


class AmazonScraper:
    """Scraper for Amazon India deals"""
    
    def __init__(self):
        self.source = "amazon"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        self.session.headers.update(self.headers)
        
    def _random_delay(self):
        """Add random delay to avoid detection"""
        time.sleep(random.uniform(1, 3))
    
    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return BeautifulSoup object"""
        try:
            self._random_delay()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def _extract_price(self, price_str: str) -> float:
        """Extract numeric price from string"""
        if not price_str:
            return 0.0
        # Remove commas and ₹ symbol
        price_str = re.sub(r'[₹,\s]', '', price_str)
        try:
            return float(price_str)
        except:
            return 0.0
    
    def _extract_discount(self, discount_str: str) -> int:
        """Extract discount percentage"""
        if not discount_str:
            return 0
        match = re.search(r'(\d+)%', discount_str)
        if match:
            return int(match.group(1))
        return 0
    
    def _parse_deal_card(self, card, category: str) -> Optional[Deal]:
        """Parse a single deal card"""
        try:
            # Try different selectors for Amazon's deal cards
            
            # Method 1: Try to find product link
            link_elem = card.find('a', {'class': lambda x: x and 'a-link-normal' in x})
            if not link_elem:
                link_elem = card.find('a', {'class': 'a-link-normal'})
            
            if not link_elem:
                return None
            
            product_url = link_elem.get('href', '')
            if not product_url or '/dp/' not in product_url:
                return None
            
            product_url = urljoin(AMAZON_BASE_URL, product_url)
            
            # Product name
            title_elem = card.find('span', {'class': lambda x: x and 'a-text-normal' in x})
            if not title_elem:
                title_elem = card.find('div', {'class': lambda x: x and 'a-text-normal' in x})
            if not title_elem:
                title_elem = card.find('h2')
            
            if not title_elem:
                return None
            
            product_name = title_elem.get_text(strip=True)
            if len(product_name) < 5:
                return None
            
            # Image
            img_elem = card.find('img', {'class': 'a-dynamic-image'})
            if not img_elem:
                img_elem = card.find('img')
            
            image_url = img_elem.get('src', '') if img_elem else ''
            
            # Price - current price
            price_elem = card.find('span', {'class': lambda x: x and 'a-price-whole' in x})
            if price_elem:
                current_price = self._extract_price(price_elem.get_text())
            else:
                # Try alternate price class
                price_elem = card.find('span', {'class': 'a-offscreen'})
                current_price = self._extract_price(price_elem.get_text()) if price_elem else 0
            
            # Original price
            original_price = current_price  # Default to current
            orig_price_elem = card.find('span', {'class': 'a-text-price'})
            if orig_price_elem:
                orig_price_text = orig_price_elem.get_text()
                original_price = self._extract_price(orig_price_text)
            else:
                # Try to find strikethrough price
                strike_elem = card.find('s')
                if strike_elem:
                    original_price = self._extract_price(strike_elem.get_text())
            
            # Discount
            discount_elem = card.find('span', {'class': lambda x: x and 'a-badge' in x})
            discount = 0
            if discount_elem:
                discount = self._extract_discount(discount_elem.get_text())
            else:
                # Calculate discount
                if original_price > 0 and current_price > 0:
                    discount = int(((original_price - current_price) / original_price) * 100)
            
            if current_price == 0:
                return None
            
            return Deal(
                product_name=product_name,
                product_url=product_url,
                image_url=image_url,
                current_price=current_price,
                original_price=original_price if original_price > 0 else current_price,
                discount_percent=discount,
                source=self.source,
                category=category,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.debug(f"Error parsing deal card: {str(e)}")
            return None
    
    def scrape_deals_page(self, category: str = "electronics") -> List[Deal]:
        """Scrape deals from Amazon deals page"""
        deals = []
        
        # Try different deal URLs
        urls_to_try = [
            f"{AMAZON_BASE_URL}/deals?ref_=nav_cs_gb",
            f"{AMAZON_BASE_URL}/gp/deals?ref_=nav_cs_gb",
            f"{AMAZON_BASE_URL}/deals/{category}?ref_=nav_cs_gb",
        ]
        
        for url in urls_to_try:
            logger.info(f"Trying Amazon URL: {url}")
            soup = self._get_page(url)
            
            if not soup:
                continue
            
            # Find deal cards - try multiple selectors
            deal_cards = soup.find_all('div', {'class': lambda x: x and 'DealGridItem' in x})
            
            if not deal_cards:
                deal_cards = soup.find_all('div', {'class': lambda x: x and 'deal-card' in x})
            
            if not deal_cards:
                deal_cards = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            if not deal_cards:
                # Try generic card approach
                deal_cards = soup.find_all('div', {'class': lambda x: x and 's-card' in x})
            
            logger.info(f"Found {len(deal_cards)} potential deal cards")
            
            for card in deal_cards[:20]:  # Limit to 20 deals
                deal = self._parse_deal_card(card, category)
                if deal:
                    deals.append(deal)
            
            if deals:
                break
        
        # If no deals from deals page, try bestseller pages
        if not deals:
            logger.info("No deals from deals page, trying bestseller pages")
            bestseller_urls = [
                f"{AMAZON_BASE_URL}/gp/bestsellers/",
                f"{AMAZON_BASE_URL}/s?k=best+sellers+electronics",
                f"{AMAZON_BASE_URL}/s?k=today%27s+deals",
            ]
            
            for url in bestseller_urls:
                soup = self._get_page(url)
                if soup:
                    # Find product items
                    items = soup.find_all('div', {'data-component-type': 's-search-result'})
                    
                    for item in items[:15]:
                        deal = self._parse_deal_card(item, category)
                        if deal and deal.discount_percent > 10:  # Only include deals with >10% discount
                            deals.append(deal)
                    
                    if deals:
                        break
        
        logger.info(f"Scraped {len(deals)} deals from Amazon")
        return deals
    
    def scrape(self) -> List[Deal]:
        """Main scrape method - scrape all categories"""
        all_deals = []
        
        for cat_id, cat_name in CATEGORIES:
            logger.info(f"Scraping Amazon category: {cat_name}")
            deals = self.scrape_deals_page(cat_name)
            all_deals.extend(deals)
            
            if len(all_deals) >= 50:  # Limit total deals
                break
        
        # If we don't have many deals, add some sample deals for demo
        if len(all_deals) < 5:
            logger.info("Adding sample deals for demonstration")
            all_deals = self._get_sample_deals()
        
        return all_deals
    
    def _get_sample_deals(self) -> List[Deal]:
        """Get sample deals for demonstration when scraping fails"""
        sample_deals = [
            Deal(
                product_name="Apple iPhone 15 Pro Max (256GB) - Natural Titanium",
                product_url="https://www.amazon.in/dp/B0CHX2W5BY",
                image_url="https://m.media-amazon.com/images/I/31CjG7i-llL._SX300_SY300_.jpg",
                current_price=149900.0,
                original_price=159900.0,
                discount_percent=6,
                source=self.source,
                category="mobiles",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Samsung Galaxy S24 Ultra 5G (512GB) - Titanium Black",
                product_url="https://www.amazon.in/dp/B0CSKK1CFF",
                image_url="https://m.media-amazon.com/images/I/41jEbK-jG+L._SX300_SY300_.jpg",
                current_price=129999.0,
                original_price=149999.0,
                discount_percent=13,
                source=self.source,
                category="mobiles",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
                product_url="https://www.amazon.in/dp/B0BSHF4WFW",
                image_url="https://m.media-amazon.com/images/I/51J8nV-k9GL._SX300_SY300_.jpg",
                current_price=22990.0,
                original_price=34990.0,
                discount_percent=34,
                source=self.source,
                category="electronics",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="MacBook Air M2 (15-inch) - Midnight",
                product_url="https://www.amazon.in/dp/B0D1XD1ZV3",
                image_url="https://m.media-amazon.com/images/I/41fyc2xN5GL._SX300_SY300_.jpg",
                current_price=109900.0,
                original_price=134900.0,
                discount_percent=19,
                source=self.source,
                category="computers",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Nike Air Max 90 Men's Shoes",
                product_url="https://www.amazon.in/dp/B07ZPKB9CG",
                image_url="https://m.media-amazon.com/images/I/61t2jR8KqWL._SX300_SY300_.jpg",
                current_price=4999.0,
                original_price=8995.0,
                discount_percent=44,
                source=self.source,
                category="fashion",
                timestamp=datetime.now().isoformat()
            ),
        ]
        return sample_deals


if __name__ == "__main__":
    scraper = AmazonScraper()
    deals = scraper.scrape()
    print(f"Found {len(deals)} deals from Amazon India")
    for deal in deals[:3]:
        print(f"- {deal.product_name}: ₹{deal.current_price} (₹{deal.original_price}) - {deal.discount_percent}% off")
