import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Building, Phone, Mail, MapPin, Star, MessageSquare } from 'lucide-react';
import { useCustomerSummary, useCustomer } from '../hooks/useCustomers';
import { useCustomerInteractions } from '../hooks/useInteractions';
import LoadingSpinner from '../../components/LoadingSpinner';
import CustomerInteractionTimeline from '../components/CustomerInteractionTimeline';
import CustomerFeedbackList from '../components/CustomerFeedbackList';

export default function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<'overview' | 'interactions' | 'feedback'>('overview');

  const { data: customer, isLoading: customerLoading } = useCustomer(id!);
  const { data: summary, isLoading: summaryLoading } = useCustomerSummary(id!);
  const { data: interactions, isLoading: interactionsLoading } = useCustomerInteractions(id!, 1, 20);

  if (customerLoading || summaryLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Customer not found</p>
        <Link to="/customers" className="text-orange-600 hover:text-orange-700 mt-2 inline-block">
          Back to Customers
        </Link>
      </div>
    );
  }

  const getLoyaltyColor = (status: string) => {
    const colors = {
      New: 'bg-gray-100 text-gray-800',
      Bronze: 'bg-amber-100 text-amber-800',
      Silver: 'bg-gray-100 text-gray-800',
      Gold: 'bg-yellow-100 text-yellow-800',
      Platinum: 'bg-purple-100 text-purple-800',
      VIP: 'bg-red-100 text-red-800',
    };
    return colors[status as keyof typeof colors] || colors.New;
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: User },
    { id: 'interactions', label: 'Interactions', icon: MessageSquare },
    { id: 'feedback', label: 'Feedback', icon: Star },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/customers"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {customer.full_name || customer.company_name || 'Unnamed Customer'}
          </h1>
          <p className="text-gray-600">{customer.email}</p>
        </div>
      </div>

      {/* Customer Header Card */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-4">
              {customer.contact_type === 'Corporate' ? (
                <Building className="h-12 w-12 text-blue-600" />
              ) : (
                <User className="h-12 w-12 text-green-600" />
              )}
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {customer.full_name || customer.company_name}
                </h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getLoyaltyColor(customer.loyalty_status)}`}>
                    {customer.loyalty_status}
                  </span>
                  <span className="text-sm text-gray-500">{customer.contact_type}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">{customer.email}</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">{customer.phone}</span>
              </div>
              {customer.region && (
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{customer.region}</span>
                </div>
              )}
              {customer.nationality && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Nationality: {customer.nationality}</span>
                </div>
              )}
            </div>

            {customer.tags.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Tags</p>
                <div className="flex flex-wrap gap-2">
                  {customer.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Statistics */}
          {summary && (
            <div className="lg:w-80">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Statistics</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-orange-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-orange-600">Interactions</p>
                  <p className="text-2xl font-bold text-orange-900">{summary.total_interactions}</p>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-green-600">Feedback</p>
                  <p className="text-2xl font-bold text-green-900">{summary.total_feedback}</p>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-blue-600">Avg Rating</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {summary.average_rating ? summary.average_rating.toFixed(1) : 'N/A'}
                  </p>
                </div>
                <div className="bg-purple-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-purple-600">Segments</p>
                  <p className="text-2xl font-bold text-purple-900">{summary.segments.length}</p>
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
        {activeTab === 'overview' && summary && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Communication Channels</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-600">Email</p>
                      <p className="text-2xl font-bold text-blue-900">{summary.interaction_channels.email}</p>
                    </div>
                    <Mail className="h-8 w-8 text-blue-600" />
                  </div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-green-600">Phone</p>
                      <p className="text-2xl font-bold text-green-900">{summary.interaction_channels.phone}</p>
                    </div>
                    <Phone className="h-8 w-8 text-green-600" />
                  </div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-purple-600">Chat</p>
                      <p className="text-2xl font-bold text-purple-900">{summary.interaction_channels.chat}</p>
                    </div>
                    <MessageSquare className="h-8 w-8 text-purple-600" />
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Feedback by Service</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(summary.feedback_by_service).map(([service, count]) => (
                  <div key={service} className="bg-gray-50 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-600">{service}</p>
                      <p className="text-xl font-bold text-gray-900">{count}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {customer.notes && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Notes</h3>
                <p className="text-gray-600">{customer.notes}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'interactions' && (
          <CustomerInteractionTimeline customerId={id!} />
        )}

        {activeTab === 'feedback' && (
          <CustomerFeedbackList customerId={id!} />
        )}
      </div>
    </div>
  );
}