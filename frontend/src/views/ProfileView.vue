<template>
  <div class="profile-view">
    <app-header />
    
    <div class="container">
      <el-card>
        <template #header><h2>个人资料</h2></template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户名">
            {{ authStore.accountUser?.accountId || authStore.user?.username }}
          </el-descriptions-item>
          <el-descriptions-item label="姓名">
            {{ getDisplayName() }}
          </el-descriptions-item>
          <el-descriptions-item label="角色">
            {{ getRoleDisplay() }}
          </el-descriptions-item>
          <el-descriptions-item :label="getRegistrationTimeLabel()">
            {{ getRegistrationTime() }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/layout/AppHeader.vue'
import dayjs from 'dayjs'

const authStore = useAuthStore()
const formatTime = (time: string) => {
  // 后端返回的是UTC时间字符串，需要转换为本地时间显示
  // 如果字符串不包含时区信息，添加'Z'表示UTC
  const timeStr = time.endsWith('Z') || time.includes('+') ? time : time + 'Z'
  return dayjs(timeStr).format('YYYY-MM-DD HH:mm')
}

const getRoleDisplay = () => {
  // Check accountUser first (for students logged in via API)
  const role = authStore.accountUser?.role || authStore.user?.role
  
  if (role === 'student') return '学生'
  if (role === 'organizer') return '组织者'
  if (role === 'admin') return '管理员'
  return '未知'
}

const getDisplayName = () => {
  // For students: show name from accountUser
  if (authStore.accountUser?.role === 'student') {
    return authStore.accountUser?.name || '-'
  }
  // For organizers: show name from user, fallback to username
  if (authStore.user?.role === 'organizer') {
    return authStore.user?.name || authStore.user?.username || '-'
  }
  // Fallback
  return authStore.accountUser?.name || authStore.user?.name || authStore.user?.username || '-'
}

const getRegistrationTimeLabel = () => {
  // For students: show "首次登录时间"
  if (authStore.accountUser?.role === 'student') {
    return '首次登录时间'
  }
  // For organizers: show "注册时间"
  return '注册时间'
}

const getRegistrationTime = () => {
  // For students: show first login time from accountUser (Credential created_at)
  if (authStore.accountUser?.role === 'student' && authStore.accountUser?.firstLoginTime) {
    return formatTime(authStore.accountUser.firstLoginTime)
  }
  // For organizers: show user created_at
  if (authStore.user?.createdAt) {
    return formatTime(authStore.user.createdAt)
  }
  return '-'
}
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}
h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}
</style>
