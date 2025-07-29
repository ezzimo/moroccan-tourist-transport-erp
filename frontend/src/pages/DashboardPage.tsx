import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, DollarSign, MapPin, CheckCircle, UserCog, Package } from 'lucide-react';
import { ArrowRight, Truck, UserCheck, Bell, Shield } from 'lucide-react';
import { useCustomers } from '../crm/hooks/useCustomers';
import { useFeedbackStats } from '../crm/hooks/useFeedback';
import { useVehicles } from '../fleet/hooks/useVehicles';
import { useDrivers } from '../driver/hooks/useDrivers';
import { useFinancialDashboard } from '../finance/hooks/useAnalytics';
import { useBookings } from '../booking/hooks/useBookings';
import { useFeaturedTourTemplates } from '../tour/hooks/useTourTemplates';
import { useActiveTours } from '../tour/hooks/useTourInstances';
import { useQADashboard } from '../qa/hooks/useCertifications';
import { useHRDashboard } from '../hr/hooks/useAnalytics';
import { useInventoryDashboard } from '../inventory/hooks/useAnalytics';
import { useNotificationStats } from '../notification/hooks/useNotifications';
import { useAuth } from '../auth/context/AuthContext';
import AdminUserManagement from '../auth/components/AdminUserManagement';
import LoadingSpinner from '../components/LoadingSpinner';

