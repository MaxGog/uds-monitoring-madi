export interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  company: string;
  position: string;
  status: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password?: string;
  role_id: number;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  role?: string;
}

export interface ApiResponse<T> {
  data: T;
}