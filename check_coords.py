#!/usr/bin/env python3
"""Quick check for coordinates in coupons.json"""

import json

with open('data/coupons.json') as f:
    data = json.load(f)

coupons = data.get('coupons', [])
food_coupons = [c for c in coupons if c.get('category') == 'food']
with_coords = [c for c in food_coupons if 'latitude' in c and 'longitude' in c]

print(f'Total food coupons: {len(food_coupons)}')
print(f'With coordinates: {len(with_coords)}')
print()
print('Sample restaurants with coordinates:')
for c in with_coords[:10]:
    desc = c.get('description', '?')
    lat = c.get('latitude', '?')
    lng = c.get('longitude', '?')
    city = c.get('city', '?')
    print(f'  {desc} ({city}): {lat}, {lng}')
