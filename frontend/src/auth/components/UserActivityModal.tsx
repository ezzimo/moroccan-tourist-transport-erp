import React, { memo, useCallback, useState, useEffect } from 'react';
import { X, Activity, Clock, User as UserIcon, Shield, AlertCircle, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { userManagementApi } from '../api/userManagementApi';
import { UserActivity, ACTIVITY_ACTIONS, User } from '../types/auth';

interface UserActivityModalProps {
  isOpen: boolean;
  user: User;
  onClose: () => void;
}

const UserActivityModal = memo(function UserActivityModal({
  isOpen,
  user,
  onClose
}: UserActivityModalProps) {
  const { hasPermission } = useAuth();
  const [activities, setActivities] = useState<UserActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(50);

  // Permission check
  const canViewActivity = hasPermission('auth', 'read', 'activity');

  // Load user activity
  const loadActivity = useCallback(async () => {
    if (!canViewActivity) {
      setError('You do not have permission to view user activity');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const activityData = await userManagementApi.getUserActivity(user.id, limit);

      setActivities(activityData);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load user activity');
      setActivities([]);
    } finally {
      setLoading(false);
    }
  }, [user.id, limit, canViewActivity]);

  // Load activity when modal opens or user changes
  useEffect(() => {
    if (isOpen && user) {
      loadActivity();
    }
  }, [isOpen, user, loadActivity]);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    loadActivity();
  }, [loadActivity]);

  // Handle load more
  const handleLoadMore = useCallback(() => {
    setLimit(prev => prev + 50);
  }, []);

  // Get activity icon and color
  const getActivityIcon = useCallback((action: string) => {
    switch (action) {
      case ACTIVITY_ACTIONS.USER_CREATED:
        return { icon: UserIcon, color: 'text-green-600' };
      case ACTIVITY_ACTIONS.USER_UPDATED:
        return { icon: UserIcon, color: 'text-blue-600' };
      case ACTIVITY_ACTIONS.USER_DELETED:
        return { icon: UserIcon, color: 'text-red-600' };
      case ACTIVITY_ACTIONS.USER_LOCKED:
        return { icon: Shield, color: 'text-red-600' };
      case ACTIVITY_ACTIONS.USER_UNLOCKED:
        return { icon: Shield, color: 'text-green-600' };
      case ACTIVITY_ACTIONS.PASSWORD_RESET:
        return { icon: Shield, color: 'text-orange-600' };
      case ACTIVITY_ACTIONS.ROLE_ASSIGNED:
        return { icon: Shield, color: 'text-purple-600' };
      case ACTIVITY_ACTIONS.BULK_UPDATE:
        return { icon: UserIcon, color: 'text-blue-600' };
      default:
        return { icon: Activity, color: 'text-gray-600' };
    }
  }, []);

  // Format activity description
  const formatActivityDescription = useCallback((activity: UserActivity) => {
    // If there's a custom description, use it
    if (activity.description) {
      return activity.description;
    }

    // Generate description based on action
    switch (activity.action) {
      case ACTIVITY_ACTIONS.USER_CREATED:
        return 'User account was created';
      case ACTIVITY_ACTIONS.USER_UPDATED:
        return 'User profile was updated';
      case ACTIVITY_ACTIONS.USER_DELETED:
        return 'User account was deleted';
      case ACTIVITY_ACTIONS.USER_LOCKED:
        return 'User account was locked';
      case ACTIVITY_ACTIONS.USER_UNLOCKED:
        return 'User account was unlocked';
      case ACTIVITY_ACTIONS.PASSWORD_RESET:
        return 'Password was reset';
      case ACTIVITY_ACTIONS.ROLE_ASSIGNED:
        return 'User roles were updated';
      case ACTIVITY_ACTIONS.BULK_UPDATE:
        return 'User was updated via bulk operation';
      default:
        return `Action: ${activity.action}`;
    }
  }, []);

  // Format metadata for display
  const formatMetadata = useCallback((metadata: Record<string, any>) => {
    if (!metadata || Object.keys(metadata).length === 0) {
      return null;
    }

    return Object.entries(metadata)
      .filter(([key, value]) => value !== null && value !== undefined)
      .map(([key, value]) => {
        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const formattedValue = typeof value === 'object' 
          ? JSON.stringify(value, null, 2)
          : String(value);
        
        return { key: formattedKey, value: formattedValue };
      });
  }, []);

  if (!isOpen) {
    return null;
  }

  if (!canViewActivity) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-4">Access Denied</h3>
            <p className="text-gray-500 mb-4">
              You do not have permission to view user activity.
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              User Activity Log
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Recent activity for {user.full_name} ({user.email})
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="text-gray-400 hover:text-gray-600 p-2"
              title="Refresh"
            >
              <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-red-400 mr-2" />
              <div className="text-red-800 text-sm">{error}</div>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="max-h-96 overflow-y-auto">
          {loading && activities.length === 0 ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-500">Loading activity...</p>
            </div>
          ) : activities.length === 0 ? (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Activity Found</h3>
              <p className="text-gray-500">
                No activity records found for this user.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {activities.map((activity, index) => {
                const { icon: Icon, color } = getActivityIcon(activity.action);
                const metadata = formatMetadata(activity.metadata);
                
                return (
                  <div
                    key={activity.id || index}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                  >
                    <div className="flex items-start space-x-3">
                      {/* Icon */}
                      <div className={`p-2 rounded-full bg-gray-100 ${color}`}>
                        <Icon className="h-4 w-4" />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {formatActivityDescription(activity)}
                            </p>
                            <p className="text-xs text-gray-500">
                              by {activity.actor_email}
                              {activity.target_user_email && activity.target_user_email !== activity.actor_email && (
                                <span> → {activity.target_user_email}</span>
                              )}
                            </p>
                          </div>
                          <div className="flex items-center text-xs text-gray-400">
                            <Clock className="h-3 w-3 mr-1" />
                            {new Date(activity.created_at).toLocaleString()}
                          </div>
                        </div>

                        {/* Resource */}
                        {activity.resource && (
                          <div className="mt-2">
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                              {activity.resource}
                            </span>
                          </div>
                        )}

                        {/* IP Address */}
                        {activity.ip_address && (
                          <div className="mt-2 text-xs text-gray-500">
                            IP: {activity.ip_address}
                          </div>
                        )}

                        {/* Metadata */}
                        {metadata && metadata.length > 0 && (
                          <div className="mt-3">
                            <details className="group">
                              <summary className="cursor-pointer text-xs text-blue-600 hover:text-blue-800">
                                View Details ({metadata.length} items)
                              </summary>
                              <div className="mt-2 p-3 bg-gray-50 rounded text-xs">
                                <dl className="space-y-1">
                                  {metadata.map(({ key, value }, idx) => (
                                    <div key={idx} className="flex">
                                      <dt className="font-medium text-gray-600 w-1/3">
                                        {key}:
                                      </dt>
                                      <dd className="text-gray-900 w-2/3 break-all">
                                        {value.length > 100 ? (
                                          <details>
                                            <summary className="cursor-pointer text-blue-600">
                                              {value.substring(0, 100)}...
                                            </summary>
                                            <pre className="mt-1 whitespace-pre-wrap">
                                              {value}
                                            </pre>
                                          </details>
                                        ) : (
                                          value
                                        )}
                                      </dd>
                                    </div>
                                  ))}
                                </dl>
                              </div>
                            </details>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Load More Button */}
              {activities.length >= limit && (
                <div className="text-center py-4">
                  <button
                    onClick={handleLoadMore}
                    disabled={loading}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2 inline-block"></div>
                        Loading...
                      </>
                    ) : (
                      'Load More'
                    )}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t mt-6">
          <div className="text-sm text-gray-500">
            Showing {activities.length} activities
            {activities.length >= limit && ' (limited)'}
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
});

export default UserActivityModal;

