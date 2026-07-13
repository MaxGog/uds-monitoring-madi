export interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  company: string;
  position: string;
  status: string;
  full_name: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password?: string;
  role: string;
  full_name: string;
  company: string;
  position: string;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  role?: string;
  full_name: string;
  company: string;
  position: string;
}