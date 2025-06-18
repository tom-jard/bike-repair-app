# Strava API Configuration Example
# Copy this file to config.py and fill in your actual credentials

# Strava API Credentials
# Get these from https://www.strava.com/settings/api
STRAVA_CLIENT_ID = "your_strava_client_id_here"
STRAVA_CLIENT_SECRET = "your_strava_client_secret_here"
STRAVA_ACCESS_TOKEN = "your_strava_access_token_here"

# Optional: OpenWeatherMap API Key for weather data
# Get this from https://openweathermap.org/api
WEATHER_API_KEY = "your_openweathermap_api_key_here"  # Optional

# Google Maps API Key for traffic comparison
# Get this from https://console.cloud.google.com/
# Enable Directions API for traffic estimation
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key_here"  # Required for traffic analysis

# Brake Pad Configuration
BRAKE_MATERIAL = "sintered"  # Options: "organic", "semi-metallic", "ceramic", "sintered"
INITIAL_THICKNESS_MM = 4.0
MINIMUM_THICKNESS_MM = 1.0

# Rider and Bike Configuration
RIDER_WEIGHT_KG = 75.0
BIKE_WEIGHT_KG = 12.0

# Analysis Configuration
DAYS_BACK = 30  # Number of days to analyze 