import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, AccountUser, LoginForm, RegisterForm } from '@/types'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accountUser = ref<AccountUser | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)

  // Computed
  const isLoggedIn = computed(() => !!accountUser.value)
  const isAdmin = computed(() => accountUser.value?.role === 'admin')
  const isStudent = computed(() => accountUser.value?.role === 'student' || user.value?.role === 'student')
  const isOrganizer = computed(() => accountUser.value?.role === 'organizer' || user.value?.role === 'organizer')

  // Initialize from localStorage
  const initAuth = () => {
    const savedAccountUser = localStorage.getItem('accountUser')
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedAccountUser) {
      accountUser.value = JSON.parse(savedAccountUser)
    }
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  // Login
  const login = async (form: LoginForm) => {
    loading.value = true
    try {
      const response = await authApi.login(form)
      
      // Check if login was successful
      if (response.data.success && response.data.code === 200) {
        const userData = response.data.data
        accountUser.value = userData
        
        // Store account user data
        localStorage.setItem('accountUser', JSON.stringify(userData))
        
        // Store token if provided
        if (userData.token) {
          token.value = userData.token
          localStorage.setItem('token', userData.token)
        }
        
        // Store user object if provided (for organizers)
        if (userData.user) {
          user.value = userData.user
          localStorage.setItem('user', JSON.stringify(userData.user))
        }
        
        return { 
          success: true, 
          userName: userData.name 
        }
      } else {
        return { 
          success: false, 
          message: response.data.msg || response.data.message || '登录失败' 
        }
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.msg || error.response?.data?.message || error.message || '登录失败'
      return { success: false, message: errorMsg }
    } finally {
      loading.value = false
    }
  }

  // Register
  const register = async (form: RegisterForm) => {
    loading.value = true
    try {
      const response = await authApi.register(form)
      const { token: newToken, user: newUser } = response.data.data
      
      token.value = newToken
      user.value = newUser
      
      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify(newUser))
      
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message || '注册失败' }
    } finally {
      loading.value = false
    }
  }

  // Logout
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = null
      user.value = null
      accountUser.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('accountUser')
    }
  }

  // Get current user
  const getCurrentUser = async () => {
    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data.data
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (error) {
      console.error('Get current user error:', error)
      logout()
    }
  }

  // Update profile
  const updateProfile = async (data: Partial<User>) => {
    try {
      const response = await authApi.updateProfile(data)
      user.value = response.data.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message || '更新失败' }
    }
  }

  return {
    user,
    accountUser,
    token,
    loading,
    isLoggedIn,
    isAdmin,
    isStudent,
    isOrganizer,
    initAuth,
    login,
    register,
    logout,
    getCurrentUser,
    updateProfile
  }
})
