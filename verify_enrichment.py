#!/usr/bin/env python3
import json

with open('data/coupons.json') as f:
    data = json.load(f)

total = data.get('count', 0)
coupons = data.get('coupons', [])
with_coords = [c for c in coupons if c.get('latitude')]

print(f'Total coupons: {total}')
print(f'With coordinates: {len(with_coords)}')

if with_coords:
    print(f'\nSample enriched coupons:')
    for c in with_coords[:5]:
        print(f'  {c.get("description")} - {c.get("city")} ({c.get("latitude")}, {c.get("longitude")})')
