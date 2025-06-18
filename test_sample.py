#!/usr/bin/env python3
"""
Simple Test Script for Brake Pad Wear Estimator

This script demonstrates the brake wear estimator with sample data.
"""

def test_sample_brake_wear():
    """Test the brake wear estimator with sample ride data."""
    
    print("🚴‍♂️ Brake Pad Wear Estimator - Sample Test")
    print("=" * 50)
    
    # Sample ride data (simulating what we'd get from Strava)
    sample_rides = [
        {
            "name": "Morning Commute",
            "distance_miles": 5.0,
            "elevation_gain_feet": 100,
            "average_speed_mph": 12,
            "weather": "dry",
            "terrain": "urban"
        },
        {
            "name": "Weekend Mountain Ride", 
            "distance_miles": 20.0,
            "elevation_gain_feet": 3000,
            "average_speed_mph": 15,
            "weather": "wet",
            "terrain": "mountainous"
        },
        {
            "name": "Rainy Evening Ride",
            "distance_miles": 10.0,
            "elevation_gain_feet": 500,
            "average_speed_mph": 14,
            "weather": "rainy",
            "terrain": "hilly"
        }
    ]
    
    # Brake pad specifications
    brake_material = "sintered"
    initial_thickness_mm = 4.0
    minimum_thickness_mm = 1.0
    rider_weight_kg = 75
    bike_weight_kg = 12
    
    # Wear rate multipliers
    weather_multipliers = {
        "dry": 1.0,
        "wet": 1.3,
        "rainy": 1.5,
        "snowy": 1.8,
        "muddy": 2.2,
        "sandy": 2.5
    }
    
    terrain_multipliers = {
        "flat": 0.8,
        "hilly": 1.2,
        "mountainous": 1.6,
        "urban": 1.1,
        "off_road": 1.4
    }
    
    material_wear_rates = {
        "organic": 0.15,
        "semi-metallic": 0.12,
        "ceramic": 0.08,
        "sintered": 0.10
    }
    
    print(f"📋 Configuration:")
    print(f"  Brake material: {brake_material}")
    print(f"  Initial thickness: {initial_thickness_mm}mm")
    print(f"  Minimum thickness: {minimum_thickness_mm}mm")
    print(f"  Rider weight: {rider_weight_kg}kg")
    print(f"  Bike weight: {bike_weight_kg}kg")
    
    print(f"\n🚴 Sample Rides:")
    for ride in sample_rides:
        print(f"  - {ride['name']}: {ride['distance_miles']} miles, {ride['elevation_gain_feet']} ft elevation")
    
    # Calculate wear for each ride
    total_wear_mm = 0.0
    total_distance_miles = 0.0
    ride_details = []
    
    base_wear_rate = material_wear_rates[brake_material]
    
    print(f"\n📊 Wear Analysis:")
    print("-" * 50)
    
    for ride in sample_rides:
        # Convert miles to kilometers
        km_ridden = ride['distance_miles'] * 1.60934
        
        # Get multipliers
        weather_mult = weather_multipliers.get(ride['weather'], 1.0)
        terrain_mult = terrain_multipliers.get(ride['terrain'], 1.0)
        
        # Calculate braking frequency based on elevation and speed
        elevation_factor = min(3.0, ride['elevation_gain_feet'] / 1000.0)
        speed_factor = min(2.0, ride['average_speed_mph'] / 20.0)
        urban_factor = 1.5 if ride['distance_miles'] < 10 else 1.0
        braking_frequency = min(10.0, 3.0 + elevation_factor + speed_factor + urban_factor)
        braking_factor = braking_frequency / 5.0
        
        # Weight factor
        total_weight = rider_weight_kg + bike_weight_kg
        weight_factor = min(1.5, max(0.8, total_weight / 100.0))
        
        # Calculate wear for this ride
        ride_wear_mm = (
            base_wear_rate *
            (km_ridden / 1000.0) *
            weather_mult *
            terrain_mult *
            braking_factor *
            weight_factor
        )
        
        total_wear_mm += ride_wear_mm
        total_distance_miles += ride['distance_miles']
        
        ride_details.append({
            'name': ride['name'],
            'wear_mm': ride_wear_mm,
            'weather': ride['weather'],
            'terrain': ride['terrain'],
            'weather_mult': weather_mult,
            'terrain_mult': terrain_mult,
            'braking_factor': braking_factor,
            'weight_factor': weight_factor
        })
        
        print(f"  {ride['name']}:")
        print(f"    - Distance: {ride['distance_miles']:.1f} miles")
        print(f"    - Weather: {ride['weather']} (x{weather_mult})")
        print(f"    - Terrain: {ride['terrain']} (x{terrain_mult})")
        print(f"    - Braking factor: {braking_factor:.2f}")
        print(f"    - Wear: {ride_wear_mm:.4f}mm")
    
    # Calculate overall results
    remaining_thickness = initial_thickness_mm - total_wear_mm
    usable_thickness = initial_thickness_mm - minimum_thickness_mm
    wear_percentage = min(100.0, max(0.0, (total_wear_mm / usable_thickness) * 100))
    
    # Estimate remaining miles
    wear_per_mile = total_wear_mm / total_distance_miles if total_distance_miles > 0 else 0
    remaining_miles = 0
    if wear_per_mile > 0:
        remaining_thickness_usable = remaining_thickness - minimum_thickness_mm
        remaining_miles = remaining_thickness_usable / wear_per_mile
    
    print(f"\n📈 Summary Results:")
    print("=" * 50)
    print(f"  Total rides analyzed: {len(sample_rides)}")
    print(f"  Total distance: {total_distance_miles:.1f} miles")
    print(f"  Total wear: {total_wear_mm:.3f}mm")
    print(f"  Remaining thickness: {remaining_thickness:.3f}mm")
    print(f"  Wear percentage: {wear_percentage:.1f}%")
    print(f"  Estimated remaining miles: {remaining_miles:.0f} miles")
    print(f"  Needs replacement: {remaining_thickness <= minimum_thickness_mm}")
    
    print(f"\n💡 Insights:")
    if wear_percentage > 50:
        print(f"  ⚠️  High wear detected! Consider replacement soon.")
    elif wear_percentage > 25:
        print(f"  📊 Moderate wear - monitor closely.")
    else:
        print(f"  ✅ Low wear - brake pads in good condition.")
    
    if remaining_miles < 500:
        print(f"  🚨 Less than 500 miles remaining - plan for replacement!")
    elif remaining_miles < 1000:
        print(f"  ⚠️  Less than 1000 miles remaining - start planning replacement.")
    else:
        print(f"  ✅ Plenty of life remaining - continue monitoring.")

if __name__ == "__main__":
    test_sample_brake_wear() 