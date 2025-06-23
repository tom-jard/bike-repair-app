import { Activity, Clock, TrendingUp, Info } from 'lucide-react';
import stravaService from '../services/stravaService.js';

export default function LoginScreen() {
  const handleLogin = () => {
    // In demo mode, simulate the OAuth flow by redirecting to our callback
    window.location.href = stravaService.getAuthUrl();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-lg w-full">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="bg-orange-100 p-3 rounded-full">
              <Activity className="h-8 w-8 text-orange-600" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Strava Time Savings
          </h1>
          <p className="text-gray-600">
            Discover how much time you save by biking instead of driving
          </p>
        </div>

        {/* Demo Mode Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-blue-800">Demo Mode</h3>
              <p className="text-sm text-blue-700 mt-1">
                This demo uses realistic sample data from San Francisco Bay Area rides. 
                No external connections are made - everything runs locally in your browser.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-4 mb-8">
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <Clock className="h-5 w-5 text-blue-500" />
            <div>
              <h3 className="font-medium text-gray-800">Time Comparison</h3>
              <p className="text-sm text-gray-600">Compare bike rides to estimated car travel times</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <TrendingUp className="h-5 w-5 text-green-500" />
            <div>
              <h3 className="font-medium text-gray-800">Traffic Analysis</h3>
              <p className="text-sm text-gray-600">Smart algorithms factor in traffic patterns and parking time</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <Activity className="h-5 w-5 text-orange-500" />
            <div>
              <h3 className="font-medium text-gray-800">Sample Data</h3>
              <p className="text-sm text-gray-600">Realistic ride data with GPS coordinates and traffic analysis</p>
            </div>
          </div>
        </div>

        <button
          onClick={handleLogin}
          className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
        >
          <span>Try Demo</span>
        </button>

        <p className="text-xs text-gray-500 text-center mt-4">
          Demo mode - no real data is accessed. Perfect for exploring the app's features safely.
        </p>
      </div>
    </div>
  );
}