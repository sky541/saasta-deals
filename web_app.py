"""
OfferOye - Coupons Web Application
Show live coupons from Indian e-commerce websites
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from flask import Flask, render_template_string, jsonify, request, make_response
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variable to store cached coupons
coupons_cache = None
cache_updated = None
REFRESH_INTERVAL_HOURS = 4

def refresh_coupons():
    """Refresh coupons from data file"""
    global coupons_cache, cache_updated
    coupons_cache = load_coupons()
    cache_updated = datetime.now()
    logger.info(f"Coupons refreshed: {len(coupons_cache)} coupons at {cache_updated}")

def check_and_refresh():
    """Check if refresh needed and refresh if needed"""
    global cache_updated
    if cache_updated is None or (datetime.now() - cache_updated) > timedelta(hours=REFRESH_INTERVAL_HOURS):
        refresh_coupons()

# Initialize background scheduler for automatic refresh (after refresh_coupons is defined)
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=refresh_coupons,
    trigger="interval",
    hours=REFRESH_INTERVAL_HOURS,
    id="coupon_refresh_job",
    name="Refresh coupons from file",
    replace_existing=True
)

# Don't call refresh_coupons() here - load_coupons not defined yet


DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GrabCoupon - Coupons & Offers</title>
    <meta name="description" content="Find the best coupon codes and offers from top Indian retailers">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #0ea5e9;
            --secondary: #38bdf8;
            --dark: #0284c7;
            --light: #f0f9ff;
            --white: #ffffff;
            --success: #22c55e;
            --danger: #ef4444;
            --orange: #f97316;
            --text: #334155;
            --gray: #94a3b8;
            --bg: #f8fafc;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8fafc;
            color: #334155;
            min-height: 100vh;
        }
        
        header {
            background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
            color: white;
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(14, 165, 233, 0.2);
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 2rem;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        
        .logo span { color: #FFD60A; }
        
        .tabs {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            scrollbar-width: none;
        }
        
        .tabs::-webkit-scrollbar {
            display: none;
        }
        
        .category-search {
            background: #f8f9fa;
            padding: 12px 20px;
            text-align: center;
        }
        
        .category-search form {
            display: flex;
            justify-content: center;
            gap: 10px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .category-search input {
            flex: 1;
            padding: 10px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 0.95rem;
        }
        
        .category-search select {
            padding: 10px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            background: white;
            cursor: pointer;
        }
        
        .category-search button {
            padding: 10px 24px;
            background: #0ea5e9;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .tab {
            padding: 8px 16px;
            background: rgba(255,255,255,0.3);
            border-radius: 20px;
            text-decoration: none;
            color: #023E8A;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .tab:hover, .tab.active {
            background: white;
            color: #00B4D8;
        }
        
        /* Category Pills - Clean Design like top coupon sites */
        .category-pills {
            background: white;
            padding: 15px 20px;
            display: flex;
            gap: 8px;
            overflow-x: auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            scrollbar-width: none;
        }
        
        .category-pills::-webkit-scrollbar {
            display: none;
        }
        
        .category-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border-radius: 25px;
            text-decoration: none;
            color: #475569;
            font-weight: 500;
            font-size: 0.9rem;
            white-space: nowrap;
            transition: all 0.2s;
            background: #f1f5f9;
            border: 1px solid transparent;
        }
        
        .category-pill:hover {
            background: #0ea5e9;
            color: white;
        }
        
        .category-pill.active {
            background: #0ea5e9;
            color: white;
            border-color: #0284c7;
        }
        
        /* Search in Hero */
        .hero-search {
            max-width: 600px;
            margin: 20px auto 0;
        }
        
        .hero-search input {
            width: 100%;
            padding: 14px 20px;
            font-size: 1rem;
            border: none;
            border-radius: 30px;
            outline: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        
        /* Mobile Responsive */
        @media (max-width: 600px) {
            header {
                padding: 10px 0;
            }
            .header-content {
                flex-direction: column;
                gap: 10px;
                padding: 0 10px;
            }
            .logo {
                font-size: 1.5rem;
            }
            .tabs {
                width: 100%;
                justify-content: center;
                flex-wrap: wrap;
            }
            .tab {
                padding: 8px 12px;
                font-size: 0.85rem;
            }
        }
        
        .hero {
            background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
            color: white;
            padding: 2rem 20px;
            text-align: center;
        }
        
        .hero h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .hero p { font-size: 1.1rem; opacity: 0.95; }
        
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }
        
        .stat {
            background: rgba(255,255,255,0.2);
            padding: 1rem 2rem;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 800;
        }
        
        .stat-label {
            font-size: 0.85rem;
            opacity: 0.9;
        }
            padding: 12px 25px;
            border-radius: 15px;
        }
        
        .stat-number { font-size: 1.8rem; font-weight: bold; color: #FFD60A; }
        .stat-label { font-size: 0.9rem; color: white; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem 20px; }
        
        .filters {
            background: rgba(255,255,255,0.9);
            padding: 1.2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .filter-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .filter-row select, .filter-row input {
            padding: 10px 16px;
            border: 2px solid #90E0EF;
            border-radius: 25px;
            font-size: 0.95rem;
            min-width: 140px;
            background: white;
        }
        
        .filter-row select:focus, .filter-row input:focus {
            outline: none;
            border-color: #00B4D8;
        }
        
        .filter-row button {
            padding: 10px 25px;
            background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .filter-row button:hover { transform: translateY(-2px); }
        
        .filter-row input, .filter-row select {
            padding: 10px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .filter-row input:focus, .filter-row select:focus {
            border-color: #6366f1;
        }
        
        .coupons-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
        }
        
        .coupon-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.25s ease;
            border: 1px solid #e2e8f0;
        }
        
        .coupon-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.12);
        }
        
        .coupon-header {
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }
        
        /* Coupon Buttons */
        .coupon-buttons {
            margin-top: 12px;
        }
        
        .btn-visit {
            display: block;
            width: 100%;
            padding: 12px;
            background: #22c55e;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            text-decoration: none;
            text-align: center;
        }
        
        .btn-visit:hover { background: #16a34a; }
        
        /* Coupon Header */
        .coupon-header {
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
            color: white;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .coupon-source {
            font-weight: bold;
            font-size: 1rem;
        }
        
        .coupon-discount {
            background: #f97316;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9rem;
        }
            border-radius: 20px;
            font-weight: bold;
            font-size: 1rem;
        }
        
        .city-badge {
            display: inline-block;
            background: #E63946;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        .coupon-body { padding: 1.2rem; }
        
        .coupon-code {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }
        
        .code-box {
            flex: 1;
            background: #CAF0F8;
            padding: 12px 15px;
            border-radius: 10px;
            font-family: monospace;
            font-size: 1.2rem;
            font-weight: bold;
            color: #0077B6;
            letter-spacing: 2px;
            text-align: center;
            border: 2px dashed #00B4D8;
        }
        
        .copy-btn {
            padding: 12px 18px;
            background: #00B4D8;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .copy-btn:hover { background: #0077B6; }
        
        .coupon-desc {
            font-size: 1rem;
            color: #023E8A;
            margin-bottom: 12px;
            line-height: 1.5;
        }
        
        .coupon-details {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 15px;
        }
        
        .detail-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .detail-item span { color: #0077B6; font-weight: 600; }
        
        .expired-tag {
            background: #ffcccc;
            color: #cc0000;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .valid-tag {
            background: #ccffcc;
            color: #006600;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .coupon-btn {
            display: block;
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s;
        }
        
        .coupon-btn:hover {
            background: linear-gradient(135deg, #0077B6 0%, #023E8A 100%);
            transform: scale(1.02);
        }
        
        footer {
            background: linear-gradient(135deg, #0077B6 0%, #023E8A 100%);
            color: white;
            padding: 2rem 20px;
            text-align: center;
            margin-top: 3rem;
        }
        
        .last-updated {
            text-align: center;
            color: #0077B6;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 1.8rem; }
            .stats-bar { gap: 15px; }
            .coupons-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">🎫 GrabCoupon - Best Coupons in India</div>
        </div>
    </header>
    
    <!-- Navigation Tabs -->
    <nav class="tabs" style="background:white;box-shadow:0 2px 4px rgba(0,0,0,0.1);padding:10px 20px;">
        <a href="/" class="tab {% if request.path == '/' and not request.args.get('category') %}active{% endif %}">🏠 All Deals</a>
        <a href="/?category=electronics" class="tab {% if request.args.get('category') == 'electronics' %}active{% endif %}">📱 Electronics</a>
        <a href="/?category=mobiles" class="tab {% if request.args.get('category') == 'mobiles' %}active{% endif %}">📲 Mobiles</a>
        <a href="/?category=fashion" class="tab {% if request.args.get('category') == 'fashion' %}active{% endif %}">👕 Fashion</a>
        <a href="/?category=food" class="tab {% if request.args.get('category') == 'food' %}active{% endif %}">🍔 Food</a>
        <a href="/?category=beauty" class="tab {% if request.args.get('category') == 'beauty' %}active{% endif %}">💄 Beauty</a>
        <a href="/?category=home" class="tab {% if request.args.get('category') == 'home' %}active{% endif %}">🏠 Home</a>
        <a href="/?category=grocery" class="tab {% if request.args.get('category') == 'grocery' %}active{% endif %}">🛒 Grocery</a>
        <a href="/?category=travel" class="tab {% if request.args.get('category') == 'travel' %}active{% endif %}">✈️ Travel</a>
        <a href="/?category=health" class="tab {% if request.args.get('category') == 'health' %}active{% endif %}">💊 Health</a>
        <a href="/?category=recharge" class="tab {% if request.args.get('category') == 'recharge' %}active{% endif %}">💰 Recharge</a>
        <a href="/local" class="tab {% if request.path == '/local' %}active{% endif %}">🍔 Local Food</a>
    </nav>
    
    <!-- Category Search Bar -->
    <div class="category-search">
        <form method="get">
            {% if request.args.get('category') %}
            <input type="hidden" name="category" value="{{ request.args.get('category') }}">
            {% endif %}
            <input type="text" name="search" placeholder="🔍 Search within {{ request.args.get('category', 'all') }}..." value="{{ request.args.get('search', '') }}">
            <select name="source">
                <option value="">All Stores</option>
                <option value="Amazon" {% if request.args.get('source')=='Amazon' %}selected{% endif %}>Amazon</option>
                <option value="Flipkart" {% if request.args.get('source')=='Flipkart' %}selected{% endif %}>Flipkart</option>
                <option value="Myntra" {% if request.args.get('source')=='Myntra' %}selected{% endif %}>Myntra</option>
                <option value="Ajio" {% if request.args.get('source')=='Ajio' %}selected{% endif %}>Ajio</option>
                <option value="Swiggy" {% if request.args.get('source')=='Swiggy' %}selected{% endif %}>Swiggy</option>
                <option value="Zomato" {% if request.args.get('source')=='Zomato' %}selected{% endif %}>Zomato</option>
            </select>
            <button type="submit">Search</button>
        </form>
    </div>
    
    {% if is_local %}
    <div class="hero">
        <h1>🍔 Local Food & Restaurant Deals</h1>
        <p>Best restaurant coupons in your city!</p>
        <p id="detecting" style="font-size: 0.9rem; opacity: 0.9;">📍 Detecting your city...</p>
        <script>
        const cities = {
            'Hyderabad': {lat: 17.3850, lon: 78.4867},
            'Bangalore': {lat: 12.9716, lon: 77.5946},
            'Mumbai': {lat: 19.0760, lon: 72.8777},
            'Delhi': {lat: 28.7041, lon: 77.1025},
            'Chennai': {lat: 13.0820, lon: 80.2707},
            'Pune': {lat: 18.5204, lon: 73.8567},
            'Kolkata': {lat: 22.5726, lon: 88.3639},
            'Chandigarh': {lat: 30.7333, lon: 76.7794},
            'Ahmedabad': {lat: 23.0225, lon: 72.5714},
            'Jaipur': {lat: 26.9124, lon: 75.7873}
        };
        function findClosestCity(lat, lon) {
            let closest = null, minDist = Infinity;
            for (const [city, coords] of Object.entries(cities)) {
                const dist = Math.sqrt(Math.pow(lat - coords.lat, 2) + Math.pow(lon - coords.lon, 2));
                if (dist < minDist) { minDist = dist; closest = city; }
            }
            return closest;
        }
        // Only run geolocation if no city is already selected
        const urlParams = new URLSearchParams(window.location.search);
        const selectedCity = urlParams.get('city');
        if (!selectedCity && navigator.geolocation && !localStorage.getItem('geoDone')) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const city = findClosestCity(position.coords.latitude, position.coords.longitude);
                    document.getElementById('detecting').innerHTML = '📍 Detected: <strong>' + city + '</strong>';
                    localStorage.setItem('geoDone', 'true');
                    setTimeout(() => {
                        const select = document.querySelector('select[name="city"]');
                        if (select && select.value === '') { select.value = city; select.form.submit(); }
                    }, 1500);
                },
                function() { document.getElementById('detecting').innerHTML = '📍 Location not available'; }
            );
        } else {
            document.getElementById('detecting').style.display = 'none';
        }
        </script>
        </script>
        <div class="stats-bar">
            <div class="stat"><div class="stat-number">{{ total_coupons }}</div><div class="stat-label">Deals</div></div>
            <div class="stat"><div class="stat-number">{{ cities|length }}</div><div class="stat-label">Cities</div></div>
        </div>
    </div>
    {% else %}
    <div class="hero">
        <h1>🎟️ Best Coupon Codes in India</h1>
        <p>Find working coupon codes from Amazon, Flipkart, Myntra, Ajio and more!</p>
        
        <!-- Search in Hero -->
        <div class="hero-search">
            <form method="get">
                {% if request.args.get('category') %}
                <input type="hidden" name="category" value="{{ request.args.get('category') }}">
                {% endif %}
                <input type="text" name="search" placeholder="🔍 Search for coupons, stores, codes..." value="{{ request.args.get('search', '') }}">
            </form>
        </div>
        
        <div class="stats-bar">
            <div class="stat"><div class="stat-number">{{ total_coupons }}</div><div class="stat-label">Active Coupons</div></div>
            <div class="stat"><div class="stat-number">{{ sources }}</div><div class="stat-label">Partner Stores</div></div>
        </div>
    </div>
    {% endif %}
    
    <div class="container">
        <div class="filters">
            <form class="filter-row" method="get">
                {% if request.args.get('category') %}
                <input type="hidden" name="category" value="{{ request.args.get('category') }}">
                {% endif %}
                {% if request.args.get('search') %}
                <input type="hidden" name="search" value="{{ request.args.get('search') }}">
                {% endif %}
                <select name="source">
                    <option value="">All Stores</option>
                    <option value="Amazon">Amazon (6)</option>
                    <option value="Flipkart">Flipkart (6)</option>
                    <option value="YouTube Shopping">YouTube Shopping (8)</option>
                    <option value="Myntra">Myntra (4)</option>
                    <option value="Swiggy">Swiggy (4)</option>
                    <option value="Zomato">Zomato (4)</option>
                    <option value="Ajio">Ajio (3)</option>
                    <option value="Croma">Croma (3)</option>
                    <option value="Meesho">Meesho (3)</option>
                    <option value="Nykaa">Nykaa (3)</option>
                    <option value="Paytm">Paytm (3)</option>
                    <option value="Reliance Digital">Reliance Digital (3)</option>
                    <option value="Snapdeal">Snapdeal (3)</option>
                    <option value="Tata Cliq">Tata Cliq (3)</option>
                    <option value="Swiggy Delivery">Swiggy Delivery (3)</option>
                    <option value="Pepperfry">Pepperfry (2)</option>
                    <option value="Shoppers Stop">Shoppers Stop (2)</option>
                    <option value="Blinkit">Blinkit</option>
                    <option value="Zepto">Zepto</option>
                    <option value="BigBasket">BigBasket</option>
                    <option value="Dmart">Dmart</option>
                    <option value="FirstCry">FirstCry</option>
                    <option value="PharmEasy">PharmEasy</option>
                    <option value="BookMyShow">BookMyShow</option>
                    <option value="MakeMyTrip">MakeMyTrip</option>
                    <option value="Goibibo">Goibibo</option>
                    <option value="Yatra">Yatra</option>
                    <option value="CRED">CRED</option>
                    <option value="Simpl">Simpl</option>
                    <option value="PineLabs">PineLabs</option>
                    <option value="Nykaa Fashion">Nykaa Fashion</option>
                    <option value="Libas">Libas</option>
                    <option value="W For Woman">W For Woman</option>
                    <option value="Allen Solly">Allen Solly</option>
                    <option value="Louis Philippe">Louis Philippe</option>
                    <option value="Peter England">Peter England</option>
                    <option value="adidas">adidas</option>
                    <option value="Nike">Nike</option>
                    <option value="Puma">Puma</option>
                    <option value="Samsung">Samsung</option>
                    <option value="OnePlus">OnePlus</option>
                    <option value="Vivo">Vivo</option>
                    <option value="Oppo">Oppo</option>
                    <option value="Realme">Realme</option>
                    <option value="Lenovo">Lenovo</option>
                    <option value="Dell">Dell</option>
                    <option value="HP">HP</option>
                    <option value="Asus">Asus</option>
                    <option value="Jio">Jio</option>
                    <option value="Airtel">Airtel</option>
                    <option value="Vi">Vi</option>
                    <option value="McDonald's">McDonald's</option>
                    <option value="KFC">KFC</option>
                    <option value="Pizza Hut">Pizza Hut</option>
                    <option value="Domino's">Domino's</option>
                    <option value="Subway">Subway</option>
                    <option value="Burger King">Burger King</option>
                    <option value="Costa Coffee">Costa Coffee</option>
                    <option value="CCD">CCD</option>
                    <option value="Barista">Barista</option>
                    <option value="Starbucks">Starbucks</option>
                    <option value="Dunkin">Dunkin</option>
                    <option value="Faasos">Faasos</option>
                    <option value="FreshMenu">FreshMenu</option>
                    <option value="Spencer's">Spencer's</option>
                    <option value="Big Bazaar">Big Bazaar</option>
                    <option value="Lifestyle">Lifestyle</option>
                    <option value="Westside">Westside</option>
                    <option value="FabIndia">FabIndia</option>
                    <option value="Urban Ladder">Urban Ladder</option>
                    <option value="Home Centre">Home Centre</option>
                    <option value="Wakefit">Wakefit</option>
                    <option value="Sleepyhead">Sleepyhead</option>
                    <option value="Nilkamal">Nilkamal</option>
                    <option value="Godrej">Godrej</option>
                    <option value="Bajaj">Bajaj</option>
                    <option value="Philips">Philips</option>
                    <option value="Syska">Syska</option>
                    <option value="Havells">Havells</option>
                    <option value="Orient">Orient</option>
                    <option value="Kaff">Kaff</option>
                    <option value="Eureka Forbes">Eureka Forbes</option>
                    <option value="Kent">Kent</option>
                    <option value="Aqua">Aqua</option>
                    <option value="Livpure">Livpure</option>
                    <option value="Pureit">Pureit</option>
                    <option value="Brita">Brita</option>
                    <option value="Voltas">Voltas</option>
                    <option value="Blue Star">Blue Star</option>
                    <option value="Daikin">Daikin</option>
                    <option value="LG">LG</option>
                    <option value="Whirlpool">Whirlpool</option>
                    <option value="IFB">IFB</option>
                    <option value="Sony">Sony</option>
                    <option value="Panasonic">Panasonic</option>
                    <option value="Toshiba">Toshiba</option>
                    <option value="Hitachi">Hitachi</option>
                    <option value="Sharp">Sharp</option>
                    <option value="Haier">Haier</option>
                    <option value="Kelvinator">Kelvinator</option>
                    <option value="Videocon">Videocon</option>
                    <option value="Onida">Onida</option>
                    <option value="Akai">Akai</option>
                    <option value="Micromax">Micromax</option>
                    <option value="Intex">Intex</option>
                    <option value="Lavie">Lavie</option>
                    <option value="Samsonite">Samsonite</option>
                    <option value="American Tourister">American Tourister</option>
                    <option value="Skybags">Skybags</option>
                    <option value="Safari">Safari</option>
                    <option value="VIP">VIP</option>
                    <option value="Delsey">Delsey</option>
                    <option value="Parker">Parker</option>
                    <option value="Pilot">Pilot</option>
                    <option value="Cello">Cello</option>
                    <option value="Maped">Maped</option>
                    <option value="Camlin">Camlin</option>
                    <option value="Faber Castell">Faber Castell</option>
                    <option value="Doms">Doms</option>
                    <option value="Reynolds">Reynolds</option>
                    <option value="Flair">Flair</option>
                    <option value="Add Gel">Add Gel</option>
                    <option value="Montex">Montex</option>
                    <option value="Roto">Roto</option>
                    <option value="Kores">Kores</option>
                    <option value="Luxor">Luxor</option>
                    <option value="Nataraj">Nataraj</option>
                    <option value="Apsara">Apsara</option>
                    <option value="Staedtler">Staedtler</option>
                    <option value="Pentel">Pentel</option>
                    <option value="Tombow">Tombow</option>
                    <option value="Mohan">Mohan</option>
                    <option value="Gem">Gem</option>
                    <option value="Casio">Casio</option>
                    <option value="Citizen">Citizen</option>
                    <option value="Seiko">Seiko</option>
                    <option value="Fastrack">Fastrack</option>
                    <option value="Titan">Titan</option>
                    <option value="Sonata">Sonata</option>
                    <option value="Maxima">Maxima</option>
                    <option value="Timex">Timex</option>
                    <option value="Roland">Roland</option>
                    <option value="Yamaha">Yamaha</option>
                    <option value="Rockstand">Rockstand</option>
                    <option value="Micheal">Micheal</option>
                    <option value="JBL">JBL</option>
                    <option value="Bose">Bose</option>
                    <option value="Sennheiser">Sennheiser</option>
                    <option value="Audio Technica">Audio Technica</option>
                    <option value="Skullcandy">Skullcandy</option>
                    <option value="Boat">Boat</option>
                    <option value="Marshall">Marshall</option>
                    <option value="Bang">Bang</option>
                    <option value="Olufsen">Olufsen</option>
                    <option value="Defy">Defy</option>
                    <option value="Blue">Blue</option>
                    <option value="Shure">Shure</option>
                    <option value="Vestel">Vestel</option>
                    <option value="TCL">TCL</option>
                    <option value="Vu">Vu</option>
                    <option value="Mi">Mi</option>
                    <option value="Motorola">Motorola</option>
                    <option value="Nokia">Nokia</option>
                    <option value="Acer">Acer</option>
                    <option value="MSI">MSI</option>
                    <option value="Apple">Apple</option>
                    <option value="Logitech">Logitech</option>
                    <option value="Microsoft">Microsoft</option>
                    <option value="Shopclues">Shopclues</option>
                    <option value="ebay">ebay</option>
                    <option value="Vijay Sales">Vijay Sales</option>
                    <option value="Poorvika">Poorvika</option>
                    <option value="Big C Mobiles">Big C Mobiles</option>
                    <option value="World Mobiles">World Mobiles</option>
                    <option value="Sangeetha Mobiles">Sangeetha Mobiles</option>
                    <option value="Lot Mobiles">Lot Mobiles</option>
                    <option value="UniverCell">UniverCell</option>
                    <option value="Redmi">Redmi</option>
                    <option value="POCO">POCO</option>
                    <option value="Infinix">Infinix</option>
                    <option value="Tecno">Tecno</option>
                    <option value="Itel">Itel</option>
                    <option value="Lava">Lava</option>
                    <option value="BSNL">BSNL</option>
                    <option value="MTNL">MTNL</option>
                    <option value="Lucknow">Lucknow</option>
                    <option value="Kanpur">Kanpur</option>
                    <option value="Nagpur">Nagpur</option>
                    <option value="Indore">Indore</option>
                    <option value="Thane">Thane</option>
                    <option value="Bhopal">Bhopal</option>
                    <option value="Visakhapatnam">Visakhapatnam</option>
                    <option value="Vadodara">Vadodara</option>
                    <option value="Coimbatore">Coimbatore</option>
                    <option value="Kochi">Kochi</option>
                    <option value="Patna">Patna</option>
                    <option value="Raipur">Raipur</option>
                    <option value="Ranchi">Ranchi</option>
                    <option value="Jammu">Jammu</option>
                    <option value="Srinagar">Srinagar</option>
                    <option value="Dehradun">Dehradun</option>
                    <option value="Mysore">Mysore</option>
                    <option value="Guwahati">Guwahati</option>
                    <option value="Bhubaneswar">Bhubaneswar</option>
                    <option value="Cuttack">Cuttack</option>
                    <option value="Puri">Puri</option>
                    <option value="Rourkela">Rourkela</option>
                    <option value="Berhampur">Berhampur</option>
                    <option value="Durgapur">Durgapur</option>
                    <option value="Asansol">Asansol</option>
                    <option value="Malda">Malda</option>
                    <option value="Shibpur">Shibpur</option>
                </select>
                <button type="submit">Apply Filters</button>
                <button type="button" onclick="window.location.href='/'">Reset</button>
            </form>
        </div>
        
        <div class="last-updated">🕐 Last updated: {{ last_updated }}</div>
        
        <div class="coupons-grid">
                    <option value="">All Stores</option>
                    <option value="Amazon">Amazon (6)</option>
                    <option value="Flipkart">Flipkart (6)</option>
                    <option value="YouTube Shopping">YouTube Shopping (8)</option>
                    <option value="Myntra">Myntra (4)</option>
                    <option value="Swiggy">Swiggy (4)</option>
                    <option value="Zomato">Zomato (4)</option>
                    <option value="Ajio">Ajio (3)</option>
                    <option value="Croma">Croma (3)</option>
                    <option value="Meesho">Meesho (3)</option>
                    <option value="Nykaa">Nykaa (3)</option>
                    <option value="Paytm">Paytm (3)</option>
                    <option value="Reliance Digital">Reliance Digital (3)</option>
                    <option value="Snapdeal">Snapdeal (3)</option>
                    <option value="Tata Cliq">Tata Cliq (3)</option>
                    <option value="Swiggy Delivery">Swiggy Delivery (3)</option>
                    <option value="Pepperfry">Pepperfry (2)</option>
                    <option value="Shoppers Stop">Shoppers Stop (2)</option>
                    <option value="Blinkit">Blinkit</option>
                    <option value="Zepto">Zepto</option>
                    <option value="BigBasket">BigBasket</option>
                    <option value="Dmart">Dmart</option>
                    <option value="FirstCry">FirstCry</option>
                    <option value="PharmEasy">PharmEasy</option>
                    <option value="BookMyShow">BookMyShow</option>
                    <option value="MakeMyTrip">MakeMyTrip</option>
                    <option value="Goibibo">Goibibo</option>
                    <option value="Yatra">Yatra</option>
                    <option value="CRED">CRED</option>
                    <option value="Simpl">Simpl</option>
                    <option value="PineLabs">PineLabs</option>
                    <option value="Nykaa Fashion">Nykaa Fashion</option>
                    <option value="Libas">Libas</option>
                    <option value="W For Woman">W For Woman</option>
                    <option value="Allen Solly">Allen Solly</option>
                    <option value="Louis Philippe">Louis Philippe</option>
                    <option value="Peter England">Peter England</option>
                    <option value="adidas">adidas</option>
                    <option value="Nike">Nike</option>
                    <option value="Puma">Puma</option>
                    <option value="Samsung">Samsung</option>
                    <option value="OnePlus">OnePlus</option>
                    <option value="Vivo">Vivo</option>
                    <option value="Oppo">Oppo</option>
                    <option value="Realme">Realme</option>
                    <option value="Lenovo">Lenovo</option>
                    <option value="Dell">Dell</option>
                    <option value="HP">HP</option>
                    <option value="Asus">Asus</option>
                    <option value="Jio">Jio</option>
                    <option value="Airtel">Airtel</option>
                    <option value="Vi">Vi</option>
                    <option value="McDonald's">McDonald's</option>
                    <option value="KFC">KFC</option>
                    <option value="Pizza Hut">Pizza Hut</option>
                    <option value="Domino's">Domino's</option>
                    <option value="Subway">Subway</option>
                    <option value="Burger King">Burger King</option>
                    <option value="Costa Coffee">Costa Coffee</option>
                    <option value="CCD">CCD</option>
                    <option value="Barista">Barista</option>
                    <option value="Starbucks">Starbucks</option>
                    <option value="Dunkin">Dunkin</option>
                    <option value="Faasos">Faasos</option>
                    <option value="FreshMenu">FreshMenu</option>
                    <option value="Spencer's">Spencer's</option>
                    <option value="Big Bazaar">Big Bazaar</option>
                    <option value="More">More</option>
                    <option value="Nilgiris">Nilgiris</option>
                    <option value="Apollo Pharmacy">Apollo Pharmacy</option>
                    <option value="NetMeds">NetMeds</option>
                </select>
                <select name="city">
                    <option value="">All Cities (includes local)</option>
                    <option value="all">All India Only</option>
                    <option value="Hyderabad">Hyderabad</option>
                    <option value="Bangalore">Bangalore</option>
                    <option value="Mumbai">Mumbai</option>
                    <option value="Delhi">Delhi</option>
                    <option value="Chennai">Chennai</option>
                    <option value="Pune">Pune</option>
                    <option value="Kolkata">Kolkata</option>
                    <option value="Chandigarh">Chandigarh</option>
                    <option value="Ahmedabad">Ahmedabad</option>
                    <option value="Jaipur">Jaipur</option>
                </select>
                <button type="submit">Apply Filters</button>
                <button type="button" onclick="window.location.href='/'">Reset</button>
            </form>
        </div>
        
        <div class="last-updated">🕐 Last updated: {{ last_updated }}</div>
        
        <div class="coupons-grid">
            {% for coupon in coupons %}
            <div class="coupon-card">
                <div class="coupon-header">
                    <span class="coupon-source">{{ coupon.source }}</span>
                    <span class="coupon-discount">{{ coupon.discount }}</span>
                </div>
                <div class="coupon-body">
                    {% if coupon.city and coupon.city != 'all' %}
                    <div class="city-badge">{{ coupon.city }}</div>
                    {% endif %}
                    <div class="coupon-code">
                        {% set coupon_code = coupon.code or coupon.coupon_code %}
                        {% if coupon_code %}
                        <div class="code-box" style="background:#22c55e;color:white;">{{ coupon_code }}</div>
                        <button class="copy-btn" onclick="copyCode('{{ coupon_code }}')">Copy</button>
                        {% else %}
                        <div class="code-box" style="background:#06b6d4;color:white;">Coupon Not Required</div>
                        {% endif %}
                    </div>
                    <p class="coupon-desc">{{ coupon.description }}</p>
                    <div class="coupon-details">
                        <div class="detail-item">Min Order: <span>{{ coupon.min_order }}</span></div>
                        <div class="detail-item">Expires: <span>{{ coupon.expires }}</span></div>
                    </div>
                    <div class="coupon-buttons">
                        <a href="{{ coupon.product_url }}" target="_blank" class="btn-visit" onclick="trackVisit('{{ loop.index }}', '{{ coupon.source }}')">🌐 Visit Site</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <footer>
        <p>© 2026 GrabCoupon - Find the Best Coupons in India</p>
    </footer>
    
    <script>
        function copyCode(code) {
            navigator.clipboard.writeText(code);
            alert('Coupon code ' + code + ' copied!');
        }
    </script>
</body>
</html>
"""


