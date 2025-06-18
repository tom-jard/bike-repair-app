"""
Strava-Integrated Brake Pad Wear Estimator

This module estimates brake pad wear based on actual ride data from Strava API,
including weather conditions, elevation data, and ride metrics.
"""

import requests
import json
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union, Any
import math
import os
from urllib.parse import urlencode


class WeatherCondition(Enum):
    """Enumeration of weather conditions that affect brake pad wear."""
    DRY = "dry"
    WET = "wet"
    RAINY = "rainy"
    SNOWY = "snowy"
    MUDDY = "muddy"
    SANDY = "sandy"


class TerrainType(Enum):
    """Enumeration of terrain types that affect brake pad wear."""
    FLAT = "flat"
    HILLY = "hilly"
    MOUNTAINOUS = "mountainous"
    URBAN = "urban"
    OFF_ROAD = "off_road"


@dataclass
class BrakePadSpecs:
    """Specifications for brake pad material and type."""
    material: str  # "organic", "semi-metallic", "ceramic", "sintered"
    compound_hardness: float  # 1-10 scale, higher = harder
    initial_thickness_mm: float
    minimum_thickness_mm: float


@dataclass
class StravaRide:
    """Represents a ride from Strava API."""
    id: int
    name: str
    distance_miles: float
    total_elevation_gain_feet: float
    average_speed_mph: float
    max_speed_mph: float
    moving_time_seconds: int
    start_date: datetime
    weather_condition: Optional[WeatherCondition] = None
    terrain_type: Optional[TerrainType] = None
    temperature_celsius: Optional[float] = None
    precipitation_mm: Optional[float] = None


class StravaAPI:
    """Handles Strava API authentication and data retrieval."""
    
    def __init__(self, client_id: str, client_secret: str, access_token: Optional[str] = None):
        """
        Initialize Strava API client.
        
        Args:
            client_id: Strava API client ID
            client_secret: Strava API client secret
            access_token: Optional access token (if already authenticated)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://www.strava.com/api/v3"
        
    def authenticate(self, authorization_code: str) -> str:
        """
        Authenticate with Strava using authorization code.
        
        Args:
            authorization_code: Authorization code from Strava OAuth flow
            
        Returns:
            Access token for API calls
        """
        url = "https://www.strava.com/oauth/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            return self.access_token
        else:
            raise Exception(f"Authentication failed: {response.text}")
    
    def refresh_token(self, refresh_token: str) -> str:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New access token
        """
        url = "https://www.strava.com/oauth/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            return self.access_token
        else:
            raise Exception(f"Token refresh failed: {response.text}")
    
    def get_activities(self, after: Optional[datetime] = None, before: Optional[datetime] = None, 
                      activity_type: str = "Ride", per_page: int = 200) -> List[Dict[str, Any]]:
        """
        Get activities from Strava API.
        
        Args:
            after: Get activities after this date
            before: Get activities before this date
            activity_type: Type of activity (Ride, Run, etc.)
            per_page: Number of activities per page
            
        Returns:
            List of activity data
        """
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "type": activity_type,
            "per_page": per_page
        }
        
        if after:
            params["after"] = int(after.timestamp())
        if before:
            params["before"] = int(before.timestamp())
        
        url = f"{self.base_url}/athlete/activities"
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get activities: {response.text}")
    
    def get_activity_details(self, activity_id: int) -> Dict[str, Any]:
        """
        Get detailed activity data including segments and weather.
        
        Args:
            activity_id: Strava activity ID
            
        Returns:
            Detailed activity data
        """
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.base_url}/activities/{activity_id}"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get activity details: {response.text}")


