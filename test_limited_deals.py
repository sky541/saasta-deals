import requests
import time

# Wait for server to start
time.sleep(2)

try:
    response = requests.get('http://localhost:5000/limited-deals')
    
    if response.status_code == 200:
        print(f"✅ /limited-deals page loaded successfully (Status: {response.status_code})")
        
        html_content = response.text
        
        # Check for brand-specific images
        branded_images = [
            'photo-1542291026',  # Nike/Adidas/Puma shoes
            'photo-1505740420928',  # JBL/Sony headphones
            'photo-1610945415295',  # Samsung phones
            'photo-1572635196237',  # Apple products
            'photo-1484704849700',  # boAt audio
            'photo-1517336714731',  # Laptops
            'photo-1542272604',  # Casual wear
        ]
        
        found_images = []
        for img_id in branded_images:
            if img_id in html_content:
                found_images.append(img_id)
        
        print(f"\n📸 Brand-specific images found: {len(found_images)}/{len(branded_images)}")
        for img in found_images:
            print(f"   • {img}")
        
        # Check for deal elements
        if 'product_name' in html_content or 'Limited Time' in html_content:
            print("\n✅ Deal elements present on page")
        
        if len(found_images) >= 5:
            print("\n🎉 SUCCESS: Images are correctly mapped to brands!")
        
    else:
        print(f"❌ Error loading page. Status: {response.status_code}")
        
except ConnectionError:
    print("❌ Could not connect to server at http://localhost:5000")
    print("Make sure the Flask app is running")
except Exception as e:
    print(f"❌ Error: {str(e)}")
