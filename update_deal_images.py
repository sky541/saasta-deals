import json
import re

# Brand-to-Image mapping with curated Unsplash URLs specific to each brand/product type
BRAND_IMAGE_MAPPING = {
    # Fashion Brands
    'US Polo': 'https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400&q=80',  # Casual shirt
    'Puma': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',  # Sport shoes
    'Adidas': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',  # Sport shoes
    'Nike': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',  # Sport shoes
    'Levi': 'https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400&q=80',  # Jeans
    'Tommy': 'https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400&q=80',  # Casual wear
    
    # Audio/Electronics Brands
    'JBL': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80',  # JBL headphones
    'boAt': 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&q=80',  # Audio device
    'Noise': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80',  # Smartwatch/audio
    'Sony': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80',  # Audio device
    'Samsung': 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&q=80',  # Electronics/phones
    'Apple': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&q=80',  # Apple products
    'Philips': 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=400&q=80',  # Beauty/Personal care
    'Dyson': 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=400&q=80',  # Hair care
    
    # Mobile Brands
    'realme': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80',  # Smartphone
    'Xiaomi': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80',  # Smartphone
    'POCO': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80',  # Smartphone
    'Redmi': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80',  # Smartphone
    'OnePlus': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80',  # OnePlus phone
    'iQOO': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80',  # Smartphone
    'OPPO': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80',  # Smartphone
    'vivo': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80',  # Smartphone
    'iPhone': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&q=80',  # iPhone
    'BoBo': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80',  # Smartphone
    
    # Computers
    'Dell': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80',  # Laptop
    'HP': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80',  # Laptop
    'Lenovo': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80',  # Laptop
    'ASUS': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80',  # Laptop
    'MacBook': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80',  # Laptop
    
    # Gaming
    'Xbox': 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400&q=80',  # Gaming console
    'PlayStation': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&q=80',  # PlayStation
    'Nintendo': 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400&q=80',  # Gaming
    
    # Wearables/Accessories
    'Watch': 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400&q=80',  # Smartwatch
    'AirPods': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80',  # Earbuds
    
    # Home/Kitchen
    'Crock-Pot': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80',  # Home appliance
    'Kimberly': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80',  # Paper products
}

# Default images by category if brand not found
DEFAULT_CATEGORY_IMAGES = {
    'fashion': 'https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400&q=80',  # Clothing
    'electronics': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80',  # Audio
    'mobiles': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80',  # Phone
    'computers': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80',  # Laptop
    'gaming': 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400&q=80',  # Gaming
    'beauty': 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=400&q=80',  # Beauty
}

def extract_brand(product_name):
    """Extract brand name from product name"""
    # Split by space and take first word as brand
    words = product_name.split()
    if words:
        brand = words[0]
        return brand
    return None

def get_image_for_product(product_name, category):
    """Get appropriate image URL for a product based on brand and category"""
    brand = extract_brand(product_name)
    
    # Check if brand has specific mapping
    if brand:
        for key, image_url in BRAND_IMAGE_MAPPING.items():
            if key.lower() in product_name.lower():
                return image_url
    
    # Fall back to category default
    return DEFAULT_CATEGORY_IMAGES.get(category, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80')

# Load and update the combined_deals.json
json_path = 'deals_bot/data/combined_deals.json'

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Found {len(data['deals'])} deals to update...")
    
    # Update each deal with brand-specific image
    updated_count = 0
    for deal in data['deals']:
        old_image = deal['image_url']
        new_image = get_image_for_product(deal['product_name'], deal['category'])
        
        if old_image != new_image:
            deal['image_url'] = new_image
            updated_count += 1
            print(f"✓ {deal['product_name']:<40} → Brand-specific image")
        else:
            print(f"→ {deal['product_name']:<40} (already correct)")
    
    # Save updated data back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully updated {updated_count} deals with brand-specific images!")
    print(f"📁 File saved: {json_path}")
    
except FileNotFoundError:
    print(f"❌ Error: File not found at {json_path}")
except json.JSONDecodeError:
    print(f"❌ Error: Invalid JSON in {json_path}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
