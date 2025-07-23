import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, MessageSquare, Bell, Smartphone, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import { Notification } from '../types/notification';
import { formatDateTime } from '../../utils/formatters';

interface NotificationCardProps {
  notification: Notification;
}

export default function NotificationCard({ notification }: NotificationCardProps) {
  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'EMAIL':
        return <Mail className="h-5 w-5" />;
      case 'SMS':
        return <MessageSquare className="h-5 w-5" />;
      case 'PUSH':
        return <Bell className="h-5 w-5" />;
      case 'WHATSAPP':
        return <Smartphone className="h-5 w-5" />;
      default:
        return <Bell className="h-5 w-5" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'DELIVERED':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'FAILED':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'SENT':
        return <CheckCircle className="h-4 w-4 text-blue-600" />;
      case 'PENDING':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'DELIVERED':
        return 'bg-green-100 text-green-800';
      case 'FAILED':
        return 'bg-red-100 text-red-800';
      case 'SENT':
        return 'bg-blue-100 text-blue-800';
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'EMAIL':
        return 'text-blue-600 bg-blue-100';
      case 'SMS':
        return 'text-green-600 bg-green-100';
      case 'PUSH':
        return 'text-purple-600 bg-purple-100';
      case 'WHATSAPP':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <Link
      to={`/notifications/${notification.id}`}
      className="block p-6 hover:bg-gray-50 transition-colors"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${getChannelColor(notification.channel)}`}>
            {getChannelIcon(notification.channel)}
          </div>
          <div>
            <h3 className="font-medium text-gray-900">
              {notification.subject || notification.type.replace('_', ' ')}
            </h3>
            <p className="text-sm text-gray-500">
              To: {notification.recipient_name || notification.recipient_email || notification.recipient_phone}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(notification.status)}`}>
            {getStatusIcon(notification.status)}
            <span className="ml-1">{notification.status}</span>
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getChannelColor(notification.channel)}`}>
            {notification.channel}
          </span>
        </div>
      </div>

      <p className="text-gray-700 mb-3 line-clamp-2">{notification.message}</p>

      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-4">
          <span>Priority: {notification.priority}</span>
          {notification.retry_count > 0 && (
            <span>Retries: {notification.retry_count}</span>
          )}
        </div>
        <div className="flex items-center gap-4">
          {notification.sent_at && (
            <span>Sent: {formatDateTime(notification.sent_at)}</span>
          )}
          {notification.delivered_at && (
            <span>Delivered: {formatDateTime(notification.delivered_at)}</span>
          )}
        </div>
      </div>

      {notification.error_message && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          Error: {notification.error_message}
        </div>
      )}
    </Link>
  );
}