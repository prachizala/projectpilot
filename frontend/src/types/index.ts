export type UserRole = 'owner' | 'member' | 'client';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  client_id?: number | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Client {
  id: number;
  owner_id: number;
  name: string;
  company?: string | null;
  email: string;
  phone?: string | null;
  notes?: string | null;
  created_at: string;
  projects_count: number;
  total_billed: number;
}

export type ProjectStatus = 'planning' | 'in_progress' | 'in_review' | 'completed' | 'on_hold';

export interface Project {
  id: number;
  owner_id: number;
  client_id: number;
  title: string;
  description?: string | null;
  status: ProjectStatus;
  budget: number;
  deadline?: string | null;
  created_at: string;
  client_name?: string;
  tasks_count: number;
}

export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: number;
  project_id: number;
  owner_id: number;
  title: string;
  description?: string | null;
  status: TaskStatus;
  position: number;
  priority: TaskPriority;
  due_date?: string | null;
  created_at: string;
}

export interface InvoiceItem {
  id?: number;
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface Invoice {
  id: number;
  owner_id: number;
  client_id: number;
  project_id?: number | null;
  invoice_number: string;
  issue_date: string;
  due_date: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  subtotal: number;
  tax_rate_pct: number;
  tax_amount: number;
  total_amount: number;
  notes?: string | null;
  created_at: string;
  client_name?: string;
  items?: InvoiceItem[];
}

export interface Proposal {
  id: number;
  owner_id: number;
  client_id?: number | null;
  title: string;
  raw_requirements: string;
  scope_summary: string;
  milestones_json: string;
  estimated_budget: number;
  status: 'draft' | 'sent' | 'approved' | 'converted';
  created_at: string;
}
