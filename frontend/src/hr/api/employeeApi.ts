import { apiClient } from '../../api/client';
import {
  Employee,
  EmployeeSummary,
  EmployeesResponse,
  EmployeeFilters,
  CreateEmployeeData,
  TerminateEmployeeData,
} from '../types/employee';

export const employeeApi = {
  getEmployees: async (filters: EmployeeFilters = {}): Promise<EmployeesResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/employees?${params}`);
    return response.data;
  },

  getEmployee: async (id: string): Promise<Employee> => {
    const response = await apiClient.get(`/employees/${id}`);
    return response.data;
  },

  getEmployeeSummary: async (id: string): Promise<EmployeeSummary> => {
    const response = await apiClient.get(`/employees/${id}/summary`);
    return response.data;
  },

  createEmployee: async (data: CreateEmployeeData): Promise<Employee> => {
    const response = await apiClient.post('/employees', data);
    return response.data;
  },

  updateEmployee: async (id: string, data: Partial<CreateEmployeeData>): Promise<Employee> => {
    const response = await apiClient.put(`/employees/${id}`, data);
    return response.data;
  },

  terminateEmployee: async (id: string, data: TerminateEmployeeData): Promise<Employee> => {
    const response = await apiClient.post(`/employees/${id}/terminate`, data);
    return response.data;
  },

  deleteEmployee: async (id: string): Promise<void> => {
    await apiClient.delete(`/employees/${id}`);
  },
};