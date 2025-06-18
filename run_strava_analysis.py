#!/usr/bin/env python3
"""
User-Friendly Strava Brake Pad Wear Analysis Script

This script loads your config and prints a readable summary of your brake pad wear analysis.
"""

import sys

try:
    import config
    from strava_brake_wear_estimator import estimate_brake_pad_wear_from_strava
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure this script is in the same folder as config.py and strava_brake_wear_estimator.py.")
    sys.exit(1)

def print_summary(result):
    print("\n📊 Strava Brake Pad Wear Analysis Results")
    print("=" * 50)
    print(f"Total rides analyzed: {result.get('ride_count', 0)}")
    print(f"Total distance: {result.get('total_distance_miles', 0):.1f} miles")
    print(f"Total wear: {result.get('total_wear_mm', 0):.3f} mm")
    print(f"Remaining thickness: {result.get('remaining_thickness_mm', 0):.3f} mm")
    print(f"Wear percentage: {result.get('wear_percentage', 0):.1f}%")
    print(f"Estimated remaining miles: {result.get('remaining_miles', 0):.0f} miles")
    print(f"Needs replacement: {result.get('needs_replacement', False)}")
    
    # Show recent rides
    ride_details = result.get('ride_details', [])
    if ride_details:
        print(f"\n📋 Recent Rides:")
        for ride in ride_details[:5]:  # Show first 5 rides
            if isinstance(ride, dict):
                print(f"  {ride.get('ride_name', 'Unknown')}: {ride.get('wear_mm', 0):.4f} mm wear, Terrain: {ride.get('terrain_type', 'unknown')}, Weather: {ride.get('weather_condition', 'unknown')}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    wear_percentage = result.get('wear_percentage', 0)
    remaining_miles = result.get('remaining_miles', 0)
    if wear_percentage > 75:
        print(f"  🚨 CRITICAL: Brake pads need immediate replacement!")
    elif wear_percentage > 50:
        print(f"  ⚠️  HIGH: Consider replacing brake pads soon.")
    elif wear_percentage > 25:
        print(f"  📊 MODERATE: Monitor brake pad wear closely.")
    else:
        print(f"  ✅ GOOD: Brake pads in good condition.")
    if remaining_miles < 500:
        print(f"  🚨 Less than 500 miles remaining - plan replacement!")
    elif remaining_miles < 1000:
        print(f"  ⚠️  Less than 1000 miles remaining - start planning.")
    else:
        print(f"  ✅ Plenty of life remaining - continue monitoring.")

def main():
    print("🚴‍♂️ Running Strava Brake Pad Wear Analysis...")
    try:
        result = estimate_brake_pad_wear_from_strava(
            strava_client_id=config.STRAVA_CLIENT_ID,
            strava_client_secret=config.STRAVA_CLIENT_SECRET,
            strava_access_token=config.STRAVA_ACCESS_TOKEN,
            brake_material=getattr(config, 'BRAKE_MATERIAL', 'sintered'),
            rider_weight_kg=getattr(config, 'RIDER_WEIGHT_KG', 75.0),
            bike_weight_kg=getattr(config, 'BIKE_WEIGHT_KG', 12.0),
            days_back=getattr(config, 'DAYS_BACK', 30),
            weather_api_key=(config.WEATHER_API_KEY if getattr(config, 'WEATHER_API_KEY', None) and config.WEATHER_API_KEY != 'your_openweathermap_api_key_here' else None)
        )
        print_summary(result)
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        print("Check your config.py and Strava credentials.")

if __name__ == "__main__":
    main() 