import request from '@/utils/request'
import type { Activity, ActivityForm, ActivityFilter, ApiResponse, PaginatedResponse } from '@/types'

export const activityApi = {
  // Get activity list with filters and pagination
  getActivities(params: ActivityFilter & { page?: number; pageSize?: number }) {
    return request.get<ApiResponse<PaginatedResponse<Activity>>>('/activities', { params })
  },

  // Get activity by ID
  getActivityById(id: number) {
    return request.get<ApiResponse<Activity>>(`/activities/${id}`)
  },

  // Create activity (organizer only)
  createActivity(data: ActivityForm) {
    return request.post<ApiResponse<Activity>>('/activities', data)
  },

  // Update activity (organizer only)
  updateActivity(id: number, data: Partial<ActivityForm>) {
    return request.put<ApiResponse<Activity>>(`/activities/${id}`, data)
  },

  // Delete activity (organizer only)
  deleteActivity(id: number) {
    return request.delete<ApiResponse>(`/activities/${id}`)
  },

  // Get activities created by current organizer
  getMyActivities(params?: { page?: number; pageSize?: number }) {
    return request.get<ApiResponse<PaginatedResponse<Activity>>>('/activities/my', { params })
  },

  // Get activity categories
  getCategories() {
    return request.get<ApiResponse<string[]>>('/activities/categories')
  },

  // Admin: Delete activity (except ongoing)
  adminDeleteActivity(id: number) {
    return request.delete<ApiResponse>(`/activities/admin/${id}`)
  },

  // Admin: Export activity list
  adminExportActivities() {
    return request.get('/activities/admin/export', {
      responseType: 'blob'
    })
  }
}
