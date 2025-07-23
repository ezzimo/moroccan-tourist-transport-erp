export interface TourTemplate {
  id: string;
  title: string;
  description?: string;
  short_description?: string;
  category: 'CULTURAL' | 'ADVENTURE' | 'DESERT' | 'COASTAL' | 'CITY' | 'CUSTOM';
  duration_days: number;
  difficulty_level: 'EASY' | 'MODERATE' | 'CHALLENGING' | 'EXPERT';
  default_language: string;
  default_region: string;
  starting_location?: string;
  ending_location?: string;
  min_participants: number;
  max_participants: number;
  base_price?: number;
  highlights?: string[];
  inclusions?: string[];
  exclusions?: string[];
  requirements?: string;
  is_active: boolean;
  is_featured: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CreateTourTemplateData {
  title: string;
  description?: string;
  short_description?: string;
  category: 'CULTURAL' | 'ADVENTURE' | 'DESERT' | 'COASTAL' | 'CITY' | 'CUSTOM';
  duration_days: number;
  difficulty_level: 'EASY' | 'MODERATE' | 'CHALLENGING' | 'EXPERT';
  default_language?: string;
  default_region: string;
  starting_location?: string;
  ending_location?: string;
  min_participants?: number;
  max_participants?: number;
  base_price?: number;
  highlights?: string[];
  inclusions?: string[];
  exclusions?: string[];
  requirements?: string;
}

export interface TourTemplateFilters {
  page?: number;
  size?: number;
  query?: string;
  category?: string;
  difficulty_level?: string;
  region?: string;
  min_duration?: number;
  max_duration?: number;
  min_participants?: number;
  max_participants?: number;
  is_active?: boolean;
  is_featured?: boolean;
}

export interface TourTemplatesResponse {
  items: TourTemplate[];
  total: number;
  page: number;
  size: number;
  pages: number;
}