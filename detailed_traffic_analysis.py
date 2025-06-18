#!/usr/bin/env python3
"""
Detailed Traffic Analysis

This script provides a more detailed analysis of traffic comparisons,
showing exactly when each ride happened and how the car time was calculated.
"""

import sys
import os
from datetime import datetime, timedelta
from traffic_comparison import analyze_strava_traffic, TrafficComparison

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

def print_detailed_analysis(comparisons: list):
    """Print detailed analysis of each activity."""
    
    if not comparisons:
        print("No activities analyzed.")
        return
    
    print("\n🚗 DETAILED TRAFFIC ANALYSIS")
    print("=" * 60)
    print("⚠️  NOTE: Car times are based on CURRENT traffic conditions,")
    print("    not historical traffic from when you actually rode.")
    print("    This is a limitation of the Google Maps API.")
    print("=" * 60)
    
    total_time_saved = 0
    total_distance = 0
    total_bike_time = 0
    total_car_time = 0
    
    for i, comp in enumerate(comparisons, 1):
        print(f"\n📊 ACTIVITY #{i}: {comp.activity_name}")
        print("-" * 50)
        print(f"   🚴‍♂️ BIKE RIDE:")
        print(f"      Distance: {comp.distance_miles:.2f} miles")
        print(f"      Time: {comp.bike_time_minutes:.1f} minutes")
        print(f"      Speed: {comp.bike_speed_mph:.1f} mph")
        
        print(f"   🚗 CAR COMPARISON:")
        print(f"      Estimated time: {comp.car_time_minutes:.1f} minutes")
        print(f"      Estimated speed: {comp.car_speed_mph:.1f} mph")
        print(f"      Traffic conditions: {comp.traffic_conditions}")
        print(f"      Route: {comp.route_summary}")
        
        print(f"   ⏱️  TIME COMPARISON:")
        if comp.time_saved_minutes > 0:
            print(f"      ✅ You beat the car by {comp.time_saved_minutes:.1f} minutes!")
            print(f"      📈 That's {comp.time_saved_percentage:.1f}% faster than driving")
        elif comp.time_saved_minutes < 0:
            print(f"      ⏰ Car would have been {abs(comp.time_saved_minutes):.1f} minutes faster")
            print(f"      📉 That's {abs(comp.time_saved_percentage):.1f}% slower than driving")
        else:
            print(f"      🤝 You tied with the car!")
        
        # Calculate efficiency
        if comp.distance_miles > 0:
            efficiency = (comp.bike_speed_mph / comp.car_speed_mph) * 100 if comp.car_speed_mph > 0 else 0
            print(f"   📊 EFFICIENCY:")
            print(f"      Bike efficiency vs car: {efficiency:.1f}%")
        
        total_time_saved += comp.time_saved_minutes
        total_distance += comp.distance_miles
        total_bike_time += comp.bike_time_minutes
        total_car_time += comp.car_time_minutes
    
    # Overall summary
    print(f"\n📈 OVERALL SUMMARY")
    print("=" * 40)
    print(f"Total activities analyzed: {len(comparisons)}")
    print(f"Total distance: {total_distance:.1f} miles")
    print(f"Total bike time: {total_bike_time:.1f} minutes")
    print(f"Total estimated car time: {total_car_time:.1f} minutes")
    print(f"Total time saved: {total_time_saved:.1f} minutes")
    
    if total_time_saved > 0:
        print(f"🚴‍♂️ You saved {total_time_saved:.1f} minutes by biking!")
        print(f"📈 Average time savings: {total_time_saved/len(comparisons):.1f} minutes per ride")
    else:
        print(f"⏰ Cars would have been {abs(total_time_saved):.1f} minutes faster overall")
    
    # Additional insights
    print(f"\n💡 INSIGHTS:")
    print(f"   Average bike speed: {total_distance/(total_bike_time/60):.1f} mph")
    print(f"   Average car speed: {total_distance/(total_car_time/60):.1f} mph")
    print(f"   Overall efficiency: {(total_distance/(total_bike_time/60))/(total_distance/(total_car_time/60))*100:.1f}%")
    
    print(f"\n⚠️  LIMITATIONS:")
    print(f"   - Car times use current traffic, not historical")
    print(f"   - Traffic patterns may have changed since your rides")
    print(f"   - This is an estimate for comparison purposes")

def main():
    """Main function to run detailed traffic analysis."""
    print("🚗 Detailed Strava Traffic Analysis")
    print("=" * 50)
    
    # Load configuration
    client_id, client_secret, access_token, maps_api_key = load_config()
    
    if not all([client_id, client_secret, access_token, maps_api_key]):
        print("\n❌ Missing required configuration. Please check your config.py file.")
        return
    
    # Get analysis period
    try:
        days_input = input("\n📅 How many days back to analyze? (default: 30): ").strip()
        days_back = int(days_input) if days_input else 30
    except ValueError:
        print("⚠️  Invalid input, using 30 days")
        days_back = 30
    
    print(f"\n🔍 Analyzing your rides from the last {days_back} days...")
    print("   (This may take a few minutes for multiple activities)")
    
    try:
        # Run analysis
        comparisons = analyze_strava_traffic(
            str(client_id), str(client_secret), str(access_token), str(maps_api_key), days_back
        )
        
        # Print detailed results
        print_detailed_analysis(comparisons)
        
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