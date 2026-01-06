import api from './api'

export interface User {
  id: string
  email: string
  full_name: string | null
  onboarding_completed: boolean
  is_admin?: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const formData = new FormData()
  formData.append('username', email)
  formData.append('password', password)

  const response = await api.post<LoginResponse>('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })

  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token)
  }

  return response.data
}

export async function register(email: string, password: string, fullName?: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/api/auth/register', {
    email,
    password,
    full_name: fullName,
  })

  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token)
  }

  return response.data
}

export function logout(): void {
  localStorage.removeItem('token')
  window.location.href = '/auth/login'
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

export function isAuthenticated(): boolean {
  return getToken() !== null
}

export async function getCurrentUser(): Promise<User | null> {
  try {
    const response = await api.get<User>('/api/auth/me')
    return response.data
  } catch (error) {
    return null
  }
}





