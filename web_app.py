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
    <title>GrabCoupon - Best Coupon Codes & Deals in India {{ '| ' + request.args.get('category')|title if request.args.get('category') else '' }}</title>
    <meta name="description" content="Find verified coupon codes, discounts & deals from Amazon, Flipkart, Myntra, Swiggy, Zomato & 50+ top Indian stores. Save big on every purchase!">
    <meta name="keywords" content="coupon codes, discount codes, deals, offers, Amazon coupons, Flipkart deals, Myntra discount, Swiggy coupon, Zomato offers, India shopping deals, promo codes">
    <meta name="author" content="GrabCoupon">
    <meta name="robots" content="index, follow">
    <meta name="googlebot" content="index, follow">
    <meta name="language" content="English">
    <meta name="revisit-after" content="1 day">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://grabcoupon.in/">
    <meta property="og:title" content="GrabCoupon - Best Coupon Codes & Deals in India">
    <meta property="og:description" content="Find verified coupon codes & discounts from 50+ top Indian stores. Save big on every purchase!">
    <meta property="og:image" content="/static/og-image.png">
    <meta property="og:site_name" content="GrabCoupon">
    <meta property="og:locale" content="en_IN">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://grabcoupon.in/">
    <meta property="twitter:title" content="GrabCoupon - Best Coupon Codes & Deals in India">
    <meta property="twitter:description" content="Find verified coupon codes & discounts from 50+ top Indian stores. Save big on every purchase!">
    <meta property="twitter:image" content="/static/og-image.png">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="https://grabcoupon.in/">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎫</text></svg>">
    
    <!-- JSON-LD Structured Data for SEO -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "GrabCoupon",
        "url": "https://grabcoupon.in",
        "description": "Find verified coupon codes and discounts from top Indian retailers",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": "https://grabcoupon.in/?search={search_term_string}"
            },
            "query-input": "required name=search_term_string"
        },
        "sameAs": [
            "https://facebook.com/grabcoupon",
            "https://twitter.com/grabcoupon",
            "https://instagram.com/grabcoupon"
        ]
    }
    </script>
    
    <!-- JSON-LD Organization Schema -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "GrabCoupon",
        "url": "https://grabcoupon.in",
        "logo": "https://grabcoupon.in/logo.png",
        "description": "Your trusted source for coupon codes and deals in India",
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+91-XXXXXXXXXX",
            "contactType": "Customer Service"
        }
    }
    </script>
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
            justify-content: center;
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
        
        .trust-bar {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            padding: 12px 20px;
            text-align: center;
            font-size: 0.95rem;
            color: #92400e;
            font-weight: 500;
        }
        
        .trust-bar span {
            margin: 0 10px;
        }
        
        @media (max-width: 600px) {
            .trust-bar {
                font-size: 0.8rem;
                padding: 10px 10px;
            }
            .trust-bar span {
                display: block;
                margin: 5px 0;
            }
            .footer-content {
                grid-template-columns: 1fr;
                text-align: center;
            }
            .coupons-grid { grid-template-columns: 1fr; }
            .logo { font-size: 1.5rem; }
            .tab { padding: 6px 10px; font-size: 0.8rem; }
        }
        
        /* Skip to content link for accessibility */
        .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: #0ea5e9;
            color: white;
            padding: 8px;
            z-index: 1001;
        }
        
        .skip-link:focus {
            top: 0;
        }
        
        /* Focus styles for accessibility */
        a:focus, button:focus, input:focus, select:focus {
            outline: 3px solid #f97316;
            outline-offset: 2px;
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
        
        /* Product Search Section */
        .product-search-section {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 20px;
            border-bottom: 2px solid #0ea5e9;
        }
        
        .product-search-box {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }
        
        .product-search-box h3 {
            color: #0369a1;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .product-search-form {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .product-search-form input {
            flex: 1;
            min-width: 250px;
            max-width: 500px;
            padding: 14px 20px;
            border: 2px solid #0ea5e9;
            border-radius: 30px;
            font-size: 1rem;
            outline: none;
        }
        
        .product-search-form input:focus {
            border-color: #0284c7;
            box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2);
        }
        
        .product-search-form button {
            padding: 14px 30px;
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .product-search-form button:hover {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            transform: translateY(-2px);
        }
        
        .quick-product-links {
            max-width: 900px;
            margin: 15px auto 0;
            text-align: center;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            align-items: center;
        }
        
        .category-quick-links {
            max-width: 1100px;
            margin: 20px auto 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
        }
        
        .quick-category {
            background: white;
            padding: 12px 15px;
            border-radius: 12px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .category-label {
            font-weight: 600;
            color: #0369a1;
            font-size: 0.85rem;
            min-width: 80px;
        }
        
        .quick-link-label {
            font-weight: 600;
            color: #64748b;
        }
        
        .quick-product-btn {
            padding: 8px 16px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            text-decoration: none;
            color: #475569;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        
        .quick-product-btn:hover {
            background: #0ea5e9;
            color: white;
            border-color: #0ea5e9;
        }
        
        @media (max-width: 600px) {
            .product-search-form input {
                min-width: 100%;
            }
            .quick-product-links {
                gap: 8px;
            }
            .quick-product-btn {
                padding: 6px 12px;
                font-size: 0.8rem;
            }
            .category-quick-links {
                gap: 10px;
            }
            .quick-category {
                padding: 10px;
                width: 100%;
                justify-content: flex-start;
            }
            .category-label {
                min-width: 100%;
                margin-bottom: 5px;
            }
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
        
        @media (max-width: 600px) {
            .filter-row {
                flex-wrap: nowrap;
                overflow-x: auto;
                padding-bottom: 10px;
            }
            .filter-row select, .filter-row input {
                min-width: 120px;
                padding: 8px 12px;
                font-size: 0.85rem;
            }
            .filter-row button {
                padding: 8px 16px;
                font-size: 0.85rem;
                white-space: nowrap;
            }
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
        
        .coupon-card.hot-deal-card {
            border: 2px solid #ef4444;
            animation: hotDealGlow 2s ease-in-out infinite;
        }
        
        @keyframes hotDealGlow {
            0%, 100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); }
            50% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
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
            padding: 14px;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 700;
            font-size: 1rem;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn-visit:hover {
            background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
        }
        
        .btn-visit.hot-deal {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }
        
        .btn-visit.hot-deal:hover {
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
        }
        
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
        
        .coupon-badge {
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
        
        .coupon-badge.hot {
            background: #ef4444;
            animation: pulse 2s infinite;
        }
        
        .coupon-badge.featured {
            background: #f59e0b;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
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
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: white;
            padding: 3rem 20px;
            text-align: center;
            margin-top: 3rem;
        }
        
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            text-align: left;
        }
        
        .footer-section h3 {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #f97316;
        }
        
        .footer-section a {
            display: block;
            color: #cbd5e1;
            text-decoration: none;
            padding: 5px 0;
            font-size: 0.9rem;
            transition: color 0.3s;
        }
        
        .footer-section a:hover {
            color: #38bdf8;
        }
        
        .footer-bottom {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid #334155;
            text-align: center;
            color: #94a3b8;
            font-size: 0.85rem;
        }
        
        .social-links {
            margin-top: 1rem;
        }
        
        .social-links a {
            display: inline-block;
            margin: 0 10px;
            font-size: 1.5rem;
        }
        
        .trust-badges {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        
        .trust-badges span {
            background: rgba(255,255,255,0.1);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        
        .last-updated {
            text-align: center;
            color: #0077B6;
            margin-bottom: 20px;
        }
        
        /* Today's Top Deals Section */
        .todays-deals {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 30px;
            border: 2px solid #f59e0b;
        }
        
        .todays-deals-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .todays-deals h2 {
            color: #92400e;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .todays-badge {
            background: #ef4444;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            animation: pulse 2s infinite;
        }
        
        .todays-deals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
        }
        
        .todays-coupon-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #f59e0b;
            transition: all 0.3s;
        }
        
        .todays-coupon-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        }
        
        .todays-coupon-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .todays-source {
            font-weight: 700;
            color: #1e293b;
        }
        
        .todays-discount {
            background: #f97316;
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-weight: 600;
        }
        
        .todays-code {
            background: #ecfccb;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-family: monospace;
            font-size: 1.1rem;
            font-weight: 700;
            color: #166534;
            margin-bottom: 10px;
            cursor: pointer;
            border: 2px dashed #22c55e;
        }
        
        .todays-desc {
            font-size: 0.9rem;
            color: #64748b;
            margin-bottom: 12px;
        }
        
        .todays-cta {
            display: block;
            width: 100%;
            padding: 10px;
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .todays-cta:hover {
            background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        }
        
        .view-all-link {
            color: #f59e0b;
            font-weight: 600;
            text-decoration: none;
        }
        
        .view-all-link:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 1.8rem; }
            .stats-bar { gap: 15px; }
            .coupons-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- Trust Signals Bar -->
    <div class="trust-bar">
        <span>✅ <strong>{{ total_coupons }}+</strong> Verified Coupons</span>
        <span>🕐 Updated <strong>Today</strong></span>
        <span>💰 Avg. Savings: <strong>₹500+</strong></span>
    </div>
    
    <header>
        <div class="header-content">
            <div class="logo">🎫 GrabCoupon</div>
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
    
    <!-- Product Search Section -->
    <div class="product-search-section">
        <div class="product-search-box">
            <h3>🔍 Find Best Deals on Any Product</h3>
            <form method="get" action="/" class="product-search-form">
                <input type="text" name="product" placeholder="Search for products (TV, Mobile, Shirt, Pizza, Medicine...)" value="{{ request.args.get('product', '') }}">
                <button type="submit">Find Deals</button>
            </form>
        </div>
        
        <!-- Category Quick Links -->
        <div class="category-quick-links">
            <div class="quick-category">
                <span class="category-label">📺 Electronics</span>
                <a href="/?product=LED+TV" class="quick-product-btn">LED TV</a>
                <a href="/?product=Refrigerator" class="quick-product-btn">Fridge</a>
                <a href="/?product=Air+Conditioner" class="quick-product-btn">AC</a>
                <a href="/?product=Laptop" class="quick-product-btn">Laptop</a>
                <a href="/?product=Mobile" class="quick-product-btn">Mobile</a>
                <a href="/?product=Headphones" class="quick-product-btn">Headphones</a>
                <a href="/?product=Washing+Machine" class="quick-product-btn">Washing Machine</a>
            </div>
            <div class="quick-category">
                <span class="category-label">👕 Fashion</span>
                <a href="/?product=Mens+Shirt" class="quick-product-btn">Men's Shirt</a>
                <a href="/?product=Womens+Dress" class="quick-product-btn">Women's Dress</a>
                <a href="/?product=Shoes" class="quick-product-btn">Shoes</a>
                <a href="/?product=Jeans" class="quick-product-btn">Jeans</a>
                <a href="/?product=Kurti" class="quick-product-btn">Kurti</a>
                <a href="/?product=Watch" class="quick-product-btn">Watch</a>
            </div>
            <div class="quick-category">
                <span class="category-label">🍔 Food</span>
                <a href="/?product=Biryani" class="quick-product-btn">Biryani</a>
                <a href="/?product=Pizza" class="quick-product-btn">Pizza</a>
                <a href="/?product=Burger" class="quick-product-btn">Burger</a>
                <a href="/?product=Fast+Food" class="quick-product-btn">Fast Food</a>
                <a href="/?product=Chicken" class="quick-product-btn">Chicken</a>
                <a href="/?product=Ice+Cream" class="quick-product-btn">Ice Cream</a>
            </div>
            <div class="quick-category">
                <span class="category-label">💄 Beauty</span>
                <a href="/?product=Makeup" class="quick-product-btn">Makeup</a>
                <a href="/?product=Skin+Care" class="quick-product-btn">Skincare</a>
                <a href="/?product=Hair+Care" class="quick-product-btn">Hair Care</a>
                <a href="/?product=Perfume" class="quick-product-btn">Perfume</a>
                <a href="/?product=Cosmetics" class="quick-product-btn">Cosmetics</a>
            </div>
            <div class="quick-category">
                <span class="category-label">🏠 Home</span>
                <a href="/?product=Furniture" class="quick-product-btn">Furniture</a>
                <a href="/?product=Bedsheet" class="quick-product-btn">Bedsheet</a>
                <a href="/?product=Pillow" class="quick-product-btn">Pillow</a>
                <a href="/?product=Curtain" class="quick-product-btn">Curtain</a>
                <a href="/?product=Decor" class="quick-product-btn">Decor</a>
                <a href="/?product=Kitchen" class="quick-product-btn">Kitchen</a>
            </div>
            <div class="quick-category">
                <span class="category-label">🛒 Grocery</span>
                <a href="/?product=Vegetables" class="quick-product-btn">Vegetables</a>
                <a href="/?product=Fruits" class="quick-product-btn">Fruits</a>
                <a href="/?product=Snacks" class="quick-product-btn">Snacks</a>
                <a href="/?product=Dairy" class="quick-product-btn">Dairy</a>
                <a href="/?product=Beverages" class="quick-product-btn">Beverages</a>
            </div>
            <div class="quick-category">
                <span class="category-label">✈️ Travel</span>
                <a href="/?product=Flight" class="quick-product-btn">Flights</a>
                <a href="/?product=Hotel" class="quick-product-btn">Hotels</a>
                <a href="/?product=Bus" class="quick-product-btn">Bus</a>
                <a href="/?product=Train" class="quick-product-btn">Train</a>
                <a href="/?product=Holiday" class="quick-product-btn">Holiday</a>
            </div>
            <div class="quick-category">
                <span class="category-label">💊 Health</span>
                <a href="/?product=Medicine" class="quick-product-btn">Medicine</a>
                <a href="/?product=Vitamins" class="quick-product-btn">Vitamins</a>
                <a href="/?product=Protein" class="quick-product-btn">Protein</a>
                <a href="/?product=Ayurvedic" class="quick-product-btn">Ayurvedic</a>
                <a href="/?product=Fitness" class="quick-product-btn">Fitness</a>
            </div>
            <div class="quick-category">
                <span class="category-label">💰 Recharge</span>
                <a href="/?product=Mobile+Recharge" class="quick-product-btn">Mobile</a>
                <a href="/?product=DTH" class="quick-product-btn">DTH</a>
                <a href="/?product=Electricity" class="quick-product-btn">Electricity</a>
                <a href="/?product=Water+Bill" class="quick-product-btn">Water Bill</a>
                <a href="/?product=Gas" class="quick-product-btn">Gas</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="filters">
            <form class="filter-row" method="get">
                {% if request.args.get('category') %}
                <input type="hidden" name="category" value="{{ request.args.get('category') }}">
                {% endif %}
                {% if request.args.get('search') %}
                <input type="hidden" name="search" value="{{ request.args.get('search') }}">
                {% endif %}
                {% if request.args.get('product') %}
                <input type="hidden" name="product" value="{{ request.args.get('product') }}">
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
        
        <!-- Today's Top Deals Section -->
        {% if todays_deals %}
        <div class="todays-deals">
            <div class="todays-deals-header">
                <h2>🔥 Today's Top Deals <span class="todays-badge">Limited Time!</span></h2>
                <a href="#all-coupons" class="view-all-link">View All Coupons ↓</a>
            </div>
            <div class="todays-deals-grid">
                {% for coupon in todays_deals %}
                <div class="todays-coupon-card">
                    <div class="todays-coupon-header">
                        <span class="todays-source">{{ coupon.source }}</span>
                        <span class="todays-discount">{{ coupon.discount }}</span>
                    </div>
                    <div class="todays-code" onclick="copyCode('{{ coupon.code or coupon.coupon_code }}')">
                        {{ coupon.code or coupon.coupon_code or 'No Code Needed' }}
                    </div>
                    <p class="todays-desc">{{ coupon.description }}</p>
                    <a href="{{ coupon.product_url or coupon.url }}" target="_blank" class="todays-cta">
                        Get Deal 🚀
                    </a>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div id="all-coupons"></div>
        <div class="coupons-grid">
            {% for coupon in coupons %}
            <div class="coupon-card {% if coupon.is_hot %}hot-deal-card{% endif %}">
                <div class="coupon-header">
                    <span class="coupon-source">{{ coupon.source }}</span>
                    <span class="coupon-discount">{{ coupon.discount }}</span>
                </div>
                <div class="coupon-body">
                    {% if coupon.is_hot %}
                    <div class="coupon-badge hot">🔥 Hot Deal</div>
                    {% elif coupon.is_featured %}
                    <div class="coupon-badge featured">⭐ Featured</div>
                    {% endif %}
                    {% if coupon.city and coupon.city != 'all' %}
                    <div class="city-badge">{{ coupon.city }}</div>
                    {% endif %}
                    <div class="coupon-code">
                        {% set coupon_code = coupon.code or coupon.coupon_code %}
                        {% if coupon_code %}
                        <div class="code-box">{{ coupon_code }}</div>
                        <button class="copy-btn" onclick="copyCode('{{ coupon_code }}')">Copy</button>
                        {% else %}
                        <div class="code-box" style="background:#06b6d4;color:white;">No Code Needed</div>
                        {% endif %}
                    </div>
                    <p class="coupon-desc">{{ coupon.description }}</p>
                    <div class="coupon-details">
                        {% if coupon.min_order %}
                        <div class="detail-item">Min Order: <span>₹{{ coupon.min_order }}</span></div>
                        {% endif %}
                        {% if coupon.expires %}
                        <div class="detail-item">Expires: <span>{{ coupon.expires }}</span></div>
                        {% endif %}
                    </div>
                    <div class="coupon-buttons">
                        <a href="{{ coupon.product_url or coupon.url }}" target="_blank" class="btn-visit {% if coupon.is_hot %}hot-deal{% endif %}" onclick="trackVisit('{{ loop.index }}', '{{ coupon.source }}')">
                            {% if coupon.is_hot %}
                            🔥 Get Deal Now
                            {% else %}
                            🚀 Visit Store
                            {% endif %}
                        </a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h3>🔗 Quick Links</h3>
                <a href="/">All Deals</a>
                <a href="/?category=electronics">Electronics</a>
                <a href="/?category=fashion">Fashion</a>
                <a href="/?category=food">Food & Dining</a>
                <a href="/?category=travel">Travel</a>
            </div>
            <div class="footer-section">
                <h3>🏪 Top Stores</h3>
                <a href="/?source=Amazon">Amazon Coupons</a>
                <a href="/?source=Flipkart">Flipkart Deals</a>
                <a href="/?source=Myntra">Myntra Offers</a>
                <a href="/?source=Swiggy">Swiggy Coupons</a>
                <a href="/?source=Zomato">Zomato Discounts</a>
                <a href="/?source=Croma">Croma Offers</a>
                <a href="/?source=Reliance Digital">Reliance Digital</a>
            </div>
            <div class="footer-section">
                <h3>📺 Electronics</h3>
                <a href="/?product=LED+TV">LED TV Deals</a>
                <a href="/?product=Refrigerator">Refrigerator Offers</a>
                <a href="/?product=Air+Conditioner">AC Coupons</a>
                <a href="/?product=Laptop">Laptop Deals</a>
                <a href="/?product=Mobile">Mobile Offers</a>
                <a href="/?product=Headphones">Headphones</a>
                <a href="/?product=Washing+Machine">Washing Machine</a>
            </div>
            <div class="footer-section">
                <h3>📄 Information</h3>
                <a href="/about">About Us</a>
                <a href="/contact">Contact Us</a>
                <a href="/privacy">Privacy Policy</a>
                <a href="/terms">Terms & Conditions</a>
                <a href="/disclaimer">Disclaimer</a>
            </div>
            <div class="footer-section">
                <h3>📱 Connect With Us</h3>
                <div class="social-links">
                    <a href="#" aria-label="Facebook">📘</a>
                    <a href="#" aria-label="Twitter">🐦</a>
                    <a href="#" aria-label="Instagram">📸</a>
                    <a href="#" aria-label="Telegram">✈️</a>
                </div>
                <p style="margin-top: 1rem; font-size: 0.9rem; color: #cbd5e1;">
                    Get latest deals delivered to your inbox!
                </p>
            </div>
        </div>
        <div class="trust-badges">
            <span>🔒 Secure Payments</span>
            <span>✅ Verified Coupons</span>
            <span>⚡ Daily Updates</span>
        </div>
        <div class="footer-bottom">
            <p>© 2026 GrabCoupon - All Rights Reserved</p>
            <p style="margin-top: 5px; font-size: 0.8rem;">
                We may earn commission when you click or buy through links on our site.
            </p>
        </div>
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
    
    # Product search - search for products across all categories
    product = request.args.get('product', '').lower()
    if product:
        # Define product keywords mapping for ALL categories
        product_keywords = {
            # Electronics
            'led tv': ['tv', 'television', 'smart tv', 'led', 'lcd'],
            'refrigerator': ['fridge', 'refrigerator', ' refrigerator'],
            'air conditioner': ['ac', 'air conditioner', 'air conditioning', 'split ac', 'window ac'],
            'laptop': ['laptop', 'notebook', 'computer', 'macbook'],
            'mobile': ['mobile', 'phone', 'smartphone', 'cellphone'],
            'headphones': ['headphone', 'earphone', 'earbuds', 'bluetooth headset'],
            'washing machine': ['washing machine', 'washer'],
            'microwave': ['microwave', 'oven'],
            'tv': ['tv', 'television', 'smart tv', 'led', 'lcd'],
            'fridge': ['fridge', 'refrigerator'],
            'ac': ['ac', 'air conditioner', 'air conditioning'],
            # Fashion
            'mens shirt': ['shirt', 'mens shirt', 'formal shirt', 'casual shirt'],
            'womens dress': ['dress', 'womens dress', 'saree', 'lehenga'],
            'shoes': ['shoes', 'sneakers', 'footwear', 'sandals', 'slippers'],
            'jeans': ['jeans', 'pants', 'trousers'],
            'kurti': ['kurti', 'kurtas', 'kurta'],
            'watch': ['watch', 'wrist watch', 'smart watch'],
            # Food
            'biryani': ['biryani', 'rice', 'non veg'],
            'pizza': ['pizza', 'pizzeria'],
            'burger': ['burger', 'fast food'],
            'fast food': ['fast food', 'junk food'],
            'chicken': ['chicken', 'non veg', 'mutton'],
            'ice cream': ['ice cream', 'dessert', 'cold drink'],
            # Beauty
            'makeup': ['makeup', 'cosmetics', 'lipstick', 'mascara'],
            'skin care': ['skin care', 'moisturizer', 'sunscreen', 'serum'],
            'hair care': ['hair care', 'shampoo', 'conditioner', 'oil'],
            'perfume': ['perfume', 'fragrance', 'attar'],
            'cosmetics': ['cosmetics', 'makeup'],
            # Home
            'furniture': ['furniture', 'sofa', 'chair', 'table'],
            'bedsheet': ['bedsheet', 'bed cover', 'linen'],
            'pillow': ['pillow', 'cushion'],
            'curtain': ['curtain', 'blinds'],
            'decor': ['decor', 'decoration', 'home decor'],
            'kitchen': ['kitchen', 'cookware', 'utensils'],
            # Grocery
            'vegetables': ['vegetables', 'veggies', 'fresh produce'],
            'fruits': ['fruits', 'fresh fruits'],
            'snacks': ['snacks', 'chips', 'biscuits'],
            'dairy': ['dairy', 'milk', 'cheese', 'yogurt'],
            'beverages': ['beverages', 'drinks', 'juice', 'water'],
            # Travel
            'flight': ['flight', 'airline', 'air ticket', 'flight booking'],
            'hotel': ['hotel', 'stay', 'resort', 'accommodation'],
            'bus': ['bus', 'bus ticket'],
            'train': ['train', 'railway', 'rail ticket'],
            'holiday': ['holiday', 'tour', 'travel package'],
            # Health
            'medicine': ['medicine', 'pharmacy', 'tablet', 'syrup'],
            'vitamins': ['vitamins', 'supplements', 'multivitamin'],
            'protein': ['protein', 'whey', 'nutrition'],
            'ayurvedic': ['ayurvedic', 'herbal', 'ayurveda'],
            'fitness': ['fitness', 'gym', 'workout'],
            # Recharge
            'mobile recharge': ['mobile recharge', 'prepaid', 'postpaid'],
            'dth': ['dth', 'set top box', 'recharge'],
            'electricity': ['electricity', 'bill', 'power'],
            'water bill': ['water bill', 'water supply'],
            'gas': ['gas', 'lpg', 'cylinder'],
        }
        
        # Get keywords for the searched product
        search_terms = [product]
        for key, keywords in product_keywords.items():
            if key in product or product in key:
                search_terms.extend(keywords)
        
        # Filter coupons that match product keywords
        filtered = [c for c in filtered 
                    if any(term in c.get('description', '').lower() or 
                           term in c.get('source', '').lower() or
                           term in c.get('category', '').lower() or
                           term in (c.get('code') or '').lower()
                           for term in search_terms)]
    
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
    
    # Get Today's Top Deals (only on main page without filters)
    todays_deals = []
    if not any([source, category, city, search, product]):
        # Show today's top deals on main page
        # Priority: is_hot > is_featured > based on day of week
        import random
        today = datetime.now().day
        
        # Get hot and featured deals first
        hot_deals = [c for c in all_coupons if c.get('is_hot')]
        featured_deals = [c for c in all_coupons if c.get('is_featured') and not c.get('is_hot')]
        
        # Combine and shuffle for variety
        todays_deals = hot_deals + featured_deals
        random.shuffle(todays_deals)
        
        # If not enough, add more from top sources
        if len(todays_deals) < 6:
            remaining = [c for c in all_coupons if c not in todays_deals][:10]
            todays_deals.extend(remaining)
        
        todays_deals = todays_deals[:6]  # Show max 6 today's deals
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        coupons=filtered[:50],
        total_coupons=len(filtered),
        sources=len(sources),
        cities=sorted([c for c in cities if c]),
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
        category_counts=categories,
        todays_deals=todays_deals
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