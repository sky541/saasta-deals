#!/usr/bin/env python3
# Remove the non-enriched restaurant coupons so scraper can re-run fresh
import json

with open('data/coupons.json') as f:
    data = json.load(f)

coupons = data.get('coupons', [])

# Keep only e-commerce coupons (no " at " in description = generic food delivery or e-commerce)
original_coupons = [c for c in coupons if ' at ' not in c.get('description', '').lower()]

print(f'Original coupons: {len(coupons)}')
print(f'Keeping (e-commerce): {len(original_coupons)}')
print(f'Removing (non-enriched restaurants): {len(coupons) - len(original_coupons)}')

# Update and save
data['coupons'] = original_coupons
data['count'] = len(original_coupons)

with open('data/coupons.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'\nSaved cleaned coupons.json with {len(original_coupons)} coupons')
