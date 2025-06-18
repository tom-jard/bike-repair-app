#!/usr/bin/env python3
"""
Historical Traffic Capture

This script captures traffic data for existing Strava rides
to populate the database with historical comparisons.
"""

import sys
import os
from datetime import datetime, timedelta
from strava_monitor import StravaMonitor, StoredTrafficComparison

def load_config():
    """Load configuration from config.py file."""
    try:
        from config import (
            STRAVA_CLIENT_ID,
            STRAVA_CLIENT_SECRET,
            STRAVA_ACCESS_TOKEN,
            GOOGLE_MAPS_API_KEY
        )
        return STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_ACCESS_TOKEN, GOOGLE_MAPS_API_KEY
    except ImportError as e:
        print(f"❌ Error loading config: {e}")
        return None, None, None, None

def capture_historical_traffic(strava_api, google_maps_api, days_back: int = 30):
    """
    Capture traffic data for historical rides.
    
    Args:
        strava_api: Strava API client
        google_maps_api: Google Maps API client
        days_back: Number of days to look back
    """
    monitor = StravaMonitor(strava_api, google_maps_api)
    
    print(f"🔍 Looking for rides from the last {days_back} days...")
    
    try:
        # Get recent activities
        after_date = datetime.now() - timedelta(days=days_back)
        activities = strava_api.get_activities(after=after_date, activity_type="Ride")
        
        if not activities:
            print("❌ No rides found in the specified time period.")
            return
        
        print(f"📊 Found {len(activities)} rides to analyze...")
        
        captured_count = 0
        skipped_count = 0
        
        for i, activity in enumerate(activities, 1):
            activity_id = activity["id"]
            activity_name = activity.get("name", "Unknown")
            
            print(f"\n[{i}/{len(activities)}] Analyzing: {activity_name}")
            
            # Check if already captured
            existing = monitor.get_all_comparisons()
            if any(comp.activity_id == activity_id for comp in existing):
                print(f"   ⏭️  Already captured, skipping...")
                skipped_count += 1
                continue
            
            # Capture traffic data
            comparison = monitor.capture_traffic_for_activity(activity_id)
            
            if comparison:
                print(f"   ✅ Captured: {comparison.time_saved_minutes:.1f} minutes saved")
                captured_count += 1
            else:
                print(f"   ❌ Failed to capture")
            
            # Rate limiting
            import time
            time.sleep(2)
        
        print(f"\n📈 Capture Summary:")
        print(f"   Total rides found: {len(activities)}")
        print(f"   New captures: {captured_count}")
        print(f"   Already captured: {skipped_count}")
        
        if captured_count > 0:
            print(f"   ✅ Successfully captured traffic data for {captured_count} rides!")
        
    except Exception as e:
        print(f"❌ Error capturing historical traffic: {e}")

def main():
    """Main function to capture historical traffic data."""
    print("📊 Historical Traffic Capture")
    print("=" * 40)
    print("This script captures traffic data for your existing rides.")
    print("Note: Traffic data will be current conditions, not historical.")
    print()
    
    # Load configuration
    client_id, client_secret, access_token, maps_api_key = load_config()
    
    if not all([client_id, client_secret, access_token, maps_api_key]):
        print("❌ Missing required configuration. Please check your config.py file.")
        return
    
    # Get time period
    try:
        days_input = input("📅 How many days back to capture? (default: 30): ").strip()
        days_back = int(days_input) if days_input else 30
    except ValueError:
        print("⚠️  Invalid input, using 30 days")
        days_back = 30
    
    print(f"\n⚠️  IMPORTANT: This will capture CURRENT traffic conditions")
    print(f"   for rides that happened in the past {days_back} days.")
    print(f"   This is useful for future reference but not historical accuracy.")
    
    confirm = input("\nContinue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled.")
        return
    
    # Initialize APIs
    from strava_brake_wear_estimator import StravaAPI
    from traffic_comparison import GoogleMapsAPI
    
    strava_api = StravaAPI(str(client_id), str(client_secret), str(access_token))
    google_maps_api = GoogleMapsAPI(str(maps_api_key))
    
    # Capture historical traffic
    capture_historical_traffic(strava_api, google_maps_api, days_back)
    
    print(f"\n✅ Historical capture complete!")
    print(f"   Run 'python3 run_monitor.py' to view stored comparisons")

if __name__ == "__main__":
    main() 