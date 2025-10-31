import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface ActiveCheckInCode {
  activityId: number
  activityTitle: string
  code: string
  expiresAt: string
  startedAt: string
}

export const useCheckinStore = defineStore('checkin', () => {
  // 当前活跃的签到码
  const activeCheckInCode = ref<ActiveCheckInCode | null>(null)
  
  // 是否显示悬浮窗
  const showFloatingWindow = ref(false)
  
  // 设置活跃的签到码
  const setActiveCheckInCode = (data: ActiveCheckInCode | null) => {
    activeCheckInCode.value = data
    if (data) {
      showFloatingWindow.value = true
      // 保存到 localStorage 以便刷新后恢复
      localStorage.setItem('activeCheckInCode', JSON.stringify(data))
    } else {
      localStorage.removeItem('activeCheckInCode')
    }
  }
  
  // 从 localStorage 恢复签到码
  const restoreCheckInCode = () => {
    const stored = localStorage.getItem('activeCheckInCode')
    if (stored) {
      try {
        const data = JSON.parse(stored)
        // 检查是否过期 - 正确解析UTC时间
        const expiresStr = data.expiresAt
        const expiresTime = expiresStr.endsWith('Z') || expiresStr.includes('+') 
          ? expiresStr 
          : expiresStr + 'Z'
        if (new Date(expiresTime) > new Date()) {
          activeCheckInCode.value = data
          showFloatingWindow.value = true
        } else {
          // 已过期，静默清除（不显示任何提示）
          localStorage.removeItem('activeCheckInCode')
        }
      } catch (e) {
        console.error('Failed to restore check-in code:', e)
        // 清除损坏的数据
        localStorage.removeItem('activeCheckInCode')
      }
    }
  }
  
  // 清除签到码
  const clearCheckInCode = () => {
    activeCheckInCode.value = null
    showFloatingWindow.value = false
    localStorage.removeItem('activeCheckInCode')
  }
  
  // 切换悬浮窗显示状态
  const toggleFloatingWindow = () => {
    showFloatingWindow.value = !showFloatingWindow.value
  }
  
  // 检查签到码是否过期
  const isExpired = computed(() => {
    if (!activeCheckInCode.value) return true
    // 正确解析UTC时间
    const expiresStr = activeCheckInCode.value.expiresAt
    const expiresTime = expiresStr.endsWith('Z') || expiresStr.includes('+') 
      ? expiresStr 
      : expiresStr + 'Z'
    return new Date(expiresTime) <= new Date()
  })
  
  return {
    activeCheckInCode,
    showFloatingWindow,
    isExpired,
    setActiveCheckInCode,
    restoreCheckInCode,
    clearCheckInCode,
    toggleFloatingWindow
  }
})
