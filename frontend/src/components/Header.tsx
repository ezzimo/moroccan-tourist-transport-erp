import React from 'react';
import { Bell, LogOut, Menu } from 'lucide-react';
import { useAuth } from '../auth/context/AuthContext';

export default function Header() {
  const { state, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <button className="lg:hidden p-2 rounded-lg hover:bg-gray-100">
            <Menu className="h-5 w-5" />
          </button>
          <h2 className="ml-2 text-xl font-semibold text-gray-900 lg:ml-0">
            Welcome back!
          </h2>
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
            <Bell className="h-5 w-5" />
          </button>
          
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {state.user?.full_name || 'User'}
              </p>
              <p className="text-xs text-gray-500">{state.user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-gray-100 transition-colors"
              title="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}