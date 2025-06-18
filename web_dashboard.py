#!/usr/bin/env python3
"""
Web Dashboard for Strava Traffic Monitor

This creates a web interface to view traffic comparison data
and monitor status from any device on your network.
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import json
from strava_monitor import StravaMonitor, StoredTrafficComparison
from traffic_comparison import GoogleMapsAPI

app = Flask(__name__)

def load_config():
    """Load configuration from config.py file."""
    try:
        from config import (
            STRAVA_CLIENT_ID,
            STRAVA_CLIENT_SECRET,
            STRAVA_ACCESS_TOKEN,
            GOOGLE_MAPS_API_KEY
        )
        return STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_ACCESS_TOKEN, GOOGLE_MAPS_API_KEY
    except ImportError:
        return None, None, None, None

def get_monitor():
    """Get monitor instance."""
    client_id, client_secret, access_token, maps_api_key = load_config()
    if not all([client_id, client_secret, access_token, maps_api_key]):
        return None
    
    from strava_brake_wear_estimator import StravaAPI
    strava_api = StravaAPI(str(client_id), str(client_secret), str(access_token))
    google_maps_api = GoogleMapsAPI(str(maps_api_key))
    
    return StravaMonitor(strava_api, google_maps_api)

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/comparisons')
def get_comparisons():
    """Get all traffic comparisons as JSON."""
    monitor = get_monitor()
    if not monitor:
        return jsonify({"error": "Monitor not available"})
    
    comparisons = monitor.get_all_comparisons()
    
    # Convert to JSON-serializable format
    data = []
    for comp in comparisons:
        data.append({
            "id": comp.id,
            "activity_id": comp.activity_id,
            "activity_name": comp.activity_name,
            "ride_date": comp.ride_date,
            "bike_time_minutes": comp.bike_time_minutes,
            "car_time_minutes": comp.car_time_minutes,
            "time_saved_minutes": comp.time_saved_minutes,
            "time_saved_percentage": comp.time_saved_percentage,
            "distance_miles": comp.distance_miles,
            "bike_speed_mph": comp.bike_speed_mph,
            "car_speed_mph": comp.car_speed_mph,
            "traffic_conditions": comp.traffic_conditions,
            "route_summary": comp.route_summary,
            "captured_at": comp.captured_at
        })
    
    return jsonify(data)

@app.route('/api/stats')
def get_stats():
    """Get summary statistics."""
    monitor = get_monitor()
    if not monitor:
        return jsonify({"error": "Monitor not available"})
    
    comparisons = monitor.get_all_comparisons()
    
    if not comparisons:
        return jsonify({
            "total_rides": 0,
            "total_distance": 0,
            "total_time_saved": 0,
            "average_time_saved": 0,
            "total_bike_time": 0,
            "total_car_time": 0,
            "average_bike_speed": 0,
            "average_car_speed": 0
        })
    
    total_time_saved = sum(comp.time_saved_minutes for comp in comparisons)
    total_distance = sum(comp.distance_miles for comp in comparisons)
    total_bike_time = sum(comp.bike_time_minutes for comp in comparisons)
    total_car_time = sum(comp.car_time_minutes for comp in comparisons)
    
    stats = {
        "total_rides": len(comparisons),
        "total_distance": round(total_distance, 1),
        "total_time_saved": round(total_time_saved, 1),
        "average_time_saved": round(total_time_saved / len(comparisons), 1),
        "total_bike_time": round(total_bike_time, 1),
        "total_car_time": round(total_car_time, 1),
        "average_bike_speed": round(total_distance / (total_bike_time / 60), 1),
        "average_car_speed": round(total_distance / (total_car_time / 60), 1)
    }
    
    return jsonify(stats)

@app.route('/api/pending')
def get_pending():
    """Get pending captures."""
    monitor = get_monitor()
    if not monitor:
        return jsonify({"error": "Monitor not available"})
    
    pending = monitor.get_pending_captures()
    return jsonify(pending)

@app.route('/api/status')
def get_status():
    """Get monitor status."""
    monitor = get_monitor()
    if not monitor:
        return jsonify({"error": "Monitor not available"})
    
    # Check internet connection
    is_online = monitor.check_internet_connection()
    
    # Get database info
    conn = sqlite3.connect(monitor.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM traffic_comparisons')
    total_comparisons = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM pending_captures')
    pending_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT MAX(captured_at) FROM traffic_comparisons')
    last_capture = cursor.fetchone()[0]
    
    conn.close()
    
    status = {
        "online": is_online,
        "total_comparisons": total_comparisons,
        "pending_captures": pending_count,
        "last_capture": last_capture,
        "last_check": datetime.now().isoformat()
    }
    
    return jsonify(status)

@app.route('/api/trigger_check')
def trigger_check():
    """Manually trigger a check for new activities."""
    monitor = get_monitor()
    if not monitor:
        return jsonify({"error": "Monitor not available"})
    
    try:
        new_comparisons = monitor.check_for_new_activities()
        return jsonify({
            "success": True,
            "new_comparisons": len(new_comparisons),
            "activities": [comp.activity_name for comp in new_comparisons]
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🌐 Starting Web Dashboard...")
    print("   Dashboard will be available at: http://localhost:5000")
    print("   On your network: http://[YOUR_MAC_MINI_IP]:5000")
    print("   Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=False) 