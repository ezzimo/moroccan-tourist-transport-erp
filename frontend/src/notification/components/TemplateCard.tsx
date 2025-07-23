import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Eye, Edit, Mail, MessageSquare, Bell, Smartphone } from 'lucide-react';
import { NotificationTemplate } from '../types/template';
import { formatDate } from '../../utils/formatters';

interface TemplateCardProps {
  template: NotificationTemplate;
  onPreview: () => void;
}

export default function TemplateCard({ template, onPreview }: TemplateCardProps) {
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
        return <FileText className="h-5 w-5" />;
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

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'TRANSACTIONAL':
        return 'bg-blue-100 text-blue-800';
      case 'MARKETING':
        return 'bg-green-100 text-green-800';
      case 'SYSTEM':
        return 'bg-gray-100 text-gray-800';
      case 'ALERT':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${getChannelColor(template.channel)}`}>
            {getChannelIcon(template.channel)}
          </div>
          <div>
            <h3 className="font-medium text-gray-900">{template.name}</h3>
            <p className="text-sm text-gray-500">{template.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {!template.is_active && (
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
              Inactive
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 mb-4">
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(template.type)}`}>
          {template.type}
        </span>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getChannelColor(template.channel)}`}>
          {template.channel}
        </span>
        <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded-full">
          {template.language.toUpperCase()}
        </span>
      </div>

      {template.subject && (
        <div className="mb-3">
          <p className="text-sm font-medium text-gray-700 mb-1">Subject:</p>
          <p className="text-sm text-gray-600 truncate">{template.subject}</p>
        </div>
      )}

      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-1">Body Preview:</p>
        <p className="text-sm text-gray-600 line-clamp-3">{template.body}</p>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <span>Used {template.usage_count} times</span>
        <span>Created {formatDate(template.created_at)}</span>
      </div>

      <div className="flex items-center justify-between pt-4 border-t">
        <div className="flex items-center gap-2">
          <button
            onClick={onPreview}
            className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Eye className="h-4 w-4 mr-1" />
            Preview
          </button>
        </div>
        <Link
          to={`/templates/${template.id}`}
          className="inline-flex items-center px-3 py-1 text-sm bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          <Edit className="h-4 w-4 mr-1" />
          Edit
        </Link>
      </div>
    </div>
  );
}