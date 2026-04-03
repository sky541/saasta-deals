#!/usr/bin/env python3
import json

cache = json.load(open('restaurant_cache.json'))
rest = list(cache.values())[0]

print('Sample restaurant from cache:')
print('Keys:', list(rest.keys()))
print('Name:', rest.get('name'))
print('City:', rest.get('city'))
print('Location:', rest.get('location'))
print('Latitude:', rest.get('latitude'))
print('Longitude:', rest.get('longitude'))
print('Rating:', rest.get('rating'))
print()

# Now check if the coupons have coordinates
coupons_data = json.load(open('data/coupons.json'))
coupons = coupons_data['coupons']
food = [c for c in coupons if c.get('category') == 'food']

print(f'Food coupons: {len(food)}')
with_coords = [c for c in food if c.get('latitude') and c.get('longitude')]
print(f'With valid coordinates: {len(with_coords)}')

if with_coords:
    sample = with_coords[0]
    print('\nSample coupon with coordinates:')
    print('Description:', sample.get('description'))
    print('City:', sample.get('city'))
    print('Latitude:', sample.get('latitude'))
    print('Longitude:', sample.get('longitude'))
else:
    print('\nNo coupons with coordinates found')
    # Check if any recent coupons have lat/lng field
    with_lat_field = [c for c in food[-10:] if 'latitude' in c]
    print(f'Recent coupons with latitude field: {len(with_lat_field)}')
    if with_lat_field:
        print('Sample:', with_lat_field[0])
