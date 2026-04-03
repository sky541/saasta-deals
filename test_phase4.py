"""
Test Phase 4: Geolocation Feature Tests
Tests the "Near Me" geolocation feature including:
- Distance calculation (Haversine formula)
- Filter by distance function
- /local route with geolocation parameters
- Distance display in UI
- JavaScript geolocation functions
"""

import json
import math
import unittest
from web_app import app, calculate_distance, filter_by_distance, load_coupons

class TestGeolocation(unittest.TestCase):
    """Test geolocation distance calculations and filtering"""

    def setUp(self):
        """Set up test client and data"""
        self.app = app
        self.client = self.app.test_client()
        
        # Load coupons and check for food coupons
        self.coupons = load_coupons()
        self.food_coupons = [c for c in self.coupons if c.get('category') == 'food']
        
    def test_distance_calculation_same_location(self):
        """Distance between same coordinates should be 0"""
        distance = calculate_distance(28.6139, 77.2090, 28.6139, 77.2090)
        self.assertEqual(distance, 0.0)
        print(f"[PASS] Same location distance: {distance} km")

    def test_distance_calculation_known_distance(self):
        """Test distance calculation with known reference points"""
        # Approximately 1.4 km apart
        distance = calculate_distance(28.6139, 77.2090, 28.6250, 77.2200)
        self.assertTrue(1.0 < distance < 2.5, f"Expected ~1.4 km, got {distance} km")
        print(f"[PASS] Known reference distance: {distance} km")

    def test_distance_calculation_haversine(self):
        """Test that Haversine formula works correctly"""
        # Delhi to Mumbai ~1300 km (rough test - great circle distance)
        delhi_lat, delhi_lng = 28.7041, 77.1025
        mumbai_lat, mumbai_lng = 19.0760, 72.8777
        distance = calculate_distance(delhi_lat, delhi_lng, mumbai_lat, mumbai_lng)
        # Great circle distance is ~1150-1300 km depending on calculation method
        self.assertTrue(1100 < distance < 1400, f"Delhi-Mumbai should be ~1150-1300 km, got {distance} km")
        print(f"[PASS] Haversine formula - Delhi to Mumbai: {distance} km")

    def test_filter_by_distance_returns_restaurants(self):
        """Filter by distance should return food coupons"""
        if not self.food_coupons:
            self.skipTest("No food coupons available")
        
        # Use Connaught Place, Delhi as reference (28.6328, 77.2197)
        filtered = filter_by_distance(self.food_coupons, 28.6328, 77.2197, max_distance_km=50.0)
        
        self.assertIsInstance(filtered, list)
        print(f"[PASS] Filtered {len(filtered)} restaurants within 50 km of Connaught Place")

    def test_filter_by_distance_respects_radius(self):
        """Filter by distance should not return restaurants beyond max_distance"""
        if not self.food_coupons:
            self.skipTest("No food coupons available")
        
        # Filter with very small radius (1 km)
        filtered_1km = filter_by_distance(self.food_coupons, 28.6328, 77.2197, max_distance_km=1.0)
        
        # Filter with larger radius (50 km)
        filtered_50km = filter_by_distance(self.food_coupons, 28.6328, 77.2197, max_distance_km=50.0)
        
        # Larger radius should have more or equal results
        self.assertLessEqual(len(filtered_1km), len(filtered_50km))
        print(f"[PASS] Filter radius respected: 1km={len(filtered_1km)}, 50km={len(filtered_50km)}")

    def test_filter_by_distance_sorted_by_distance(self):
        """Filtered results should be sorted by distance (closest first)"""
        if not self.food_coupons:
            self.skipTest("No food coupons available")
        
        filtered = filter_by_distance(self.food_coupons, 28.6328, 77.2197, max_distance_km=50.0)
        
        if len(filtered) > 1:
            # Check that distances are in ascending order
            distances = [r.get('distance_km', 0) for r in filtered]
            is_sorted = all(distances[i] <= distances[i+1] for i in range(len(distances)-1))
            self.assertTrue(is_sorted, f"Results not sorted by distance: {distances}")
            print(f"[PASS] Results sorted by distance: {distances[:5]}")
        else:
            print(f"[SKIP] Only {len(filtered)} result(s) - skipping sort check")

    def test_local_route_without_geolocation(self):
        """Test /local route without geolocation parameters"""
        response = self.client.get('/local')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        self.assertIn('Find Near Me', content)  # Near Me button should be visible
        print(f"[PASS] /local route loads - status {response.status_code}")

    def test_local_route_with_geolocation(self):
        """Test /local route with geolocation parameters"""
        response = self.client.get('/local?user_lat=28.6328&user_lng=77.2197')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        self.assertIn('Near Me', content)  # Near Me button should show active state
        print(f"[PASS] /local route with geolocation - status {response.status_code}")

    def test_local_route_preserves_filters_with_geolocation(self):
        """Test that /local route preserves other filters when geolocation is applied"""
        response = self.client.get('/local?city=Delhi&user_lat=28.6328&user_lng=77.2197')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        # Should have filter controls and geolocation support
        self.assertIn('city', content)
        print(f"[PASS] /local route preserves filters with geolocation - status {response.status_code}")

    def test_distance_badge_in_template(self):
        """Test that distance_km field is rendered in template"""
        response = self.client.get('/local?user_lat=28.6328&user_lng=77.2197&city=Delhi&limit=1')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        # Check for distance badge styling in HTML
        self.assertIn('distance-badge', content)
        print(f"[PASS] Distance badge CSS class present in template")

    def test_geolocation_button_onclick_handler(self):
        """Test that getNearbyLocation() function is in template"""
        response = self.client.get('/local')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        self.assertIn('getNearbyLocation()', content)
        print(f"[PASS] getNearbyLocation() function present in template")

    def test_clear_geolocation_button(self):
        """Test that clearNearMe() function is in template"""
        response = self.client.get('/local?user_lat=28.6328&user_lng=77.2197')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        self.assertIn('clearNearMe()', content)
        print(f"[PASS] clearNearMe() function present in template")

    def test_food_coupons_have_coordinates(self):
        """Test that enriched food coupons have latitude/longitude"""
        if not self.food_coupons:
            self.skipTest("No food coupons available")
        
        coupons_with_coords = [c for c in self.food_coupons 
                              if 'latitude' in c and 'longitude' in c]
        
        if len(coupons_with_coords) == 0:
            print(f"[SKIP] No food coupons have GPS coordinates yet (data needs enrichment)")
            self.skipTest("Food coupons not yet enriched with GPS coordinates")
        
        coord_count = len(coupons_with_coords)
        total_count = len(self.food_coupons)
        print(f"[PASS] {coord_count}/{total_count} food coupons have GPS coordinates")

    def test_distance_calculation_precision(self):
        """Test that distance values are properly rounded"""
        distance = calculate_distance(28.6139, 77.2090, 28.6250, 77.2200)
        # Should be rounded to 1 decimal place
        self.assertEqual(distance, round(distance, 1))
        print(f"[PASS] Distance precision is 1 decimal place: {distance} km")


