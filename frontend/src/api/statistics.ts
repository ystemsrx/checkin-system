import request from '@/utils/request'
import type { Activity, ActivityStatistics, ApiResponse } from '@/types'

export const statisticsApi = {
  // Get activity statistics (organizer only)
  getActivityStatistics(activityId: number) {
    return request.get<ApiResponse<ActivityStatistics>>(`/statistics/activity/${activityId}`)
  },

  // Get overall statistics for organizer
  getOrganizerStatistics() {
    return request.get<ApiResponse<{
      totalActivities: number
      totalRegistrations: number
      totalCheckIns: number
      averageCheckInRate: number
      recentActivities: Activity[]
    }>>('/statistics/organizer')
  },

  // Export statistics to Excel
  exportStatistics(activityId: number) {
    return request.get(`/statistics/export/${activityId}`, {
      responseType: 'blob'
    })
  },

  // Get registration trend
  getRegistrationTrend(params: { startDate: string; endDate: string }) {
    return request.get<ApiResponse<{ date: string; count: number }[]>>('/statistics/trend', { params })
  }
}
