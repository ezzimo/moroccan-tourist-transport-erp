import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentApi } from '../api/documentApi';
import { UploadDocumentData } from '../types/document';

export function useEmployeeDocuments(filters: any = {}) {
  return useQuery({
    queryKey: ['employee-documents', filters],
    queryFn: () => documentApi.getDocuments(filters),
  });
}

export function useExpiringDocuments(daysAhead = 30) {
  return useQuery({
    queryKey: ['expiring-documents', daysAhead],
    queryFn: () => documentApi.getExpiringDocuments(daysAhead),
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UploadDocumentData) => documentApi.uploadDocument(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-documents'] });
      queryClient.invalidateQueries({ queryKey: ['expiring-documents'] });
    },
  });
}