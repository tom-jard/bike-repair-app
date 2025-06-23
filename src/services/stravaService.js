import { STRAVA_CONFIG, STRAVA_ENDPOINTS, RATE_LIMITS } from '../config/strava.js';

class StravaService {
  constructor() {
    this.accessToken = localStorage.getItem('strava_access_token');
    this.refreshToken = localStorage.getItem('strava_refresh_token');
    this.tokenExpiry = localStorage.getItem('strava_token_expiry');
    this.lastRequestTime = 0;
  }

  // Rate limiting helper
  async enforceRateLimit() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    
    if (timeSinceLastRequest < RATE_LIMITS.delay_between_requests) {
      const delay = RATE_LIMITS.delay_between_requests - timeSinceLastRequest;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    this.lastRequestTime = Date.now();
  }

  // Generate Strava OAuth URL
  getAuthUrl() {
    const params = new URLSearchParams({
      client_id: STRAVA_CONFIG.client_id,
      redirect_uri: STRAVA_CONFIG.redirect_uri,
      response_type: 'code',
      scope: STRAVA_CONFIG.scope,
      approval_prompt: 'auto'
    });

    return `${STRAVA_ENDPOINTS.authorize}?${params.toString()}`;
  }

  // Exchange authorization code for access token
  async exchangeToken(code) {
    try {
      // For demo purposes, we'll simulate a successful token exchange
      // In production, this MUST be done server-side
      
      console.warn('⚠️ DEMO MODE: Token exchange simulated. In production, this must be done server-side.');
      
      // Simulate API response delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Generate mock tokens for demo
      const mockTokenData = {
        access_token: `demo_access_token_${Date.now()}`,
        refresh_token: `demo_refresh_token_${Date.now()}`,
        expires_in: 21600, // 6 hours
        athlete: {
          id: 12345,
          firstname: "Demo",
          lastname: "User",
          city: "San Francisco",
          state: "CA",
          country: "USA"
        }
      };
      
      // Store tokens and expiry
      this.accessToken = mockTokenData.access_token;
      this.refreshToken = mockTokenData.refresh_token;
      this.tokenExpiry = Date.now() + (mockTokenData.expires_in * 1000);
      
      localStorage.setItem('strava_access_token', this.accessToken);
      localStorage.setItem('strava_refresh_token', this.refreshToken);
      localStorage.setItem('strava_token_expiry', this.tokenExpiry.toString());
      localStorage.setItem('demo_athlete', JSON.stringify(mockTokenData.athlete));
      
      return mockTokenData;
    } catch (error) {
      console.error('Token exchange error:', error);
      throw new Error('Failed to authenticate with Strava. Please try again.');
    }
  }

  // Refresh access token if needed
  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      console.warn('⚠️ DEMO MODE: Token refresh simulated.');
      
      // Simulate refresh delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Generate new mock tokens
      const mockTokenData = {
        access_token: `demo_access_token_refreshed_${Date.now()}`,
        refresh_token: this.refreshToken,
        expires_in: 21600
      };
      
      this.accessToken = mockTokenData.access_token;
      this.tokenExpiry = Date.now() + (mockTokenData.expires_in * 1000);
      
      localStorage.setItem('strava_access_token', this.accessToken);
      localStorage.setItem('strava_token_expiry', this.tokenExpiry.toString());
      
