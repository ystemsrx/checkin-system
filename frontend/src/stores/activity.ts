import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Activity, ActivityFilter, PaginatedResponse } from '@/types'
import { activityApi } from '@/api/activity'

export const useActivityStore = defineStore('activity', () => {
  const activities = ref<Activity[]>([])
  const currentActivity = ref<Activity | null>(null)
  const pagination = ref({
    total: 0,
    page: 1,
    pageSize: 10,
    totalPages: 0
  })
  const loading = ref(false)
  const filter = ref<ActivityFilter>({})

  // Fetch activities with filters
  const fetchActivities = async (params?: ActivityFilter & { page?: number; pageSize?: number }) => {
    loading.value = true
    try {
      const response = await activityApi.getActivities({
        ...filter.value,
        ...params,
        page: params?.page || pagination.value.page,
        pageSize: params?.pageSize || pagination.value.pageSize
      })
      
      const data: PaginatedResponse<Activity> = response.data.data
      activities.value = data.items
      pagination.value = {
        total: data.total,
        page: data.page,
        pageSize: data.pageSize,
        totalPages: data.totalPages
      }
      
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message || '获取活动列表失败' }
    } finally {
      loading.value = false
    }
  }

  // Fetch activity by ID
  const fetchActivityById = async (id: number) => {
    loading.value = true
    try {
      const response = await activityApi.getActivityById(id)
      currentActivity.value = response.data.data
      return { success: true, data: response.data.data }
    } catch (error: any) {
      return { success: false, message: error.message || '获取活动详情失败' }
    } finally {
      loading.value = false
    }
  }

  // Create activity
  const createActivity = async (data: any) => {
    loading.value = true
    try {
      const response = await activityApi.createActivity(data)
      return { success: true, data: response.data.data }
    } catch (error: any) {
      return { success: false, message: error.message || '创建活动失败' }
    } finally {
      loading.value = false
    }
  }

  // Update activity
  const updateActivity = async (id: number, data: any) => {
    loading.value = true
    try {
      const response = await activityApi.updateActivity(id, data)
      return { success: true, data: response.data.data }
    } catch (error: any) {
      return { success: false, message: error.message || '更新活动失败' }
    } finally {
      loading.value = false
    }
  }

  // Delete activity
  const deleteActivity = async (id: number) => {
    loading.value = true
    try {
      await activityApi.deleteActivity(id)
      activities.value = activities.value.filter(a => a.id !== id)
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message || '删除活动失败' }
    } finally {
      loading.value = false
    }
  }

  // Set filter
  const setFilter = (newFilter: ActivityFilter) => {
    filter.value = { ...filter.value, ...newFilter }
  }

  // Clear filter
  const clearFilter = () => {
    filter.value = {}
  }

  // Reset
  const reset = () => {
    activities.value = []
    currentActivity.value = null
    pagination.value = {
      total: 0,
      page: 1,
      pageSize: 10,
      totalPages: 0
    }
    filter.value = {}
  }

  return {
    activities,
    currentActivity,
    pagination,
    loading,
    filter,
    fetchActivities,
    fetchActivityById,
    createActivity,
    updateActivity,
    deleteActivity,
    setFilter,
    clearFilter,
    reset
  }
})
