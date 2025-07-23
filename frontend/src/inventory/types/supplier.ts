export interface Supplier {
  id: string;
  name: string;
  code: string;
  type: 'PARTS_SUPPLIER' | 'SERVICE_PROVIDER' | 'EQUIPMENT_SUPPLIER' | 'CONSUMABLES_SUPPLIER' | 'OTHER';
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  payment_terms?: string;
  delivery_time_days?: number;
  performance_rating?: number;
  status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';
  created_at: string;
}

export interface SuppliersResponse {
  items: Supplier[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CreateSupplierData {
  name: string;
  code: string;
  type: 'PARTS_SUPPLIER' | 'SERVICE_PROVIDER' | 'EQUIPMENT_SUPPLIER' | 'CONSUMABLES_SUPPLIER' | 'OTHER';
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  payment_terms?: string;
  delivery_time_days?: number;
}