def load_coupons() -> List[Dict[str, Any]]:
    """Load coupons from JSON file"""
    # Try multiple paths for local and deployed environments
    paths_to_try = [
        "deals_bot/data/coupons.json",
        "data/coupons.json",
        "../deals_bot/data/coupons.json",
    ]
    for filepath in paths_to_try:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return data.get("coupons", [])
            except:
                pass
    return []

# Initial load after load_coupons is defined
refresh_coupons()


@app.route('/local')
def local_deals():
    """Local restaurants and food deals page"""
    global coupons_cache
    check_and_refresh()
    all_coupons = coupons_cache if coupons_cache else load_coupons()
    
    # Filter only food/restaurants
    food_coupons = [c for c in all_coupons if c.get('category') == 'food']
    
    # Get unique cities from food deals - proper cities only
    all_cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Delhi', 'Chennai', 'Pune', 'Kolkata', 'Chandigarh', 'Ahmedabad', 'Jaipur']
    
    # Apply city filter
    city = request.args.get('city', '')
    if city and city != 'all':
        food_coupons = [c for c in food_coupons if c.get('city') == city or c.get('city') == 'all']
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        coupons=food_coupons[:50],
        total_coupons=len(food_coupons),
        sources=[],  # Empty - hide source filter on local page
        cities=all_cities,
        selected_city=city,
        last_updated=cache_updated.strftime('%Y-%m-%d %H:%M') if cache_updated else 'N/A',
        is_local=True,
        category_counts={}
    )


