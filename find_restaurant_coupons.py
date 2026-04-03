#!/usr/bin/env python3
import json

with open('data/coupons.json') as f:
    data = json.load(f)

coupons = data.get('coupons', [])

# Look for coupons with 'At ' (from "X% Off at Restaurant_Name")
restaurant_coupons = [c for c in coupons if ' at ' in c.get('description', '').lower()]
print(f'Coupons with " at " (restaurant-specific): {len(restaurant_coupons)}')

if restaurant_coupons:
    print(f'\nSample restaurant coupons:')
    for c in restaurant_coupons[:5]:
        print(f'  {c.get("description")} ({c.get("city")})')
        print(f'    Keys: {list(c.keys())}')
        print(f'    Lat: {c.get("latitude")}, Lng: {c.get("longitude")}')
        print()

# Count how many have coordinates
with_coords = [c for c in restaurant_coupons if c.get('latitude')]
print(f'Restaurant coupons with coordinates: {len(with_coords)}/{len(restaurant_coupons)}')