export default function DashboardPage() {
  console.log('🔧 DashboardPage: Component initializing');
  
  const { isAdmin, hasPermission, state: authState } = useAuth();
  const { data: customersData, isLoading: customersLoading } = useCustomers({ size: 5 });
  const { data: feedbackStats, isLoading: statsLoading } = useFeedbackStats(30);
  const { data: vehiclesData, isLoading: vehiclesLoading } = useVehicles({ size: 5 });
  const { data: driversData, isLoading: driversLoading } = useDrivers({ size: 5 });
  const { data: financialData, isLoading: financialLoading } = useFinancialDashboard();
  const { data: bookingsData, isLoading: bookingsLoading } = useBookings({ size: 5 });
  const { data: featuredTemplates, isLoading: templatesLoading } = useFeaturedTourTemplates(5);
  const { data: activeTours, isLoading: toursLoading } = useActiveTours();
  const { data: qaDashboard, isLoading: qaLoading } = useQADashboard();
  const { data: hrDashboard, isLoading: hrLoading } = useHRDashboard();
  const { data: inventoryDashboard, isLoading: inventoryLoading } = useInventoryDashboard();
  const { data: notificationStats, isLoading: notificationLoading } = useNotificationStats(30);

  // Check if user can access user management
  const canManageUsers = isAdmin || hasPermission('auth', 'read', 'users');

  console.log('🔧 DashboardPage: Auth state', {
    isAdmin,
    canManageUsers,
    userEmail: authState.user?.email,
    userRoles: authState.user?.roles?.map(r => r.name),
    permissions: authState.user?.permissions?.slice(0, 5) // Log first 5 permissions
  });

  const stats = [
    {
      name: 'Total Customers',
      value: customersData?.total ?? 0,
      icon: Users,
      color: 'text-blue-600 bg-blue-100',
      href: '/customers',
    },
    {
      name: 'Fleet Vehicles',
      value: vehiclesData?.total ?? 0,
      icon: Truck,
      color: 'text-orange-600 bg-orange-100',
      href: '/fleet',
    },
    {
      name: 'Active Drivers',
      value: driversData?.items?.filter(d => d.status === 'Active').length ?? 0,
      icon: UserCheck,
      color: 'text-green-600 bg-green-100',
      href: '/drivers',
    },
    {
      name: 'Monthly Revenue',
      value: financialData ? `${(financialData.total_revenue_mtd / 1000).toFixed(0)}K` : '0',
      icon: DollarSign,
      color: 'text-green-600 bg-green-100',
      href: '/finance',
    },
    {
      name: 'Active Bookings',
      value: bookingsData?.items?.filter(b => b.status === 'Confirmed').length ?? 0,
      icon: Calendar,
      color: 'text-purple-600 bg-purple-100',
      href: '/bookings',
    },
    {
      name: 'Tour Templates',
      value: featuredTemplates?.length ?? 0,
      icon: MapPin,
      color: 'text-purple-600 bg-purple-100',
      href: '/tours',
    },
    {
      name: 'Active Tours',
      value: activeTours?.length ?? 0,
      icon: MapPin,
      color: 'text-indigo-600 bg-indigo-100',
      href: '/tours/instances',
    },
    {
      name: 'QA Audits',
      value: qaDashboard?.audit_summary?.total_audits ?? 0,
      icon: CheckCircle,
      color: 'text-teal-600 bg-teal-100',
      href: '/qa',
    },
    {
      name: 'Total Employees',
      value: hrDashboard?.total_employees ?? 0,
      icon: UserCog,
      color: 'text-purple-600 bg-purple-100',
      href: '/hr/employees',
    },
    {
      name: 'Inventory Items',
      value: inventoryDashboard?.total_items ?? 0,
      icon: Package,
      color: 'text-indigo-600 bg-indigo-100',
      href: '/inventory/items',
    },
    {
      name: 'Notifications Sent',
      value: notificationStats?.total_notifications ?? 0,
      icon: Bell,
      color: 'text-purple-600 bg-purple-100',
      href: '/notifications',
    },
  ];

  if (customersLoading || statsLoading || vehiclesLoading || driversLoading || financialLoading || bookingsLoading || templatesLoading || toursLoading || qaLoading || hrLoading || inventoryLoading || notificationLoading) {
    console.log('🔧 DashboardPage: Still loading data');
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  console.log('🔧 DashboardPage: Rendering dashboard', {
    statsCount: stats.length,
    showAdminSection: canManageUsers
  });

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Welcome to Transport ERP</h1>
        <p className="text-orange-100">
          Manage your Moroccan tourist transport operations with ease
        </p>
        {isAdmin && (
          <div className="mt-3 flex items-center text-orange-100">
            <Shield className="h-4 w-4 mr-2" />
            <span className="text-sm">Administrator Access</span>
          </div>
        )}
      </div>

      {/* Admin User Management Section */}
      {canManageUsers && (
        <div className="bg-white rounded-lg border p-6">
          <AdminUserManagement />
        </div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Link
              key={stat.name}
              to={stat.href}
              className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
              </div>
            </Link>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Customers */}
        <div className="bg-white rounded-lg border">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Recent Customers</h3>
              <Link
                to="/customers"
                className="text-sm text-orange-600 hover:text-orange-700"
              >
                View all
              </Link>
            </div>
          </div>
          <div className="p-6">
            {customersData?.items?.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No customers yet</p>
            ) : (
              <div className="space-y-3">
                {customersData?.items?.slice(0, 5).map((customer) => (
                  <Link
                    key={customer.id}
                    to={`/customers/${customer.id}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div>
                      <p className="font-medium text-gray-900">
                        {customer.full_name || customer.company_name || 'Unnamed Customer'}
                      </p>
                      <p className="text-sm text-gray-500">{customer.email}</p>
                    </div>
                    <span className="text-xs text-gray-400">
                      {customer.last_interaction 
                        ? new Date(customer.last_interaction).toLocaleDateString()
                        : 'No interactions'
                      }
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Fleet Overview */}
        <div className="bg-white rounded-lg border">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Fleet Overview</h3>
              <Link
                to="/fleet"
                className="text-sm text-orange-600 hover:text-orange-700"
              >
                View all
              </Link>
            </div>
          </div>
          <div className="p-6">
            {vehiclesData?.items?.length ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Vehicles</span>
                  <span className="font-medium">{vehiclesData.total}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Available</span>
                  <span className="font-medium text-green-600">
                    {vehiclesData.items.filter(v => v.status === 'Available').length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">In Use</span>
                  <span className="font-medium text-blue-600">
                    {vehiclesData.items.filter(v => v.status === 'In Use').length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Maintenance</span>
                  <span className="font-medium text-yellow-600">
                    {vehiclesData.items.filter(v => v.status === 'Under Maintenance').length}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No vehicles in fleet</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Access Links */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Link
            to="/customers"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <Users className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Manage Customers</p>
              <p className="text-sm text-gray-500">View and edit customer profiles</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors ml-auto" />
          </Link>
          
          <Link
            to="/fleet"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <Truck className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Fleet Management</p>
              <p className="text-sm text-gray-500">Manage vehicles and maintenance</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors ml-auto" />
          </Link>
          
          <Link
            to="/drivers"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <UserCheck className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Driver Management</p>
              <p className="text-sm text-gray-500">Manage driver assignments</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors ml-auto" />
          </Link>
          
          <Link
            to="/finance"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <DollarSign className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Financial Management</p>
              <p className="text-sm text-gray-500">Invoices, payments, and reports</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors ml-auto" />
          </Link>
          
          <Link
            to="/tours"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <MapPin className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Tour Operations</p>
              <p className="text-sm text-gray-500">Manage tours and templates</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors ml-auto" />
          </Link>
          
          <Link
            to="/qa"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <CheckCircle className="h-8 w-8 text-teal-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">QA & Compliance</p>
              <p className="text-sm text-gray-500">Quality assurance and compliance</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors ml-auto" />
          </Link>
          
          <Link
            to="/hr/employees"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <UserCog className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Human Resources</p>
              <p className="text-sm text-gray-500">Manage employees and training</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors ml-auto" />
          </Link>
          
          <Link
            to="/inventory/items"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <Package className="h-8 w-8 text-indigo-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Inventory Management</p>
              <p className="text-sm text-gray-500">Manage stock and suppliers</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors ml-auto" />
          </Link>
          
          <Link
            to="/bookings"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <Calendar className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Booking Management</p>
              <p className="text-sm text-gray-500">Manage reservations and bookings</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 transition-colors ml-auto" />
          </Link>

          {/* Admin User Management Quick Action */}
          {canManageUsers && (
            <Link
              to="/admin/users"
              className="flex items-center p-4 border border-blue-200 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors group"
            >
              <Shield className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="font-medium text-blue-900">User Management</p>
                <p className="text-sm text-blue-700">Manage users and permissions</p>
              </div>
              <ArrowRight className="h-5 w-5 text-blue-400 group-hover:text-blue-600 transition-colors ml-auto" />
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}