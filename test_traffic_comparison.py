#!/usr/bin/env python3
"""
Test Traffic Comparison

This script demonstrates the traffic comparison feature with sample data.
Note: This requires both Strava and Google Maps API credentials to work with real data.
"""

from traffic_comparison import TrafficComparison, print_traffic_summary

def test_with_sample_data():
    """Test the traffic comparison with sample data."""
    
    print("🚗 Traffic Comparison Test")
    print("=" * 40)
    print("This test shows the format of traffic comparison results.")
    print("For real analysis, you need Strava and Google Maps API credentials.\n")
    
    # Create sample traffic comparison data
    sample_comparisons = [
        TrafficComparison(
            activity_id=123456,
            activity_name="Morning Commute",
            bike_time_minutes=25.5,
            car_time_minutes=35.2,
            time_saved_minutes=9.7,
            time_saved_percentage=27.6,
            distance_miles=8.2,
            bike_speed_mph=19.3,
            car_speed_mph=14.0,
            traffic_conditions="Moderate Traffic",
            route_summary="I-5 S"
        ),
        TrafficComparison(
            activity_id=123457,
            activity_name="Evening Ride Home",
            bike_time_minutes=28.0,
            car_time_minutes=45.8,
            time_saved_minutes=17.8,
            time_saved_percentage=38.9,
            distance_miles=8.2,
            bike_speed_mph=17.6,
            car_speed_mph=10.7,
            traffic_conditions="Heavy Traffic",
            route_summary="I-5 N"
        ),
        TrafficComparison(
            activity_id=123458,
            activity_name="Weekend Coffee Run",
            bike_time_minutes=15.2,
            car_time_minutes=12.1,
            time_saved_minutes=-3.1,
            time_saved_percentage=-25.6,
            distance_miles=3.8,
            bike_speed_mph=15.0,
            car_speed_mph=18.8,
            traffic_conditions="Light Traffic",
            route_summary="Local streets"
        )
    ]
    
    # Print the sample results
    print_traffic_summary(sample_comparisons)
    
    print("\n📝 To run with real data:")
    print("1. Set up Google Maps API (see README.md)")
    print("2. Add GOOGLE_MAPS_API_KEY to your config.py")
    print("3. Run: python3 run_traffic_analysis.py")

if __name__ == "__main__":
    test_with_sample_data() 