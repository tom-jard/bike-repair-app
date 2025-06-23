import { STRAVA_CONFIG, STRAVA_ENDPOINTS, RATE_LIMITS } from '../config/strava.js';

class StravaService {
  constructor() {
    this.accessToken = localStorage.getItem('strava_access_token');
    this.refreshToken = localStorage.getItem('strava_refresh_token');
    this.tokenExpiry = localStorage.getItem('strava_token_expiry');
    this.lastRequestTime = 0;
    this.isDemoMode = true; // Always run in demo mode for this version
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

  // Generate demo auth URL (doesn't actually go to Strava)
  getAuthUrl() {
    // In demo mode, return a fake URL that will trigger our demo flow
    return window.location.origin + '?code=demo_auth_code&scope=read,activity:read_all';
  }

  // Simulate token exchange (no external requests)
  async exchangeToken(code) {
    try {
      console.log('🎭 DEMO MODE: Simulating Strava authentication...');
      
      // Simulate API response delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Generate mock tokens for demo
      const mockTokenData = {
        access_token: `demo_access_token_${Date.now()}`,
        refresh_token: `demo_refresh_token_${Date.now()}`,
        expires_in: 21600, // 6 hours
        athlete: {
          id: 12345,
          firstname: "Demo",
          lastname: "Cyclist",
          city: "San Francisco",
          state: "CA",
          country: "USA",
          profile: "https://via.placeholder.com/150"
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
      console.error('Demo token exchange error:', error);
      throw new Error('Demo authentication failed. Please try again.');
    }
  }

  // Simulate token refresh (no external requests)
  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      console.log('🎭 DEMO MODE: Simulating token refresh...');
      
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
      console.error('Demo token refresh error:', error);
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

  // Simulate API request (no external requests)
  async makeAuthenticatedRequest(endpoint) {
    await this.ensureValidToken();
    await this.enforceRateLimit();

    console.log(`🎭 DEMO MODE: Simulating API request to ${endpoint}`);
    
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 700));
    
    // Return mock response based on endpoint
    if (endpoint.includes('/athlete/activities')) {
      return this.generateMockActivities();
    } else if (endpoint.includes('/athlete')) {
      return this.getMockAthlete();
    }
    
    return {};
  }

  // Generate mock activities for demo
  generateMockActivities() {
    const activities = [];
    const now = new Date();
    
    const rideNames = [
      "Morning Commute to Downtown",
      "Evening Ride Home",
      "Weekend Coffee Run",
      "Golden Gate Park Loop",
      "Bay Trail Adventure",
      "Hill Climb Challenge",
      "Lunch Break Ride",
      "Sunset Cruise Along Embarcadero",
      "Market Street Sprint",
      "Presidio Exploration"
    ];

    const locations = [
      // SF Financial District to Mission
      { start: [37.7946, -122.3999], end: [37.7599, -122.4148] },
      // Castro to Fisherman's Wharf
      { start: [37.7609, -122.4350], end: [37.8080, -122.4177] },
      // Sunset to Downtown
      { start: [37.7431, -122.4660], end: [37.7879, -122.4075] },
      // Richmond to SOMA
      { start: [37.7806, -122.4644], end: [37.7749, -122.4194] },
      // Potrero Hill to North Beach
      { start: [37.7587, -122.4043], end: [37.8006, -122.4103] },
      // Haight to Financial District
      { start: [37.7692, -122.4481], end: [37.7946, -122.3999] },
      // Marina to Mission Bay
      { start: [37.8021, -122.4416], end: [37.7706, -122.3900] },
      // Noe Valley to Chinatown
      { start: [37.7506, -122.4331], end: [37.7941, -122.4078] },
      // Glen Park to Russian Hill
      { start: [37.7338, -122.4336], end: [37.8014, -122.4186] },
      // Bernal Heights to Pacific Heights
      { start: [37.7441, -122.4147], end: [37.7886, -122.4324] }
    ];
    
    for (let i = 0; i < 10; i++) {
      const daysAgo = i + Math.random() * 2;
      const date = new Date(now.getTime() - (daysAgo * 24 * 60 * 60 * 1000));
      
      // Vary ride characteristics
      const baseDistance = 3000 + Math.random() * 12000; // 3-15km
      const hilliness = Math.random();
      const elevationGain = hilliness * 400; // 0-400m elevation
      
      // Calculate realistic moving time based on distance and elevation
      const baseSpeed = 20 - (hilliness * 5); // 15-20 km/h depending on hills
      const movingTimeHours = (baseDistance / 1000) / baseSpeed;
      const movingTime = movingTimeHours * 3600; // Convert to seconds
      
      const location = locations[i % locations.length];
      
      activities.push({
        id: 1000000 + i,
        name: rideNames[i % rideNames.length],
        type: 'Ride',
        sport_type: 'Ride',
        start_date: date.toISOString(),
        distance: baseDistance,
        moving_time: Math.round(movingTime),
        start_latlng: location.start,
        end_latlng: location.end,
        average_speed: baseDistance / movingTime, // m/s
        max_speed: (baseDistance / movingTime) * 1.4, // m/s
        total_elevation_gain: Math.round(elevationGain),
        has_heartrate: Math.random() > 0.2,
        average_heartrate: Math.round(140 + Math.random() * 30),
        max_heartrate: Math.round(170 + Math.random() * 20)
      });
    }
    
    return activities.sort((a, b) => new Date(b.start_date) - new Date(a.start_date));
  }

  getMockAthlete() {
    const stored = localStorage.getItem('demo_athlete');
    if (stored) {
      return JSON.parse(stored);
    }
    
    return {
      id: 12345,
      firstname: "Demo",
      lastname: "Cyclist",
      city: "San Francisco",
      state: "CA",
      country: "USA",
      profile: "https://via.placeholder.com/150"
    };
  }

  // Get athlete information
  async getAthlete() {
    try {
      return await this.makeAuthenticatedRequest('/athlete');
    } catch (error) {
      console.error('Error fetching athlete:', error);
      throw error;
    }
  }

  // Get recent activities
  async getActivities(page = 1, perPage = 30) {
    try {
      const activities = await this.makeAuthenticatedRequest('/athlete/activities');
      
      // Filter for rides only and format data
      return activities
        .filter(activity => activity.type === 'Ride')
        .slice((page - 1) * perPage, page * perPage)
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
      isDemoMode: this.isDemoMode
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