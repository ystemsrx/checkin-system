<template>
  <div class="dashboard-view">
    <app-header />
    
    <div class="container">
      <div class="page-header">
        <h1>控制台</h1>
        <p>活动数据概览</p>
      </div>

      <div v-loading="loading" class="stats-grid">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #ecf5ff">
              <el-icon :size="32" color="#409eff"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">总活动数</p>
              <h2 class="stat-value">{{ stats.totalActivities }}</h2>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f0f9ff">
              <el-icon :size="32" color="#67c23a"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">总报名数</p>
              <h2 class="stat-value">{{ stats.totalRegistrations }}</h2>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #fef0f0">
              <el-icon :size="32" color="#f56c6c"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">总签到数</p>
              <h2 class="stat-value">{{ stats.totalCheckIns }}</h2>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #fdf6ec">
              <el-icon :size="32" color="#e6a23c"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">平均签到率</p>
              <h2 class="stat-value">{{ stats.averageCheckInRate }}%</h2>
            </div>
          </div>
        </el-card>
      </div>

      <div class="content-grid">
        <el-card class="recent-activities">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
              <el-button
                type="primary"
                size="small"
                :icon="Plus"
                @click="router.push('/organizer/activities/create')"
              >
                创建活动
              </el-button>
            </div>
          </template>
          <el-table :data="recentActivities" style="width: 100%">
            <el-table-column prop="title" label="活动名称" min-width="200">
              <template #default="{ row }">
                <el-link type="primary" @click="goToActivity(row.id)">
                  {{ row.title }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag :type="getCategoryType(row.category)">
                  {{ getCategoryLabel(row.category) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" effect="plain">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="currentParticipants" label="报名/限制" width="120">
              <template #default="{ row }">
                {{ row.currentParticipants }} / {{ row.maxParticipants }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  :icon="View"
                  @click="goToRegistrations(row.id)"
                >
                  查看统计
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card class="quick-actions">
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="actions-list">
            <el-button
              class="action-btn"
              @click="router.push('/organizer/activities/create')"
            >
              <el-icon><Plus /></el-icon>
              <span>创建新活动</span>
            </el-button>
            <el-button
              class="action-btn"
              @click="router.push('/organizer/activities')"
            >
              <el-icon><Management /></el-icon>
              <span>管理活动</span>
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { statisticsApi } from '@/api/statistics'
import { activityApi } from '@/api/activity'
import AppHeader from '@/components/layout/AppHeader.vue'
import {
  Calendar,
  UserFilled,
  CircleCheck,
  TrendCharts,
  Plus,
  View,
  Management
} from '@element-plus/icons-vue'
import type { Activity } from '@/types'

const router = useRouter()

const loading = ref(false)
const stats = ref({
  totalActivities: 0,
  totalRegistrations: 0,
  totalCheckIns: 0,
  averageCheckInRate: 0
})
const recentActivities = ref<Activity[]>([])

onMounted(() => {
  loadStatistics()
  loadRecentActivities()
})

const loadStatistics = async () => {
  loading.value = true
  try {
    const response = await statisticsApi.getOrganizerStatistics()
    const data = response.data.data
    stats.value = {
      totalActivities: data.totalActivities,
      totalRegistrations: data.totalRegistrations,
      totalCheckIns: data.totalCheckIns,
      averageCheckInRate: Math.round(data.averageCheckInRate)
    }
  } catch (error) {
    console.error('Load statistics error:', error)
  } finally {
    loading.value = false
  }
}

const loadRecentActivities = async () => {
  try {
    const response = await activityApi.getMyActivities({ pageSize: 5 })
    recentActivities.value = response.data.data.items
  } catch (error) {
    console.error('Load activities error:', error)
  }
}

const getCategoryType = (category: string) => {
  const types: Record<string, any> = {
    academic: 'primary',
    cultural: 'success',
    sports: 'warning',
    volunteer: 'info',
    other: 'default'
  }
  return types[category] || 'default'
}

const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    academic: '学术',
    cultural: '文艺',
    sports: '体育',
    volunteer: '志愿',
    other: '其他'
  }
  return labels[category] || '其他'
}

const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    upcoming: 'info',
    ongoing: 'success',
    completed: 'default',
    cancelled: 'danger'
  }
  return types[status] || 'default'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    upcoming: '未开始',
    ongoing: '进行中',
    completed: '已结束',
    cancelled: '已取消'
  }
  return labels[status] || '未知'
}

const goToActivity = (id: number) => {
  router.push(`/activities/${id}`)
}

const goToRegistrations = (id: number) => {
  router.push(`/organizer/activities/${id}/statistics`)
}
</script>

<style scoped>
.dashboard-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.page-header p {
  font-size: 14px;
  color: #909399;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.stat-card {
  cursor: default;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
  height: 64px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
