#!/usr/bin/env python3
"""
Strava Monitor Runner

This script runs the Strava activity monitor to capture traffic data
when rides are finished for accurate historical comparison.
"""

import sys
import os
from strava_monitor import start_monitor, view_stored_comparisons

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

def main():
    """Main function to run the monitor."""
    print("🚴‍♂️ Strava Activity Monitor")
    print("=" * 40)
    print("This monitor captures traffic data when you finish rides")
    print("for accurate historical comparison.")
    print()
    
    # Load configuration
    client_id, client_secret, access_token, maps_api_key = load_config()
    
    if not all([client_id, client_secret, access_token, maps_api_key]):
        print("❌ Missing required configuration. Please check your config.py file.")
        return
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Start monitoring (captures traffic when rides finish)")
        print("2. View stored traffic comparisons")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🚴‍♂️ Starting Strava monitor...")
            print("This will continuously check for new activities every 5 minutes.")
            print("When you finish a ride, it will automatically capture traffic data.")
            print("Press Ctrl+C to stop monitoring.")
            print()
            
            try:
                start_monitor(
                    str(client_id), str(client_secret), 
                    str(access_token), str(maps_api_key)
                )
            except KeyboardInterrupt:
                print("\n🛑 Monitor stopped.")
                continue
                
        elif choice == "2":
            print("\n📊 Loading stored traffic comparisons...")
            try:
                view_stored_comparisons(
                    str(client_id), str(client_secret), 
                    str(access_token), str(maps_api_key)
                )
            except Exception as e:
                print(f"❌ Error loading comparisons: {e}")
                
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 