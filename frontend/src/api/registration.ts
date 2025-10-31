import request from '@/utils/request'
import type { Registration, ApiResponse, PaginatedResponse } from '@/types'

export const registrationApi = {
  // Register for an activity
  register(activityId: number, subItem?: string) {
    return request.post<ApiResponse<Registration>>(`/registrations/${activityId}`, { subItem })
  },

  // Cancel registration
  cancelRegistration(activityId: number) {
    return request.delete<ApiResponse>(`/registrations/${activityId}`)
  },

  // Get user's registrations
  getMyRegistrations(params?: { page?: number; pageSize?: number }) {
    return request.get<ApiResponse<PaginatedResponse<Registration>>>('/registrations/my', { params })
  },

  // Get registrations for an activity (organizer only)
  getActivityRegistrations(activityId: number, params?: { page?: number; pageSize?: number }) {
    return request.get<ApiResponse<PaginatedResponse<Registration>>>(`/registrations/activity/${activityId}`, { params })
  },

  // Check registration status
  checkRegistrationStatus(activityId: number) {
    return request.get<ApiResponse<{ isRegistered: boolean; registration?: Registration }>>(`/registrations/status/${activityId}`)
  }
}
