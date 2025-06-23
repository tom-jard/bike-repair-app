import { useEffect, useState } from 'react';
import stravaService from '../services/stravaService.js';

export default function AuthCallback({ onAuthComplete }) {
  const [status, setStatus] = useState('processing');
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const error = urlParams.get('error');

        if (error) {
          throw new Error(`Authentication failed: ${error}`);
        }

        if (!code) {
          throw new Error('No authorization code received');
        }

        setStatus('exchanging');
        
        // Simulate the token exchange process
        await stravaService.exchangeToken(code);
        
        setStatus('success');
        
        // Clear URL parameters
        window.history.replaceState({}, document.title, window.location.pathname);
        
        // Notify parent component
        setTimeout(() => {
          onAuthComplete(true);
        }, 1500);

      } catch (err) {
        console.error('Auth callback error:', err);
        setError(err.message);
        setStatus('error');
      }
    };

    handleCallback();
  }, [onAuthComplete]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full text-center">
        {status === 'processing' && (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Setting Up Demo</h2>
            <p className="text-gray-600">Preparing your demo experience...</p>
          </>
        )}

        {status === 'exchanging' && (
          <>
            <div className="animate-pulse">
              <div className="h-12 w-12 bg-orange-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-orange-600 text-2xl">🎭</span>
              </div>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Loading Sample Data</h2>
            <p className="text-gray-600">Generating realistic ride data for demonstration...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="h-12 w-12 bg-green-100 rounded-full mx-auto mb-4 flex items-center justify-center">
              <span className="text-green-600 text-2xl">✅</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Demo Ready!</h2>
            <p className="text-gray-600">Taking you to your dashboard...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="h-12 w-12 bg-red-100 rounded-full mx-auto mb-4 flex items-center justify-center">
              <span className="text-red-600 text-2xl">❌</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Demo Setup Failed</h2>
            <p className="text-red-600 text-sm mb-4">{error}</p>
            <button
              onClick={() => onAuthComplete(false)}
              className="bg-orange-500 hover:bg-orange-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Try Again
            </button>
          </>
        )}
      </div>
    </div>
  );
}