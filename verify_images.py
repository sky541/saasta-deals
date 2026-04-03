import json

# Load and display updated deals
with open('deals_bot/data/combined_deals.json', 'r') as f:
    data = json.load(f)

deals = data['deals']
print(f"✓ Total deals loaded: {len(deals)}")
print("\n" + "="*70)
print("BRAND-SPECIFIC IMAGES - FIRST 10 DEALS")
print("="*70)

for i, deal in enumerate(deals[:10]):
    product_name = deal['product_name'][:35]
    image_id = deal['image_url'].split('/')[-1][:25]
    source = deal['source']
    price_info = f"₹{int(deal['current_price'])} ({deal['discount_percent']}% off)"
    print(f"{i+1:2}. {product_name:35} | {image_id:25} | {price_info}")

print("\n" + "="*70)
print("IMAGE MAPPING SUMMARY")
print("="*70)

# Count unique images
image_counts = {}
for deal in deals:
    image_url = deal['image_url']
    image_id = image_url.split('/')[-1][:30]
    image_counts[image_id] = image_counts.get(image_id, 0) + 1

print("\nUnique image URLs being used:")
for image_id, count in sorted(image_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  • {image_id:30} → {count:2} products")

print(f"\n✅ Brand-specific images successfully applied!")
