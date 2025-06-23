import { useState, useEffect } from 'react';
import { LogOut, RefreshCw, Clock, Car, Bike, TrendingUp, Calendar, MapPin, User, AlertCircle, Info } from 'lucide-react';
import stravaService from '../services/stravaService.js';
import travelTimeService from '../services/travelTimeService.js';

export default function Dashboard() {
  const [activities, setActivities] = useState([]);
  const [athlete, setAthlete] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [tokenInfo, setTokenInfo] = useState(null);
  const [stats, setStats] = useState({
    totalRides: 0,
    totalTimeSaved: 0,
    averageTimeSaved: 0,
    totalDistance: 0
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get token info
      const tokenInfo = stravaService.getTokenInfo();
      setTokenInfo(tokenInfo);
      
      // Load athlete data
      const athleteData = await stravaService.getAthlete();
      setAthlete(athleteData);
      
      // Load activities
      await loadActivities();
      
    } catch (err) {
      console.error('Error loading initial data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadActivities = async () => {
    try {
      setError(null);
      
      const rides = await stravaService.getActivities(1, 50);
      
      // Filter rides that have coordinates
      const ridesWithCoords = rides.filter(ride => 
        ride.startCoords && ride.endCoords && 
        ride.startCoords.length === 2 && ride.endCoords.length === 2 &&
        ride.distance > 500 // Filter out very short rides (less than 500m)
      );

      setActivities(ridesWithCoords.map(ride => ({
        ...ride,
        carTravelTime: null,
        timeSaved: null,
        analyzing: false,
        error: null
      })));

    } catch (err) {
      console.error('Error loading activities:', err);
      setError(err.message);
    }
  };

  const analyzeActivity = async (activityId) => {
    setActivities(prev => prev.map(activity => 
      activity.id === activityId 
        ? { ...activity, analyzing: true, error: null }
        : activity
    ));

    try {
      const activity = activities.find(a => a.id === activityId);
      
      const carData = await travelTimeService.getCarTravelTime(
        activity.startCoords,
        activity.endCoords,
        activity.date
      );

      const bikeTimeMinutes = activity.movingTime / 60;
      const carTimeMinutes = carData.duration / 60;
      const timeSaved = carTimeMinutes - bikeTimeMinutes;

      setActivities(prev => prev.map(a => 
        a.id === activityId 
          ? { 
              ...a, 
              carTravelTime: carData,
              timeSaved: timeSaved,
              analyzing: false 
            }
          : a
      ));

      updateStats();

    } catch (err) {
      console.error('Error analyzing activity:', err);
      setActivities(prev => prev.map(activity => 
        activity.id === activityId 
          ? { ...activity, analyzing: false, error: err.message }
          : activity
      ));
    }
  };

  const analyzeAll = async () => {
    setAnalyzing(true);
    
    const unanalyzedActivities = activities.filter(a => !a.carTravelTime && !a.analyzing);
    
    for (const activity of unanalyzedActivities) {
      await analyzeActivity(activity.id);
      // Add delay to respect rate limits
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    setAnalyzing(false);
  };

  const updateStats = () => {
    const analyzedActivities = activities.filter(a => a.timeSaved !== null);
    
    if (analyzedActivities.length === 0) return;

    const totalTimeSaved = analyzedActivities.reduce((sum, a) => sum + a.timeSaved, 0);
    const totalDistance = analyzedActivities.reduce((sum, a) => sum + (a.distance / 1000), 0); // Convert to km
    
    setStats({
      totalRides: analyzedActivities.length,
      totalTimeSaved: Math.round(totalTimeSaved),
      averageTimeSaved: Math.round(totalTimeSaved / analyzedActivities.length),
      totalDistance: Math.round(totalDistance)
    });
  };

  useEffect(() => {
    updateStats();
  }, [activities]);

  const formatTime = (seconds) => {
    const minutes = Math.round(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  const formatDistance = (meters) => {
    const km = meters / 1000;
    return km < 10 ? `${km.toFixed(1)}km` : `${Math.round(km)}km`;
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      weekday: 'short'
    });
  };

  const getTimeSavedColor = (timeSaved) => {
    if (timeSaved > 0) return 'text-green-600 bg-green-50';
    if (timeSaved < 0) return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getTrafficBadgeColor = (condition) => {
    switch (condition) {
      case 'light': return 'bg-green-100 text-green-800';
      case 'moderate': return 'bg-yellow-100 text-yellow-800';
      case 'heavy': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your rides...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-orange-100 p-2 rounded-lg">
                <Bike className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Strava Time Savings</h1>
                {athlete && (
                  <p className="text-sm text-gray-600">
                    Welcome back, {athlete.firstname}!
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {tokenInfo && tokenInfo.isDemoMode && (
                <div className="flex items-center space-x-1 text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                  <Info className="h-3 w-3" />
                  <span>Demo Mode</span>
                </div>
              )}
              
              {tokenInfo && tokenInfo.expiresAt && (
                <div className="text-xs text-gray-500">
                  Token expires: {tokenInfo.expiresAt.toLocaleDateString()}
                </div>
              )}
              
              <button
                onClick={loadActivities}
                disabled={loading}
                className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
              
              <button
                onClick={() => {
                  stravaService.logout();
                  window.location.reload();
                }}
                className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Demo Mode Notice */}
        {tokenInfo && tokenInfo.isDemoMode && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-blue-800">Demo Mode Active</h3>
                <p className="text-sm text-blue-700 mt-1">
                  You're viewing sample data. To connect to real Strava data, you'll need to set up proper server-side authentication. 
                  The current implementation shows how the app would work with real data.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Athlete Info */}
        {athlete && (
          <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
            <div className="flex items-center space-x-4">
              <div className="bg-orange-100 p-3 rounded-full">
                <User className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {athlete.firstname} {athlete.lastname}
                </h2>
                <p className="text-gray-600">
                  {athlete.city && athlete.state && `${athlete.city}, ${athlete.state}`}
                  {athlete.country && ` • ${athlete.country}`}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        {stats.totalRides > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <Bike className="h-5 w-5 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Analyzed Rides</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.totalRides}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center">
                <div className="bg-green-100 p-2 rounded-lg">
                  <Clock className="h-5 w-5 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Time Saved</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.totalTimeSaved}m</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center">
                <div className="bg-purple-100 p-2 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Avg Time Saved</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.averageTimeSaved}m</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center">
                <div className="bg-orange-100 p-2 rounded-lg">
                  <MapPin className="h-5 w-5 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Distance</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.totalDistance}km</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Recent Rides</h2>
          
          {activities.length > 0 && (
            <button
              onClick={analyzeAll}
              disabled={analyzing}
              className="flex items-center space-x-2 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              {analyzing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4" />
                  <span>Analyze All</span>
                </>
              )}
            </button>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center space-x-3">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Activities List */}
        {activities.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Bike className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No rides found</h3>
            <p className="text-gray-600 mb-4">
              {tokenInfo?.isDemoMode 
                ? "Demo data is loading. In real mode, your recent rides with GPS coordinates would appear here."
                : "We couldn't find any recent rides with GPS coordinates."
              }
            </p>
            <button
              onClick={loadActivities}
              className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Refresh Activities
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {activities.map((activity) => (
              <div key={activity.id} className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{activity.name}</h3>
                      {activity.carTravelTime && (
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTrafficBadgeColor(activity.carTravelTime.trafficCondition)}`}>
                          {activity.carTravelTime.trafficCondition} traffic
                        </span>
                      )}
                      {activity.carTravelTime && (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {activity.carTravelTime.source === 'google_maps' ? 'Google Maps' : 'Estimated'}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(activity.date)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MapPin className="h-4 w-4" />
                        <span>{formatDistance(activity.distance)}</span>
                      </div>
                      {activity.elevationGain > 0 && (
                        <div className="flex items-center space-x-1">
                          <TrendingUp className="h-4 w-4" />
                          <span>{Math.round(activity.elevationGain)}m elevation</span>
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Bike Time */}
                      <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                        <Bike className="h-5 w-5 text-blue-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-600">Bike Time</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {formatTime(activity.movingTime)}
                          </p>
                        </div>
                      </div>

                      {/* Car Time */}
                      <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <Car className="h-5 w-5 text-gray-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-600">Car Time</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {activity.carTravelTime 
                              ? formatTime(activity.carTravelTime.duration)
                              : '—'
                            }
                          </p>
                        </div>
                      </div>

                      {/* Time Saved */}
                      <div className={`flex items-center space-x-3 p-3 rounded-lg ${activity.timeSaved !== null ? getTimeSavedColor(activity.timeSaved) : 'bg-gray-50'}`}>
                        <Clock className="h-5 w-5" />
                        <div>
                          <p className="text-sm font-medium">Time Saved</p>
                          <p className="text-lg font-semibold">
                            {activity.timeSaved !== null 
                              ? `${activity.timeSaved > 0 ? '+' : ''}${Math.round(activity.timeSaved)}m`
                              : '—'
                            }
                          </p>
                        </div>
                      </div>
                    </div>

                    {activity.error && (
                      <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
                        <AlertCircle className="h-4 w-4 text-red-600" />
                        <p className="text-sm text-red-800">{activity.error}</p>
                      </div>
                    )}
                  </div>

                  {/* Analyze Button */}
                  {!activity.carTravelTime && !activity.analyzing && (
                    <button
                      onClick={() => analyzeActivity(activity.id)}
                      className="ml-4 bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                      Analyze
                    </button>
                  )}

                  {activity.analyzing && (
                    <div className="ml-4 flex items-center space-x-2 text-orange-600">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-600"></div>
                      <span className="text-sm font-medium">Analyzing...</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}