      return mockTokenData;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.logout();
      throw error;
    }
  }

  // Check if token needs refresh
  async ensureValidToken() {
    if (!this.accessToken) {
      throw new Error('Not authenticated');
    }

    // Check if token is expired or will expire in the next 5 minutes
    const fiveMinutesFromNow = Date.now() + (5 * 60 * 1000);
    if (this.tokenExpiry && this.tokenExpiry < fiveMinutesFromNow) {
      await this.refreshAccessToken();
    }
  }

  // Make authenticated API request (demo mode)
  async makeAuthenticatedRequest(url, options = {}) {
    await this.ensureValidToken();
    await this.enforceRateLimit();

    // In demo mode, we'll simulate API responses
    console.log(`🔄 Demo API Request: ${url}`);
    
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 700));
    
    return {
      ok: true,
      status: 200,
      json: async () => {
        if (url.includes('/athlete/activities')) {
          return this.generateMockActivities();
        } else if (url.includes('/athlete')) {
          return this.getMockAthlete();
        }
        return {};
      }
    };
  }

  // Generate mock activities for demo
  generateMockActivities() {
    const activities = [];
    const now = new Date();
    
    for (let i = 0; i < 10; i++) {
      const date = new Date(now.getTime() - (i * 24 * 60 * 60 * 1000) - Math.random() * 12 * 60 * 60 * 1000);
      const distance = 2000 + Math.random() * 15000; // 2-17km
      const movingTime = 600 + Math.random() * 3000; // 10-60 minutes
      
      // Generate realistic coordinates (San Francisco Bay Area)
      const baseLat = 37.7749;
      const baseLng = -122.4194;
      const startLat = baseLat + (Math.random() - 0.5) * 0.1;
      const startLng = baseLng + (Math.random() - 0.5) * 0.1;
      const endLat = startLat + (Math.random() - 0.5) * 0.05;
      const endLng = startLng + (Math.random() - 0.5) * 0.05;
      
      activities.push({
        id: 1000000 + i,
        name: this.generateRideName(i),
        type: 'Ride',
        sport_type: 'Ride',
        start_date: date.toISOString(),
        distance: distance,
        moving_time: movingTime,
        start_latlng: [startLat, startLng],
        end_latlng: [endLat, endLng],
        average_speed: distance / movingTime,
        max_speed: (distance / movingTime) * 1.5,
        total_elevation_gain: Math.random() * 500,
        has_heartrate: Math.random() > 0.3,
        average_heartrate: 140 + Math.random() * 40,
        max_heartrate: 160 + Math.random() * 40
      });
    }
    
    return activities;
  }

  generateRideName(index) {
    const names = [
      "Morning Commute",
      "Evening Ride Home",
      "Weekend Coffee Run",
      "Golden Gate Park Loop",
      "Bay Trail Adventure",
      "Hill Climb Challenge",
      "Lunch Break Ride",
      "Sunset Cruise",
      "Market Street Sprint",
      "Presidio Exploration"
    ];
    return names[index % names.length];
  }

  getMockAthlete() {
    const stored = localStorage.getItem('demo_athlete');
    if (stored) {
      return JSON.parse(stored);
    }
    
    return {
      id: 12345,
      firstname: "Demo",
      lastname: "User",
      city: "San Francisco",
      state: "CA",
      country: "USA",
      profile: "https://via.placeholder.com/150"
    };
  }

  // Get athlete information
  async getAthlete() {
    try {
      const response = await this.makeAuthenticatedRequest(STRAVA_ENDPOINTS.athlete);
      
      if (!response.ok) {
        throw new Error('Failed to fetch athlete data');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching athlete:', error);
      throw error;
    }
  }

  // Get recent activities with improved error handling
  async getActivities(page = 1, perPage = 30) {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: Math.min(perPage, 200).toString()
      });

      const response = await this.makeAuthenticatedRequest(
        `${STRAVA_ENDPOINTS.activities}?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch activities: ${response.status}`);
      }

      const activities = await response.json();
      
      // Filter for rides only and add additional data
      return activities
        .filter(activity => activity.type === 'Ride')
        .map(activity => ({
          id: activity.id,
          name: activity.name,
          date: new Date(activity.start_date),
          distance: activity.distance, // meters
          movingTime: activity.moving_time, // seconds
          startCoords: activity.start_latlng,
          endCoords: activity.end_latlng,
          averageSpeed: activity.average_speed, // m/s
          maxSpeed: activity.max_speed, // m/s
          elevationGain: activity.total_elevation_gain, // meters
          type: activity.type,
          sportType: activity.sport_type,
          hasHeartrate: activity.has_heartrate,
          averageHeartrate: activity.average_heartrate,
          maxHeartrate: activity.max_heartrate
        }));
    } catch (error) {
      console.error('Error fetching activities:', error);
      throw error;
    }
  }

  // Get activities with pagination support
  async getAllRecentActivities(maxActivities = 100) {
    const allActivities = [];
    let page = 1;
    const perPage = 30;

    try {
      while (allActivities.length < maxActivities) {
        const activities = await this.getActivities(page, perPage);
        
        if (activities.length === 0) {
          break;
        }

        allActivities.push(...activities);
        
        if (activities.length < perPage) {
          break;
        }

        page++;
      }

      return allActivities.slice(0, maxActivities);
    } catch (error) {
      console.error('Error fetching all activities:', error);
      throw error;
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.accessToken;
  }

  // Get token expiry info
  getTokenInfo() {
    return {
      hasToken: !!this.accessToken,
      hasRefreshToken: !!this.refreshToken,
      expiresAt: this.tokenExpiry ? new Date(this.tokenExpiry) : null,
      isExpired: this.tokenExpiry ? Date.now() > this.tokenExpiry : false,
      isDemoMode: true
    };
  }

  // Logout
  logout() {
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiry = null;
    localStorage.removeItem('strava_access_token');
    localStorage.removeItem('strava_refresh_token');
    localStorage.removeItem('strava_token_expiry');
    localStorage.removeItem('demo_athlete');
  }
}

export default new StravaService();