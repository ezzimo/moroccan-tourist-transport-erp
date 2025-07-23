export interface HRDashboard {
  total_employees: number;
  active_employees: number;
  new_hires_this_month: number;
  pending_applications: number;
  training_completion_rate: number;
  by_department: Record<string, number>;
  upcoming_contract_renewals: number;
  expiring_documents: number;
  overdue_trainings: number;
}

export interface HRAnalytics {
  employee_growth: {
    month: string;
    count: number;
  }[];
  training_completion: {
    program: string;
    completion_rate: number;
  }[];
  recruitment_funnel: {
    stage: string;
    count: number;
  }[];
  department_distribution: {
    department: string;
    count: number;
    percentage: number;
  }[];
}