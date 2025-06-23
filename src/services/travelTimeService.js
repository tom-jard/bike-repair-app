import { MAPS_CONFIG, TRAFFIC_PATTERNS } from '../config/maps.js';

class TravelTimeService {
  // Calculate straight-line distance between two coordinates (Haversine formula)
  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = this.toRadians(lat2 - lat1);
    const dLon = this.toRadians(lon2 - lon1);
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c; // Distance in kilometers
  }

  toRadians(degrees) {
    return degrees * (Math.PI/180);
  }

  // Get car travel time using Google Maps API
  async getCarTimeWithMaps(startCoords, endCoords, departureTime) {
    if (!MAPS_CONFIG.api_key) {
      throw new Error('Google Maps API key not configured');
    }

    try {
      const params = new URLSearchParams({
        origin: `${startCoords[0]},${startCoords[1]}`,
        destination: `${endCoords[0]},${endCoords[1]}`,
        mode: 'driving',
        departure_time: Math.floor(departureTime.getTime() / 1000),
        traffic_model: 'best_guess',
        key: MAPS_CONFIG.api_key
      });

      const response = await fetch(`${MAPS_CONFIG.directions_endpoint}?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error('Maps API request failed');
      }

      const data = await response.json();
      
      if (data.status !== 'OK' || !data.routes.length) {
        throw new Error('No route found');
      }

      const route = data.routes[0];
      const leg = route.legs[0];
      
      // Use duration_in_traffic if available, otherwise use duration
      const duration = leg.duration_in_traffic || leg.duration;
      
      return {
        duration: duration.value, // seconds
        distance: leg.distance.value, // meters
        trafficCondition: this.analyzeTrafficCondition(leg),
        source: 'google_maps'
      };
    } catch (error) {
      console.error('Google Maps API error:', error);
      throw error;
    }
  }

  // Analyze traffic condition from Google Maps response
  analyzeTrafficCondition(leg) {
    if (!leg.duration_in_traffic) {
      return 'unknown';
    }

    const normalDuration = leg.duration.value;
    const trafficDuration = leg.duration_in_traffic.value;
    const ratio = trafficDuration / normalDuration;

    if (ratio > 1.5) return 'heavy';
    if (ratio > 1.2) return 'moderate';
    return 'light';
  }

  // Estimate car travel time using mock algorithm
  estimateCarTimeWithMock(startCoords, endCoords, departureTime) {
    console.log('🚗 Estimating car time with mock algorithm...');
    console.log('Start coords:', startCoords);
    console.log('End coords:', endCoords);
    console.log('Departure time:', departureTime);

    // Calculate straight-line distance
    const distance = this.calculateDistance(
      startCoords[0], startCoords[1],
      endCoords[0], endCoords[1]
    );

    console.log('Straight-line distance:', distance, 'km');

    // Estimate road distance (typically 1.2-1.4x straight-line for urban areas)
    const roadDistance = distance * 1.3;

    // Base speed assumptions
    const baseSpeedKmh = 35; // Average urban driving speed
    
    // Apply traffic multipliers
    const hour = departureTime.getHours();
    const dayOfWeek = departureTime.getDay();
    
    const hourlyMultiplier = TRAFFIC_PATTERNS.hourly[hour] || 1.0;
    const dailyMultiplier = TRAFFIC_PATTERNS.daily[dayOfWeek] || 1.0;
    
    console.log('Traffic multipliers - hourly:', hourlyMultiplier, 'daily:', dailyMultiplier);
    
    // Calculate adjusted speed
    const adjustedSpeed = baseSpeedKmh / (hourlyMultiplier * dailyMultiplier);
    
    // Calculate base travel time
    const baseTravelTimeHours = roadDistance / adjustedSpeed;
    const baseTravelTimeSeconds = baseTravelTimeHours * 3600;
    
    // Add parking and preparation time (5-10 minutes)
    const parkingTime = 7 * 60; // 7 minutes in seconds
    
    // Add traffic light delays (estimate based on distance)
    const trafficLightDelay = Math.min(roadDistance * 30, 300); // Max 5 minutes
    
    const totalTime = baseTravelTimeSeconds + parkingTime + trafficLightDelay;
    
    console.log('Calculated car time:', Math.round(totalTime), 'seconds');
    
    // Determine traffic condition
    const trafficCondition = this.getTrafficCondition(hourlyMultiplier, dailyMultiplier);
    
    return {
      duration: Math.round(totalTime),
      distance: roadDistance * 1000, // Convert to meters
      trafficCondition,
      source: 'estimated'
    };
  }

  getTrafficCondition(hourlyMultiplier, dailyMultiplier) {
    const combinedMultiplier = hourlyMultiplier * dailyMultiplier;
    
    if (combinedMultiplier > 1.4) return 'heavy';
    if (combinedMultiplier > 1.1) return 'moderate';
    return 'light';
  }

  // Main method to get car travel time
  async getCarTravelTime(startCoords, endCoords, departureTime) {
    console.log('🚗 Getting car travel time...');
    console.log('Start:', startCoords, 'End:', endCoords);
    
    if (!startCoords || !endCoords || startCoords.length !== 2 || endCoords.length !== 2) {
      throw new Error('Invalid coordinates');
    }

    // Validate coordinates are reasonable (not null/undefined/zero)
    if (startCoords[0] === 0 || startCoords[1] === 0 || endCoords[0] === 0 || endCoords[1] === 0) {
      throw new Error('Invalid coordinate values');
    }

    try {
      // Try Google Maps API first if available
      if (MAPS_CONFIG.api_key && MAPS_CONFIG.api_key.trim() !== '') {
        console.log('🗺️ Trying Google Maps API...');
        return await this.getCarTimeWithMaps(startCoords, endCoords, departureTime);
      }
    } catch (error) {
      console.warn('Google Maps API failed, falling back to estimation:', error.message);
    }

    // Fall back to mock estimation
    console.log('📊 Using mock estimation algorithm...');
    return this.estimateCarTimeWithMock(startCoords, endCoords, departureTime);
  }
}

export default new TravelTimeService();