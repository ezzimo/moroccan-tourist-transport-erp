import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <div className="mx-auto h-24 w-24 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mb-6">
            <span className="text-4xl font-bold text-white">404</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Page Not Found</h1>
          <p className="text-gray-600">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        <div className="space-y-4">
          <Link
            to="/dashboard"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 transition-all"
          >
            <Home className="h-5 w-5 mr-2" />
            Go to Dashboard
          </Link>
          
          <div className="text-sm text-gray-500">
            <button
              onClick={() => window.history.back()}
              className="inline-flex items-center text-orange-600 hover:text-orange-700"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Go back
            </button>
          </div>
        </div>

        <div className="mt-8 text-xs text-gray-400">
          <p>Moroccan Tourist Transport ERP System</p>
        </div>
      </div>
    </div>
  );
}