"""
Traffic Comparison Module

This module compares bike ride times to car travel times using Google Maps API.
It analyzes Strava activities and estimates how long the same route would take by car.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time

@dataclass
class TrafficComparison:
    """Results of traffic comparison analysis."""
    activity_id: int
    activity_name: str
    bike_time_minutes: float
    car_time_minutes: float
    time_saved_minutes: float
    time_saved_percentage: float
    distance_miles: float
    bike_speed_mph: float
    car_speed_mph: float
    traffic_conditions: str
    route_summary: str

class GoogleMapsAPI:
    """Handles Google Maps API calls for traffic estimation."""
    
    def __init__(self, api_key: str):
        """
        Initialize Google Maps API client.
        
        Args:
            api_key: Google Maps API key with Directions API enabled
        """
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    def get_route_time(self, start_lat: float, start_lng: float, 
                      end_lat: float, end_lng: float, 
                      departure_time: Optional[datetime] = None) -> Dict:
        """
        Get car travel time between two points.
        
        Args:
            start_lat, start_lng: Starting coordinates
            end_lat, end_lng: Ending coordinates
            departure_time: When the trip would depart (for traffic estimation)
            
        Returns:
            Dictionary with route information
        """
        params = {
            "origin": f"{start_lat},{start_lng}",
            "destination": f"{end_lat},{end_lng}",
            "mode": "driving",
            "key": self.api_key
        }
        
        # Add departure time for traffic estimation
        if departure_time:
            params["departure_time"] = "now"  # Use current traffic conditions
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "OK" and data.get("routes"):
                    route = data["routes"][0]
                    leg = route["legs"][0]
                    
                    # Get duration in traffic (if available) or regular duration
                    duration_in_traffic = leg.get("duration_in_traffic", leg["duration"])
                    
                    return {
                        "duration_seconds": duration_in_traffic["value"],
                        "duration_text": duration_in_traffic["text"],
                        "distance_meters": leg["distance"]["value"],
                        "distance_text": leg["distance"]["text"],
                        "traffic_conditions": self._analyze_traffic(leg),
                        "route_summary": route.get("summary", "Unknown route")
                    }
                else:
                    return {"error": f"API Error: {data.get('status', 'Unknown')}"}
            else:
                return {"error": f"HTTP Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def _analyze_traffic(self, leg: Dict) -> str:
        """
        Analyze traffic conditions based on route data.
        
        Args:
            leg: Route leg data from Google Maps API
            
        Returns:
            Traffic condition description
        """
        # Check if we have traffic data
        if "duration_in_traffic" in leg:
            regular_duration = leg["duration"]["value"]
            traffic_duration = leg["duration_in_traffic"]["value"]
            
            if traffic_duration > regular_duration * 1.3:
                return "Heavy Traffic"
            elif traffic_duration > regular_duration * 1.1:
                return "Moderate Traffic"
            else:
                return "Light Traffic"
        else:
            return "Unknown Traffic"

class StravaTrafficAnalyzer:
    """Analyzes Strava activities and compares to car travel times."""
    
    def __init__(self, strava_api, google_maps_api: GoogleMapsAPI):
        """
        Initialize the traffic analyzer.
        
        Args:
            strava_api: Strava API client
            google_maps_api: Google Maps API client
        """
        self.strava_api = strava_api
        self.google_maps_api = google_maps_api
    
    def analyze_activity_traffic(self, activity_id: int) -> Optional[TrafficComparison]:
        """
        Analyze a single Strava activity for traffic comparison.
        
        Args:
            activity_id: Strava activity ID
            
        Returns:
            TrafficComparison object or None if analysis fails
        """
        try:
            # Get activity details from Strava
            activity = self.strava_api.get_activity_details(activity_id)
            
            if not activity:
                return None
            
            # Extract activity data
            activity_name = activity.get("name", "Unknown Activity")
            moving_time_seconds = activity.get("moving_time", 0)
            distance_meters = activity.get("distance", 0)
            start_date = datetime.fromisoformat(activity.get("start_date", "").replace("Z", "+00:00"))
            
            # Get start and end coordinates
            start_latlng = activity.get("start_latlng")
            end_latlng = activity.get("end_latlng")
            
            if not start_latlng or not end_latlng:
                return None
            
            start_lat, start_lng = start_latlng
            end_lat, end_lng = end_latlng
            
            # Get car route time
            route_data = self.google_maps_api.get_route_time(
                start_lat, start_lng, end_lat, end_lng, start_date
            )
            
            if "error" in route_data:
                print(f"Error getting route data: {route_data['error']}")
                return None
            
            # Calculate metrics
            bike_time_minutes = moving_time_seconds / 60.0
            car_time_minutes = route_data["duration_seconds"] / 60.0
            time_saved_minutes = car_time_minutes - bike_time_minutes
            time_saved_percentage = (time_saved_minutes / car_time_minutes) * 100 if car_time_minutes > 0 else 0
            
            distance_miles = distance_meters * 0.000621371
            bike_speed_mph = distance_miles / (bike_time_minutes / 60.0) if bike_time_minutes > 0 else 0
            car_speed_mph = distance_miles / (car_time_minutes / 60.0) if car_time_minutes > 0 else 0
            
            return TrafficComparison(
                activity_id=activity_id,
                activity_name=activity_name,
                bike_time_minutes=bike_time_minutes,
                car_time_minutes=car_time_minutes,
                time_saved_minutes=time_saved_minutes,
                time_saved_percentage=time_saved_percentage,
                distance_miles=distance_miles,
                bike_speed_mph=bike_speed_mph,
                car_speed_mph=car_speed_mph,
                traffic_conditions=route_data["traffic_conditions"],
                route_summary=route_data["route_summary"]
            )
            
        except Exception as e:
            print(f"Error analyzing activity {activity_id}: {e}")
            return None
    
    def analyze_recent_activities(self, days_back: int = 7) -> List[TrafficComparison]:
        """
        Analyze recent Strava activities for traffic comparison.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of TrafficComparison objects
        """
        try:
            # Get recent activities
            after_date = datetime.now() - timedelta(days=days_back)
            activities = self.strava_api.get_activities(after=after_date, activity_type="Ride")
            
            results = []
            
            for activity in activities:
                activity_id = activity["id"]
                print(f"Analyzing activity: {activity.get('name', 'Unknown')}")
                
                comparison = self.analyze_activity_traffic(activity_id)
                if comparison:
                    results.append(comparison)
                
                # Rate limiting - be nice to APIs
                time.sleep(1)
            
            return results
            
        except Exception as e:
            print(f"Error analyzing recent activities: {e}")
            return []

def print_traffic_summary(comparisons: List[TrafficComparison]):
    """Print a summary of traffic comparisons."""
    
    if not comparisons:
        print("No activities analyzed.")
        return
    
    print("\n🚗 Traffic Comparison Summary")
    print("=" * 50)
    
    total_time_saved = 0
    total_distance = 0
    total_bike_time = 0
    total_car_time = 0
    
    for comp in comparisons:
        print(f"\n📊 {comp.activity_name}")
        print(f"   Distance: {comp.distance_miles:.1f} miles")
        print(f"   Bike time: {comp.bike_time_minutes:.1f} minutes")
        print(f"   Car time: {comp.car_time_minutes:.1f} minutes")
        print(f"   Time saved: {comp.time_saved_minutes:.1f} minutes ({comp.time_saved_percentage:.1f}%)")
        print(f"   Traffic: {comp.traffic_conditions}")
        print(f"   Route: {comp.route_summary}")
        
        if comp.time_saved_minutes > 0:
            print(f"   ✅ Beat car by {comp.time_saved_minutes:.1f} minutes!")
        else:
            print(f"   ⏰ Car was {abs(comp.time_saved_minutes):.1f} minutes faster")
        
        total_time_saved += comp.time_saved_minutes
        total_distance += comp.distance_miles
        total_bike_time += comp.bike_time_minutes
        total_car_time += comp.car_time_minutes
    
    # Overall summary
    print(f"\n📈 Overall Summary")
    print("=" * 30)
    print(f"Total activities: {len(comparisons)}")
    print(f"Total distance: {total_distance:.1f} miles")
    print(f"Total bike time: {total_bike_time:.1f} minutes")
    print(f"Total car time: {total_car_time:.1f} minutes")
    print(f"Total time saved: {total_time_saved:.1f} minutes")
    
    if total_time_saved > 0:
        print(f"🚴‍♂️ You saved {total_time_saved:.1f} minutes by biking!")
    else:
        print(f"⏰ Cars would have been {abs(total_time_saved):.1f} minutes faster overall")

def analyze_strava_traffic(strava_client_id: str, strava_client_secret: str, 
                          strava_access_token: str, google_maps_api_key: str,
                          days_back: int = 7) -> List[TrafficComparison]:
    """
    Convenience function to analyze Strava traffic.
    
    Args:
        strava_client_id: Strava API client ID
        strava_client_secret: Strava API client secret
        strava_access_token: Strava access token
        google_maps_api_key: Google Maps API key
        days_back: Number of days to analyze
        
    Returns:
        List of TrafficComparison objects
    """
    from strava_brake_wear_estimator import StravaAPI
    
    # Initialize APIs
    strava_api = StravaAPI(strava_client_id, strava_client_secret, strava_access_token)
    google_maps_api = GoogleMapsAPI(google_maps_api_key)
    
    # Create analyzer
    analyzer = StravaTrafficAnalyzer(strava_api, google_maps_api)
    
    # Analyze activities
    return analyzer.analyze_recent_activities(days_back)

# Example usage
if __name__ == "__main__":
    print("Traffic Comparison Module")
    print("To use this module, you need:")
    print("1. Strava API credentials")
    print("2. Google Maps API key with Directions API enabled")
    print("3. Call analyze_strava_traffic() with your credentials") 