import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, MapPin, Calendar, Users, Clock } from 'lucide-react';
import { useTourInstance } from '../hooks/useTourInstances';
import { useTourItinerary } from '../hooks/useItinerary';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function TourDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: tour, isLoading: tourLoading } = useTourInstance(id!);
  const { data: itinerary, isLoading: itineraryLoading } = useTourItinerary(id!);

  if (tourLoading || itineraryLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!tour) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Tour not found</p>
        <Link to="/tours/instances" className="text-orange-600 hover:text-orange-700 mt-2 inline-block">
          Back to Tour Instances
        </Link>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    const colors = {
      PLANNED: 'bg-blue-100 text-blue-800',
      CONFIRMED: 'bg-green-100 text-green-800',
      IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
      COMPLETED: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-red-100 text-red-800',
      POSTPONED: 'bg-orange-100 text-orange-800',
    };
    return colors[status as keyof typeof colors] || colors.PLANNED;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/tours/instances"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{tour.title}</h1>
          <p className="text-gray-600">{tour.lead_participant_name}</p>
        </div>
      </div>

      {/* Tour Overview */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-4">
              <MapPin className="h-12 w-12 text-orange-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Tour Details</h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(tour.status)}`}>
                    {tour.status.replace('_', ' ')}
                  </span>
                  <span className="text-sm text-gray-500">{tour.language}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Start Date:</span> {new Date(tour.start_date).toLocaleDateString()}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">End Date:</span> {new Date(tour.end_date).toLocaleDateString()}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Participants:</span> {tour.participant_count}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Lead Passenger:</span> {tour.lead_participant_name}
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Current Day:</span> {tour.current_day}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Progress:</span> {tour.completion_percentage.toFixed(0)}%
                </p>
                {tour.assigned_guide_id && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Guide:</span> Assigned
                  </p>
                )}
                {tour.assigned_vehicle_id && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Vehicle:</span> Assigned
                  </p>
                )}
              </div>
            </div>

            {tour.special_requirements && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Special Requirements</p>
                <p className="text-sm text-gray-600">{tour.special_requirements}</p>
              </div>
            )}
          </div>

          {/* Progress */}
          <div className="lg:w-80">
            <div className="bg-orange-50 p-4 rounded-lg">
              <h4 className="font-medium text-orange-900 mb-3">Tour Progress</h4>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-orange-700">Completion</span>
                    <span className="font-medium text-orange-900">{tour.completion_percentage.toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-orange-200 rounded-full h-2">
                    <div
                      className="bg-orange-600 h-2 rounded-full"
                      style={{ width: `${tour.completion_percentage}%` }}
                    />
                  </div>
                </div>
                <div className="text-sm text-orange-700">
                  Day {tour.current_day} of {Math.ceil((new Date(tour.end_date).getTime() - new Date(tour.start_date).getTime()) / (1000 * 60 * 60 * 24)) + 1}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Itinerary */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Itinerary</h3>
        {!itinerary || itinerary.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No itinerary items yet</p>
        ) : (
          <div className="space-y-4">
            {itinerary.map((item) => (
              <div key={item.id} className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center text-sm font-medium">
                    {item.day_number}
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-gray-900">{item.title}</h4>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      {item.activity_type}
                    </span>
                    {item.is_completed && (
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        Completed
                      </span>
                    )}
                  </div>
                  {item.description && (
                    <p className="text-sm text-gray-600 mb-2">{item.description}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    {item.display_time && (
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {item.display_time}
                      </span>
                    )}
                    {item.location_name && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {item.location_name}
                      </span>
                    )}
                    {item.cost && (
                      <span>{item.cost} MAD</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}