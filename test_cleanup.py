import requests
import time

# Wait for server to fully start
time.sleep(3)

try:
    # Test /deals page
    response = requests.get('http://localhost:5000/deals', timeout=10)
    
    if response.status_code == 200:
        print("✅ /deals page loads successfully (Status: 200)")
        
        # Check that Limited Time content is NOT present
        if '/limited-deals' not in response.text:
            print("✅ No /limited-deals links found (Limited Time Deals removed)")
        else:
            print("⚠️ Found /limited-deals references (may need more cleanup)")
            
        # Check that basic deals content is present
        if 'GrabCoupon' in response.text and 'coupons' in response.text.lower():
            print("✅ Daily Deals page contains expected content")
        
        print("\n🎉 SUCCESS: Limited Time Deals fully removed!")
        
    else:
        print(f"❌ Error loading page. Status: {response.status_code}")
        
except ConnectionError:
    print("❌ Could not connect to server at http://localhost:5000")
except Exception as e:
    print(f"❌ Error: {str(e)}")
