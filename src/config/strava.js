// Strava API Configuration
export const STRAVA_CONFIG = {
  client_id: "164037", // Replace with your actual Strava client ID
  redirect_uri: window.location.origin + "/auth/callback",
  scope: "read,activity:read_all"
};

// Strava API endpoints
export const STRAVA_ENDPOINTS = {
  authorize: "https://www.strava.com/oauth/authorize",
  token: "https://www.strava.com/oauth/token",
  activities: "https://www.strava.com/api/v3/athlete/activities"
};