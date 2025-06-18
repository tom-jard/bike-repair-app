# Mac Mini Setup Guide

This guide will help you set up the Strava Traffic Monitor to run continuously on a Mac Mini.

## 🖥️ Mac Mini Requirements

- **Mac Mini** (any recent model with macOS)
- **Always-on internet connection**
- **Python 3.7+** (usually pre-installed on macOS)
- **At least 4GB RAM** (for smooth operation)

## 📋 Setup Steps

### 1. Transfer Files to Mac Mini

Copy the entire `Bike Repair App` folder to your Mac Mini. You can use:
- **AirDrop** (if both devices support it)
- **iCloud Drive**
- **USB drive**
- **Network file sharing**

### 2. Install Python Dependencies

Open Terminal on the Mac Mini and navigate to the Bike Repair App folder:

```bash
cd "path/to/Bike Repair App"
pip3 install -r requirements.txt
```

### 3. Configure API Keys

Edit the `config.py` file with your API credentials:

```python
# Strava API Credentials
STRAVA_CLIENT_ID = "your_strava_client_id"
STRAVA_CLIENT_SECRET = "your_strava_client_secret"
STRAVA_ACCESS_TOKEN = "your_strava_access_token"

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
```

### 4. Test the Setup

Run a quick test to make sure everything works:

```bash
python3 test_traffic_comparison.py
```

## 🚀 Starting the Service

### Option 1: Manual Start (for testing)

```bash
python3 start_mac_mini_service.py
```

This will start both the monitor and web dashboard.

### Option 2: Auto-start on Boot (recommended)

Create a Launch Agent to automatically start the service when the Mac Mini boots:

1. **Create the Launch Agent file:**

```bash
mkdir -p ~/Library/LaunchAgents
```

Create a file called `com.strava.monitor.plist` in `~/Library/LaunchAgents/`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.strava.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/your/Bike Repair App/start_mac_mini_service.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/strava_monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/strava_monitor_error.log</string>
    <key>WorkingDirectory</key>
    <string>/path/to/your/Bike Repair App</string>
</dict>
</plist>
```

**Important:** Replace `/path/to/your/Bike Repair App` with the actual path on your Mac Mini.

2. **Load the Launch Agent:**

```bash
launchctl load ~/Library/LaunchAgents/com.strava.monitor.plist
```

3. **Start the service:**

```bash
launchctl start com.strava.monitor
```

## 🌐 Accessing the Dashboard

### Local Access
- Open a web browser on the Mac Mini
- Go to: `http://localhost:5000`

### Network Access
- Find your Mac Mini's IP address: `ifconfig | grep "inet " | grep -v 127.0.0.1`
- From any device on your network, go to: `http://[MAC_MINI_IP]:5000`

### Example:
If your Mac Mini's IP is `192.168.1.100`, you can access the dashboard from your phone, laptop, or any device on your network at:
`http://192.168.1.100:5000`

## 📱 Mobile Access

### iPhone/iPad
1. Open Safari
2. Go to the dashboard URL
3. Tap the share button
4. Select "Add to Home Screen"
5. Now you have a "Strava Monitor" app icon!

### Android
1. Open Chrome
2. Go to the dashboard URL
3. Tap the menu (three dots)
4. Select "Add to Home screen"
5. Now you have a "Strava Monitor" app icon!

## 🔧 Monitoring and Maintenance

### Check Service Status
```bash
# Check if the service is running
ps aux | grep python3 | grep strava

# View logs
tail -f /tmp/strava_monitor.log
tail -f /tmp/strava_monitor_error.log
```

### Stop the Service
```bash
# If using Launch Agent
launchctl stop com.strava.monitor

# If running manually
# Press Ctrl+C in the terminal
```

### Restart the Service
```bash
launchctl unload ~/Library/LaunchAgents/com.strava.monitor.plist
launchctl load ~/Library/LaunchAgents/com.strava.monitor.plist
launchctl start com.strava.monitor
```

### Update the Service
1. Stop the service
2. Replace the files with updated versions
3. Restart the service

## 📊 Dashboard Features

The web dashboard provides:

- **Real-time statistics** (total rides, time saved, etc.)
- **Connection status** (online/offline)
- **Recent rides** with detailed traffic comparisons
- **Manual refresh** button
- **Responsive design** (works on mobile)

## 🔒 Security Considerations

- The dashboard is only accessible on your local network
- No authentication is required (add if needed for security)
- Consider using HTTPS for production use
- Keep your API keys secure

## 🛠️ Troubleshooting

### Service Won't Start
1. Check Python installation: `python3 --version`
2. Check dependencies: `pip3 list | grep flask`
3. Check config file: `cat config.py`
4. Check logs: `tail -f /tmp/strava_monitor_error.log`

### Can't Access Dashboard
1. Check if service is running: `ps aux | grep web_dashboard`
2. Check firewall settings
3. Verify IP address: `ifconfig`
4. Try local access first: `http://localhost:5000`

### Monitor Not Detecting Rides
1. Check Strava API credentials
2. Verify internet connection
3. Check API rate limits
4. Look for errors in logs

## 📈 Performance Tips

- **SSD storage** recommended for faster database access
- **8GB+ RAM** for better performance with many rides
- **Ethernet connection** for more reliable network access
- **Regular restarts** (weekly) to prevent memory leaks

## 🔄 Updates

To update the service:

1. Stop the service
2. Backup your database: `cp traffic_comparisons.db traffic_comparisons.db.backup`
3. Replace the Python files
4. Restart the service

The database will be preserved, so you won't lose your historical data.

## 📞 Support

If you encounter issues:

1. Check the logs first
2. Verify all dependencies are installed
3. Test with a simple ride first
4. Check your API keys are valid

The service is designed to be robust and self-healing, automatically restarting if any component fails. 