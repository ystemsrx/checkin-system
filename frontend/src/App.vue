<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCheckinStore } from '@/stores/checkin'
import CheckInFloatingWindow from '@/components/CheckInFloatingWindow.vue'

const authStore = useAuthStore()
const checkinStore = useCheckinStore()

onMounted(() => {
  authStore.initAuth()
  // 恢复签到码（如果有的话）
  checkinStore.restoreCheckInCode()
})
</script>

<template>
  <div id="app">
    <router-view />
    <!-- 签到码悬浮窗（仅组织者可见） -->
    <CheckInFloatingWindow v-if="authStore.isOrganizer" />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  background-color: #f5f7fa;
}
</style>
