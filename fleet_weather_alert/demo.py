#!/usr/bin/env python3
"""Demo script for the Fleet Weather Alert System."""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_data(data, title="Data"):
    """Print formatted data."""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2, default=str))

def demo_fleet_management():
    """Demo fleet management features."""
    print_section("FLEET MANAGEMENT DEMO")
    
    # Get fleet summary
    response = requests.get(f"{BASE_URL}/api/fleet/summary")
    if response.status_code == 200:
        print_data(response.json(), "Fleet Summary")
    
    # Get active trucks
    response = requests.get(f"{BASE_URL}/api/fleet/trucks?status=active&limit=5")
    if response.status_code == 200:
        trucks = response.json()
        print(f"\nActive Trucks ({len(trucks)}):")
        for truck in trucks:
            print(f"  - Truck {truck['truck_id']}: {truck['license_plate']} at ({truck['location_lat']:.2f}, {truck['location_lng']:.2f})")
    
    # Get operators
    response = requests.get(f"{BASE_URL}/api/fleet/operators?limit=3")
    if response.status_code == 200:
        operators = response.json()
        print(f"\nOperators ({len(operators)}):")
        for op in operators:
            print(f"  - {op['name']}: {op['contact_info']} ({op['alert_preference']})")

def demo_weather_alerts():
    """Demo weather alert system."""
    print_section("WEATHER ALERT SYSTEM DEMO")
    
    # Get alert statistics
    response = requests.get(f"{BASE_URL}/api/alerts/stats/summary")
    if response.status_code == 200:
        stats = response.json()
        print_data(stats, "Alert Statistics")
    
    # Get recent alerts
    response = requests.get(f"{BASE_URL}/api/alerts?limit=5")
    if response.status_code == 200:
        alerts = response.json()
        if alerts:
            print(f"\nRecent Alerts ({len(alerts)}):")
            for alert in alerts:
                print(f"  - {alert['alert_type'].upper()}: {alert['message']} (Severity: {alert['severity']})")
        else:
            print("\nNo alerts currently active")

def demo_hot_topics():
    """Demo hot topics system."""
    print_section("HOT TOPICS SYSTEM DEMO")
    
    # Get trending posts
    response = requests.get(f"{BASE_URL}/api/hot-topics/trending?limit=3")
    if response.status_code == 200:
        data = response.json()
        posts = data['trending_posts']
        print(f"\nTop 3 Trending Posts:")
        for i, post in enumerate(posts, 1):
            print(f"  {i}. {post['title']} (Score: {post['engagement_score']:.1f})")
            print(f"     Category: {post['category']}, Likes: {post['likes']}, Views: {post['views']}")
    
    # Get categories
    response = requests.get(f"{BASE_URL}/api/hot-topics/categories")
    if response.status_code == 200:
        data = response.json()
        categories = data['categories']
        print(f"\nCategories with Trending Posts ({len(categories)}):")
        for category, posts in list(categories.items())[:5]:
            print(f"  - {category}: {len(posts)} trending posts")

def demo_api_endpoints():
    """Demo various API endpoints."""
    print_section("API ENDPOINTS DEMO")
    
    endpoints = [
        ("Health Check", f"{BASE_URL}/api/health"),
        ("Fleet Summary", f"{BASE_URL}/api/fleet/summary"),
        ("Alert Stats", f"{BASE_URL}/api/alerts/stats/summary"),
        ("Hot Topics Stats", f"{BASE_URL}/api/hot-topics/stats"),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ {name}:")
                if isinstance(data, dict) and len(data) <= 5:
                    for key, value in data.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"   Status: {response.status_code}, Data available")
            else:
                print(f"\n❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"\n❌ {name}: Error - {e}")

def main():
    """Run the complete demo."""
    print("🚛 FLEET WEATHER ALERT SYSTEM - LIVE DEMO")
    print("=" * 60)
    print(f"System URL: {BASE_URL}")
    print(f"API Docs: {BASE_URL}/api/docs")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"\n❌ System not responding (HTTP {response.status_code})")
            print("Make sure the system is running with: python3 run.py")
            return
    except Exception as e:
        print(f"\n❌ Cannot connect to system: {e}")
        print("Make sure the system is running with: python3 run.py")
        return
    
    # Run demos
    demo_fleet_management()
    demo_weather_alerts()
    demo_hot_topics()
    demo_api_endpoints()
    
    print_section("DEMO COMPLETED")
    print("🎉 All demos completed successfully!")
    print(f"\nNext steps:")
    print(f"  1. Visit the web dashboard: {BASE_URL}")
    print(f"  2. Explore the API documentation: {BASE_URL}/api/docs")
    print(f"  3. Check the logs: tail -f fleet_weather.log")
    print(f"  4. Monitor weather alerts in real-time")

if __name__ == "__main__":
    main()