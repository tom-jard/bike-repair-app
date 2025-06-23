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
      // Note: In production, this should be done server-side to keep client_secret secure
      const response = await fetch(STRAVA_ENDPOINTS.token, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          client_id: STRAVA_CONFIG.client_id,
          client_secret: 'your_client_secret', // This should be handled server-side in production
          code: code,
          grant_type: 'authorization_code'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to exchange token');
      }

      const data = await response.json();
      
      // Store tokens and expiry
      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      this.tokenExpiry = Date.now() + (data.expires_in * 1000);
      
      localStorage.setItem('strava_access_token', this.accessToken);
      localStorage.setItem('strava_refresh_token', this.refreshToken);
      localStorage.setItem('strava_token_expiry', this.tokenExpiry.toString());
      
      return data;
    } catch (error) {
      console.error('Token exchange error:', error);
      throw error;
    }
  }

  // Refresh access token if needed
  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(STRAVA_ENDPOINTS.token, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          client_id: STRAVA_CONFIG.client_id,
          client_secret: 'your_client_secret', // This should be handled server-side in production
          refresh_token: this.refreshToken,
          grant_type: 'refresh_token'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }

      const data = await response.json();
      
      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      this.tokenExpiry = Date.now() + (data.expires_in * 1000);
      
      localStorage.setItem('strava_access_token', this.accessToken);
      localStorage.setItem('strava_refresh_token', this.refreshToken);
      localStorage.setItem('strava_token_expiry', this.tokenExpiry.toString());
      
      return data;
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

  // Make authenticated API request
  async makeAuthenticatedRequest(url, options = {}) {
    await this.ensureValidToken();
    await this.enforceRateLimit();

    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        ...options.headers
      }
    });

    if (response.status === 401) {
      // Token might be invalid, try to refresh
      try {
        await this.refreshAccessToken();
        // Retry the request with new token
        return await fetch(url, {
          ...options,
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            ...options.headers
          }
        });
      } catch (refreshError) {
        this.logout();
        throw new Error('Authentication expired');
      }
    }

    if (response.status === 429) {
      throw new Error('Rate limit exceeded. Please try again later.');
    }

    return response;
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
        per_page: Math.min(perPage, 200).toString() // Strava max is 200
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
          break; // No more activities
        }

        allActivities.push(...activities);
        
        if (activities.length < perPage) {
          break; // Last page
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
      isExpired: this.tokenExpiry ? Date.now() > this.tokenExpiry : false
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
  }
}

export default new StravaService();