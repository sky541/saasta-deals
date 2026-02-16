"""
OfferOye - Coupons Web Application
Show live coupons from Indian e-commerce websites
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from flask import Flask, render_template_string, jsonify, request

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

# Don't call refresh_coupons() here - load_coupons not defined yet


DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OfferOye - Coupons & Offers</title>
    <meta name="description" content="Find the best coupon codes and offers from top Indian retailers">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #00B4D8;
            --secondary: #90E0EF;
            --dark: #0077B6;
            --light: #CAF0F8;
            --white: #ffffff;
            --success: #28a745;
            --danger: #E63946;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(180deg, #CAF0F8 0%, #90E0EF 100%);
            color: #023E8A;
            min-height: 100vh;
        }
        
        header {
            background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
            color: white;
            padding: 1.2rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
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
        
        .hero {
            background: linear-gradient(135deg, #00B4D8 0%, #48CAE4 100%);
            color: white;
            padding: 2.5rem 20px;
            text-align: center;
        }
        
        .hero h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .hero p { font-size: 1.2rem; opacity: 0.95; }
        
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }
        
        .stat {
            background: rgba(255,255,255,0.25);
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
            background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .filter-row button:hover { transform: translateY(-2px); }
        
        .coupons-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
        }
        
        .coupon-card {
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,119,182,0.15);
            transition: all 0.3s;
            border: 3px solid transparent;
        }
        
        .coupon-card:hover {
            transform: translateY(-5px);
            border-color: #00B4D8;
            box-shadow: 0 12px 30px rgba(0,119,182,0.25);
        }
        
        .coupon-header {
            background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
            color: white;
            padding: 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .coupon-source {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .coupon-discount {
            background: #FFD60A;
            color: #0077B6;
            padding: 5px 15px;
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
            <div class="logo">🎫 OfferOye</div>
        </div>
    </header>
    
    <div class="hero">
        <h1>🎟️ Best Coupon Codes in India</h1>
        <p>Find working coupon codes from Amazon, Flipkart, Myntra, Ajio and more!</p>
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-number">{{ total_coupons }}</div>
                <div class="stat-label">Active Coupons</div>
            </div>
            <div class="stat">
                <div class="stat-number">{{ sources }}</div>
                <div class="stat-label">Partner Stores</div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="filters">
            <form class="filter-row" method="get">
                <select name="source">
                    <option value="">All Stores</option>
                    <option value="Amazon">Amazon</option>
                    <option value="Flipkart">Flipkart</option>
                    <option value="Myntra">Myntra</option>
                    <option value="Ajio">Ajio</option>
                    <option value="Croma">Croma</option>
                    <option value="Paytm">Paytm</option>
                    <option value="Snapdeal">Snapdeal</option>
                    <option value="Meesho">Meesho</option>
                    <option value="Nykaa">Nykaa</option>
                    <option value="Swiggy">Swiggy</option>
                    <option value="Zomato">Zomato</option>
                    <option value="Reliance Digital">Reliance Digital</option>
                    <option value="Tata Cliq">Tata Cliq</option>
                    <option value="Shoppers Stop">Shoppers Stop</option>
                    <option value="Pepperfry">Pepperfry</option>
                    <option value="YouTube Shopping">YouTube Shopping</option>
                    <option value="Local Restaurant">Local Restaurant</option>
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
                <select name="category">
                    <option value="">All Categories</option>
                    <option value="all">All</option>
                    <option value="electronics">Electronics</option>
                    <option value="fashion">Fashion</option>
                    <option value="mobiles">Mobiles</option>
                    <option value="food">Food & Dining</option>
                    <option value="beauty">Beauty</option>
                    <option value="home">Home</option>
                </select>
                <input type="text" name="search" placeholder="Search coupons...">
                <button type="submit">Apply</button>
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
                        <div class="code-box">{{ coupon.coupon_code }}</div>
                        <button class="copy-btn" onclick="copyCode('{{ coupon.coupon_code }}')">Copy</button>
                    </div>
                    <p class="coupon-desc">{{ coupon.description }}</p>
                    <div class="coupon-details">
                        <div class="detail-item">Min Order: <span>{{ coupon.min_order }}</span></div>
                        <div class="detail-item">Expires: <span>{{ coupon.expires }}</span></div>
                    </div>
                    <a href="{{ coupon.product_url }}" target="_blank" class="coupon-btn">Apply Now →</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <footer>
        <p>© 2026 OfferOye - Find the Best Coupons in India</p>
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
        filtered = [c for c in filtered if search in c.get('description', '').lower() or search in c.get('coupon_code', '').lower()]
    
    # Get stats
    sources = set(c.get('source') for c in all_coupons)
    cities = set(c.get('city') for c in all_coupons if c.get('city') != 'all')
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        coupons=filtered[:50],
        total_coupons=len(filtered),
        sources=len(sources),
        cities=sorted(cities),
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M")
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


def run_server(host='0.0.0.0', port=None):
    if port is None:
        port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting OfferOye on http://{host}:{port}")
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
        "next_refresh": "in 12 hours"
    })

if __name__ == "__main__":
    run_server()
