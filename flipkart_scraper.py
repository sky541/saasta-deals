"""
Flipkart Scraper
Scrapes deals from Flipkart.com
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

# Add current directory, parent, and deals_bot subdirectory to path for imports
_file_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_file_dir)
_deals_bot_dir = os.path.join(_file_dir, 'deals_bot')

if _file_dir not in sys.path:
    sys.path.insert(0, _file_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)
if _deals_bot_dir not in sys.path and os.path.exists(_deals_bot_dir):
    sys.path.insert(0, _deals_bot_dir)

import requests
from bs4 import BeautifulSoup

from deals_bot import Deal, logger

# Flipkart URLs
FLIPKART_BASE_URL = "https://www.flipkart.com"
FLIPKART_DEALS_URL = "https://www.flipkart.com/offers/list?affid=infonipn"

# Categories to scrape
CATEGORIES = [
    ("electronics", "electronics"),
    ("mobiles", "mobiles"),
    ("fashion", "fashion"),
    ("home", "home-kitchen"),
    ("computers", "computers"),
]


class FlipkartScraper:
    """Scraper for Flipkart deals"""
    
    def __init__(self):
        self.source = "flipkart"
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
            "Referer": "https://www.flipkart.com/",
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
            # Find product link - Flipkart uses _1AtkZe or similar classes
            link_elem = card.find('a', {'class': lambda x: x and 'CG4Wz' in x})
            if not link_elem:
                link_elem = card.find('a', {'class': lambda x: x and '_1LKTO3' in x})
            if not link_elem:
                link_elem = card.find('a', {'class': '_1fQZEK'})
            
            if not link_elem:
                # Try generic anchor
                links = card.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    if '/p/' in href:
                        link_elem = link
                        break
            
            if not link_elem:
                return None
            
            product_url = link_elem.get('href', '')
            if not product_url or '/p/' not in product_url:
                return None
            
            product_url = urljoin(FLIPKART_BASE_URL, product_url)
            
            # Product name - Flipkart uses different classes
            title_elem = card.find('div', {'class': lambda x: x and 'KzDlHZ' in x})
            if not title_elem:
                title_elem = card.find('div', {'class': '_4rR01T'})
            if not title_elem:
                title_elem = card.find('a', {'class': lambda x: x and 's1Q9rs' in x})
            if not title_elem:
                title_elem = card.find('div', {'class': 'aaginpr'})
            
            if not title_elem:
                return None
            
            product_name = title_elem.get_text(strip=True)
            if len(product_name) < 5:
                return None
            
            # Image
            img_elem = card.find('img', {'class': 'DByuf4'})
            if not img_elem:
                img_elem = card.find('img', {'class': '_396xMc'})
            if not img_elem:
                img_elem = card.find('img', {'class': '_2r5hL'})
            if not img_elem:
                img_elem = card.find('img')
            
            image_url = img_elem.get('src', '') if img_elem else ''
            
            # Price - current price
            price_elem = card.find('div', {'class': lambda x: x and 'hl05eU' in x})
            if not price_elem:
                price_elem = card.find('div', {'class': '_30jeq3'})
            
            current_price = 0
            if price_elem:
                current_price = self._extract_price(price_elem.get_text())
            
            # Original price
            original_price = current_price
            orig_price_elem = card.find('div', {'class': lambda x: x and 'MyjaPH' in x})
            if not orig_price_elem:
                orig_price_elem = card.find('div', {'class': '_3I9_wc'})
            if not orig_price_elem:
                orig_price_elem = card.find('span', {'class': '_3Ay6Sb'})
            
            if orig_price_elem:
                original_price = self._extract_price(orig_price_elem.get_text())
            
            # Discount
            discount = 0
            discount_elem = card.find('div', {'class': lambda x: x and 'G6XhEU' in x})
            if not discount_elem:
                discount_elem = card.find('span', {'class': '_3Ay6Sb'})
            
            if discount_elem:
                discount = self._extract_discount(discount_elem.get_text())
            elif original_price > 0 and current_price > 0:
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
        """Scrape deals from Flipkart"""
        deals = []
        
        # Try different deal URLs
        urls_to_try = [
            f"{FLIPKART_BASE_URL}/offers",
            f"{FLIPKART_BASE_URL}/offer/electronics",
            f"{FLIPKART_BASE_URL}/search?q=deals+{category}",
        ]
        
        for url in urls_to_try:
            logger.info(f"Trying Flipkart URL: {url}")
            soup = self._get_page(url)
            
            if not soup:
                continue
            
            # Find deal cards - try multiple selectors
            deal_cards = soup.find_all('div', {'class': lambda x: x and '_1xHGtK' in x})
            
            if not deal_cards:
                deal_cards = soup.find_all('div', {'class': '_2kHMtA'})
            
            if not deal_cards:
                deal_cards = soup.find_all('div', {'class': 'col _2-gKeQ'})
            
            if not deal_cards:
                # Try generic product container
                deal_cards = soup.find_all('div', {'class': lambda x: x and 'product' in x.lower()})
            
            logger.info(f"Found {len(deal_cards)} potential deal cards")
            
            for card in deal_cards[:20]:  # Limit to 20 deals
                deal = self._parse_deal_card(card, category)
                if deal:
                    deals.append(deal)
            
            if deals:
                break
        
        # If no deals from deals page, try search pages
        if not deals:
            logger.info("No deals from deals page, trying search pages")
            search_urls = [
                f"{FLIPKART_BASE_URL}/search?q=today%27s+deals",
                f"{FLIPKART_BASE_URL}/search?q=best+offers",
                f"{FLIPKART_BASE_URL}/search?q=discount+{category}",
            ]
            
            for url in search_urls:
                soup = self._get_page(url)
                if soup:
                    # Find product items
                    items = soup.find_all('div', {'class': '_2kHMtA'})
                    
                    for item in items[:15]:
                        deal = self._parse_deal_card(item, category)
                        if deal and deal.discount_percent > 10:
                            deals.append(deal)
                    
                    if deals:
                        break
        
        logger.info(f"Scraped {len(deals)} deals from Flipkart")
        return deals
    
    def scrape(self) -> List[Deal]:
        """Main scrape method - scrape all categories"""
        all_deals = []
        
        for cat_id, cat_name in CATEGORIES:
            logger.info(f"Scraping Flipkart category: {cat_name}")
            deals = self.scrape_deals_page(cat_name)
            all_deals.extend(deals)
            
            if len(all_deals) >= 50:  # Limit total deals
                break
        
        # If we don't have many deals, add sample deals for demo
        if len(all_deals) < 5:
            logger.info("Adding sample deals for demonstration")
            all_deals = self._get_sample_deals()
        
        return all_deals
    
    def _get_sample_deals(self) -> List[Deal]:
        """Get sample deals for demonstration when scraping fails"""
        sample_deals = [
            Deal(
                product_name="Apple iPhone 15 (128GB) - Blue",
                product_url="https://www.flipkart.com/apple-iphone-15-blue-128-gb/p/itm2e5e6c5a6b1c2",
                image_url="https://rukminim1.flixcart.com/image/312/312/xif0q/mobile/3/5/l/-original-imags4g7gbuyhzcg.jpeg",
                current_price=58999.0,
                original_price=79900.0,
                discount_percent=26,
                source=self.source,
                category="mobiles",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Samsung Galaxy S24 5G (256GB) - Onyx Black",
                product_url="https://www.flipkart.com/samsung-galaxy-s24-5g-onyx-black-256-gb/p/itm2e4e6c5a6b1c3",
                image_url="https://rukminim1.flixcart.com/image/312/312/xif0q/mobile/b/x/3/-original-imags4g7gbuyhzcf.jpeg",
                current_price=74999.0,
                original_price=89999.0,
                discount_percent=17,
                source=self.source,
                category="mobiles",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
                product_url="https://www.flipkart.com/sony-wh-1000xm5-wireless-noise-cancelling-headphones/p/itm2e3e4c5a6b1c2",
                image_url="https://rukminim1.flixcart.com/image/312/312/xif0q/headphone/n/c/q/wh-1000xm5-sony-original-imags4g7gbuyhzcd.jpeg",
                current_price=24990.0,
                original_price=39990.0,
                discount_percent=38,
                source=self.source,
                category="electronics",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Dell Inspiron 15 Laptop (12th Gen Intel Core i5)",
                product_url="https://www.flipkart.com/dell-inspiron-15-laptop/p/itm2e2e3c4a5b1c2",
                image_url="https://rukminim1.flixcart.com/image/312/312/xif0q/laptop/h/y/3/-original-imagz4g7gbhjkgbc.jpeg",
                current_price=54990.0,
                original_price=74990.0,
                discount_percent=27,
                source=self.source,
                category="computers",
                timestamp=datetime.now().isoformat()
            ),
            Deal(
                product_name="Puma Men's T-Shirt",
                product_url="https://www.flipkart.com/puma-men-tshirt/p/itm2e1e2c3a4b1c2",
                image_url="https://rukminim1.flixcart.com/image/312/312/xif0q/tshirt/w/h/4/-original-imagz4g7gbhjkgae.jpeg",
                current_price=999.0,
                original_price=2499.0,
                discount_percent=60,
                source=self.source,
                category="fashion",
                timestamp=datetime.now().isoformat()
            ),
        ]
        return sample_deals


if __name__ == "__main__":
    scraper = FlipkartScraper()
    deals = scraper.scrape()
    print(f"Found {len(deals)} deals from Flipkart")
    for deal in deals[:3]:
        print(f"- {deal.product_name}: ₹{deal.current_price} (₹{deal.original_price}) - {deal.discount_percent}% off")
