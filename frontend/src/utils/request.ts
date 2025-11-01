import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types'
import { ElMessage } from 'element-plus'

// 用于防止重复弹出401提示
let isUnauthorizedHandling = false

// 清除认证信息并跳转到登录页
const handleUnauthorized = (message?: string) => {
  if (isUnauthorizedHandling) {
    return
  }
  isUnauthorizedHandling = true

  // 清除所有本地存储的认证信息
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('accountUser')
  
  // 显示提示信息
  ElMessage.warning(message || '登录已过期，请重新登录')
  
  // 延迟跳转，让用户看到提示信息
  setTimeout(() => {
    // 跳转到登录页，并保存当前路径用于登录后跳转回来
    const currentPath = window.location.pathname + window.location.search
    // 如果当前不在登录页，则跳转
    if (!window.location.pathname.includes('/login')) {
      window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`
    }
    isUnauthorizedHandling = false
  }, 500)
}

// Create axios instance
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
request.interceptors.request.use(
  (config) => {
    // Add token to headers
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // Skip validation for blob responses (file downloads)
    if (response.config.responseType === 'blob') {
      return response
    }
    
    const res = response.data
    
    // If the response code is not 200, treat it as an error
    if (res.code !== 200) {
      console.error('API Error:', res.message)
      
      // Handle specific error codes
      if (res.code === 401) {
        // Unauthorized - handle logout and redirect
        handleUnauthorized(res.message)
        return Promise.reject(new Error(res.message || '未授权'))
      }
      
      return Promise.reject(new Error(res.message || 'Error'))
    }
    
    return response
  },
  (error) => {
    console.error('Response error:', error)
    
    if (error.response) {
      // Extract error message from response
      const errorMessage = error.response.data?.message || error.response.data?.msg
      
      // Handle HTTP errors
      switch (error.response.status) {
        case 400:
          // Bad request - preserve the backend error message
          console.error('Bad request:', errorMessage)
          break
        case 401:
          // Unauthorized - handle logout and redirect
          handleUnauthorized(errorMessage)
          break
        case 403:
          console.error('Access denied:', errorMessage)
          break
        case 404:
          console.error('Resource not found:', errorMessage)
          break
        case 500:
          console.error('Server error:', errorMessage)
          break
      }
      
      // Attach the error message to the error object for easier access
      if (errorMessage) {
        error.message = errorMessage
      }
    }
    
    return Promise.reject(error)
  }
)

export default request
