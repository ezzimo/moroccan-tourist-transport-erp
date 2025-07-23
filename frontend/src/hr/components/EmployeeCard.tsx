import React from 'react';
import { Link } from 'react-router-dom';
import { User, Mail, Phone, MapPin, Calendar, Building } from 'lucide-react';
import { Employee } from '../types/employee';

interface EmployeeCardProps {
  employee: Employee;
}

export default function EmployeeCard({ employee }: EmployeeCardProps) {
  const getStatusColor = (status: string) => {
    const colors = {
      ACTIVE: 'bg-green-100 text-green-800',
      PROBATION: 'bg-yellow-100 text-yellow-800',
      SUSPENDED: 'bg-red-100 text-red-800',
      TERMINATED: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.ACTIVE;
  };

  const getEmploymentTypeColor = (type: string) => {
    const colors = {
      FULL_TIME: 'bg-blue-100 text-blue-800',
      PART_TIME: 'bg-purple-100 text-purple-800',
      CONTRACT: 'bg-orange-100 text-orange-800',
    };
    return colors[type as keyof typeof colors] || colors.FULL_TIME;
  };

  return (
    <Link
      to={`/hr/employees/${employee.id}`}
      className="block bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <User className="h-10 w-10 text-blue-600" />
          <div>
            <h3 className="font-medium text-gray-900">{employee.full_name}</h3>
            <p className="text-sm text-gray-500">{employee.position}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(employee.status)}`}>
            {employee.status}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEmploymentTypeColor(employee.employment_type)}`}>
            {employee.employment_type.replace('_', ' ')}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Mail className="h-4 w-4" />
          <span className="truncate">{employee.email}</span>
        </div>
        {employee.phone && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Phone className="h-4 w-4" />
            <span>{employee.phone}</span>
          </div>
        )}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Building className="h-4 w-4" />
          <span>{employee.department}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          <span>Hired: {new Date(employee.hire_date).toLocaleDateString()}</span>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>ID: {employee.employee_id}</span>
        {employee.base_salary && (
          <span className="font-medium text-gray-900">
            {employee.base_salary.toLocaleString()} MAD
          </span>
        )}
      </div>
    </Link>
  );
}