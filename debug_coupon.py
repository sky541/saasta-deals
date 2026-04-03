#!/usr/bin/env python3
"""Debug script to check restaurant cache and coupon integration"""

import json

# Check restaurant cache
try:
    with open('restaurant_cache.json') as f:
        cache = json.load(f)
    restaurants = cache.get('restaurants', [])
    print(f'Restaurant cache: {len(restaurants)} restaurants')
    if restaurants:
        print(f'\nSample restaurant:')
        print(f'  Name: {restaurants[0].get("name")}')
        print(f'  City: {restaurants[0].get("city")}')
        print(f'  Location: {restaurants[0].get("location")}')
        print(f'  Latitude: {restaurants[0].get("latitude")}')
        print(f'  Longitude: {restaurants[0].get("longitude")}')
        print(f'  Keys: {list(restaurants[0].keys())}')
        print()
except Exception as e:
    print(f'Error loading restaurant_cache.json: {e}')
    print()

# Check coupons
print('='*60)
with open('data/coupons.json') as f:
    data = json.load(f)
coupons = data['coupons']
food = [c for c in coupons if c.get('category') == 'food']

print(f'Food coupons: {len(food)}')
print(f'Total coupons: {len(coupons)}')

# Check which ones have coordinates
with_coords = [c for c in food if 'latitude' in c and 'longitude' in c]
print(f'With coordinates: {len(with_coords)}')

if with_coords:
    print(f'\nSample with coords:')
    c = with_coords[0]
    print(f'  Description: {c.get("description")}')
    print(f'  City: {c.get("city")}')
    print(f'  Lat/Lng: ({c.get("latitude")}, {c.get("longitude")})')
else:
    print(f'\nNo food coupons with coordinates. Sample food coupons:')
    for i, c in enumerate(food[:3]):
        print(f'{i}: {c.get("description")} - {c.get("coupon_code")}')

