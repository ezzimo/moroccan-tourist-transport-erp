import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Mail, Phone, MapPin, Calendar, Building, Star } from 'lucide-react';
import { useEmployee, useEmployeeSummary } from '../hooks/useEmployees';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function EmployeeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'training'>('overview');

  const { data: employee, isLoading: employeeLoading } = useEmployee(id!);
  const { data: summary, isLoading: summaryLoading } = useEmployeeSummary(id!);

  if (employeeLoading || summaryLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Employee not found</p>
        <Link to="/hr/employees" className="text-orange-600 hover:text-orange-700 mt-2 inline-block">
          Back to Employees
        </Link>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    const colors = {
      ACTIVE: 'bg-green-100 text-green-800',
      PROBATION: 'bg-yellow-100 text-yellow-800',
      SUSPENDED: 'bg-red-100 text-red-800',
      TERMINATED: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.ACTIVE;
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: User },
    { id: 'documents', label: 'Documents', icon: Building },
    { id: 'training', label: 'Training', icon: Star },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/hr/employees"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{employee.full_name}</h1>
          <p className="text-gray-600">{employee.position} • {employee.department}</p>
        </div>
      </div>

      {/* Employee Header Card */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-4">
              <User className="h-12 w-12 text-blue-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{employee.full_name}</h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(employee.status)}`}>
                    {employee.status}
                  </span>
                  <span className="text-sm text-gray-500">{employee.employment_type}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">{employee.email}</span>
              </div>
              {employee.phone && (
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{employee.phone}</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Building className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">{employee.department}</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">
                  Hired: {new Date(employee.hire_date).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          {/* Statistics */}
          {summary && (
            <div className="lg:w-80">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Statistics</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-orange-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-orange-600">Years of Service</p>
                  <p className="text-2xl font-bold text-orange-900">{summary.years_of_service.toFixed(1)}</p>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-green-600">Training Hours</p>
                  <p className="text-2xl font-bold text-green-900">{summary.total_training_hours}</p>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-blue-600">Completed Trainings</p>
                  <p className="text-2xl font-bold text-blue-900">{summary.completed_trainings}</p>
                </div>
                <div className="bg-purple-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-purple-600">Certificates</p>
                  <p className="text-2xl font-bold text-purple-900">{summary.certificates_count}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg border p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {employee.national_id && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">National ID</p>
                    <p className="text-gray-900">{employee.national_id}</p>
                  </div>
                )}
                {employee.birth_date && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Birth Date</p>
                    <p className="text-gray-900">{new Date(employee.birth_date).toLocaleDateString()}</p>
                  </div>
                )}
                {employee.gender && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Gender</p>
                    <p className="text-gray-900">{employee.gender}</p>
                  </div>
                )}
                {employee.marital_status && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Marital Status</p>
                    <p className="text-gray-900">{employee.marital_status}</p>
                  </div>
                )}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Employment Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">Employee ID</p>
                  <p className="text-gray-900">{employee.employee_id}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Contract Type</p>
                  <p className="text-gray-900">{employee.contract_type || 'Not specified'}</p>
                </div>
                {employee.base_salary && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Base Salary</p>
                    <p className="text-gray-900">{employee.base_salary.toLocaleString()} MAD</p>
                  </div>
                )}
                {summary?.manager_name && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Manager</p>
                    <p className="text-gray-900">{summary.manager_name}</p>
                  </div>
                )}
              </div>
            </div>

            {employee.address && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Address</h3>
                <p className="text-gray-600">{employee.address}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="text-center py-8">
            <Building className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Employee Documents</h3>
            <p className="text-gray-600">Document management functionality will be available soon.</p>
          </div>
        )}

        {activeTab === 'training' && (
          <div className="text-center py-8">
            <Star className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Training History</h3>
            <p className="text-gray-600">Training records and progress will be displayed here.</p>
          </div>
        )}
      </div>
    </div>
  );
}