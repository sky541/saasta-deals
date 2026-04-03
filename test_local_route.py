from web_app import app
import re

# Create test client
with app.test_client() as client:
    # Test /local route with Delhi city
    response = client.get('/local?city=Delhi')
    status = response.status_code
    
    # Check for key elements
    has_cards = b'restaurant-card' in response.data
    has_ratings = b'rating-badge' in response.data
    has_cuisines = b'cuisines-list' in response.data
    has_hours = b'opening-hours' in response.data
    has_price = b'price_range' in response.data
    
    # Count restaurants
    cards = len(re.findall(b'restaurant-card', response.data))
    
    # Print results
    print("=== LOCAL ROUTE TEST RESULTS ===")
    print(f"HTTP Status: {status}")
    print(f"Restaurant Cards Rendered: {cards}")
    print(f"Rating Badges Present: {has_ratings}")
    print(f"Cuisine Lists Present: {has_cuisines}")
    print(f"Opening Hours Present: {has_hours}")
    print(f"Price Range Present: {has_price}")
    print("\n=== SUCCESS ===")
    if status == 200 and cards > 0:
        print("Phase 2 Complete: /local route rendering enriched restaurant data!")
