import React from 'react';
import { FileText, Download, Upload, AlertTriangle } from 'lucide-react';
import LoadingSpinner from '../../components/LoadingSpinner';

interface VehicleDocumentsProps {
  vehicleId: string;
}

export default function VehicleDocuments({ vehicleId }: VehicleDocumentsProps) {
  // Mock data for now - in real implementation, use document hooks
  const documents = [
    {
      id: '1',
      document_type: 'Registration',
      title: 'Vehicle Registration Certificate',
      file_name: 'registration_123A45.pdf',
      expiry_date: '2025-06-15',
      is_expired: false,
      needs_renewal: false,
      uploaded_at: '2024-01-15T10:00:00Z',
    },
    {
      id: '2',
      document_type: 'Insurance',
      title: 'Insurance Policy',
      file_name: 'insurance_policy.pdf',
      expiry_date: '2024-12-31',
      is_expired: false,
      needs_renewal: true,
      uploaded_at: '2024-01-01T09:00:00Z',
    },
    {
      id: '3',
      document_type: 'Inspection',
      title: 'Technical Inspection Certificate',
      file_name: 'inspection_cert.pdf',
      expiry_date: '2024-08-30',
      is_expired: false,
      needs_renewal: true,
      uploaded_at: '2023-08-30T14:00:00Z',
    },
  ];

  const getDocumentTypeColor = (type: string) => {
    const colors = {
      Registration: 'text-blue-600 bg-blue-100',
      Insurance: 'text-green-600 bg-green-100',
      Inspection: 'text-yellow-600 bg-yellow-100',
      Maintenance: 'text-purple-600 bg-purple-100',
      Purchase: 'text-gray-600 bg-gray-100',
      Other: 'text-orange-600 bg-orange-100',
    };
    return colors[type as keyof typeof colors] || colors.Other;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Vehicle Documents</h3>
        <button className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
          <Upload className="h-4 w-4 mr-2" />
          Upload Document
        </button>
      </div>
      
      {documents.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Documents</h3>
          <p className="text-gray-600">Upload vehicle documents to keep track of compliance.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {documents.map((doc) => (
            <div key={doc.id} className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-gray-400" />
                  <div>
                    <h4 className="font-medium text-gray-900">{doc.title}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDocumentTypeColor(doc.document_type)}`}>
                        {doc.document_type}
                      </span>
                      <span className="text-sm text-gray-500">{doc.file_name}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {doc.needs_renewal && (
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  )}
                  <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="font-medium text-gray-700">Uploaded:</p>
                  <p className="text-gray-600">
                    {new Date(doc.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
                {doc.expiry_date && (
                  <div>
                    <p className="font-medium text-gray-700">Expires:</p>
                    <p className={`${doc.needs_renewal ? 'text-yellow-600' : 'text-gray-600'}`}>
                      {new Date(doc.expiry_date).toLocaleDateString()}
                    </p>
                  </div>
                )}
                <div>
                  <p className="font-medium text-gray-700">Status:</p>
                  <p className={`${doc.is_expired ? 'text-red-600' : doc.needs_renewal ? 'text-yellow-600' : 'text-green-600'}`}>
                    {doc.is_expired ? 'Expired' : doc.needs_renewal ? 'Renewal Required' : 'Valid'}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}