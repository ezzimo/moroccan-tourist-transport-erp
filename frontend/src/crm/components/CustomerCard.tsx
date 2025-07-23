import React from 'react';
import { Link } from 'react-router-dom';
import { User, Building, Phone, Mail, MapPin, Tag } from 'lucide-react';
import { Customer } from '../types/customer';

interface CustomerCardProps {
  customer: Customer;
}

export default function CustomerCard({ customer }: CustomerCardProps) {
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

  return (
    <Link
      to={`/customers/${customer.id}`}
      className="block bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          {customer.contact_type === 'Corporate' ? (
            <Building className="h-10 w-10 text-blue-600" />
          ) : (
            <User className="h-10 w-10 text-green-600" />
          )}
          <div>
            <h3 className="font-medium text-gray-900">
              {customer.full_name || customer.company_name || 'Unnamed Customer'}
            </h3>
            <p className="text-sm text-gray-500">{customer.contact_type}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getLoyaltyColor(customer.loyalty_status)}`}>
            {customer.loyalty_status}
          </span>
          {!customer.is_active && (
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
              Inactive
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Mail className="h-4 w-4" />
          <span className="truncate">{customer.email}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Phone className="h-4 w-4" />
          <span>{customer.phone}</span>
        </div>
        {customer.region && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <MapPin className="h-4 w-4" />
            <span>{customer.region}</span>
          </div>
        )}
        {customer.last_interaction && (
          <div className="text-sm text-gray-500">
            Last contact: {new Date(customer.last_interaction).toLocaleDateString()}
          </div>
        )}
      </div>

      {customer.tags.length > 0 && (
        <div className="flex items-center gap-2">
          <Tag className="h-4 w-4 text-gray-400" />
          <div className="flex flex-wrap gap-1">
            {customer.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
            {customer.tags.length > 3 && (
              <span className="text-xs text-gray-500">+{customer.tags.length - 3} more</span>
            )}
          </div>
        </div>
      )}
    </Link>
  );
}