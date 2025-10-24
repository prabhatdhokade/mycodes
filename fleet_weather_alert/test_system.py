"""Test script for the Fleet Weather Alert System."""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test all API endpoints."""
    print("🧪 Testing Fleet Weather Alert System API...")
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"   Health Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Database: {data['database_status']}")
            print(f"   Weather Service: {data['weather_service_status']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test fleet summary
    print("\n2. Testing fleet summary...")
    try:
        response = requests.get(f"{BASE_URL}/api/fleet/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total Trucks: {data['total_trucks']}")
            print(f"   Active Trucks: {data['active_trucks']}")
            print(f"   Total Operators: {data['total_operators']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test alerts
    print("\n3. Testing alerts...")
    try:
        response = requests.get(f"{BASE_URL}/api/alerts")
        if response.status_code == 200:
            alerts = response.json()
            print(f"   Total Alerts: {len(alerts)}")
            if alerts:
                print(f"   Latest Alert: {alerts[0]['message']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test alert statistics
    print("\n4. Testing alert statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/alerts/stats/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"   Pending Alerts: {data['pending_alerts']}")
            print(f"   Critical Alerts: {data['severity_breakdown']['critical']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test hot topics
    print("\n5. Testing hot topics...")
    try:
        response = requests.get(f"{BASE_URL}/api/hot-topics/trending?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"   Trending Posts: {len(data['trending_posts'])}")
            if data['trending_posts']:
                top_post = data['trending_posts'][0]
                print(f"   Top Post Score: {top_post['engagement_score']:.2f}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test categories
    print("\n6. Testing categories...")
    try:
        response = requests.get(f"{BASE_URL}/api/hot-topics/categories")
        if response.status_code == 200:
            data = response.json()
            print(f"   Categories: {len(data['categories'])}")
            for category, posts in list(data['categories'].items())[:3]:
                print(f"   {category}: {len(posts)} trending posts")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ API testing completed!")

def test_weather_simulation():
    """Test weather monitoring simulation."""
    print("\n🌤️ Testing weather monitoring...")
    
    # Get active trucks
    try:
        response = requests.get(f"{BASE_URL}/api/fleet/trucks?status=active")
        if response.status_code == 200:
            trucks = response.json()
            print(f"   Found {len(trucks)} active trucks")
            
            # Simulate weather check by triggering the scheduler
            print("   Simulating weather check...")
            time.sleep(2)  # Wait for potential alerts
            
            # Check for new alerts
            response = requests.get(f"{BASE_URL}/api/alerts")
            if response.status_code == 200:
                alerts = response.json()
                print(f"   Current alerts: {len(alerts)}")
                
                # Show recent alerts
                recent_alerts = [a for a in alerts if a['created_at'] > (datetime.utcnow().isoformat().replace('Z', '+00:00'))]
                if recent_alerts:
                    print("   Recent weather alerts:")
                    for alert in recent_alerts[:3]:
                        print(f"     - {alert['alert_type']}: {alert['message']}")
    except Exception as e:
        print(f"   Error: {e}")

def main():
    """Run all tests."""
    print("🚛 Fleet Weather Alert System - Test Suite")
    print("=" * 50)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test weather simulation
    test_weather_simulation()
    
    print("\n🎉 All tests completed!")
    print("\nAccess the system at:")
    print(f"  Web Dashboard: {BASE_URL}")
    print(f"  API Docs: {BASE_URL}/api/docs")

if __name__ == "__main__":
    main()