# Strava Time Savings Analyzer

A React web application that integrates with the Strava API to analyze and visualize time savings from biking versus driving.

## 🚀 Features

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

## 🎯 Demo Mode

This application currently runs in **demo mode** to showcase functionality without requiring complex server-side setup. In demo mode:

- ✅ **Sample Data**: Realistic mock ride data from San Francisco Bay Area
- ✅ **Full UI**: Complete interface with all features working
- ✅ **Traffic Analysis**: Real traffic estimation using Google Maps API (if configured)
- ✅ **Time Calculations**: Accurate time savings calculations
- ⚠️ **Simulated Auth**: OAuth flow is simulated (real implementation requires server-side token exchange)

## 🛠️ Setup

### Quick Start (Demo Mode)

1. **Clone and Install**:
```bash
git clone <repository-url>
cd strava-time-savings-app
npm install
```

2. **Start Development Server**:
```bash
npm run dev
```

3. **Open Browser**: Navigate to `http://localhost:3000`

4. **Try the Demo**: Click "Connect with Strava" to see the demo in action!

### Production Setup

For a production deployment with real Strava data, you'll need:

#### 1. Strava API Configuration

1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Create a new application with these settings:
   - **Application Name**: Your app name
   - **Category**: Choose appropriate category
   - **Website**: Your website or `http://localhost:3000`
   - **Authorization Callback Domain**: `localhost` (for development)
3. Copy your Client ID and update `src/config/strava.js`:

```javascript
export const STRAVA_CONFIG = {
  client_id: "your_actual_strava_client_id",
  redirect_uri: window.location.origin + "/auth/callback",
  scope: "read,activity:read_all"
};
```

#### 2. Server-Side Token Exchange

**⚠️ Important**: The current demo implementation handles token exchange in the frontend for simplicity. For production, you **must** implement server-side token exchange:

```javascript
// Backend endpoint example (Node.js/Express)
app.post('/api/strava/token', async (req, res) => {
  const { code } = req.body;
  
  const response = await fetch('https://www.strava.com/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: process.env.STRAVA_CLIENT_ID,
      client_secret: process.env.STRAVA_CLIENT_SECRET, // Keep this secret!
      code: code,
      grant_type: 'authorization_code'
    })
  });
  
  const data = await response.json();
  res.json(data);
});
```

#### 3. Google Maps API (Optional)

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

## 🔧 How It Works

### Demo Mode Flow
1. User clicks "Connect with Strava"
2. Simulated OAuth flow with mock tokens
3. Displays realistic sample ride data
4. Analyzes time savings using real traffic estimation algorithms

### Production Flow
1. User authenticates with real Strava OAuth
2. Fetches actual ride data from Strava API
3. Calculates car travel times using Google Maps or intelligent estimation
4. Displays real time savings analysis

### Travel Time Analysis

#### Google Maps Integration
- Real-time traffic data and optimal routing
- Considers current traffic conditions
- Provides accurate duration estimates

#### Intelligent Mock Algorithm
When Google Maps isn't available, the app uses a sophisticated estimation:

```javascript
// Traffic patterns by time and day
const trafficMultipliers = {
  rushHour: 1.4-1.5,    // 7-9 AM, 5-7 PM
  lunchTime: 1.1,       // 12-1 PM
  lateNight: 0.7-0.8,   // 11 PM - 5 AM
  weekend: 0.9          // Saturday/Sunday
};

// Additional factors
const carTimeFactors = {
  roadDistance: straightLineDistance * 1.3,
  baseSpeed: 35, // km/h urban average
  parkingTime: 7, // minutes
  trafficLights: distanceBasedDelay
};
```

## 📊 Features

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
- **Rush Hours**: 40-50% slower (7-9 AM, 5-7 PM)
- **Lunch Time**: 10% slower (12-1 PM)
- **Late Night**: 20-30% faster (11 PM - 5 AM)
- **Weekends**: Generally lighter traffic
- **Parking**: +7 minutes average
- **Urban Efficiency**: 35 km/h average speed

## 🔒 Security & Privacy

- **OAuth 2.0**: Secure authentication flow
- **Minimal Permissions**: Only reads activity data
- **Local Processing**: All analysis happens in your browser
- **No Data Collection**: No user data sent to external servers
- **Demo Mode**: Safe to try without real credentials

## 🚀 Deployment

### Development
```bash
npm run dev     # Start development server
npm run build   # Build for production
npm run preview # Preview production build
```

### Production Considerations

1. **HTTPS Required**: OAuth requires HTTPS in production
2. **Environment Variables**: Use proper environment configuration
3. **Server-Side Auth**: Implement backend token exchange
4. **CORS Proxy**: May be needed for Google Maps API
5. **Rate Limiting**: Implement proper API rate limiting

## 🛠️ Technology Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast development and build tool
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Beautiful icons
- **Strava API v3**: Activity data with OAuth 2.0
- **Google Maps Directions API**: Traffic data (optional)

## 🔍 Troubleshooting

### Demo Mode Issues
- **No data showing**: Refresh the page and try again
- **Analysis not working**: Check browser console for errors
- **Slow performance**: Demo includes realistic delays to simulate API calls

### Production Issues
1. **"Authentication failed"**: 
   - Check your Strava Client ID
   - Verify redirect URI matches your app settings
   - Ensure HTTPS in production

2. **"Rate limit exceeded"**: 
   - Wait for the rate limit window to reset
   - Implement proper rate limiting

3. **CORS errors**: 
   - Implement server-side token exchange
   - Use CORS proxy for Google Maps API

## 📈 Future Enhancements

- **Real-time monitoring**: Continuous analysis of new rides
- **Historical trends**: Long-term time savings analysis
- **Route optimization**: Suggest faster bike routes
- **Weather integration**: Factor weather conditions into analysis
- **Social features**: Compare with other cyclists
- **Carbon footprint**: Calculate environmental impact

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (both demo and production modes)
5. Submit a pull request

## 📄 License

MIT License - feel free to use and modify as needed.

## 🆘 Support

- **Demo Mode**: Should work out of the box
- **Strava API**: Check [Strava Developer Documentation](https://developers.strava.com/docs/)
- **Google Maps API**: Check [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- **Issues**: Create an issue in this repository

---

**🚴‍♂️ Happy cycling!** Discover how much time you save by choosing the bike over the car.