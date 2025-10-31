import request from '@/utils/request'
import type { User, AccountUser, LoginForm, RegisterForm, ApiResponse } from '@/types'

export const authApi = {
  // Login with account
  login(data: LoginForm) {
    return request.post<ApiResponse<AccountUser>>('/auth/login', data)
  },

  // Register
  register(data: RegisterForm) {
    return request.post<ApiResponse<{ token: string; user: User }>>('/auth/register', data)
  },

  // Get current user info
  getCurrentUser() {
    return request.get<ApiResponse<User>>('/auth/me')
  },

  // Logout
  logout() {
    return request.post<ApiResponse>('/auth/logout')
  },

  // Update profile
  updateProfile(data: Partial<User>) {
    return request.put<ApiResponse<User>>('/auth/profile', data)
  },

  // Change password
  changePassword(data: { oldPassword: string; newPassword: string }) {
    return request.put<ApiResponse>('/auth/password', data)
  },

  // Admin: Create organizer
  createOrganizer(data: { adminAccount: string; adminPassword: string; account: string; password: string; name?: string }) {
    return request.post<ApiResponse>('/auth/admin/create-organizer', data)
  }
}
