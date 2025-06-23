# Strava Time Savings Analyzer

A React web application that integrates with the Strava API to analyze and visualize time savings from biking versus driving.

## Features

- **Strava OAuth Integration**: Secure authentication with your Strava account
- **Intelligent Travel Time Estimation**: 
  - Uses Google Maps Directions API when available
  - Falls back to smart mock algorithm considering traffic patterns, parking time, and delays
- **Time Comparison Analysis**: Compare actual bike times vs estimated car travel times
- **Beautiful Dashboard**: Clean, responsive interface showing:
  - Individual ride analysis
  - Summary statistics
  - Traffic condition indicators
  - Time savings visualization
- **Rate Limiting**: Respects Strava API limits with automatic token refresh

## Setup

### 1. Strava API Configuration

1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Create a new application with these settings:
   - **Application Name**: Your app name
   - **Category**: Choose appropriate category
   - **Club**: Leave blank unless applicable
   - **Website**: Your website or `http://localhost:3000`
   - **Authorization Callback Domain**: `localhost` (for development)
3. Copy your Client ID and Client Secret
4. Update `src/config/strava.js`:

```javascript
export const STRAVA_CONFIG = {
  client_id: "your_actual_strava_client_id",
  redirect_uri: window.location.origin + "/auth/callback",
  scope: "read,activity:read_all"
};
```

**Important Security Note**: The current implementation includes the client secret in the frontend code for demonstration purposes. In a production environment, you should:
- Handle token exchange on your backend server
- Never expose client secrets in frontend code
- Use environment variables for sensitive configuration

### 2. Google Maps API (Optional)

For more accurate car travel time estimates:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Directions API**
4. Create an API key with appropriate restrictions
5. Update `src/config/maps.js`:

```javascript
export const MAPS_CONFIG = {
  api_key: "your_google_maps_api_key",
  directions_endpoint: "https://maps.googleapis.com/maps/api/directions/json"
};
```

**Note**: If no Google Maps API key is provided, the app will use an intelligent mock algorithm that factors in:
- Traffic patterns by time of day and day of week
- Parking and preparation time
- Traffic light delays
- Urban driving conditions

### 3. Install and Run

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## How It Works

### Authentication Flow
1. User clicks "Connect with Strava"
2. Redirected to Strava OAuth with proper scopes
3. After authorization, returns with authorization code
4. Code is exchanged for access token and refresh token
5. Tokens stored locally with automatic refresh handling

### API Integration
- **Rate Limiting**: Respects Strava's 100 requests per 15 minutes limit
- **Token Management**: Automatic refresh when tokens expire
- **Error Handling**: Graceful handling of API errors and rate limits
- **Data Filtering**: Only analyzes rides with GPS coordinates and reasonable distance

### Travel Time Analysis
1. Fetches recent rides from Strava API
2. Filters rides with GPS coordinates and minimum distance
3. For each ride, estimates car travel time using:
   - **Google Maps API**: Real-time traffic data and optimal routing
   - **Mock Algorithm**: Intelligent estimation based on:
     - Straight-line distance × road factor (1.3x)
     - Base urban speed (35 km/h)
     - Traffic multipliers by time/day
     - Parking time (+7 minutes)
     - Traffic light delays

### Time Savings Calculation
```
Time Saved = Estimated Car Time - Actual Bike Time
```

Positive values mean biking was faster, negative means driving would have been faster.

## Features

### Dashboard Statistics
- Total analyzed rides
- Total time saved
- Average time saved per ride
- Total distance covered

### Individual Ride Analysis
- Ride name and date
- Distance and bike time
- Estimated car time with traffic conditions
- Time saved/lost comparison
- Traffic condition indicators (light/moderate/heavy)
- Data source indicator (Google Maps vs Estimated)

### Smart Traffic Estimation
When Google Maps isn't available, the mock algorithm considers:

**Traffic Patterns**:
- Rush hours (7-9 AM, 5-7 PM): 1.4-1.5x slower
- Lunch time (12-1 PM): 1.1x slower  
- Late night (11 PM - 5 AM): 0.7-0.8x faster
- Weekends: Generally lighter traffic

**Additional Factors**:
- Parking time: +7 minutes average
- Traffic lights: Distance-based delay estimation
- Urban efficiency: 35 km/h average speed

## API Limits and Rate Limiting

### Strava API Limits
- **Daily**: 1,000 requests per day
- **15-minute**: 100 requests per 15 minutes
- **Per-request**: 200ms minimum delay between requests

### Google Maps API Limits
- **Free Tier**: 2,500 requests per day
- **Paid Plans**: Higher limits available

The app automatically handles rate limiting and will show appropriate error messages if limits are exceeded.

## Technology Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast development and build tool
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Beautiful icons
- **Strava API v3**: Activity data with OAuth 2.0
- **Google Maps Directions API**: Traffic data (optional)

## Security & Privacy

- **OAuth 2.0**: Secure authentication flow
- **Token Management**: Automatic refresh with secure storage
- **Minimal Permissions**: Only reads activity data (no write permissions)
- **Local Processing**: All analysis happens in your browser
- **No Data Collection**: No user data sent to external servers

## Browser Compatibility

- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge
- Mobile responsive design

## Development

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Troubleshooting

### Common Issues

1. **"Authentication failed"**: 
   - Check your Strava Client ID in `src/config/strava.js`
   - Verify redirect URI matches your Strava app settings
   - Ensure you're using the correct authorization callback domain

2. **"Rate limit exceeded"**: 
   - Wait for the rate limit window to reset (15 minutes)
   - The app will automatically retry after the limit resets

3. **"No activities found"**: 
   - Ensure your rides have GPS data
   - Check that rides are longer than 500 meters
   - Verify your Strava privacy settings allow API access

4. **"Failed to analyze"**: 
   - Check network connection
   - Verify Google Maps API key (if using)
   - Check browser console for detailed error messages

### API Setup Issues

1. **Strava OAuth Errors**:
   - Verify your app's authorization callback domain is set to `localhost`
   - Check that your Client ID matches exactly
   - Ensure your app has the correct scopes: `read,activity:read_all`

2. **Google Maps CORS Issues**:
   - The app will automatically fall back to mock estimation
   - Consider using a backend proxy for production deployments

### Token Issues

1. **Token Expired**: The app automatically refreshes tokens
2. **Invalid Token**: Logout and re-authenticate
3. **Missing Refresh Token**: Re-authenticate to get new tokens

## Production Deployment

For production deployment, consider:

1. **Backend Token Exchange**: Move client secret to backend
2. **Environment Variables**: Use proper environment configuration
3. **HTTPS**: Required for OAuth in production
4. **CORS Proxy**: For Google Maps API if needed
5. **Error Monitoring**: Add error tracking service

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use and modify as needed.

## Support

For issues related to:
- **Strava API**: Check [Strava Developer Documentation](https://developers.strava.com/docs/)
- **Google Maps API**: Check [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- **App Issues**: Create an issue in this repository