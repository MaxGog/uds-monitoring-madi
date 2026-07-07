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
  role: string;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  role?: string;
}