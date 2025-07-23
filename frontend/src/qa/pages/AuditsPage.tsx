import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { useAudits } from '../hooks/useAudits';
import { QualityAuditFilters } from '../types/audit';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export default function AuditsPage() {
  const [filters, setFilters] = useState<QualityAuditFilters>({ page: 1, size: 20 });
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const { data: auditsData, isLoading, error } = useAudits(filters);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters(prev => ({ ...prev, query: searchQuery, page: 1 }));
  };

  const handleFilterChange = (newFilters: Partial<QualityAuditFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 }));
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
        <p className="text-red-600">Failed to load audits. Please try again.</p>
      </div>
    );
  }

  const audits = auditsData?.items || [];

  const getStatusColor = (status: string) => {
    const colors = {
      SCHEDULED: 'bg-blue-100 text-blue-800',
      IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
      COMPLETED: 'bg-green-100 text-green-800',
      CANCELLED: 'bg-gray-100 text-gray-800',
      OVERDUE: 'bg-red-100 text-red-800',
    };
    return colors[status as keyof typeof colors] || colors.SCHEDULED;
  };

  const getOutcomeColor = (outcome: string) => {
    const colors = {
      Pass: 'text-green-600',
      Fail: 'text-red-600',
      Conditional: 'text-yellow-600',
    };
    return colors[outcome as keyof typeof colors] || 'text-gray-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quality Audits</h1>
          <p className="text-gray-600">Schedule and manage quality audits</p>
        </div>
        <Link
          to="/qa/audits/create"
          className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Schedule Audit
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border p-4 space-y-4">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search audits by title, audit number, or entity..."
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
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Filter className="h-5 w-5" />
          </button>
        </form>

        {showFilters && (
          <div className="bg-gray-50 border rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Entity Type</label>
                <select
                  value={filters.entity_type || ''}
                  onChange={(e) => handleFilterChange({ entity_type: e.target.value || undefined })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">All Types</option>
                  <option value="TOUR">Tour</option>
                  <option value="FLEET">Fleet</option>
                  <option value="BOOKING">Booking</option>
                  <option value="OFFICE">Office</option>
                  <option value="DRIVER">Driver</option>
                  <option value="GUIDE">Guide</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Audit Type</label>
                <select
                  value={filters.audit_type || ''}
                  onChange={(e) => handleFilterChange({ audit_type: e.target.value || undefined })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">All Types</option>
                  <option value="INTERNAL">Internal</option>
                  <option value="EXTERNAL">External</option>
                  <option value="CUSTOMER_FEEDBACK">Customer Feedback</option>
                  <option value="REGULATORY">Regulatory</option>
                  <option value="FOLLOW_UP">Follow-up</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => handleFilterChange({ status: e.target.value || undefined })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">All Statuses</option>
                  <option value="SCHEDULED">Scheduled</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="COMPLETED">Completed</option>
                  <option value="OVERDUE">Overdue</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Outcome</label>
                <select
                  value={filters.outcome || ''}
                  onChange={(e) => handleFilterChange({ outcome: e.target.value || undefined })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">All Outcomes</option>
                  <option value="Pass">Pass</option>
                  <option value="Fail">Fail</option>
                  <option value="Conditional">Conditional</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Audits List */}
      {audits.length === 0 ? (
        <EmptyState
          icon={CheckCircle}
          title="No audits found"
          description="Schedule your first quality audit to get started"
          action={{
            label: 'Schedule Audit',
            onClick: () => window.location.href = '/qa/audits/create',
          }}
        />
      ) : (
        <div className="bg-white rounded-lg border">
          <div className="divide-y">
            {audits.map((audit) => (
              <Link
                key={audit.id}
                to={`/qa/audits/${audit.id}`}
                className="block p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-medium text-gray-900">{audit.title}</h3>
                      <span className="text-sm text-gray-500">#{audit.audit_number}</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>{audit.entity_type}</span>
                      {audit.entity_name && <span>• {audit.entity_name}</span>}
                      <span>• {audit.audit_type}</span>
                      <span>• {audit.auditor_name}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(audit.status)}`}>
                      {audit.status.replace('_', ' ')}
                    </span>
                    {audit.is_overdue && (
                      <AlertCircle className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      Scheduled: {new Date(audit.scheduled_date).toLocaleDateString()}
                    </span>
                    {audit.completion_date && (
                      <span>Completed: {new Date(audit.completion_date).toLocaleDateString()}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-4">
                    {audit.total_score !== null && (
                      <span className="text-sm font-medium">
                        Score: {audit.total_score.toFixed(1)}%
                      </span>
                    )}
                    {audit.outcome && (
                      <span className={`text-sm font-medium ${getOutcomeColor(audit.outcome)}`}>
                        {audit.outcome}
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {auditsData && auditsData.pages > 1 && (
            <div className="flex items-center justify-between border-t px-4 py-3">
              <div className="flex items-center text-sm text-gray-500">
                Showing {((filters.page || 1) - 1) * (filters.size || 20) + 1} to{' '}
                {Math.min((filters.page || 1) * (filters.size || 20), auditsData.total)} of{' '}
                {auditsData.total} results
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setFilters(prev => ({ ...prev, page: (prev.page || 1) - 1 }))}
                  disabled={(filters.page || 1) <= 1}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="px-3 py-1">
                  Page {filters.page || 1} of {auditsData.pages}
                </span>
                <button
                  onClick={() => setFilters(prev => ({ ...prev, page: (prev.page || 1) + 1 }))}
                  disabled={(filters.page || 1) >= auditsData.pages}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}