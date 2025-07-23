import React, { useState } from 'react';
import { MessageSquare, Phone, Mail, Clock } from 'lucide-react';
import { useInteractions } from '../hooks/useInteractions';
import { InteractionFilters } from '../types/interaction';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function InteractionsPage() {
  const [filters, setFilters] = useState<InteractionFilters>({ page: 1, size: 20 });
  
  const { data: interactionsData, isLoading } = useInteractions(filters);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const interactions = interactionsData?.items || [];

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'email':
        return <Mail className="h-5 w-5" />;
      case 'phone':
        return <Phone className="h-5 w-5" />;
      case 'chat':
      case 'whatsapp':
        return <MessageSquare className="h-5 w-5" />;
      default:
        return <MessageSquare className="h-5 w-5" />;
    }
  };

  const getChannelColor = (channel: string) => {
    const colors = {
      email: 'text-blue-600 bg-blue-100',
      phone: 'text-green-600 bg-green-100',
      chat: 'text-purple-600 bg-purple-100',
      whatsapp: 'text-green-600 bg-green-100',
      sms: 'text-orange-600 bg-orange-100',
      'in-person': 'text-gray-600 bg-gray-100',
    };
    return colors[channel as keyof typeof colors] || colors.chat;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Customer Interactions</h1>
        <p className="text-gray-600">Track all customer communications</p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <MessageSquare className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Interactions</p>
              <p className="text-2xl font-bold text-gray-900">{interactionsData?.total || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Phone className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Phone Calls</p>
              <p className="text-2xl font-bold text-gray-900">
                {interactions.filter(i => i.channel === 'phone').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Mail className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Emails</p>
              <p className="text-2xl font-bold text-gray-900">
                {interactions.filter(i => i.channel === 'email').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Follow-ups</p>
              <p className="text-2xl font-bold text-gray-900">
                {interactions.filter(i => i.follow_up_required).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Interactions List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-medium text-gray-900">Recent Interactions</h3>
        </div>
        <div className="divide-y">
          {interactions.map((interaction) => (
            <div key={interaction.id} className="p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${getChannelColor(interaction.channel)}`}>
                    {getChannelIcon(interaction.channel)}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {interaction.subject || `${interaction.channel} interaction`}
                    </h4>
                    <p className="text-sm text-gray-500">
                      {new Date(interaction.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getChannelColor(interaction.channel)}`}>
                    {interaction.channel}
                  </span>
                  {interaction.follow_up_required && (
                    <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs font-medium rounded-full">
                      Follow-up
                    </span>
                  )}
                </div>
              </div>
              
              <p className="text-gray-700 mb-3">{interaction.summary}</p>
              
              <div className="flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center gap-4">
                  {interaction.duration_minutes && (
                    <span>Duration: {interaction.duration_minutes} min</span>
                  )}
                </div>
                {interaction.follow_up_date && (
                  <span>Follow-up: {new Date(interaction.follow_up_date).toLocaleDateString()}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}