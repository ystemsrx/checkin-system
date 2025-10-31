// User types
export interface User {
  id: number
  username: string
  email: string
  role: 'student' | 'organizer'
  name?: string
  avatar?: string
  createdAt: string
}

// Account-based user info from external API
export interface AccountUser {
  name: string
  accountId: string
  avatarUrl?: string
  bio?: string
  role?: 'student' | 'organizer' | 'admin'
  token?: string
  user?: User
  firstLoginTime?: string
}

export interface LoginForm {
  account: string
  password: string
}

export interface RegisterForm {
  username: string
  email: string
  password: string
  confirmPassword: string
  role: 'student' | 'organizer'
}

// Activity types
export type ActivityCategory = 'academic' | 'cultural' | 'sports' | 'volunteer' | 'other'
export type ActivityStatus = 'upcoming' | 'ongoing' | 'completed' | 'cancelled'

export interface ActivitySubItem {
  name: string
  maxParticipants: number
  currentParticipants?: number
}

export interface Activity {
  id: number
  title: string
  description: string
  category: ActivityCategory
  status: ActivityStatus
  organizerId: number
  organizerName: string
  startTime: string
  endTime: string
  location: string
  maxParticipants: number
  currentParticipants: number
  registrationDeadline: string
  coverImage?: string
  images?: string[]
  tags?: string[]
  subItems?: ActivitySubItem[]
  createdAt: string
  updatedAt: string
}

export interface ActivityForm {
  title: string
  description: string
  category: ActivityCategory
  startTime: string
  endTime: string
  location: string
  maxParticipants: number
  registrationDeadline: string
  images?: string[]
  tags?: string[]
  subItems?: ActivitySubItem[]
}

// Registration types
export interface Registration {
  id: number
  activityId: number
  userId: number
  userName: string
  userEmail: string
  status: 'registered' | 'checked_in' | 'cancelled'
  subItem?: string
  registeredAt: string
  checkedInAt?: string
  activity?: Activity
}

// Check-in types
export interface CheckIn {
  id: number
  activityId: number
  activityTitle?: string
  userId: number
  userName?: string
  userEmail?: string
  checkedInAt: string
  method: 'qrcode' | 'code'
}

export interface CheckInCode {
  id?: number
  activityId: number
  code: string
  expiresAt: string
  createdAt: string
}

export interface CheckInStats {
  totalRegistrations: number
  checkedIn: number
  notCheckedIn: number
  checkInRate: number
}

// Statistics types
export interface ActivityStatistics {
  activityId: number
  activityTitle: string
  totalRegistrations: number
  totalCheckIns: number
  checkInRate: number
  registrationTrend: {
    date: string
    count: number
  }[]
  categoryDistribution: {
    category: ActivityCategory
    count: number
  }[]
}

// Filter types
export interface ActivityFilter {
  category?: ActivityCategory
  status?: ActivityStatus
  organizerId?: number
  startDate?: string
  endDate?: string
  keyword?: string
}

// Notification types
export interface Notification {
  id: number
  userId: number
  title: string
  content: string
  type: 'activity_update' | 'registration_success' | 'check_in_reminder' | 'system_announcement'
  isRead: boolean
  createdAt: string
}

// API Response types
export interface ApiResponse<T = any> {
  success?: boolean
  code: number
  message?: string
  msg?: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}