class WeatherAPI:
    """Handles weather data retrieval for ride dates and locations."""
    
    def __init__(self, api_key: str):
        """
        Initialize weather API client.
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_weather_for_ride(self, lat: float, lon: float, date: datetime) -> Dict[str, Any]:
        """
        Get weather data for a specific location and date.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Date of the ride
            
        Returns:
            Weather data dictionary
        """
        # Convert to Unix timestamp
        timestamp = int(date.timestamp())
        
        url = f"{self.base_url}/onecall/timemachine"
        params = {
            "lat": lat,
            "lon": lon,
            "dt": timestamp,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                return data["data"][0]
        
        return {}


class StravaBrakeWearEstimator:
    """Estimates brake pad wear based on Strava ride data."""
    
    # Weather wear multipliers (higher = more wear)
    WEATHER_MULTIPLIERS = {
        WeatherCondition.DRY: 1.0,
        WeatherCondition.WET: 1.3,
        WeatherCondition.RAINY: 1.5,
        WeatherCondition.SNOWY: 1.8,
        WeatherCondition.MUDDY: 2.2,
        WeatherCondition.SANDY: 2.5,
    }
    
    # Terrain wear multipliers based on elevation gain per mile
    ELEVATION_TERRAIN_THRESHOLDS = {
        0: TerrainType.FLAT,      # 0-50 ft/mile
        50: TerrainType.HILLY,    # 50-200 ft/mile
        200: TerrainType.MOUNTAINOUS,  # 200+ ft/mile
    }
    
    TERRAIN_MULTIPLIERS = {
        TerrainType.FLAT: 0.8,
        TerrainType.HILLY: 1.2,
        TerrainType.MOUNTAINOUS: 1.6,
        TerrainType.URBAN: 1.1,
        TerrainType.OFF_ROAD: 1.4,
    }
    
    # Material wear rates (mm per 1000 km under standard conditions)
    MATERIAL_WEAR_RATES = {
        "organic": 0.15,
        "semi-metallic": 0.12,
        "ceramic": 0.08,
        "sintered": 0.10,
    }
    
    def __init__(self, brake_pad_specs: BrakePadSpecs, strava_api: StravaAPI, 
                 weather_api: Optional[WeatherAPI] = None):
        """
        Initialize the estimator.
        
        Args:
            brake_pad_specs: Brake pad specifications
            strava_api: Strava API client
            weather_api: Optional weather API client
        """
        self.brake_pad_specs = brake_pad_specs
        self.strava_api = strava_api
        self.weather_api = weather_api
    
    def _determine_terrain_type(self, elevation_gain_feet: float, distance_miles: float) -> TerrainType:
        """
        Determine terrain type based on elevation gain per mile.
        
        Args:
            elevation_gain_feet: Total elevation gain in feet
            distance_miles: Distance in miles
            
        Returns:
            Terrain type
        """
        if distance_miles == 0:
            return TerrainType.FLAT
        
        elevation_per_mile = elevation_gain_feet / distance_miles
        
        if elevation_per_mile < 50:
            return TerrainType.FLAT
        elif elevation_per_mile < 200:
            return TerrainType.HILLY
        else:
            return TerrainType.MOUNTAINOUS
    
    def _determine_weather_condition(self, weather_data: Dict[str, Any]) -> WeatherCondition:
        """
        Determine weather condition from weather API data.
        
        Args:
            weather_data: Weather data from API
            
        Returns:
            Weather condition
        """
        if not weather_data:
            return WeatherCondition.DRY
        
        weather_id = weather_data.get("weather", [{}])[0].get("id", 800)
        precipitation = weather_data.get("rain", {}).get("1h", 0)
        
        # Weather condition mapping based on OpenWeatherMap weather codes
        if weather_id >= 200 and weather_id < 300:  # Thunderstorm
            return WeatherCondition.RAINY
        elif weather_id >= 300 and weather_id < 400:  # Drizzle
            return WeatherCondition.WET
        elif weather_id >= 500 and weather_id < 600:  # Rain
            return WeatherCondition.RAINY if precipitation > 2.5 else WeatherCondition.WET
        elif weather_id >= 600 and weather_id < 700:  # Snow
            return WeatherCondition.SNOWY
        elif weather_id >= 700 and weather_id < 800:  # Atmosphere (fog, mist, etc.)
            return WeatherCondition.WET
        else:  # Clear or clouds
            return WeatherCondition.DRY
    
    def _calculate_braking_frequency(self, elevation_gain_feet: float, distance_miles: float, 
                                   average_speed_mph: float) -> float:
        """
        Estimate braking frequency based on ride characteristics.
        
        Args:
            elevation_gain_feet: Total elevation gain
            distance_miles: Distance in miles
            average_speed_mph: Average speed in mph
            
        Returns:
            Braking frequency on 1-10 scale
        """
        # Base frequency
        base_frequency = 3.0
        
        # Elevation factor (more elevation = more braking)
        elevation_factor = min(3.0, elevation_gain_feet / 1000.0)
        
        # Speed factor (higher speeds = more braking)
        speed_factor = min(2.0, average_speed_mph / 20.0)
        
        # Urban factor (shorter rides likely urban with more stops)
        urban_factor = 1.5 if distance_miles < 10 else 1.0
        
        return min(10.0, base_frequency + elevation_factor + speed_factor + urban_factor)
    
    def process_strava_ride(self, activity_data: Dict[str, Any]) -> StravaRide:
        """
        Process raw Strava activity data into a StravaRide object.
        
        Args:
            activity_data: Raw activity data from Strava API
            
        Returns:
            Processed StravaRide object
        """
        # Convert meters to miles
        distance_miles = activity_data.get("distance", 0) * 0.000621371
        
        # Convert m/s to mph
        average_speed_mph = activity_data.get("average_speed", 0) * 2.23694
        max_speed_mph = activity_data.get("max_speed", 0) * 2.23694
        
        # Convert meters to feet
        elevation_gain_feet = activity_data.get("total_elevation_gain", 0) * 3.28084
        
        # Parse start date
        start_date = datetime.fromisoformat(activity_data.get("start_date", "").replace("Z", "+00:00"))
        
        # Determine terrain type
        terrain_type = self._determine_terrain_type(elevation_gain_feet, distance_miles)
        
        # Calculate braking frequency
        braking_frequency = self._calculate_braking_frequency(
            elevation_gain_feet, distance_miles, average_speed_mph
        )
        
        # Get weather data if available
        weather_condition = None
        temperature_celsius = None
        precipitation_mm = None
        
        if self.weather_api and activity_data.get("start_latlng"):
            lat, lon = activity_data["start_latlng"]
            weather_data = self.weather_api.get_weather_for_ride(lat, lon, start_date)
            weather_condition = self._determine_weather_condition(weather_data)
            temperature_celsius = weather_data.get("temp")
            precipitation_mm = weather_data.get("rain", {}).get("1h", 0)
        
        return StravaRide(
            id=activity_data["id"],
            name=activity_data.get("name", "Unknown Ride"),
            distance_miles=distance_miles,
            total_elevation_gain_feet=elevation_gain_feet,
            average_speed_mph=average_speed_mph,
            max_speed_mph=max_speed_mph,
            moving_time_seconds=activity_data.get("moving_time", 0),
            start_date=start_date,
            weather_condition=weather_condition,
            terrain_type=terrain_type,
            temperature_celsius=temperature_celsius,
            precipitation_mm=precipitation_mm
        )
    
    def estimate_wear_for_ride(self, ride: StravaRide, rider_weight_kg: float = 70.0, 
                              bike_weight_kg: float = 15.0) -> Dict[str, Union[float, str]]:
        """
        Estimate brake pad wear for a single ride.
        
        Args:
            ride: StravaRide object
            rider_weight_kg: Rider weight in kilograms
            bike_weight_kg: Bike weight in kilograms
            
        Returns:
            Dictionary with wear estimates
        """
        # Convert miles to kilometers
        km_ridden = ride.distance_miles * 1.60934
        
        # Base wear rate for the material
        base_wear_rate = self.MATERIAL_WEAR_RATES.get(
            self.brake_pad_specs.material, 0.12
        )
        
        # Calculate wear multipliers
        weather_multiplier = self.WEATHER_MULTIPLIERS.get(
            ride.weather_condition or WeatherCondition.DRY, 1.0
        )
        terrain_multiplier = self.TERRAIN_MULTIPLIERS.get(ride.terrain_type or TerrainType.FLAT, 1.0)
        
        # Speed factor (higher speeds = more wear)
        speed_factor = min(1.5, max(0.5, ride.average_speed_mph / 30.0))
        
        # Braking frequency factor
        braking_frequency = self._calculate_braking_frequency(
            ride.total_elevation_gain_feet, ride.distance_miles, ride.average_speed_mph
        )
        braking_factor = braking_frequency / 5.0
        
        # Weight factor
        total_weight = rider_weight_kg + bike_weight_kg
        weight_factor = min(1.5, max(0.8, total_weight / 100.0))
        
        # Temperature factor
        temp_factor = 1.0
        if ride.temperature_celsius is not None:
            if ride.temperature_celsius < -10 or ride.temperature_celsius > 40:
                temp_factor = 1.2
        
        # Calculate total wear
        total_wear_mm = (
            base_wear_rate *
            (km_ridden / 1000.0) *
            weather_multiplier *
            terrain_multiplier *
            speed_factor *
            braking_factor *
            weight_factor *
            temp_factor
        )
        
        return {
            "ride_id": ride.id,
            "ride_name": ride.name,
            "wear_mm": round(total_wear_mm, 4),
            "weather_condition": ride.weather_condition.value if ride.weather_condition else "unknown",
            "terrain_type": ride.terrain_type.value if ride.terrain_type else "unknown",
            "weather_multiplier": weather_multiplier,
            "terrain_multiplier": terrain_multiplier,
            "speed_factor": round(speed_factor, 2),
            "braking_factor": round(braking_factor, 2),
            "weight_factor": round(weight_factor, 2),
            "temp_factor": temp_factor
        }
    
    def estimate_total_wear(self, rides: List[StravaRide], rider_weight_kg: float = 70.0,
                           bike_weight_kg: float = 15.0) -> Dict[str, Union[float, bool, int, List[Dict[str, Union[float, str]]]]]:
        """
        Estimate total brake pad wear across multiple rides.
        
        Args:
            rides: List of StravaRide objects
            rider_weight_kg: Rider weight in kilograms
            bike_weight_kg: Bike weight in kilograms
            
        Returns:
            Dictionary with total wear estimates
        """
        total_wear_mm = 0.0
        total_distance_miles = 0.0
        ride_details = []
        
        for ride in rides:
            ride_wear = self.estimate_wear_for_ride(ride, rider_weight_kg, bike_weight_kg)
            total_wear_mm += float(ride_wear["wear_mm"])
            total_distance_miles += ride.distance_miles
            ride_details.append(ride_wear)
        
        # Calculate remaining thickness
        remaining_thickness = self.brake_pad_specs.initial_thickness_mm - total_wear_mm
        
        # Calculate wear percentage
        usable_thickness = self.brake_pad_specs.initial_thickness_mm - self.brake_pad_specs.minimum_thickness_mm
        wear_percentage = min(100.0, max(0.0, (total_wear_mm / usable_thickness) * 100))
        
        # Estimate remaining miles
        remaining_miles = 0.0
        if total_wear_mm > 0:
            wear_per_mile = total_wear_mm / total_distance_miles
            remaining_thickness_usable = remaining_thickness - self.brake_pad_specs.minimum_thickness_mm
            if wear_per_mile > 0:
                remaining_miles = remaining_thickness_usable / wear_per_mile
        
        return {
            "total_wear_mm": round(total_wear_mm, 3),
            "remaining_thickness_mm": round(remaining_thickness, 3),
            "wear_percentage": round(wear_percentage, 1),
            "total_distance_miles": round(total_distance_miles, 1),
            "remaining_miles": round(remaining_miles, 0),
            "needs_replacement": remaining_thickness <= self.brake_pad_specs.minimum_thickness_mm,
            "ride_count": len(rides),
            "ride_details": ride_details
        }
    
    def get_recent_rides_wear(self, days_back: int = 30, rider_weight_kg: float = 70.0,
                             bike_weight_kg: float = 15.0) -> Dict[str, Union[float, bool, int, List[Dict[str, Union[float, str]]]]]:
        """
        Get brake pad wear for recent rides from Strava.
        
        Args:
            days_back: Number of days to look back
            rider_weight_kg: Rider weight in kilograms
            bike_weight_kg: Bike weight in kilograms
            
        Returns:
            Dictionary with wear estimates for recent rides
        """
        after_date = datetime.now() - timedelta(days=days_back)
        activities = self.strava_api.get_activities(after=after_date, activity_type="Ride")
        
        rides = []
        for activity in activities:
            ride = self.process_strava_ride(activity)
            rides.append(ride)
        
        return self.estimate_total_wear(rides, rider_weight_kg, bike_weight_kg)


def estimate_brake_pad_wear_from_strava(
    strava_client_id: str,
    strava_client_secret: str,
    strava_access_token: str,
    brake_material: str = "organic",
    rider_weight_kg: float = 70.0,
    bike_weight_kg: float = 15.0,
    days_back: int = 30,
    weather_api_key: Optional[str] = None
) -> Dict[str, Union[float, bool, int, List[Dict[str, Union[float, str]]]]]:
    """
    Convenience function to estimate brake pad wear from Strava data.
    
    Args:
        strava_client_id: Strava API client ID
        strava_client_secret: Strava API client secret
        strava_access_token: Strava access token
        brake_material: Brake pad material
        rider_weight_kg: Rider weight in kilograms
        bike_weight_kg: Bike weight in kilograms
        days_back: Number of days to analyze
        weather_api_key: Optional OpenWeatherMap API key for weather data
        
    Returns:
        Dictionary with wear estimates
    """
    # Create brake pad specs
    brake_specs = BrakePadSpecs(
        material=brake_material,
        compound_hardness=5.0,
        initial_thickness_mm=4.0,
        minimum_thickness_mm=1.0
    )
    
    # Create Strava API client
    strava_api = StravaAPI(strava_client_id, strava_client_secret, strava_access_token)
    
    # Create weather API client if key provided
    weather_api = None
    if weather_api_key:
        weather_api = WeatherAPI(weather_api_key)
    
    # Create estimator
    estimator = StravaBrakeWearEstimator(brake_specs, strava_api, weather_api)
    
    # Get wear estimates
    return estimator.get_recent_rides_wear(days_back, rider_weight_kg, bike_weight_kg)


# Example usage
if __name__ == "__main__":
    # Example configuration (replace with actual values)
    STRAVA_CLIENT_ID = "your_strava_client_id"
    STRAVA_CLIENT_SECRET = "your_strava_client_secret"
    STRAVA_ACCESS_TOKEN = "your_strava_access_token"
    WEATHER_API_KEY = "your_openweathermap_api_key"  # Optional
    
    try:
        result = estimate_brake_pad_wear_from_strava(
            strava_client_id=STRAVA_CLIENT_ID,
            strava_client_secret=STRAVA_CLIENT_SECRET,
            strava_access_token=STRAVA_ACCESS_TOKEN,
            brake_material="sintered",
            rider_weight_kg=75,
            bike_weight_kg=12,
            days_back=30,
            weather_api_key=WEATHER_API_KEY
        )
        
        print("=== Brake Pad Wear Analysis ===")
        print(f"Total wear: {result.get('total_wear_mm', 0)}mm")
        print(f"Remaining thickness: {result.get('remaining_thickness_mm', 0)}mm")
        print(f"Wear percentage: {result.get('wear_percentage', 0)}%")
        print(f"Total distance: {result.get('total_distance_miles', 0)} miles")
        print(f"Remaining miles: {result.get('remaining_miles', 0)} miles")
        print(f"Needs replacement: {result.get('needs_replacement', False)}")
        print(f"Rides analyzed: {result.get('ride_count', 0)}")
        
        print("\n=== Recent Rides ===")
        ride_details = result.get('ride_details', [])
        for ride in ride_details[:5]:  # Show first 5 rides
            if isinstance(ride, dict):
                ride_name = ride.get('ride_name', 'Unknown')
                wear_mm = ride.get('wear_mm', 0)
                print(f"{ride_name}: {wear_mm}mm wear")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set up your Strava API credentials and access token.") 