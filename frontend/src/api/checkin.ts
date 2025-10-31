import request from '@/utils/request'
import type { CheckIn, CheckInCode, ApiResponse } from '@/types'

export const checkinApi = {
  // Check in with QR code
  checkInWithQRCode(data: { activityId: number; qrData: string }) {
    return request.post<ApiResponse<CheckIn>>('/checkin/qrcode', data)
  },

  // Check in with code
  checkInWithCode(data: { activityId: number; code: string }) {
    return request.post<ApiResponse<CheckIn>>('/checkin/code', data)
  },

  // Generate check-in QR code (organizer only)
  generateQRCode(activityId: number) {
    return request.post<ApiResponse<{ qrData: string }>>(`/checkin/generate-qr/${activityId}`)
  },

  // Generate check-in code (organizer only)
  generateCode(activityId: number, duration: number = 15) {
    return request.post<ApiResponse<CheckInCode>>(`/checkin/generate-code/${activityId}`, { duration })
  },

  // Get check-in list for activity (organizer only)
  getActivityCheckIns(activityId: number) {
    return request.get<ApiResponse<CheckIn[]>>(`/checkin/activity/${activityId}`)
  },

  // Get check-in statistics
  getCheckInStats(activityId: number) {
    return request.get<ApiResponse<{ total: number; checkedIn: number; rate: number }>>(`/checkin/stats/${activityId}`)
  },

  // Get my recent check-ins (student only)
  getMyRecentCheckIns() {
    return request.get<ApiResponse<CheckIn[]>>('/checkin/my-recent')
  },

  // Force end check-in (organizer only)
  endCheckIn(activityId: number) {
    return request.post<ApiResponse<{ updated_count: number }>>(`/checkin/end-checkin/${activityId}`)
  }
}
