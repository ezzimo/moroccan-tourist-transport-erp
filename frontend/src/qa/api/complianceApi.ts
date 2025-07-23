import { apiClient } from '../../api/client';
import {
  ComplianceRequirement,
  CreateComplianceRequirementData,
  ComplianceRequirementFilters,
  ComplianceRequirementsResponse,
  AssessComplianceData,
} from '../types/compliance';

export const complianceApi = {
  getComplianceRequirements: async (filters: ComplianceRequirementFilters = {}): Promise<ComplianceRequirementsResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/compliance/?${params}`);
    return response.data;
  },

  getComplianceRequirement: async (id: string): Promise<ComplianceRequirement> => {
    const response = await apiClient.get(`/compliance/${id}`);
    return response.data;
  },

  createComplianceRequirement: async (data: CreateComplianceRequirementData): Promise<ComplianceRequirement> => {
    const response = await apiClient.post('/compliance', data);
    return response.data;
  },

  updateComplianceRequirement: async (id: string, data: Partial<CreateComplianceRequirementData>): Promise<ComplianceRequirement> => {
    const response = await apiClient.put(`/compliance/${id}`, data);
    return response.data;
  },

  assessCompliance: async (id: string, data: AssessComplianceData): Promise<ComplianceRequirement> => {
    const response = await apiClient.post(`/compliance/${id}/assess`, data);
    return response.data;
  },

  deleteComplianceRequirement: async (id: string): Promise<void> => {
    await apiClient.delete(`/compliance/${id}`);
  },
};