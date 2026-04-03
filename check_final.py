#!/usr/bin/env python3
import json

with open('data/coupons.json') as f:
    data = json.load(f)

print(f'Total coupons: {data["count"]}')
coupons = data['coupons']
with_coords = [c for c in coupons if c.get('latitude')]
print(f'With coordinates: {len(with_coords)}')

if with_coords:
    print(f'\nSample coupons with coordinates:')
    for c in with_coords[:3]:
        print(f'  {c.get("description")} - {c.get("city")} ({c.get("latitude")}, {c.get("longitude")})')
else:
    print('No coupons with coordinates found')