@app.route('/')
def index():
    """Main dashboard page"""
    global coupons_cache
    # Check if refresh needed on each request
    check_and_refresh()
    all_coupons = coupons_cache if coupons_cache else load_coupons()
    
    # Apply filters
    source = request.args.get('source', '')
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    search = request.args.get('search', '').lower()
    
    filtered = all_coupons
    if source:
        filtered = [c for c in filtered if c.get('source') == source]
    if category and category != 'all':
        filtered = [c for c in filtered if c.get('category') == category]
    if city and city != 'all':
        # Show coupons for specific city or all (non-city specific)
        filtered = [c for c in filtered if c.get('city') == city or c.get('city') == 'all']
    if search:
        filtered = [c for c in filtered if search in c.get('description', '').lower() or search in (c.get('code') or c.get('coupon_code') or '').lower()]
    
    # Get stats
    sources = set(c.get('source') for c in all_coupons)
    cities = set(c.get('city') for c in all_coupons if c.get('city') != 'all')
    
    # Get category counts for tabs
    categories = {}
    for c in all_coupons:
        cat = c.get('category', 'all')
        if cat == 'all':
            continue
        categories[cat] = categories.get(cat, 0) + 1
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        coupons=filtered[:50],
        total_coupons=len(filtered),
        sources=len(sources),
        cities=sorted([c for c in cities if c]),
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
        category_counts=categories
    )


