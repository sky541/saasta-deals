"""
OfferOye - Coupons Web Application
Show live coupons from Indian e-commerce websites
"""

import os
import json
import logging
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup

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
            /* Trust + Savings Theme - Based on CouponDunia & GrabOn */
            --primary: #22c55e;      /* Green - trust/money */
            --primary-dark: #16a34a;
            --secondary: #f97316;    /* Orange - excitement */
            --accent: #ef4444;       /* Red - urgency */
            --dark: #1e293b;         /* Slate - premium feel */
            --light: #f8fafc;
            --white: #ffffff;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #334155;
            --text-light: #64748b;
            --gray: #94a3b8;
            --bg: #f8fafc;
            --border: #e2e8f0;
        }
        
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f8fafc;
            color: #334155;
            min-height: 100vh;
        }
        
        /* Main Header Navigation */
        .main-header {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 0.75rem 2rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .main-header .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            color: white;
            font-size: 1.5rem;
            font-weight: 700;
            text-decoration: none;
        }
        
        .main-header .logo-icon {
            font-size: 1.3rem;
        }
        
        .main-nav {
            display: flex;
            gap: 2rem;
        }
        
        .main-nav .nav-link {
            color: rgba(255,255,255,0.9);
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .main-nav .nav-link:hover,
        .main-nav .nav-link.active {
            color: white;
            background: rgba(255,255,255,0.2);
        }
        
        .header-cta .cta-button {
            background: white;
            color: #22c55e;
            padding: 0.6rem 1.5rem;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.3s ease;
        }
        
        .header-cta .cta-button:hover {
            transform: scale(1.05);
        }
        
        @media (max-width: 768px) {
            .main-nav { display: none; }
        }
        
        /* Combined Search Form */
        .combined-search-form {
            width: 100%;
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .search-bar-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            flex-wrap: nowrap;
        }
        
        .main-search-input {
            flex: 1;
            min-width: 300px;
            max-width: 400px;
            padding: 14px 22px;
            border: 3px solid white;
            border-radius: 50px;
            font-size: 1rem;
            background: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        .main-search-input:focus {
            outline: none;
            border-color: #22c55e;
        }
        
        .filter-select {
            padding: 12px 18px;
            border: 3px solid white;
            border-radius: 50px;
            font-size: 0.9rem;
            background: white;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            min-width: 130px;
        }
        
        .filter-select:focus {
            outline: none;
            border-color: #22c55e;
        }
        
        .search-bar-row .search-btn {
            padding: 14px 35px;
            background: #22c55e;
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .search-bar-row .search-btn:hover {
            background: #16a34a;
            transform: translateY(-2px);
        }
        
        @media (max-width: 900px) {
            .search-bar-row {
                flex-wrap: wrap;
                gap: 12px;
            }
            .main-search-input {
                width: 100%;
                max-width: 100%;
            }
            .filter-select {
                flex: 1;
                min-width: 120px;
            }
        }
        
        /* Hero Section - Like GrabOn & CouponDunia */
        .hero-section {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #15803d 100%);
            padding: 40px 20px 50px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.5;
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
            max-width: 700px;
            margin: 0 auto;
        }
        
        .hero-title {
            color: white;
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        
        .hero-title span {
            display: inline;
        }
        
        .hero-subtitle {
            color: rgba(255,255,255,0.95);
            font-size: 1.1rem;
            margin-bottom: 25px;
            font-weight: 500;
        }
        
        /* Search Box */
        .search-container {
            position: relative;
            max-width: 600px;
            margin: 0 auto 20px;
        }
        
        .search-box {
            display: flex;
            align-items: center;
            background: white;
            border-radius: 50px;
            padding: 8px 8px 8px 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        .search-icon {
            font-size: 1.2rem;
            margin-right: 10px;
        }
        
        .search-box input {
            flex: 1;
            border: none;
            outline: none;
            font-size: 1rem;
            padding: 10px;
        }
        
        .search-btn {
            background: #22c55e;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 30px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .search-btn:hover {
            background: #16a34a;
            transform: scale(1.02);
        }
        
        .search-suggestions {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            margin-top: 5px;
            display: none;
            z-index: 100;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .search-suggestions.show {
            display: block;
        }
        
        .suggestion-item {
            padding: 12px 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: background 0.2s;
        }
        
        .suggestion-item:hover {
            background: #f0fdf4;
        }
        
        /* Popular Searches */
        .popular-searches {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            align-items: center;
        }
        
        .popular-label {
            color: rgba(255,255,255,0.8);
            font-weight: 500;
        }
        
        .popular-tag {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.3s;
        }
        
        .popular-tag:hover {
            background: white;
            color: #22c55e;
        }
        
        /* Trust Badges Hero */
        .trust-badges-hero {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
            flex-wrap: wrap;
        }
        
        .badge-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
        }
        
        .badge-icon {
            font-size: 1.5rem;
        }
        
        .badge-text {
            font-size: 0.95rem;
        }
        
        /* Category Bar */
        .category-bar {
            display: flex;
            justify-content: center;
            gap: 10px;
            padding: 15px 20px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            flex-wrap: wrap;
            overflow-x: auto;
        }
        
        .category-pill {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 10px 20px;
            background: #f1f5f9;
            border-radius: 25px;
            text-decoration: none;
            color: #475569;
            font-weight: 500;
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .category-pill:hover, .category-pill.active {
            background: #22c55e;
            color: white;
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .hero-title {
                font-size: 1.8rem;
                flex-direction: column;
            }
            .hero-icon {
                font-size: 2.5rem;
            }
            .search-box {
                flex-direction: column;
                border-radius: 20px;
                padding: 15px;
            }
            .search-box input {
                width: 100%;
                text-align: center;
                margin-bottom: 10px;
            }
            .search-btn {
                width: 100%;
            }
            .trust-badges-hero {
                gap: 20px;
            }
            .badge-item {
                font-size: 0.85rem;
            }
            .category-bar {
                justify-content: flex-start;
                padding: 10px;
            }
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
        
        
        .container { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
        
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
        
        .product-search-input {
            flex: 2;
            min-width: 200px;
            padding: 10px 16px;
            border: 2px solid #22c55e;
            border-radius: 25px;
            font-size: 0.95rem;
            background: white;
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
        
        /* Product Search Results */
        .product-search-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        }
        
        .product-results-header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .product-results-header h3 {
            color: #1e293b;
            font-size: 1.4rem;
            margin-bottom: 5px;
        }
        
        .product-results-header p {
            color: #64748b;
            font-size: 0.9rem;
        }
        
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        
        .product-card {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 15px;
            transition: all 0.3s ease;
            background: white;
        }
        
        .product-card:hover {
            border-color: #22c55e;
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(34, 197, 94, 0.15);
        }
        
        .product-card-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }
        
        .product-image {
            width: 80px;
            height: 80px;
            object-fit: contain;
            border-radius: 8px;
            background: #f8fafc;
        }
        
        .product-info {
            flex: 1;
        }
        
        .product-title {
            font-size: 0.95rem;
            color: #1e293b;
            font-weight: 600;
            margin-bottom: 5px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .product-rating {
            font-size: 0.85rem;
            color: #f59e0b;
        }
        
        .product-price-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 12px 0;
        }
        
        .product-price {
            font-size: 1.4rem;
            font-weight: 700;
            color: #22c55e;
        }
        
        .product-original-price {
            font-size: 0.9rem;
            color: #94a3b8;
            text-decoration: line-through;
        }
        
        .product-source {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .product-source.amazon {
            background: #ff990020;
            color: #ff9900;
        }
        
        .product-source.flipkart {
            background: #2874f020;
            color: #2874f0;
        }
        
        .product-link {
            display: block;
            width: 100%;
            padding: 10px;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        .product-link:hover {
            transform: scale(1.02);
        }
        
        .product-loading {
            text-align: center;
            padding: 40px;
        }
        
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top-color: #22c55e;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .coupons-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 25px;
        }
        
        /* Section Title */
        .section-title {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .section-title h2 {
            font-size: 1.8rem;
            color: #1e293b;
            margin-bottom: 8px;
        }
        
        .section-title p {
            color: #64748b;
            font-size: 0.95rem;
        }
        
        /* Coupon Card - Like CouponDunia */
        .coupon-card {
            background: white;
            border-radius: 16px;
            overflow: visible;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border: 1px solid #e2e8f0;
            position: relative;
            margin-top: 8px;
        }
        
        .coupon-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        
        .coupon-card.hot-deal-card {
            border: 2px solid #ef4444;
        }
        
        /* Trust Badge - Top Bar Style */
        .trust-badge {
            position: absolute;
            top: -8px;
            left: 15px;
            padding: 4px 12px;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            z-index: 10;
            color: white;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .trust-badge.hot {
            background: #ef4444;
        }
        
        .trust-badge.exclusive {
            background: #f97316;
        }
        
        .coupon-header {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            padding: 1rem;
            padding-top: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 1;
        }
        
        .trust-badge.verified {
            background: #22c55e;
            color: white;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
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
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
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
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 1.8rem; }
            .stats-bar { gap: 15px; }
            .coupons-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- Header Navigation -->
    <header class="main-header">
        <div class="header-container">
            <a href="/" class="logo">
                <span class="logo-icon">🎫</span> GrabCoupon
            </a>
            <nav class="main-nav">
                <a href="/" class="nav-link {% if request.path == '/' %}active{% endif %}">Home</a>
                <a href="/local" class="nav-link {% if request.path == '/local' %}active{% endif %}">Local Food Deals</a>
                <a href="/about" class="nav-link {% if request.path == '/about' %}active{% endif %}">About Us</a>
                <a href="/contact" class="nav-link {% if request.path == '/contact' %}active{% endif %}">Contact Us</a>
            </nav>
        </div>
    </header>
    
    <!-- Hero Section with Search - Like GrabOn & CouponDunia -->
    <div class="hero-section">
        <div class="hero-content">
            <!-- Combined Search and Filters -->
            <form class="combined-search-form" method="get">
                <div class="search-bar-row">
                    <input type="text" 
                           id="searchInput"
                           name="search" 
                           placeholder="Search coupons, products (TV, fridge, mobile...)" 
                           value="{{ request.args.get('search', '') }}"
                           autocomplete="off"
                           class="main-search-input">
                    
                    <select name="source" class="filter-select">
                        <option value="">All Stores</option>
                        <option value="Amazon" {% if request.args.get('source')=='Amazon' %}selected{% endif %}>Amazon</option>
                        <option value="Flipkart" {% if request.args.get('source')=='Flipkart' %}selected{% endif %}>Flipkart</option>
                        <option value="Myntra" {% if request.args.get('source')=='Myntra' %}selected{% endif %}>Myntra</option>
                        <option value="Swiggy" {% if request.args.get('source')=='Swiggy' %}selected{% endif %}>Swiggy</option>
                        <option value="Zomato" {% if request.args.get('source')=='Zomato' %}selected{% endif %}>Zomato</option>
                    </select>
                    
                    <select name="city" class="filter-select">
                        <option value="">All Cities</option>
                        <option value="all" {% if request.args.get('city')=='all' %}selected{% endif %}>All India</option>
                        <option value="Hyderabad" {% if request.args.get('city')=='Hyderabad' %}selected{% endif %}>Hyderabad</option>
                        <option value="Bangalore" {% if request.args.get('city')=='Bangalore' %}selected{% endif %}>Bangalore</option>
                        <option value="Mumbai" {% if request.args.get('city')=='Mumbai' %}selected{% endif %}>Mumbai</option>
                        <option value="Delhi" {% if request.args.get('city')=='Delhi' %}selected{% endif %}>Delhi</option>
                        <option value="Chennai" {% if request.args.get('city')=='Chennai' %}selected{% endif %}>Chennai</option>
                    </select>
                    
                    <button type="submit" class="search-btn">Search</button>
                </div>
            </form>
            
            <!-- Popular Searches -->
            <div class="popular-searches">
                <span class="popular-label">Popular:</span>
                <a href="/?search=Amazon" class="popular-tag">Amazon</a>
                <a href="/?search=Flipkart" class="popular-tag">Flipkart</a>
                <a href="/?search=Myntra" class="popular-tag">Myntra</a>
                <a href="/?search=Swiggy" class="popular-tag">Swiggy</a>
                <a href="/?search=Zomato" class="popular-tag">Zomato</a>
            </div>
        </div>
        
        <!-- Trust Badges -->
        <div class="trust-badges-hero">
            <div class="badge-item">
                <span class="badge-icon">✅</span>
                <span class="badge-text"><strong>{{ total_coupons }}+</strong> Verified Coupons</span>
            </div>
            <div class="badge-item">
                <span class="badge-icon">🛡️</span>
                <span class="badge-text">100% Authentic Deals</span>
            </div>
            <div class="badge-item">
                <span class="badge-icon">⚡</span>
                <span class="badge-text">Daily Updated</span>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="filters" style="display: none;">
            <form class="filter-row" method="get">
                {% if request.args.get('category') %}
                <input type="hidden" name="category" value="{{ request.args.get('category') }}">
                {% endif %}
                {% if request.args.get('search') %}
                <input type="hidden" name="search" value="{{ request.args.get('search') }}">
                {% endif %}
                
                <!-- Product Search Bar -->
                <input type="text" 
                       name="product_search" 
                       placeholder="🔍 Search products (TV, fridge, mobile...)" 
                       value="{{ request.args.get('product_search', '') }}"
                       class="product-search-input"
                       style="flex: 2; min-width: 200px;">
                
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
        
        <!-- Section Title -->
        <div class="section-title">
            <h2>
                {% if request.args.get('product_search') %}
                📦 Deals for "{{ request.args.get('product_search') }}"
                {% elif request.args.get('search') %}
                🔍 Results for "{{ request.args.get('search') }}"
                {% elif request.args.get('category') %}
                {{ request.args.get('category')|title }} Deals & Coupons
                {% elif request.args.get('source') %}
                {{ request.args.get('source') }} Coupons & Deals
                {% else %}
                💰 All Coupons & Deals
                {% endif %}
            </h2>
        </div>
        
        <!-- Product Search Results Section -->
        <div id="productResults" class="product-search-section" style="display: none;">
            <div class="product-results-header">
                <h3>🛍️ Product Price Comparison</h3>
                <p>Best deals from trusted stores</p>
            </div>
            <div id="productResultsGrid" class="product-grid"></div>
            <div id="productLoading" class="product-loading" style="display: none;">
                <div class="loading-spinner"></div>
                <p>Searching for best prices...</p>
            </div>
        </div>
        
        <div class="coupons-grid">
            {% for coupon in coupons %}
            <div class="coupon-card {% if coupon.is_hot %}hot-deal-card{% endif %}">
                <!-- Trust Badge -->
                {% if coupon.is_hot %}
                <div class="trust-badge hot">🔥 HOT</div>
                {% elif coupon.is_featured %}
                <div class="trust-badge exclusive">⭐ EXCLUSIVE</div>
                {% else %}
                <div class="trust-badge verified">✓ VERIFIED</div>
                {% endif %}
                
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
        // Product Search Functionality
        async function searchProducts(query) {
            const productResultsSection = document.getElementById('productResults');
            const productResultsGrid = document.getElementById('productResultsGrid');
            const productLoading = document.getElementById('productLoading');
            
            if (!productResultsSection || !query || query.length < 2) {
                if (productResultsSection) productResultsSection.style.display = 'none';
                return;
            }
            
            // Show product results section
            productResultsSection.style.display = 'block';
            productLoading.style.display = 'block';
            productResultsGrid.innerHTML = '';
            
            try {
                const response = await fetch(`/api/search-products?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                productLoading.style.display = 'none';
                
                if (data.products && data.products.length > 0) {
                    productResultsGrid.innerHTML = data.products.map(product => `
                        <div class="product-card">
                            <div class="product-card-header">
                                ${product.image ? `<img src="${product.image}" alt="${product.title}" class="product-image">` : '<div class="product-image" style="display:flex;align-items:center;justify-content:center;font-size:2rem;">${product.source_icon}</div>'}
                                <div class="product-info">
                                    <div class="product-title">${product.title}</div>
                                    ${product.rating ? `<div class="product-rating">⭐ ${product.rating}</div>` : ''}
                                </div>
                            </div>
                            <div class="product-price-row">
                                <div>
                                    <div class="product-price">${product.price}</div>
                                    ${product.original_price ? `<div class="product-original-price">${product.original_price}</div>` : ''}
                                </div>
                                <span class="product-source ${product.source.toLowerCase()}">${product.source_icon} ${product.source}</span>
                            </div>
                            <a href="${product.url}" target="_blank" rel="noopener noreferrer" class="product-link">
                                View Deal →
                            </a>
                        </div>
                    `).join('');
                } else {
                    productResultsGrid.innerHTML = '<p style="text-align:center;grid-column:1/-1;color:#64748b;">No products found. Try a different search term.</p>';
                }
                
            } catch (error) {
                console.error('Product search error:', error);
                productLoading.style.display = 'none';
                productResultsGrid.innerHTML = '<p style="text-align:center;grid-column:1/-1;color:#ef4444;">Unable to search products. Please try again.</p>';
            }
        }
        
        // Check if we have a search query and trigger product search
        const urlParams = new URLSearchParams(window.location.search);
        const searchQuery = urlParams.get('search');
        if (searchQuery) {
            // Delay slightly to ensure page loads
            setTimeout(() => searchProducts(searchQuery), 500);
        }
        
        // Search Autocomplete - Like GrabOn & CouponDunia
        const searchInput = document.getElementById('searchInput');
        const suggestionsBox = document.getElementById('searchSuggestions');
        
        // Popular search suggestions
        const popularSearches = [
            { text: 'Amazon', icon: '🛒' },
            { text: 'Flipkart', icon: '🛒' },
            { text: 'Myntra', icon: '👕' },
            { text: 'Swiggy', icon: '🍔' },
            { text: 'Zomato', icon: '🍔' },
            { text: 'Ajio', icon: '👕' },
            { text: 'Nykaa', icon: '💄' },
            { text: 'Croma', icon: '📱' },
            { text: 'Meesho', icon: '🛒' },
            { text: 'Electronics', icon: '📱' },
            { text: 'Fashion', icon: '👕' },
            { text: 'Food', icon: '🍔' }
        ];
        
        if (searchInput) {
            searchInput.addEventListener('input', function(e) {
                const value = e.target.value.toLowerCase();
                if (value.length < 1) {
                    suggestionsBox.classList.remove('show');
                    return;
                }
                
                const filtered = popularSearches.filter(s => 
                    s.text.toLowerCase().includes(value)
                );
                
                if (filtered.length > 0) {
                    suggestionsBox.innerHTML = filtered.map(s => 
                        `<div class="suggestion-item" onclick="window.location.href='/?search=${s.text}'">
                            <span>${s.icon}</span>
                            <span>${s.text}</span>
                        </div>`
                    ).join('');
                    suggestionsBox.classList.add('show');
                } else {
                    suggestionsBox.classList.remove('show');
                }
            });
            
            // Hide suggestions on click outside
            document.addEventListener('click', function(e) {
                if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                    suggestionsBox.classList.remove('show');
                }
            });
        }
        
        // Improved Copy Code with Toast Notification
        function copyCode(code) {
            if (!code || code === 'No Code Needed') return;
            
            navigator.clipboard.writeText(code).then(() => {
                showToast('✅ Coupon code "' + code + '" copied!');
            }).catch(() => {
                // Fallback
                const textarea = document.createElement('textarea');
                textarea.value = code;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast('✅ Coupon code "' + code + '" copied!');
            });
        }
        
        // Toast Notification Function
        function showToast(message) {
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%);
                background: #22c55e;
                color: white;
                padding: 15px 30px;
                border-radius: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                z-index: 10000;
                font-weight: 600;
                animation: slideUp 0.3s ease;
            `;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideDown 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, 2500);
        }
        
        // Add toast animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideUp {
                from { transform: translateX(-50%) translateY(20px); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
            @keyframes slideDown {
                from { transform: translateX(-50%) translateY(0); opacity: 1; }
                to { transform: translateX(-50%) translateY(20px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        // Track deal clicks
        function trackDealClick(dealId, source) {
            console.log('Deal clicked:', dealId, 'Source:', source);
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


@app.route('/about')
def about():
    """About Us page"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>About Us - GrabCoupon | Best Deals & Coupons in India</title>
        <meta name="description" content="Learn about GrabCoupon - your trusted destination for the best deals, discounts, and coupon codes in India.">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; color: #333; line-height: 1.6; }
            .header { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
            .logo { font-size: 1.8rem; font-weight: bold; color: white; text-decoration: none; display: flex; align-items: center; gap: 10px; }
            .logo i { font-size: 1.5rem; }
            .nav-links { display: flex; gap: 2rem; }
            .nav-links a { color: white; text-decoration: none; font-weight: 500; transition: opacity 0.3s; }
            .nav-links a:hover { opacity: 0.8; }
            .container { max-width: 1200px; margin: 0 auto; padding: 3rem 2rem; }
            .page-title { text-align: center; margin-bottom: 3rem; }
            .page-title h1 { font-size: 2.5rem; color: #11998e; margin-bottom: 1rem; }
            .page-title p { font-size: 1.2rem; color: #666; }
            .content-section { background: white; border-radius: 15px; padding: 2.5rem; margin-bottom: 2rem; box-shadow: 0 2px 15px rgba(0,0,0,0.05); }
            .content-section h2 { color: #11998e; margin-bottom: 1.5rem; font-size: 1.8rem; }
            .content-section p { margin-bottom: 1rem; color: #555; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; margin-top: 2rem; }
            .feature-card { background: #f8f9fa; padding: 2rem; border-radius: 12px; text-align: center; transition: transform 0.3s, box-shadow 0.3s; }
            .feature-card:hover { transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
            .feature-card i { font-size: 3rem; color: #11998e; margin-bottom: 1rem; }
            .feature-card h3 { margin-bottom: 0.8rem; color: #333; }
            .feature-card p { color: #666; margin: 0; }
            .stats { display: flex; justify-content: space-around; flex-wrap: wrap; gap: 2rem; margin: 3rem 0; text-align: center; }
            .stat-item h3 { font-size: 2.5rem; color: #11998e; }
            .stat-item p { color: #666; font-weight: 500; }
            .cta-section { text-align: center; padding: 3rem; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-radius: 15px; color: white; }
            .cta-section h2 { color: white; margin-bottom: 1rem; }
            .cta-section p { margin-bottom: 1.5rem; opacity: 0.9; }
            .cta-btn { display: inline-block; padding: 1rem 2.5rem; background: white; color: #11998e; text-decoration: none; border-radius: 30px; font-weight: bold; transition: transform 0.3s; }
            .cta-btn:hover { transform: scale(1.05); }
            .footer { background: #1a1a2e; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }
            .footer a { color: #38ef7d; text-decoration: none; }
            @media (max-width: 768px) { .nav-links { display: none; } .page-title h1 { font-size: 2rem; } }
        </style>
    </head>
    <body>
        <header class="header">
            <a href="/" class="logo"><i class="fas fa-tag"></i> GrabCoupon</a>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/local">Local Food Deals</a>
                <a href="/about">About Us</a>
                <a href="/contact">Contact Us</a>
            </nav>
        </header>
        
        <div class="container">
            <div class="page-title">
                <h1>About GrabCoupon</h1>
                <p>Your Trusted Destination for the Best Deals & Discounts in India</p>
            </div>
            
            <div class="content-section">
                <h2>Who We Are</h2>
                <p>GrabCoupon is India's leading coupon and deal aggregation platform, dedicated to helping shoppers save money on their online purchases. We partner with top e-commerce brands to bring you the latest and verified coupon codes, deals, and discounts.</p>
                <p>Our mission is simple: to make saving money effortless for every Indian shopper. Whether you're shopping on Amazon, Flipkart, Myntra, or any other popular platform, we've got you covered with exclusive deals and verified coupons.</p>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <h3>500+</h3>
                    <p>Active Coupons</p>
                </div>
                <div class="stat-item">
                    <h3>50+</h3>
                    <p>Partner Stores</p>
                </div>
                <div class="stat-item">
                    <h3>₹1Cr+</h3>
                    <p>Savings Verified</p>
                </div>
                <div class="stat-item">
                    <h3>1Lakh+</h3>
                    <p>Happy Users</p>
                </div>
            </div>
            
            <div class="content-section">
                <h2>Why Choose GrabCoupon?</h2>
                <div class="features">
                    <div class="feature-card">
                        <i class="fas fa-check-circle"></i>
                        <h3>Verified Codes</h3>
                        <p>Every coupon is manually tested and verified before publishing</p>
                    </div>
                    <div class="feature-card">
                        <i class="fas fa-bolt"></i>
                        <h3>Instant Updates</h3>
                        <p>Real-time deal updates from all major e-commerce platforms</p>
                    </div>
                    <div class="feature-card">
                        <i class="fas fa-rupee-sign"></i>
                        <h3>Maximum Savings</h3>
                        <p>We find the best deals so you save more on every purchase</p>
                    </div>
                    <div class="feature-card">
                        <i class="fas fa-mobile-alt"></i>
                        <h3>Easy to Use</h3>
                        <p>Simple and intuitive interface for hassle-free shopping</p>
                    </div>
                </div>
            </div>
            
            <div class="content-section">
                <h2>How It Works</h2>
                <p><strong>1. Browse Deals:</strong> Explore thousands of verified coupons and deals from your favorite stores.</p>
                <p><strong>2. Copy Code:</strong> Click on any coupon to copy the code instantly to your clipboard.</p>
                <p><strong>3. Save Money:</strong> Apply the code at checkout and watch your savings grow!</p>
            </div>
            
            <div class="cta-section">
                <h2>Start Saving Today!</h2>
                <p>Join thousands of smart shoppers who are already saving big on every purchase.</p>
                <a href="/" class="cta-btn">Browse All Deals</a>
            </div>
        </div>
        
        <footer class="footer">
            <p>&copy; 2026 GrabCoupon. All rights reserved. | <a href="/">Home</a> | <a href="/contact">Contact</a></p>
        </footer>
    </body>
    </html>
    '''


@app.route('/contact')
def contact():
    """Contact Us page"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contact Us - GrabCoupon | Get in Touch</title>
        <meta name="description" content="Contact GrabCoupon - We'd love to hear from you! Reach out for partnerships, support, or general inquiries.">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; color: #333; line-height: 1.6; }
            .header { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
            .logo { font-size: 1.8rem; font-weight: bold; color: white; text-decoration: none; display: flex; align-items: center; gap: 10px; }
            .logo i { font-size: 1.5rem; }
            .nav-links { display: flex; gap: 2rem; }
            .nav-links a { color: white; text-decoration: none; font-weight: 500; transition: opacity 0.3s; }
            .nav-links a:hover { opacity: 0.8; }
            .container { max-width: 1200px; margin: 0 auto; padding: 3rem 2rem; }
            .page-title { text-align: center; margin-bottom: 3rem; }
            .page-title h1 { font-size: 2.5rem; color: #11998e; margin-bottom: 1rem; }
            .page-title p { font-size: 1.2rem; color: #666; }
            .contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
            .contact-card { background: white; border-radius: 15px; padding: 2.5rem; text-align: center; box-shadow: 0 2px 15px rgba(0,0,0,0.05); transition: transform 0.3s; }
            .contact-card:hover { transform: translateY(-5px); }
            .contact-card i { font-size: 3rem; color: #11998e; margin-bottom: 1rem; }
            .contact-card h3 { margin-bottom: 0.8rem; color: #333; }
            .contact-card p { color: #666; margin: 0; }
            .contact-card a { color: #11998e; text-decoration: none; font-weight: 500; }
            .contact-card a:hover { text-decoration: underline; }
            .form-section { background: white; border-radius: 15px; padding: 2.5rem; margin-top: 2rem; box-shadow: 0 2px 15px rgba(0,0,0,0.05); }
            .form-section h2 { color: #11998e; margin-bottom: 1.5rem; text-align: center; }
            .form-group { margin-bottom: 1.5rem; }
            .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #333; }
            .form-group input, .form-group textarea { width: 100%; padding: 1rem; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 1rem; transition: border-color 0.3s; font-family: inherit; }
            .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #11998e; }
            .form-group textarea { min-height: 150px; resize: vertical; }
            .submit-btn { width: 100%; padding: 1rem; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: transform 0.3s, box-shadow 0.3s; }
            .submit-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(17, 153, 142, 0.3); }
            .response-message { display: none; padding: 1rem; border-radius: 10px; margin-top: 1rem; text-align: center; }
            .response-message.success { background: #d4edda; color: #155724; }
            .response-message.error { background: #f8d7da; color: #721c24; }
            .footer { background: #1a1a2e; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }
            .footer a { color: #38ef7d; text-decoration: none; }
            @media (max-width: 768px) { .nav-links { display: none; } .page-title h1 { font-size: 2rem; } }
        </style>
    </head>
    <body>
        <header class="header">
            <a href="/" class="logo"><i class="fas fa-tag"></i> GrabCoupon</a>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/local">Local Food Deals</a>
                <a href="/about">About Us</a>
                <a href="/contact">Contact Us</a>
            </nav>
        </header>
        
        <div class="container">
            <div class="page-title">
                <h1>Contact Us</h1>
                <p>We'd love to hear from you! Get in touch with us for any queries or suggestions.</p>
            </div>
            
            <div class="contact-grid">
                <div class="contact-card">
                    <i class="fas fa-envelope"></i>
                    <h3>Email Us</h3>
                    <p>For general inquiries:</p>
                    <a href="mailto:support@grabcoupon.in">support@grabcoupon.in</a>
                </div>
                <div class="contact-card">
                    <i class="fas fa-handshake"></i>
                    <h3>Partner With Us</h3>
                    <p>For business partnerships:</p>
                    <a href="mailto:partners@grabcoupon.in">partners@grabcoupon.in</a>
                </div>
                <div class="contact-card">
                    <i class="fas fa-ad"></i>
                    <h3>Advertising</h3>
                    <p>For advertising opportunities:</p>
                    <a href="mailto:ads@grabcoupon.in">ads@grabcoupon.in</a>
                </div>
            </div>
            
            <div class="form-section">
                <h2>Send us a Message</h2>
                <form id="contactForm">
                    <div class="form-group">
                        <label for="name">Your Name</label>
                        <input type="text" id="name" name="name" placeholder="Enter your name" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" id="email" name="email" placeholder="Enter your email" required>
                    </div>
                    <div class="form-group">
                        <label for="subject">Subject</label>
                        <input type="text" id="subject" name="subject" placeholder="What is this about?" required>
                    </div>
                    <div class="form-group">
                        <label for="message">Message</label>
                        <textarea id="message" name="message" placeholder="Write your message here..." required></textarea>
                    </div>
                    <button type="submit" class="submit-btn">Send Message</button>
                </form>
                <div id="responseMessage" class="response-message"></div>
            </div>
        </div>
        
        <footer class="footer">
            <p>&copy; 2026 GrabCoupon. All rights reserved. | <a href="/">Home</a> | <a href="/about">About</a></p>
        </footer>
        
        <script>
            document.getElementById('contactForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const messageDiv = document.getElementById('responseMessage');
                messageDiv.style.display = 'block';
                messageDiv.className = 'response-message success';
                messageDiv.innerHTML = '<i class="fas fa-check-circle"></i> Thank you for your message! We will get back to you soon.';
                this.reset();
                setTimeout(() => { messageDiv.style.display = 'none'; }, 5000);
            });
        </script>
    </body>
    </html>
    '''


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
    product_search = request.args.get('product_search', '').lower()
    
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
    if product_search:
        # Search for products like TV, fridge, mobile, etc. in description and title
        filtered = [c for c in filtered if product_search in c.get('description', '').lower() or product_search in c.get('title', '').lower() or product_search in (c.get('code') or c.get('coupon_code') or '').lower()]
    
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


@app.route('/api/search-products')
def api_search_products():
    """Search for products across e-commerce sites and return price comparisons"""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'error': 'Please enter a valid search term', 'products': []})
    
    products = []
    
    try:
        # Search Amazon
        amazon_results = search_amazon_products(query)
        products.extend(amazon_results)
        
        # Search Flipkart
        flipkart_results = search_flipkart_products(query)
        products.extend(flipkart_results)
        
        # Sort by price (lowest first)
        products.sort(key=lambda x: x.get('price_numeric', 999999))
        
        # Return top 20 results
        return jsonify({
            'query': query,
            'products': products[:20],
            'count': len(products)
        })
        
    except Exception as e:
        logger.error(f"Product search error: {e}")
        return jsonify({'error': 'Search temporarily unavailable', 'products': []})


def search_amazon_products(query):
    """Search Amazon India for products"""
    products = []
    try:
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find product cards
            for item in soup.select('.sg-col-4-of-12, .s-result-item')[:10]:
                try:
                    # Get title
                    title_elem = item.select_one('h2 a span, .a-text-normal, .a-size-medium')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # Get URL
                    link_elem = item.select_one('h2 a, a.a-link-normal')
                    if not link_elem:
                        continue
                    url = 'https://www.amazon.in' + link_elem.get('href', '')
                    if 'amazon.in/dp' not in url and 'amazon.in/gp/product' not in url:
                        continue
                    
                    # Get price
                    price_elem = item.select_one('.a-price-whole, .a-offscreen, [data-a-color="price"] .a-offscreen')
                    price_text = price_elem.get_text(strip=True) if price_elem else ''
                    price_numeric = int(re.sub(r'[^0-9]', '', price_text)) if price_text else 0
                    
                    # Get rating
                    rating_elem = item.select_one('.a-icon-alt, .a-popover-preload')
                    rating = rating_elem.get_text(strip=True) if rating_elem else ''
                    
                    # Get image
                    img_elem = item.select_one('img.s-image')
                    image = img_elem.get('src', '') if img_elem else ''
                    
                    if price_numeric > 0:
                        products.append({
                            'title': title[:100],
                            'url': url,
                            'price': f'₹{price_numeric:,}',
                            'price_numeric': price_numeric,
                            'rating': rating[:20],
                            'source': 'Amazon',
                            'source_icon': '🛒',
                            'image': image,
                            'verified': True
                        })
                except Exception:
                    continue
                    
    except Exception as e:
        logger.error(f"Amazon search error: {e}")
    
    return products


def search_flipkart_products(query):
    """Search Flipkart for products"""
    products = []
    try:
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find product cards
            for item in soup.select('._1AtVbE, ._13oc-S')[:10]:
                try:
                    # Get title
                    title_elem = item.select_one('._4rR01T, ._2B099h, a[title]')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # Get URL
                    link_elem = item.select_one('a._1fQZEK')
                    if not link_elem:
                        continue
                    url = 'https://www.flipkart.com' + link_elem.get('href', '')
                    
                    # Get price
                    price_elem = item.select_one('._30jeq3._1_WB1e, ._1_WB1e')
                    price_text = price_elem.get_text(strip=True) if price_elem else ''
                    price_numeric = int(re.sub(r'[^0-9]', '', price_text)) if price_text else 0
                    
                    # Get original price (if discounted)
                    orig_price_elem = item.select_one('._1_WB1e + span, ._2I5kjh')
                    orig_price_text = orig_price_elem.get_text(strip=True) if orig_price_elem else ''
                    
                    # Get rating
                    rating_elem = item.select_one('._2_R_DZ span, ._3LWZlK')
                    rating = rating_elem.get_text(strip=True) if rating_elem else ''
                    
                    # Get image
                    img_elem = item.select_one('img._396y4z')
                    image = img_elem.get('src', '') if img_elem else ''
                    
                    if price_numeric > 0:
                        product = {
                            'title': title[:100],
                            'url': url,
                            'price': f'₹{price_numeric:,}',
                            'price_numeric': price_numeric,
                            'rating': rating,
                            'source': 'Flipkart',
                            'source_icon': '🛍️',
                            'image': image,
                            'verified': True
                        }
                        if orig_price_text:
                            product['original_price'] = orig_price_text
                        products.append(product)
                except Exception:
                    continue
                    
    except Exception as e:
        logger.error(f"Flipkart search error: {e}")
    
    return products


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