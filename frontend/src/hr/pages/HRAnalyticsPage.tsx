import React from 'react';
import { Users, TrendingUp, Award, Clock } from 'lucide-react';
import { useHRDashboard } from '../hooks/useAnalytics';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function HRAnalyticsPage() {
  const { data: dashboard, isLoading } = useHRDashboard();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Failed to load HR analytics</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">HR Analytics</h1>
        <p className="text-gray-600">Human resources insights and metrics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Employees</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.total_employees}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">New Hires (This Month)</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.new_hires_this_month}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center">
            <Award className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Training Completion</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.training_completion_rate.toFixed(1)}%</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Pending Applications</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.pending_applications}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Department Distribution */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Employees by Department</h3>
        <div className="space-y-4">
          {Object.entries(dashboard.by_department).map(([department, count]) => {
            const percentage = (count / dashboard.total_employees) * 100;
            return (
              <div key={department} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="font-medium text-gray-900">{department}</span>
                  <span className="text-sm text-gray-500">({count} employees)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-orange-600 h-2 rounded-full"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12">
                    {percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Stats</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Active Employees</span>
              <span className="font-medium">{dashboard.active_employees}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Contract Renewals Due</span>
              <span className="font-medium">{dashboard.upcoming_contract_renewals}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Expiring Documents</span>
              <span className="font-medium">{dashboard.expiring_documents || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Overdue Trainings</span>
              <span className="font-medium">{dashboard.overdue_trainings || 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Alerts & Notifications</h3>
          <div className="space-y-3">
            {dashboard.upcoming_contract_renewals > 0 && (
              <div className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
                <Clock className="h-5 w-5 text-yellow-600" />
                <span className="text-sm text-yellow-800">
                  {dashboard.upcoming_contract_renewals} contracts need renewal
                </span>
              </div>
            )}
            {dashboard.pending_applications > 0 && (
              <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                <Users className="h-5 w-5 text-blue-600" />
                <span className="text-sm text-blue-800">
                  {dashboard.pending_applications} applications pending review
                </span>
              </div>
            )}
            {dashboard.training_completion_rate < 80 && (
              <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
                <Award className="h-5 w-5 text-orange-600" />
                <span className="text-sm text-orange-800">
                  Training completion rate below target (80%)
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}