import React, { useState } from 'react';
import { Plus, Search, Filter, Users, Clock, CheckCircle, X } from 'lucide-react';
import { useJobApplications } from '../hooks/useRecruitment';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export default function RecruitmentPage() {
  const [filters, setFilters] = useState<any>({ page: 1, size: 20 });
  const [searchQuery, setSearchQuery] = useState('');

  const { data: applicationsData, isLoading, error } = useJobApplications(filters);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters((prev: any) => ({ ...prev, query: searchQuery, page: 1 }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load job applications. Please try again.</p>
      </div>
    );
  }

  const applications = applicationsData?.items || [];

  const getStageColor = (stage: string) => {
    const colors = {
      RECEIVED: 'bg-blue-100 text-blue-800',
      SCREENING: 'bg-yellow-100 text-yellow-800',
      PHONE_INTERVIEW: 'bg-purple-100 text-purple-800',
      IN_PERSON_INTERVIEW: 'bg-indigo-100 text-indigo-800',
      TECHNICAL_TEST: 'bg-orange-100 text-orange-800',
      REFERENCE_CHECK: 'bg-teal-100 text-teal-800',
      OFFER_MADE: 'bg-green-100 text-green-800',
      HIRED: 'bg-green-200 text-green-900',
      REJECTED: 'bg-red-100 text-red-800',
    };
    return colors[stage as keyof typeof colors] || colors.RECEIVED;
  };

  const getSourceColor = (source: string) => {
    const colors = {
      JOB_BOARD: 'bg-blue-100 text-blue-800',
      COMPANY_WEBSITE: 'bg-green-100 text-green-800',
      REFERRAL: 'bg-purple-100 text-purple-800',
      SOCIAL_MEDIA: 'bg-pink-100 text-pink-800',
      OTHER: 'bg-gray-100 text-gray-800',
    };
    return colors[source as keyof typeof colors] || colors.OTHER;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Recruitment</h1>
          <p className="text-gray-600">Manage job applications and hiring process</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
          <Plus className="h-5 w-5 mr-2" />
          Add Application
        </button>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg border p-4">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search applications by name, position, or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            Search
          </button>
        </form>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Applications</p>
              <p className="text-2xl font-bold text-gray-900">{applications.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">In Progress</p>
              <p className="text-2xl font-bold text-gray-900">
                {applications.filter(a => !['HIRED', 'REJECTED'].includes(a.stage)).length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Hired</p>
              <p className="text-2xl font-bold text-gray-900">
                {applications.filter(a => a.stage === 'HIRED').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <X className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Rejected</p>
              <p className="text-2xl font-bold text-gray-900">
                {applications.filter(a => a.stage === 'REJECTED').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Applications List */}
      {applications.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No applications found"
          description="Job applications will appear here"
          action={{
            label: 'Add Application',
            onClick: () => {},
          }}
        />
      ) : (
        <div className="bg-white rounded-lg border">
          <div className="divide-y">
            {applications.map((application) => (
              <div key={application.id} className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-1">{application.full_name}</h3>
                    <p className="text-gray-600 mb-2">{application.position_applied} • {application.department}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>{application.email}</span>
                      <span>{application.phone}</span>
                      {application.years_of_experience && (
                        <span>{application.years_of_experience} years experience</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSourceColor(application.source)}`}>
                      {application.source.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStageColor(application.stage)}`}>
                      {application.stage.replace('_', ' ')}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center gap-4">
                    <span>Applied: {new Date(application.application_date).toLocaleDateString()}</span>
                    {application.expected_salary && (
                      <span>Expected: {application.expected_salary.toLocaleString()} MAD</span>
                    )}
                    {application.overall_rating && (
                      <span>Rating: {application.overall_rating}/10</span>
                    )}
                  </div>
                  {application.interview_date && (
                    <span>Interview: {new Date(application.interview_date).toLocaleDateString()}</span>
                  )}
                </div>

                {application.skills.length > 0 && (
                  <div className="mt-3">
                    <div className="flex flex-wrap gap-1">
                      {application.skills.slice(0, 5).map((skill) => (
                        <span
                          key={skill}
                          className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                      {application.skills.length > 5 && (
                        <span className="text-xs text-gray-500">+{application.skills.length - 5} more</span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}