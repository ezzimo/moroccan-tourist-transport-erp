import React from 'react';
import { Users, Plus } from 'lucide-react';

export default function SegmentsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customer Segments</h1>
          <p className="text-gray-600">Organize customers into targeted groups</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
          <Plus className="h-5 w-5 mr-2" />
          Create Segment
        </button>
      </div>

      {/* Coming Soon */}
      <div className="bg-white rounded-lg border p-12 text-center">
        <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-medium text-gray-900 mb-2">Customer Segments</h3>
        <p className="text-gray-600 max-w-md mx-auto">
          Customer segmentation functionality will be available soon. Create targeted groups based on behavior, preferences, and demographics.
        </p>
      </div>
    </div>
  );
}