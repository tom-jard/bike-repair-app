#!/usr/bin/env python3
"""
Simple Strava Access Token Helper

This script helps you get your Strava access token for the brake wear estimator.
"""

import webbrowser
import requests
import json

def get_strava_token():
    """Get Strava access token through OAuth flow."""
    
    print("🚴‍♂️ Strava Access Token Setup")
    print("=" * 40)
    
    # Get credentials from user
    client_id = input("Enter your Strava Client ID: ").strip()
    client_secret = input("Enter your Strava Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required!")
        return None
    
    # Step 1: Get authorization URL
    print("\n🔐 Step 1: Authorize Application")
    print("-" * 30)
    
    auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all"
    
    print("Opening Strava authorization page...")
    try:
        webbrowser.open(auth_url)
    except:
        print(f"Please manually visit: {auth_url}")
    
    print("\nAfter authorizing, you'll be redirected to a URL like:")
    print("http://localhost?state=&code=YOUR_AUTHORIZATION_CODE")
    print("Copy the 'code' parameter value (everything after 'code=')")
    
    authorization_code = input("\nEnter the authorization code: ").strip()
    
    if not authorization_code:
        print("❌ Authorization code is required!")
        return None
    
    # Step 2: Exchange code for access token
    print("\n🔄 Step 2: Getting Access Token")
    print("-" * 30)
    
    url = "https://www.strava.com/oauth/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": authorization_code,
        "grant_type": "authorization_code"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            refresh_token = token_data.get("refresh_token", "")
            
            print(f"✅ Success! Access token: {access_token[:20]}...")
            
            # Save to config file
            print("\n💾 Saving to config.py...")
            update_config_file(client_id, client_secret, access_token)
            
            return access_token
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None

def update_config_file(client_id, client_secret, access_token):
    """Update config.py with the new credentials."""
    
    try:
        # Read current config
        with open('config.py', 'r') as f:
            config_content = f.read()
        
        # Replace placeholder values
        config_content = config_content.replace('"your_strava_client_id_here"', f'"{client_id}"')
        config_content = config_content.replace('"your_strava_client_secret_here"', f'"{client_secret}"')
        config_content = config_content.replace('"your_strava_access_token_here"', f'"{access_token}"')
        
        # Write updated config
        with open('config.py', 'w') as f:
            f.write(config_content)
        
        print("✅ Config file updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating config file: {e}")
        print("Please manually update config.py with:")
        print(f"STRAVA_CLIENT_ID = \"{client_id}\"")
        print(f"STRAVA_CLIENT_SECRET = \"{client_secret}\"")
        print(f"STRAVA_ACCESS_TOKEN = \"{access_token}\"")

def test_connection():
    """Test the Strava API connection."""
    
    try:
        from config import STRAVA_ACCESS_TOKEN
        
        if STRAVA_ACCESS_TOKEN == "your_strava_access_token_here":
            print("❌ Access token not configured yet!")
            return False
        
        headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}
        url = "https://www.strava.com/api/v3/athlete"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            athlete_data = response.json()
            print(f"✅ Connected successfully!")
            print(f"   Athlete: {athlete_data.get('firstname', '')} {athlete_data.get('lastname', '')}")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    """Main function."""
    
    print("Welcome to the Strava API Setup!")
    print("This will help you get your access token for the brake wear estimator.\n")
    
    # Check if already configured
    try:
        from config import STRAVA_ACCESS_TOKEN
        if STRAVA_ACCESS_TOKEN != "your_strava_access_token_here":
            print("✅ Strava API already configured!")
            test = input("Test connection? (y/n): ").strip().lower()
            if test == 'y':
                test_connection()
            return
    except:
        pass
    
    # Get new token
    token = get_strava_token()
    
    if token:
        print("\n🎉 Setup complete!")
        print("You can now use the Strava-integrated brake wear estimator.")
        
        test = input("\nTest connection? (y/n): ").strip().lower()
        if test == 'y':
            test_connection()
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main() 