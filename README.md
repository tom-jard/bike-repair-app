# Bike Repair App - Strava Traffic Monitor

A comprehensive Python application that monitors Strava activities and compares bike ride times to car travel times using real traffic data. Perfect for cyclists who want to track their time savings and traffic efficiency.

## 🚴‍♂️ Features

### Core Functionality
- **Real-time Strava monitoring** - Automatically detects completed rides
- **Traffic comparison** - Compares bike times to car travel times with real traffic data
- **Offline resilience** - Stores activities when offline, processes when connection returns
- **Web dashboard** - Beautiful interface accessible from any device
- **Mobile app experience** - Add to home screen for native app feel

### Brake Pad Wear Analysis
- **Standalone version** - Manual input for wear estimation
- **Strava-integrated version** - Real ride data with weather integration
- **Material-specific calculations** - Different wear rates for various brake pad types
- **Weather and terrain factors** - Comprehensive wear modeling

## 📁 Project Structure

```
Bike Repair App/
├── Core Modules/
│   ├── strava_monitor.py              # Main monitoring system
│   ├── traffic_comparison.py          # Traffic analysis engine
│   ├── strava_brake_wear_estimator.py # Strava-integrated brake analysis
│   └── brake_wear_estimator.py        # Standalone brake analysis
│
├── Web Interface/
│   ├── web_dashboard.py               # Flask web server
│   └── templates/dashboard.html       # Dashboard UI
│
├── Service Management/
│   ├── start_mac_mini_service.py      # Mac Mini service manager
│   ├── run_monitor.py                 # Monitor runner
│   ├── run_strava_analysis.py         # Brake wear analysis runner
│   └── run_traffic_analysis.py        # Traffic analysis runner
│
├── Data Capture/
│   ├── capture_historical_traffic.py  # Historical data capture
│   └── get_strava_token.py            # Strava OAuth helper
│
├── Testing & Examples/
│   ├── test_sample.py                 # Sample brake wear test
│   └── test_traffic_comparison.py     # Traffic comparison demo
│
├── Configuration/
│   ├── config_example.py              # Configuration template
│   └── requirements.txt               # Python dependencies
│
├── Documentation/
│   ├── README.md                      # This file
│   ├── MAC_MINI_SETUP.md             # Mac Mini deployment guide
│   └── README_Strava.md               # Detailed Strava documentation
│
└── Database/
    └── traffic_comparisons.db         # SQLite database (auto-created)
```

## 🚀 Quick Start

### Option 1: Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/bike-repair-app.git
cd bike-repair-app

# Install dependencies
pip3 install -r requirements.txt

# Copy and configure settings
cp config_example.py config.py
# Edit config.py with your API keys

# Test the setup
python3 test_traffic_comparison.py
```

### Option 2: Mac Mini Deployment
```bash
# Follow the complete setup guide
# See MAC_MINI_SETUP.md for detailed instructions

# Start the full service
python3 start_mac_mini_service.py
```

## 🔧 Configuration

### Required API Keys
1. **Strava API** - Get from [Strava API Settings](https://www.strava.com/settings/api)
2. **Google Maps API** - Get from [Google Cloud Console](https://console.cloud.google.com/)

### Configuration File
Copy `config_example.py` to `config.py` and fill in your credentials:
```python
STRAVA_CLIENT_ID = "your_client_id"
STRAVA_CLIENT_SECRET = "your_client_secret"
STRAVA_ACCESS_TOKEN = "your_access_token"
GOOGLE_MAPS_API_KEY = "your_maps_api_key"
```

## 📊 Usage Examples

### Monitor Traffic Comparisons
```bash
# Start continuous monitoring
python3 run_monitor.py

# View web dashboard
python3 web_dashboard.py
# Then visit http://localhost:5000
```

### Analyze Brake Wear
```bash
# Run brake wear analysis
python3 run_strava_analysis.py

# Test with sample data
python3 test_sample.py
```

### Capture Historical Data
```bash
# Capture traffic data for existing rides
python3 capture_historical_traffic.py
```

## 🌐 Web Dashboard

The web dashboard provides:
- **Real-time statistics** - Total rides, time saved, efficiency metrics
- **Connection status** - Monitor online/offline status
- **Recent rides** - Detailed traffic comparisons
- **Mobile-friendly** - Responsive design for all devices
- **Network access** - Accessible from any device on your network

### Access URLs
- **Local:** `http://localhost:5000`
- **Network:** `http://[YOUR_IP]:5000`

## 📱 Mobile Access

### iPhone/iPad
1. Open Safari → Go to dashboard URL
2. Tap share button → "Add to Home Screen"
3. Now you have a native app icon!

### Android
1. Open Chrome → Go to dashboard URL
2. Tap menu → "Add to Home screen"
3. Native app experience

## 🔄 GitHub Management

### Repository Setup
```bash
# Initialize git repository
git init

# Add files (excluding sensitive data)
git add .

# Initial commit
git commit -m "Initial commit: Strava Traffic Monitor"

# Add remote repository
git remote add origin https://github.com/yourusername/bike-repair-app.git

# Push to GitHub
git push -u origin main
```

### Development Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create pull request on GitHub
# Merge after review
```

### Deployment Workflow
```bash
# On Mac Mini, pull latest changes
git pull origin main

# Restart service if needed
launchctl restart com.strava.monitor
```

### Security Best Practices
- ✅ **Never commit** `config.py` (contains API keys)
- ✅ **Use environment variables** for production
- ✅ **Regular backups** of database files
- ✅ **Monitor API usage** and rate limits

## 🛠️ Development

### Adding New Features
1. Create feature branch: `git checkout -b feature/name`
2. Implement changes
3. Test thoroughly
4. Update documentation
5. Create pull request

### Testing
```bash
# Run all tests
python3 test_sample.py
python3 test_traffic_comparison.py

# Test web dashboard
python3 web_dashboard.py
# Visit http://localhost:5000
```

### Code Style
- Follow PEP 8 Python style guide
- Add docstrings to all functions
- Include type hints where helpful
- Write clear commit messages

## 📈 Performance & Monitoring

### Database Management
- SQLite database auto-created on first run
- Regular backups recommended
- Monitor database size over time

### API Rate Limits
- Strava: 1000 requests/day
- Google Maps: Varies by plan
- Monitor usage in dashboard

### System Requirements
- **Mac Mini:** 4GB+ RAM, SSD recommended
- **Python:** 3.7+ required
- **Network:** Always-on internet connection

## 🔒 Security

### API Key Management
- Store keys in `config.py` (not in git)
- Use environment variables for production
- Rotate keys regularly
- Monitor for unauthorized usage

### Network Security
- Dashboard only accessible on local network
- Consider adding authentication for production
- Use HTTPS for external access

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Update documentation
6. Submit pull request

## 📄 License

This project is open source. Please ensure you comply with:
- Strava's API terms of service
- Google Maps API terms of service
- Any other third-party service agreements

## 🆘 Support

### Common Issues
1. **API rate limits** - Check usage in dashboard
2. **Connection issues** - Monitor offline/online status
3. **Database errors** - Check file permissions
4. **Service won't start** - Check logs and dependencies

### Getting Help
1. Check the logs: `tail -f /tmp/strava_monitor.log`
2. Verify configuration in `config.py`
3. Test with sample data first
4. Check GitHub issues for known problems

---

**Happy cycling! 🚴‍♂️** Track your rides, beat traffic, and keep your bike in top condition.