@app.route('/api/coupons')
def api_coupons():
    """API endpoint with filtering support"""
    all_coupons = load_coupons()
    
    # Apply filters
    source = request.args.get('source', '')
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    
    filtered = all_coupons
    if source:
        filtered = [c for c in filtered if c.get('source') == source]
    if category and category != 'all':
        filtered = [c for c in filtered if c.get('category') == category]
    if city and city != 'all':
        filtered = [c for c in filtered if c.get('city') == city or c.get('city') == 'all']
    
    return jsonify({
        "count": len(filtered),
        "coupons": filtered,
        "timestamp": datetime.now().isoformat()
    })


# Visitor tracking data file
VISITORS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'visitors.json')

def get_visitors_data():
    """Load visitors data from JSON file"""
    if os.path.exists(VISITORS_FILE):
        try:
            with open(VISITORS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"visits": [], "stats": {"total": 0, "today": 0}}
    return {"visits": [], "stats": {"total": 0, "today": 0}}

def save_visitors_data(data):
    """Save visitors data to JSON file"""
    os.makedirs(os.path.dirname(VISITORS_FILE), exist_ok=True)
    with open(VISITORS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/api/track_visit')
def api_track_visit():
    """Track a coupon visit"""
    coupon_id = request.args.get('id', '')
    source = request.args.get('source', 'unknown')
    
    data = get_visitors_data()
    
    # Add visit
    visit = {
        "id": coupon_id,
        "source": source,
        "timestamp": datetime.now().isoformat(),
        "user_agent": request.headers.get('User-Agent', '')[:200]
    }
    data["visits"].append(visit)
    
    # Update stats
    data["stats"]["total"] = data["stats"].get("total", 0) + 1
    
    # Count today's visits
    today = datetime.now().date().isoformat()
    today_visits = sum(1 for v in data["visits"] if v.get("timestamp", "").startswith(today))
    data["stats"]["today"] = today_visits
    
    # Keep only last 1000 visits
    if len(data["visits"]) > 1000:
        data["visits"] = data["visits"][-1000:]
    
    save_visitors_data(data)
    
    return jsonify({"status": "success", "total_visits": data["stats"]["total"]})

@app.route('/api/visitors')
def api_visitors():
    """Get visitor statistics"""
    data = get_visitors_data()
    return jsonify(data)

def run_server(host='0.0.0.0', port=None):
    if port is None:
        port = int(os.environ.get('PORT', 5000))
    
    # Start the background scheduler
    if not scheduler.running:
        scheduler.start()
        logger.info(f"Background scheduler started - will refresh coupons every {REFRESH_INTERVAL_HOURS} hours")
    
    logger.info(f"Starting GrabCoupon on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)


@app.route('/refresh')
def refresh():
    """Manually refresh coupons"""
    refresh_coupons()
    return jsonify({"status": "success", "last_updated": cache_updated.isoformat() if cache_updated else None, "coupons_count": len(coupons_cache) if coupons_cache else 0})

@app.route('/status')
def status():
    """Show cache status"""
    return jsonify({
        "last_updated": cache_updated.isoformat() if cache_updated else None,
        "coupons_count": len(coupons_cache) if coupons_cache else 0,
        "next_refresh": f"in {REFRESH_INTERVAL_HOURS} hours"
    })

if __name__ == "__main__":
    run_server()
