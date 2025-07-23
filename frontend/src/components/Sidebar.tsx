import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Home, Users, MessageSquare, Star, BarChart3, User, Building2, Truck, UserCheck, DollarSign, Calendar, MapPin, CheckCircle, UserCog, Package, Bell } from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Customers', href: '/customers', icon: Users },
  { name: 'Interactions', href: '/interactions', icon: MessageSquare },
  { name: 'Feedback', href: '/feedback', icon: Star },
  { name: 'Segments', href: '/segments', icon: BarChart3 },
  { name: 'Fleet', href: '/fleet', icon: Truck },
  { name: 'Drivers', href: '/drivers', icon: UserCheck },
  { name: 'Finance', href: '/finance', icon: DollarSign },
  { name: 'Bookings', href: '/bookings', icon: Calendar },
  { name: 'Tours', href: '/tours', icon: MapPin },
  { name: 'QA & Compliance', href: '/qa', icon: CheckCircle },
  { name: 'Human Resources', href: '/hr/employees', icon: UserCog },
  { name: 'Inventory', href: '/inventory/items', icon: Package },
  { name: 'Notifications', href: '/notifications', icon: Bell },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <div className="hidden lg:flex lg:flex-shrink-0">
      <div className="flex flex-col w-64">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200 overflow-y-auto">
          {/* Logo */}
          <div className="flex items-center flex-shrink-0 px-6 py-6 border-b border-gray-200">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
                <Building2 className="h-5 w-5 text-white" />
              </div>
              <div className="ml-3">
                <h1 className="text-lg font-semibold text-gray-900">Transport ERP</h1>
                <p className="text-xs text-gray-500">Moroccan Tourism</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 flex flex-col pt-6">
            <nav className="flex-1 px-4 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href || 
                  (item.href !== '/dashboard' && location.pathname.startsWith(item.href));
                
                return (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? 'bg-orange-100 text-orange-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon
                      className={`mr-3 h-5 w-5 flex-shrink-0 ${
                        isActive ? 'text-orange-500' : 'text-gray-400 group-hover:text-gray-500'
                      }`}
                    />
                    {item.name}
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {/* User section */}
          <div className="flex-shrink-0 border-t border-gray-200 p-4">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-gray-500" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">Admin User</p>
                <p className="text-xs text-gray-500">admin@example.com</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}