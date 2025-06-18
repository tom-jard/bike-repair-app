#!/usr/bin/env python3
"""
Traffic Analysis Runner

This script analyzes your Strava activities and compares bike times to car travel times.
It uses Google Maps API to estimate car travel times with real traffic data.
"""

import sys
import os
from traffic_comparison import analyze_strava_traffic, print_traffic_summary

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
        print("❌ Error loading config file:")
        print(f"   {e}")
        print("\n📝 Please make sure you have:")
        print("   1. A config.py file with your API credentials")
        print("   2. GOOGLE_MAPS_API_KEY added to your config")
        print("\n🔧 To set up Google Maps API:")
        print("   1. Go to https://console.cloud.google.com/")
        print("   2. Create a project and enable Directions API")
        print("   3. Create an API key")
        print("   4. Add GOOGLE_MAPS_API_KEY = 'your_key' to config.py")
        return None, None, None, None

def main():
    """Main function to run traffic analysis."""
    print("🚗 Strava Traffic Analysis")
    print("=" * 40)
    
    # Load configuration
    client_id, client_secret, access_token, maps_api_key = load_config()
    
    if not all([client_id, client_secret, access_token, maps_api_key]):
        print("\n❌ Missing required configuration. Please check your config.py file.")
        return
    
    # Get analysis period
    try:
        days_input = input("\n📅 How many days back to analyze? (default: 7): ").strip()
        days_back = int(days_input) if days_input else 7
    except ValueError:
        print("⚠️  Invalid input, using 7 days")
        days_back = 7
    
    print(f"\n🔍 Analyzing your rides from the last {days_back} days...")
    print("   (This may take a few minutes for multiple activities)")
    
    try:
        # Run analysis - cast to strings to satisfy type checker
        comparisons = analyze_strava_traffic(
            str(client_id), str(client_secret), str(access_token), str(maps_api_key), days_back
        )
        
        # Print results
        print_traffic_summary(comparisons)
        
        if comparisons:
            print(f"\n✅ Analysis complete! Analyzed {len(comparisons)} activities.")
        else:
            print("\n⚠️  No activities found in the specified time period.")
            
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print("\n🔧 Troubleshooting:")
        print("   - Check your API keys are correct")
        print("   - Ensure Google Maps API has Directions API enabled")
        print("   - Verify your Strava access token is valid")

if __name__ == "__main__":
    main() 