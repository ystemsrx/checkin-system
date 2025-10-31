import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types'

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
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
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
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
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
