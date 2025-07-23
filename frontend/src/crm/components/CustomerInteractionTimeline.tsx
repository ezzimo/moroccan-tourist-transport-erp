import React from 'react';
import { MessageSquare, Phone, Mail, Clock, User } from 'lucide-react';
import { useCustomerInteractions } from '../hooks/useInteractions';
import LoadingSpinner from '../../components/LoadingSpinner';

interface CustomerInteractionTimelineProps {
  customerId: string;
}

export default function CustomerInteractionTimeline({ customerId }: CustomerInteractionTimelineProps) {
  const { data: interactionsData, isLoading } = useCustomerInteractions(customerId, 1, 50);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
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

  if (interactions.length === 0) {
    return (
      <div className="text-center py-8">
        <MessageSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Interactions Yet</h3>
        <p className="text-gray-600">Start tracking customer communications here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Interaction Timeline</h3>
      
      <div className="flow-root">
        <ul className="-mb-8">
          {interactions.map((interaction, index) => (
            <li key={interaction.id}>
              <div className="relative pb-8">
                {index !== interactions.length - 1 && (
                  <span
                    className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                    aria-hidden="true"
                  />
                )}
                <div className="relative flex space-x-3">
                  <div className={`flex items-center justify-center h-8 w-8 rounded-full ring-8 ring-white ${getChannelColor(interaction.channel)}`}>
                    {getChannelIcon(interaction.channel)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {interaction.subject || `${interaction.channel} interaction`}
                        </p>
                        <p className="text-sm text-gray-500">
                          {new Date(interaction.timestamp).toLocaleString()}
                        </p>
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
                    <div className="mt-2">
                      <p className="text-sm text-gray-700">{interaction.summary}</p>
                    </div>
                    <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                      {interaction.duration_minutes && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {interaction.duration_minutes} min
                        </span>
                      )}
                      {interaction.staff_member_id && (
                        <span className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          Staff Member
                        </span>
                      )}
                      {interaction.follow_up_date && (
                        <span>
                          Follow-up: {new Date(interaction.follow_up_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}