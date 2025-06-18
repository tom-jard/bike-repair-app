#!/usr/bin/env python3
"""
Mac Mini Service Startup Script

This script starts both the Strava monitor and web dashboard
for continuous operation on a Mac Mini.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from datetime import datetime

class MacMiniService:
    """Manages the Strava monitor and web dashboard services."""
    
    def __init__(self):
        self.monitor_process = None
        self.dashboard_process = None
        self.running = False
        
    def start_monitor(self):
        """Start the Strava monitor in a separate process."""
        print("🚴‍♂️ Starting Strava monitor...")
        try:
            self.monitor_process = subprocess.Popen([
                sys.executable, "run_monitor.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"   ✅ Monitor started (PID: {self.monitor_process.pid})")
            return True
        except Exception as e:
            print(f"   ❌ Failed to start monitor: {e}")
            return False
    
    def start_dashboard(self):
        """Start the web dashboard in a separate process."""
        print("🌐 Starting web dashboard...")
        try:
            self.dashboard_process = subprocess.Popen([
                sys.executable, "web_dashboard.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"   ✅ Dashboard started (PID: {self.dashboard_process.pid})")
            return True
        except Exception as e:
            print(f"   ❌ Failed to start dashboard: {e}")
            return False
    
    def stop_services(self):
        """Stop all running services."""
        print("\n🛑 Stopping services...")
        
        if self.monitor_process:
            print(f"   Stopping monitor (PID: {self.monitor_process.pid})")
            self.monitor_process.terminate()
            try:
                self.monitor_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.monitor_process.kill()
        
        if self.dashboard_process:
            print(f"   Stopping dashboard (PID: {self.dashboard_process.pid})")
            self.dashboard_process.terminate()
            try:
                self.dashboard_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
        
        print("   ✅ All services stopped")
    
    def check_processes(self):
        """Check if processes are still running."""
        if self.monitor_process and self.monitor_process.poll() is not None:
            print("⚠️  Monitor process has stopped unexpectedly")
            return False
        
        if self.dashboard_process and self.dashboard_process.poll() is not None:
            print("⚠️  Dashboard process has stopped unexpectedly")
            return False
        
        return True
    
    def log_status(self):
        """Log current status."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        monitor_status = "Running" if self.monitor_process and self.monitor_process.poll() is None else "Stopped"
        dashboard_status = "Running" if self.dashboard_process and self.dashboard_process.poll() is None else "Stopped"
        
        print(f"[{timestamp}] Monitor: {monitor_status}, Dashboard: {dashboard_status}")
    
    def run(self):
        """Main service loop."""
        print("🚀 Mac Mini Strava Traffic Monitor Service")
        print("=" * 50)
        print("This service will run continuously and restart if needed.")
        print("Press Ctrl+C to stop all services.")
        print()
        
        # Start services
        if not self.start_monitor():
            print("❌ Failed to start monitor. Exiting.")
            return
        
        if not self.start_dashboard():
            print("❌ Failed to start dashboard. Exiting.")
            self.stop_services()
            return
        
        self.running = True
        
        # Main loop
        try:
            while self.running:
                # Check if processes are still running
                if not self.check_processes():
                    print("🔄 Restarting failed services...")
                    
                    if self.monitor_process and self.monitor_process.poll() is not None:
                        self.start_monitor()
                    
                    if self.dashboard_process and self.dashboard_process.poll() is not None:
                        self.start_dashboard()
                
                # Log status every 5 minutes
                if int(time.time()) % 300 == 0:
                    self.log_status()
                
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Received stop signal...")
            self.running = False
            self.stop_services()

def get_mac_mini_ip():
    """Get the Mac Mini's IP address for network access."""
    try:
        import socket
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def main():
    """Main function."""
    print("🚀 Starting Mac Mini Strava Traffic Monitor Service")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("config.py"):
        print("❌ Error: config.py not found!")
        print("   Make sure you're running this from the Bike Repair App directory.")
        return
    
    # Show network access info
    ip_address = get_mac_mini_ip()
    print(f"📱 Network Access:")
    print(f"   Local: http://localhost:5000")
    print(f"   Network: http://{ip_address}:5000")
    print(f"   (Other devices on your network can access the dashboard)")
    print()
    
    # Create and run service
    service = MacMiniService()
    
    # Set up signal handlers
    def signal_handler(signum, frame):
        print("\n🛑 Received signal to stop...")
        service.running = False
        service.stop_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the service
    service.run()

if __name__ == "__main__":
    main() 