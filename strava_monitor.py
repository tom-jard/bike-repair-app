#!/usr/bin/env python3
"""
Strava Activity Monitor

This script monitors for new Strava activities and immediately captures
traffic data when a ride is finished for accurate historical comparison.
Enhanced to handle offline scenarios and connection issues.
"""

import time
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from dataclasses import dataclass, asdict
from traffic_comparison import GoogleMapsAPI, TrafficComparison

@dataclass
class StoredTrafficComparison:
    """Stored traffic comparison data."""
    id: Optional[int]
    activity_id: int
    activity_name: str
    ride_date: str
    bike_time_minutes: float
    car_time_minutes: float
    time_saved_minutes: float
    time_saved_percentage: float
    distance_miles: float
    bike_speed_mph: float
    car_speed_mph: float
    traffic_conditions: str
    route_summary: str
    captured_at: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float

class StravaMonitor:
    """Monitors Strava for new activities and captures traffic data."""
    
    def __init__(self, strava_api, google_maps_api: GoogleMapsAPI, db_path: str = "traffic_comparisons.db"):
        """
        Initialize the monitor.
        
        Args:
            strava_api: Strava API client
            google_maps_api: Google Maps API client
            db_path: Path to SQLite database
        """
        self.strava_api = strava_api
        self.google_maps_api = google_maps_api
        self.db_path = db_path
        self.last_activity_id = None
        self.last_check_time = None
        self.connection_errors = 0
        self.max_retries = 3
        self.setup_database()
    
    def setup_database(self):
        """Set up SQLite database for storing traffic comparisons."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER UNIQUE,
                activity_name TEXT,
                ride_date TEXT,
                bike_time_minutes REAL,
                car_time_minutes REAL,
                time_saved_minutes REAL,
                time_saved_percentage REAL,
                distance_miles REAL,
                bike_speed_mph REAL,
                car_speed_mph REAL,
                traffic_conditions TEXT,
                route_summary TEXT,
                captured_at TEXT,
                start_lat REAL,
                start_lng REAL,
                end_lat REAL,
                end_lng REAL
            )
        ''')
        
        # Add table for pending activities that need traffic capture
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER UNIQUE,
                activity_name TEXT,
                ride_date TEXT,
                bike_time_minutes REAL,
                distance_miles REAL,
                bike_speed_mph REAL,
                start_lat REAL,
                start_lng REAL,
                end_lat REAL,
                end_lng REAL,
                discovered_at TEXT,
                retry_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_internet_connection(self) -> bool:
        """Check if internet connection is available."""
        try:
            # Try to connect to a reliable service
            requests.get("https://www.google.com", timeout=5)
            return True
        except:
            return False
    
    def get_last_processed_activity(self) -> Optional[int]:
        """Get the last processed activity ID from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT MAX(activity_id) FROM traffic_comparisons')
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result[0] else None
    
    def store_pending_activity(self, activity: Dict):
        """Store activity for later traffic capture when offline."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Extract activity data
            activity_id = activity["id"]
            activity_name = activity.get("name", "Unknown Activity")
            moving_time_seconds = activity.get("moving_time", 0)
            distance_meters = activity.get("distance", 0)
            start_date = datetime.fromisoformat(activity.get("start_date", "").replace("Z", "+00:00"))
            
            start_latlng = activity.get("start_latlng")
            end_latlng = activity.get("end_latlng")
            
            if not start_latlng or not end_latlng:
                return
            
            start_lat, start_lng = start_latlng
            end_lat, end_lng = end_latlng
            
            bike_time_minutes = moving_time_seconds / 60.0
            distance_miles = distance_meters * 0.000621371
            bike_speed_mph = distance_miles / (bike_time_minutes / 60.0) if bike_time_minutes > 0 else 0
            
            cursor.execute('''
                INSERT OR REPLACE INTO pending_captures 
                (activity_id, activity_name, ride_date, bike_time_minutes, distance_miles,
                 bike_speed_mph, start_lat, start_lng, end_lat, end_lng, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                activity_id, activity_name, start_date.isoformat(),
                bike_time_minutes, distance_miles, bike_speed_mph,
                start_lat, start_lng, end_lat, end_lng, datetime.now().isoformat()
            ))
            
            conn.commit()
            print(f"   📱 Stored for later capture (offline)")
            
        except Exception as e:
            print(f"   ❌ Error storing pending activity: {e}")
        finally:
            conn.close()
    
    def get_pending_captures(self) -> List[Dict]:
        """Get all pending activities that need traffic capture."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT activity_id, activity_name, ride_date, bike_time_minutes,
                   distance_miles, bike_speed_mph, start_lat, start_lng, end_lat, end_lng,
                   discovered_at, retry_count
            FROM pending_captures
            WHERE retry_count < 3
            ORDER BY discovered_at ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        pending = []
        for row in rows:
            pending.append({
                "activity_id": row[0],
                "activity_name": row[1],
                "ride_date": row[2],
                "bike_time_minutes": row[3],
                "distance_miles": row[4],
                "bike_speed_mph": row[5],
                "start_lat": row[6],
                "start_lng": row[7],
                "end_lat": row[8],
                "end_lng": row[9],
                "discovered_at": row[10],
                "retry_count": row[11]
            })
        
        return pending
    
    def process_pending_captures(self) -> int:
        """Process pending activities when connection is restored."""
        pending = self.get_pending_captures()
        
        if not pending:
            return 0
        
        print(f"   🔄 Processing {len(pending)} pending captures...")
        
        processed = 0
        for pending_activity in pending:
            try:
                # Try to capture traffic data
                comparison = self.capture_traffic_for_pending(pending_activity)
                
                if comparison:
                    # Remove from pending
                    self.remove_pending_activity(pending_activity["activity_id"])
                    processed += 1
                    print(f"      ✅ Processed: {pending_activity['activity_name']}")
                else:
                    # Increment retry count
                    self.increment_retry_count(pending_activity["activity_id"])
                    print(f"      ⚠️  Failed, will retry: {pending_activity['activity_name']}")
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"      ❌ Error processing pending: {e}")
                self.increment_retry_count(pending_activity["activity_id"])
        
        return processed
    
    def capture_traffic_for_pending(self, pending_activity: Dict) -> Optional[StoredTrafficComparison]:
        """Capture traffic data for a pending activity."""
        try:
            # Get car route time
            route_data = self.google_maps_api.get_route_time(
                pending_activity["start_lat"], pending_activity["start_lng"],
                pending_activity["end_lat"], pending_activity["end_lng"]
            )
            
            if "error" in route_data:
                return None
            
            # Calculate metrics
            bike_time_minutes = pending_activity["bike_time_minutes"]
            car_time_minutes = route_data["duration_seconds"] / 60.0
            time_saved_minutes = car_time_minutes - bike_time_minutes
            time_saved_percentage = (time_saved_minutes / car_time_minutes) * 100 if car_time_minutes > 0 else 0
            
            distance_miles = pending_activity["distance_miles"]
            bike_speed_mph = pending_activity["bike_speed_mph"]
            car_speed_mph = distance_miles / (car_time_minutes / 60.0) if car_time_minutes > 0 else 0
            
            # Create stored comparison
            comparison = StoredTrafficComparison(
                id=None,
                activity_id=pending_activity["activity_id"],
                activity_name=pending_activity["activity_name"],
                ride_date=pending_activity["ride_date"],
                bike_time_minutes=bike_time_minutes,
                car_time_minutes=car_time_minutes,
                time_saved_minutes=time_saved_minutes,
                time_saved_percentage=time_saved_percentage,
                distance_miles=distance_miles,
                bike_speed_mph=bike_speed_mph,
                car_speed_mph=car_speed_mph,
                traffic_conditions=route_data["traffic_conditions"],
                route_summary=route_data["route_summary"],
                captured_at=datetime.now().isoformat(),
                start_lat=pending_activity["start_lat"],
                start_lng=pending_activity["start_lng"],
                end_lat=pending_activity["end_lat"],
                end_lng=pending_activity["end_lng"]
            )
            
            # Store in database
            self.store_traffic_comparison(comparison)
            
            return comparison
            
        except Exception as e:
            print(f"Error capturing traffic for pending activity: {e}")
            return None
    
    def remove_pending_activity(self, activity_id: int):
        """Remove activity from pending captures."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM pending_captures WHERE activity_id = ?', (activity_id,))
        conn.commit()
        conn.close()
    
    def increment_retry_count(self, activity_id: int):
        """Increment retry count for pending activity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE pending_captures 
            SET retry_count = retry_count + 1 
            WHERE activity_id = ?
        ''', (activity_id,))
        
        conn.commit()
        conn.close()
    
    def store_traffic_comparison(self, comparison: StoredTrafficComparison):
        """Store traffic comparison in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO traffic_comparisons 
            (activity_id, activity_name, ride_date, bike_time_minutes, car_time_minutes,
             time_saved_minutes, time_saved_percentage, distance_miles, bike_speed_mph,
             car_speed_mph, traffic_conditions, route_summary, captured_at,
             start_lat, start_lng, end_lat, end_lng)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            comparison.activity_id, comparison.activity_name, comparison.ride_date,
            comparison.bike_time_minutes, comparison.car_time_minutes,
            comparison.time_saved_minutes, comparison.time_saved_percentage,
            comparison.distance_miles, comparison.bike_speed_mph, comparison.car_speed_mph,
            comparison.traffic_conditions, comparison.route_summary, comparison.captured_at,
            comparison.start_lat, comparison.start_lng, comparison.end_lat, comparison.end_lng
        ))
        
        conn.commit()
        conn.close()
    
    def capture_traffic_for_activity(self, activity_id: int) -> Optional[StoredTrafficComparison]:
        """
        Capture traffic data for a specific activity.
        
        Args:
            activity_id: Strava activity ID
            
        Returns:
            StoredTrafficComparison object or None if failed
        """
        try:
            # Get activity details from Strava
            activity = self.strava_api.get_activity_details(activity_id)
            
            if not activity:
                print(f"❌ Could not get activity details for {activity_id}")
                return None
            
            # Extract activity data
            activity_name = activity.get("name", "Unknown Activity")
            moving_time_seconds = activity.get("moving_time", 0)
            distance_meters = activity.get("distance", 0)
            start_date = datetime.fromisoformat(activity.get("start_date", "").replace("Z", "+00:00"))
            
            # Get start and end coordinates
            start_latlng = activity.get("start_latlng")
            end_latlng = activity.get("end_latlng")
            
            if not start_latlng or not end_latlng:
                print(f"❌ No coordinates for activity {activity_id}")
                return None
            
            start_lat, start_lng = start_latlng
            end_lat, end_lng = end_latlng
            
            # Get car route time with current traffic
            route_data = self.google_maps_api.get_route_time(
                start_lat, start_lng, end_lat, end_lng, start_date
            )
            
            if "error" in route_data:
                print(f"❌ Error getting route data: {route_data['error']}")
                return None
            
            # Calculate metrics
            bike_time_minutes = moving_time_seconds / 60.0
            car_time_minutes = route_data["duration_seconds"] / 60.0
            time_saved_minutes = car_time_minutes - bike_time_minutes
            time_saved_percentage = (time_saved_minutes / car_time_minutes) * 100 if car_time_minutes > 0 else 0
            
            distance_miles = distance_meters * 0.000621371
            bike_speed_mph = distance_miles / (bike_time_minutes / 60.0) if bike_time_minutes > 0 else 0
            car_speed_mph = distance_miles / (car_time_minutes / 60.0) if car_time_minutes > 0 else 0
            
            # Create stored comparison
            comparison = StoredTrafficComparison(
                id=None,
                activity_id=activity_id,
                activity_name=activity_name,
                ride_date=start_date.isoformat(),
                bike_time_minutes=bike_time_minutes,
                car_time_minutes=car_time_minutes,
                time_saved_minutes=time_saved_minutes,
                time_saved_percentage=time_saved_percentage,
                distance_miles=distance_miles,
                bike_speed_mph=bike_speed_mph,
                car_speed_mph=car_speed_mph,
                traffic_conditions=route_data["traffic_conditions"],
                route_summary=route_data["route_summary"],
                captured_at=datetime.now().isoformat(),
                start_lat=start_lat,
                start_lng=start_lng,
                end_lat=end_lat,
                end_lng=end_lng
            )
            
            # Store in database
            self.store_traffic_comparison(comparison)
            
            return comparison
            
        except Exception as e:
            print(f"❌ Error capturing traffic for activity {activity_id}: {e}")
            return None
    
    def check_for_new_activities(self) -> List[StoredTrafficComparison]:
        """
        Check for new activities and capture traffic data.
        
        Returns:
            List of newly captured traffic comparisons
        """
        try:
            # Check internet connection first
            if not self.check_internet_connection():
                print(f"   📱 No internet connection at {datetime.now().strftime('%H:%M:%S')}")
                return []
            
            # Process any pending captures first
            processed_pending = self.process_pending_captures()
            if processed_pending > 0:
                print(f"   ✅ Processed {processed_pending} pending captures")
            
            # Get recent activities (last 24 hours)
            after_date = datetime.now() - timedelta(hours=24)
            activities = self.strava_api.get_activities(after=after_date, activity_type="Ride")
            
            if not activities:
                return []
            
            # Get last processed activity ID
            last_processed = self.get_last_processed_activity()
            
            new_comparisons = []
            
            for activity in activities:
                activity_id = activity["id"]
                
                # Skip if already processed
                if last_processed and activity_id <= last_processed:
                    continue
                
                print(f"🚴‍♂️ New activity detected: {activity.get('name', 'Unknown')}")
                print(f"   Capturing traffic data...")
                
                # Try to capture traffic data
                comparison = self.capture_traffic_for_activity(activity_id)
                
                if comparison:
                    new_comparisons.append(comparison)
                    print(f"   ✅ Traffic captured: {comparison.time_saved_minutes:.1f} minutes saved")
                else:
                    # Store for later capture if we're having connection issues
                    print(f"   📱 Storing for later capture...")
                    self.store_pending_activity(activity)
                
                # Rate limiting
                time.sleep(2)
            
            return new_comparisons
            
        except Exception as e:
            print(f"❌ Error checking for new activities: {e}")
            return []
    
    def monitor_continuously(self, check_interval: int = 300):
        """
        Continuously monitor for new activities.
        
        Args:
            check_interval: Seconds between checks (default: 5 minutes)
        """
        print(f"🚴‍♂️ Starting Strava monitor...")
        print(f"   Checking for new activities every {check_interval} seconds")
        print(f"   📱 Offline mode: Activities will be stored and processed when connection is restored")
        print(f"   Press Ctrl+C to stop")
        
        try:
            while True:
                new_comparisons = self.check_for_new_activities()
                
                if new_comparisons:
                    print(f"\n📊 Captured {len(new_comparisons)} new traffic comparisons:")
                    for comp in new_comparisons:
                        print(f"   - {comp.activity_name}: {comp.time_saved_minutes:.1f} min saved")
                else:
                    print(f"   No new activities found at {datetime.now().strftime('%H:%M:%S')}")
                
                print(f"   Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitor stopped by user")
    
    def get_all_comparisons(self) -> List[StoredTrafficComparison]:
        """Get all stored traffic comparisons."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, activity_id, activity_name, ride_date, bike_time_minutes,
                   car_time_minutes, time_saved_minutes, time_saved_percentage,
                   distance_miles, bike_speed_mph, car_speed_mph, traffic_conditions,
                   route_summary, captured_at, start_lat, start_lng, end_lat, end_lng
            FROM traffic_comparisons
            ORDER BY ride_date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        comparisons = []
        for row in rows:
            comparison = StoredTrafficComparison(
                id=row[0], activity_id=row[1], activity_name=row[2], ride_date=row[3],
                bike_time_minutes=row[4], car_time_minutes=row[5], time_saved_minutes=row[6],
                time_saved_percentage=row[7], distance_miles=row[8], bike_speed_mph=row[9],
                car_speed_mph=row[10], traffic_conditions=row[11], route_summary=row[12],
                captured_at=row[13], start_lat=row[14], start_lng=row[15], end_lat=row[16], end_lng=row[17]
            )
            comparisons.append(comparison)
        
        return comparisons

def print_stored_comparisons(comparisons: List[StoredTrafficComparison]):
    """Print stored traffic comparisons."""
    if not comparisons:
        print("No stored comparisons found.")
        return
    
    print(f"\n📊 STORED TRAFFIC COMPARISONS")
    print("=" * 60)
    print(f"Total comparisons: {len(comparisons)}")
    print("=" * 60)
    
    total_time_saved = 0
    total_distance = 0
    
    for comp in comparisons:
        ride_date = datetime.fromisoformat(comp.ride_date).strftime("%Y-%m-%d %H:%M")
        captured_date = datetime.fromisoformat(comp.captured_at).strftime("%Y-%m-%d %H:%M")
        
        print(f"\n📅 {ride_date} - {comp.activity_name}")
        print(f"   Distance: {comp.distance_miles:.2f} miles")
        print(f"   Bike: {comp.bike_time_minutes:.1f} min ({comp.bike_speed_mph:.1f} mph)")
        print(f"   Car: {comp.car_time_minutes:.1f} min ({comp.car_speed_mph:.1f} mph)")
        print(f"   Traffic: {comp.traffic_conditions}")
        print(f"   Route: {comp.route_summary}")
        
        if comp.time_saved_minutes > 0:
            print(f"   ✅ Saved {comp.time_saved_minutes:.1f} minutes ({comp.time_saved_percentage:.1f}%)")
        else:
            print(f"   ⏰ Car was {abs(comp.time_saved_minutes):.1f} minutes faster")
        
        print(f"   📊 Captured: {captured_date}")
        
        total_time_saved += comp.time_saved_minutes
        total_distance += comp.distance_miles
    
    print(f"\n📈 OVERALL SUMMARY")
    print("=" * 30)
    print(f"Total distance: {total_distance:.1f} miles")
    print(f"Total time saved: {total_time_saved:.1f} minutes")
    if total_time_saved > 0:
        print(f"🚴‍♂️ You've saved {total_time_saved:.1f} minutes by biking!")

# Example usage functions
def start_monitor(strava_client_id: str, strava_client_secret: str, 
                 strava_access_token: str, google_maps_api_key: str):
    """Start the continuous monitor."""
    from strava_brake_wear_estimator import StravaAPI
    
    # Initialize APIs
    strava_api = StravaAPI(strava_client_id, strava_client_secret, strava_access_token)
    google_maps_api = GoogleMapsAPI(google_maps_api_key)
    
    # Create monitor
    monitor = StravaMonitor(strava_api, google_maps_api)
    
    # Start monitoring
    monitor.monitor_continuously()

def view_stored_comparisons(strava_client_id: str, strava_client_secret: str, 
                           strava_access_token: str, google_maps_api_key: str):
    """View all stored traffic comparisons."""
    from strava_brake_wear_estimator import StravaAPI
    
    # Initialize APIs
    strava_api = StravaAPI(strava_client_id, strava_client_secret, strava_access_token)
    google_maps_api = GoogleMapsAPI(google_maps_api_key)
    
    # Create monitor
    monitor = StravaMonitor(strava_api, google_maps_api)
    
    # Get and display comparisons
    comparisons = monitor.get_all_comparisons()
    print_stored_comparisons(comparisons)

if __name__ == "__main__":
    print("Strava Activity Monitor")
    print("This module provides continuous monitoring of Strava activities")
    print("and captures traffic data when rides are finished.")
    print("Enhanced with offline support and connection resilience.")
    print("\nUse start_monitor() to begin continuous monitoring")
    print("Use view_stored_comparisons() to view captured data") 