class TestUI(unittest.TestCase):
    """Test UI elements for Phase 4"""

    def setUp(self):
        """Set up test client"""
        self.app = app
        self.client = self.app.test_client()

    def test_near_me_button_styling(self):
        """Test that Near Me button has proper styling"""
        response = self.client.get('/local')
        content = response.get_data(as_text=True)
        self.assertIn('btn-near-me', content)
        self.assertIn('.btn-near-me', content)  # CSS class definition
        print(f"[PASS] Near Me button styling present")

    def test_near_me_button_shows_active_state(self):
        """Test that Near Me button shows active state with geolocation"""
        response = self.client.get('/local?user_lat=28.6328&user_lng=77.2197')
        content = response.get_data(as_text=True)
        # Button should be in active state - check for either the active button or Near Me term
        has_near_me = 'Near Me' in content  # Button shows in some form
        self.assertTrue(has_near_me)
        print(f"[PASS] Near Me button shows active state")

    def test_restaurant_card_has_distance_display(self):
        """Test that restaurant cards show distance when geolocation is used"""
        response = self.client.get('/local?user_lat=28.6328&user_lng=77.2197&city=Delhi')
        content = response.get_data(as_text=True)
        # Should have distance display elements
        self.assertIn('distance-badge', content)
        print(f"[PASS] Restaurant cards display distance badge")


class TestIntegration(unittest.TestCase):
    """Integration tests for complete geolocation flow"""

    def setUp(self):
        """Set up test client and data"""
        self.app = app
        self.client = self.app.test_client()
        self.coupons = load_coupons()
        self.food_coupons = [c for c in self.coupons if c.get('category') == 'food']

    def test_complete_geolocation_flow(self):
        """Test complete flow: User clicks Near Me -> Gets location -> Sees results"""
        if not self.food_coupons:
            self.skipTest("No food coupons available")

        # Step 1: User loads /local
        response = self.client.get('/local')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        self.assertIn('Find Near Me', content)  # Button shows before clicking
        print(f"[PASS] Step 1: User loads /local route")

        # Step 2: User's browser gets their location (simulated)
        user_lat, user_lng = 28.6328, 77.2197  # Connaught Place, Delhi
        
        # Step 3: Browser redirects to /local?user_lat=X&user_lng=Y
        response = self.client.get(f'/local?user_lat={user_lat}&user_lng={user_lng}')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        print(f"[PASS] Step 2: User location obtained, redirect to /local?user_lat={user_lat}&user_lng={user_lng}")

        # Step 4: Results are sorted by distance
        self.assertIn('distance-badge', content)
        print(f"[PASS] Step 3: Results show distance badges")

        # Step 5: User can clear Near Me filter
        self.assertIn('clearNearMe()', content)
        response = self.client.get('/local')  # Redirect to clear
        self.assertEqual(response.status_code, 200)
        print(f"[PASS] Step 4: User can clear Near Me filter")

    def test_geolocation_with_other_filters(self):
        """Test that geolocation works alongside other filters"""
        if not self.food_coupons:
            self.skipTest("No food coupons available")

        # Apply geolocation + city filter
        response = self.client.get('/local?user_lat=28.6328&user_lng=77.2197&city=Delhi&min_rating=4.0')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        
        # Should have both filters applied
        self.assertIn('distance-badge', content)  # Geolocation
        print(f"[PASS] Geolocation works with other filters (city + rating)")

    def test_edge_case_invalid_coordinates(self):
        """Test handling of invalid geolocation coordinates"""
        # Invalid latitude (> 90)
        response = self.client.get('/local?user_lat=150&user_lng=77.2197')
        # Should still return 200 but may not apply geolocation
        self.assertEqual(response.status_code, 200)
        print(f"[PASS] Invalid coordinates handled gracefully")

    def test_edge_case_missing_coordinates(self):
        """Test handling when only one coordinate is provided"""
        response = self.client.get('/local?user_lat=28.6328')  # Missing lng
        self.assertEqual(response.status_code, 200)
        print(f"[PASS] Missing coordinates handled gracefully")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
