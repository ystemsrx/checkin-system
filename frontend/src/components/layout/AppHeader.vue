<template>
  <el-header class="app-header">
    <div class="header-content">
      <div class="logo" @click="router.push('/')">
        <el-icon :size="28"><Calendar /></el-icon>
        <span>班级活动报名系统</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        :ellipsis="false"
        class="header-menu"
      >
        <el-sub-menu v-if="authStore.isAdmin" index="/admin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>管理</span>
          </template>
          <el-menu-item
            index="/admin/manage-organizers"
            @click="router.push('/admin/manage-organizers')"
          >
            <el-icon><User /></el-icon>
            <span>组织者管理</span>
          </el-menu-item>
          <el-menu-item
            index="/admin/manage-activities"
            @click="router.push('/admin/manage-activities')"
          >
            <el-icon><Management /></el-icon>
            <span>活动管理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/activities" @click="router.push('/activities')">
          <el-icon><List /></el-icon>
          <span>活动列表</span>
        </el-menu-item>

        <template v-if="authStore.isLoggedIn">
          <el-menu-item
            v-if="authStore.isStudent"
            index="/my-activities"
            @click="router.push('/my-activities')"
          >
            <el-icon><Star /></el-icon>
            <span>我的活动</span>
          </el-menu-item>

          <el-menu-item
            v-if="authStore.isStudent"
            index="/checkin"
            @click="router.push('/checkin')"
          >
            <el-icon><Check /></el-icon>
            <span>签到</span>
          </el-menu-item>

          <el-menu-item
            v-if="authStore.isOrganizer"
            index="/organizer/dashboard"
            @click="router.push('/organizer/dashboard')"
          >
            <el-icon><DataAnalysis /></el-icon>
            <span>控制台</span>
          </el-menu-item>

          <el-menu-item
            v-if="authStore.isOrganizer"
            index="/organizer/activities"
            @click="router.push('/organizer/activities')"
          >
            <el-icon><Management /></el-icon>
            <span>管理活动</span>
          </el-menu-item>
        </template>
      </el-menu>

      <div class="header-actions">
        <template v-if="authStore.isLoggedIn">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ authStore.user?.username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="primary" @click="router.push('/login')">登录</el-button>
        </template>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    await authStore.logout()
    ElMessage.success('退出成功')
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.app-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 24px;
  height: 64px;
  line-height: 64px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  cursor: pointer;
  user-select: none;
}

.header-menu {
  flex: 1;
  margin: 0 40px;
  border-bottom: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #303133;
}
</style>
