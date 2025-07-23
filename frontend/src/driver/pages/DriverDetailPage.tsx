import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Calendar, Award, AlertTriangle, MapPin } from 'lucide-react';
import { useDriver } from '../hooks/useDrivers';
import { useDriverAssignmentsByDriver } from '../hooks/useAssignments';
import { useDriverTraining } from '../hooks/useTraining';
import { useDriverIncidents } from '../hooks/useIncidents';
import LoadingSpinner from '../../components/LoadingSpinner';
import DriverAssignmentHistory from '../components/DriverAssignmentHistory';
import DriverTrainingHistory from '../components/DriverTrainingHistory';
import DriverIncidentHistory from '../components/DriverIncidentHistory';
import DriverComplianceStatus from '../components/DriverComplianceStatus';

export default function DriverDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<'overview' | 'assignments' | 'training' | 'incidents'>('overview');

  const { data: driver, isLoading: driverLoading } = useDriver(id!);
  const { data: assignmentsData } = useDriverAssignmentsByDriver(id!, undefined);
  const { data: trainingData } = useDriverTraining(id!);
  const { data: incidentsData } = useDriverIncidents(id!);

  if (driverLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!driver) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Driver not found</p>
        <Link to="/drivers" className="text-orange-600 hover:text-orange-700 mt-2 inline-block">
          Back to Drivers
        </Link>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    const colors = {
      Active: 'bg-green-100 text-green-800',
      'On Leave': 'bg-yellow-100 text-yellow-800',
      'In Training': 'bg-blue-100 text-blue-800',
      Suspended: 'bg-red-100 text-red-800',
      Terminated: 'bg-gray-100 text-gray-800',
      Retired: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.Active;
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: User },
    { id: 'assignments', label: 'Assignments', icon: MapPin },
    { id: 'training', label: 'Training', icon: Award },
    { id: 'incidents', label: 'Incidents', icon: AlertTriangle },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/drivers"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {driver.full_name}
          </h1>
          <p className="text-gray-600">{driver.license_number}</p>
        </div>
      </div>

      {/* Driver Header Card */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-4">
              <User className="h-12 w-12 text-orange-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {driver.full_name}
                </h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(driver.status)}`}>
                    {driver.status}
                  </span>
                  <span className="text-sm text-gray-500">{driver.employment_type}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">License Type:</span> {driver.license_type}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Phone:</span> {driver.phone}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Email:</span> {driver.email || 'N/A'}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Age:</span> {driver.age} years
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Years of Service:</span> {driver.years_of_service.toFixed(1)} years
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Tours Completed:</span> {driver.total_tours_completed}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Performance Rating:</span> {driver.performance_rating ? `${driver.performance_rating.toFixed(1)}/5` : 'N/A'}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Total Incidents:</span> {driver.total_incidents}
                </p>
              </div>
            </div>

            {driver.languages_spoken.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Languages</p>
                <div className="flex flex-wrap gap-2">
                  {driver.languages_spoken.map((language) => (
                    <span
                      key={language}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                    >
                      {language}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center gap-4">
              {driver.tour_guide_certified && (
                <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                  <Award className="h-3 w-3 mr-1" />
                  Tour Guide Certified
                </span>
              )}
              {driver.first_aid_certified && (
                <span className="inline-flex items-center px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                  <Award className="h-3 w-3 mr-1" />
                  First Aid Certified
                </span>
              )}
            </div>
          </div>

          {/* Compliance Status */}
          <div className="lg:w-80">
            <DriverComplianceStatus driver={driver} />
          </div>
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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Date of Birth:</span>
                    <span className="font-medium">
                      {new Date(driver.date_of_birth).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Gender:</span>
                    <span className="font-medium">{driver.gender}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Nationality:</span>
                    <span className="font-medium">{driver.nationality}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">National ID:</span>
                    <span className="font-medium">{driver.national_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Employee ID:</span>
                    <span className="font-medium">{driver.employee_id || 'N/A'}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Emergency Contact</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Name:</span>
                    <span className="font-medium">{driver.emergency_contact_name || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Phone:</span>
                    <span className="font-medium">{driver.emergency_contact_phone || 'N/A'}</span>
                  </div>
                </div>

                <h3 className="text-lg font-medium text-gray-900 mb-4 mt-6">Employment</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Hire Date:</span>
                    <span className="font-medium">
                      {new Date(driver.hire_date).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Employment Type:</span>
                    <span className="font-medium">{driver.employment_type}</span>
                  </div>
                </div>
              </div>
            </div>

            {driver.notes && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Notes</h3>
                <p className="text-gray-600">{driver.notes}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'assignments' && (
          <DriverAssignmentHistory driverId={id!} />
        )}

        {activeTab === 'training' && (
          <DriverTrainingHistory driverId={id!} />
        )}

        {activeTab === 'incidents' && (
          <DriverIncidentHistory driverId={id!} />
        )}
      </div>
    </div>
  );
}