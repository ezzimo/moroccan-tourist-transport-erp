import React from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle, AlertTriangle, FileText, Award, TrendingUp, Calendar } from 'lucide-react';
import { useQADashboard } from '../hooks/useCertifications';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function QAPage() {
  const { data: dashboard, isLoading } = useQADashboard();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Audits',
      value: dashboard?.audit_summary.total_audits || 0,
      icon: CheckCircle,
      color: 'text-blue-600 bg-blue-100',
      href: '/qa/audits',
    },
    {
      name: 'Open Non-Conformities',
      value: dashboard?.nonconformity_summary.total_open || 0,
      icon: AlertTriangle,
      color: 'text-red-600 bg-red-100',
      href: '/qa/nonconformities',
    },
    {
      name: 'Compliance Requirements',
      value: dashboard?.compliance_summary.total_requirements || 0,
      icon: FileText,
      color: 'text-green-600 bg-green-100',
      href: '/qa/compliance',
    },
    {
      name: 'Active Certifications',
      value: dashboard?.certification_summary.active || 0,
      icon: Award,
      color: 'text-purple-600 bg-purple-100',
      href: '/qa/certifications',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Quality Assurance & Compliance</h1>
        <p className="text-gray-600">Monitor quality standards and regulatory compliance</p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Link
              key={stat.name}
              to={stat.href}
              className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Audit Summary */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Audit Performance</h3>
          {dashboard?.audit_summary && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Pass Rate</span>
                <span className="font-medium text-green-600">
                  {dashboard.audit_summary.pass_rate.toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Completed This Month</span>
                <span className="font-medium">{dashboard.audit_summary.completed_this_month}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Overdue Audits</span>
                <span className={`font-medium ${dashboard.audit_summary.overdue_audits > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {dashboard.audit_summary.overdue_audits}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Non-Conformity Summary */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Non-Conformities</h3>
          {dashboard?.nonconformity_summary && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Critical Open</span>
                <span className={`font-medium ${dashboard.nonconformity_summary.critical_open > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {dashboard.nonconformity_summary.critical_open}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Overdue Actions</span>
                <span className={`font-medium ${dashboard.nonconformity_summary.overdue_actions > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {dashboard.nonconformity_summary.overdue_actions}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Resolved This Month</span>
                <span className="font-medium text-green-600">
                  {dashboard.nonconformity_summary.resolved_this_month}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Compliance Summary */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Compliance Status</h3>
          {dashboard?.compliance_summary && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Compliant</span>
                <span className="font-medium text-green-600">
                  {dashboard.compliance_summary.compliant}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Non-Compliant</span>
                <span className={`font-medium ${dashboard.compliance_summary.non_compliant > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {dashboard.compliance_summary.non_compliant}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Expiring Soon</span>
                <span className={`font-medium ${dashboard.compliance_summary.expiring_soon > 0 ? 'text-yellow-600' : 'text-green-600'}`}>
                  {dashboard.compliance_summary.expiring_soon}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Certification Summary */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Certifications</h3>
          {dashboard?.certification_summary && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Active</span>
                <span className="font-medium text-green-600">
                  {dashboard.certification_summary.active}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Expiring Soon</span>
                <span className={`font-medium ${dashboard.certification_summary.expiring_soon > 0 ? 'text-yellow-600' : 'text-green-600'}`}>
                  {dashboard.certification_summary.expiring_soon}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Expired</span>
                <span className={`font-medium ${dashboard.certification_summary.expired > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {dashboard.certification_summary.expired}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Navigation */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/qa/audits/create"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <CheckCircle className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Schedule Audit</p>
              <p className="text-sm text-gray-500">Create new quality audit</p>
            </div>
          </Link>
          
          <Link
            to="/qa/nonconformities/create"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Report Issue</p>
              <p className="text-sm text-gray-500">Create non-conformity</p>
            </div>
          </Link>
          
          <Link
            to="/qa/compliance"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <FileText className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Check Compliance</p>
              <p className="text-sm text-gray-500">Review requirements</p>
            </div>
          </Link>
          
          <Link
            to="/qa/reports"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <TrendingUp className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">View Reports</p>
              <p className="text-sm text-gray-500">Generate QA reports</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}