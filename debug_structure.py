#!/usr/bin/env python3
import json

with open('data/coupons.json') as f:
    data = json.load(f)

print(f'Top-level keys: {list(data.keys())}')
print(f'Timestamps: {data.get("timestamp")}')
print(f'Count: {data.get("count")}')

coupons = data.get('coupons', [])
print(f'Coupons in list: {len(coupons)}')

# Check for restaurant coupons with coordinates
food = [c for c in coupons  if c.get('category') == 'food']
print(f'Food coupons: {len(food)}')

# Check for coordinates
has_coords = [c for c in food if c.get('latitude') and c.get('longitude')]
print(f'Food coupons with coords: {len(has_coords)}')

if has_coords:
    c = has_coords[0]
    print(f'\nSample with coords:')
    print(f'  Description: {c.get("description")}')
    print(f'  Lat/Lng: ({c.get("latitude")}, {c.get("longitude")})')
else:
    print(f'\nNo coupons with coordinates.')
    # Show last few food coupons
    print(f'\nLast 3 food coupons:')
    for c in food[-3:]:
        print(f'  {c.get("description")} - keys: {list(c.keys())}')
