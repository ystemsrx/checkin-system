<template>
  <div class="my-activities-view">
    <app-header />
    
    <div class="container">
      <div class="page-header">
        <h1>我的活动</h1>
        <p>查看已报名的活动</p>
      </div>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="未开始" name="upcoming" />
        <el-tab-pane label="进行中" name="ongoing" />
        <el-tab-pane label="已结束" name="completed" />
      </el-tabs>

      <div v-loading="loading" class="activities-list">
        <el-card
          v-for="registration in filteredRegistrations"
          :key="registration.id"
          class="activity-item"
          shadow="hover"
        >
          <div class="item-content">
            <div class="item-info">
              <h3 @click="goToDetail(registration.activityId)">
                {{ getActivityTitle(registration.activityId) }}
              </h3>
              <div class="meta">
                <el-tag :type="getStatusType(registration.status)">
                  {{ getStatusLabel(registration.status) }}
                </el-tag>
                <el-tag :type="getActivityStatusType(registration.activityId)">
                  {{ getActivityStatusLabel(registration.activityId) }}
                </el-tag>
                <span class="time">
                  <el-icon><Clock /></el-icon>
                  报名时间: {{ formatTime(registration.registeredAt) }}
                </span>
                <span v-if="registration.checkedInAt" class="time">
                  <el-icon><CircleCheck /></el-icon>
                  签到时间: {{ formatTime(registration.checkedInAt) }}
                </span>
              </div>
            </div>
            <div class="item-actions">
              <el-button
                type="primary"
                :icon="View"
                @click="goToDetail(registration.activityId)"
              >
                查看详情
              </el-button>
              <el-button
                v-if="registration.status === 'registered'"
                type="danger"
                :icon="Close"
                @click="handleCancel(registration.activityId)"
              >
                取消报名
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <el-empty
        v-if="!loading && filteredRegistrations.length === 0"
        description="暂无报名活动"
      >
        <el-button type="primary" @click="router.push('/activities')">
          去报名
        </el-button>
      </el-empty>

      <div v-if="pagination.total > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 30]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { registrationApi } from '@/api/registration'
import { activityApi } from '@/api/activity'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import dayjs from 'dayjs'
import { Clock, CircleCheck, View, Close } from '@element-plus/icons-vue'
import type { Registration, Activity } from '@/types'

const router = useRouter()

const activeTab = ref('all')
const loading = ref(false)
const registrations = ref<Registration[]>([])
const activities = ref<Map<number, Activity>>(new Map())
const pagination = reactive({
  total: 0,
  page: 1,
  pageSize: 10
})

onMounted(() => {
  loadRegistrations()
})

const loadRegistrations = async () => {
  loading.value = true
  try {
    const response = await registrationApi.getMyRegistrations({
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    const data = response.data.data
    registrations.value = data.items
    pagination.total = data.total

    // Load activity details
    const activityIds = [...new Set(data.items.map((r: Registration) => r.activityId))]
    await loadActivities(activityIds)
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const loadActivities = async (ids: number[]) => {
  try {
    const promises = ids.map(id => activityApi.getActivityById(id))
    const responses = await Promise.all(promises)
    responses.forEach(response => {
      const activity = response.data.data
      activities.value.set(activity.id, activity)
    })
  } catch (error) {
    console.error('Load activities error:', error)
  }
}

const handleTabChange = () => {
  pagination.page = 1
  loadRegistrations()
}

// 根据活动时间判断状态
const getActivityStatus = (activityId: number) => {
  const activity = activities.value.get(activityId)
  if (!activity) return 'unknown'
  
  // 后端已经返回了正确的状态，直接使用
  return activity.status
}

// 过滤报名记录
const filteredRegistrations = computed(() => {
  if (activeTab.value === 'all') {
    return registrations.value
  }
  
  return registrations.value.filter(reg => {
    const activityStatus = getActivityStatus(reg.activityId)
    return activityStatus === activeTab.value
  })
})

const handlePageChange = () => {
  loadRegistrations()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadRegistrations()
}

const getActivityTitle = (activityId: number) => {
  return activities.value.get(activityId)?.title || '加载中...'
}

const getActivityStatusType = (activityId: number) => {
  const status = getActivityStatus(activityId)
  const types: Record<string, any> = {
    upcoming: 'warning',
    ongoing: 'success',
    completed: 'info'
  }
  return types[status] || 'default'
}

const getActivityStatusLabel = (activityId: number) => {
  const status = getActivityStatus(activityId)
  const labels: Record<string, string> = {
    upcoming: '未开始',
    ongoing: '进行中',
    completed: '已结束'
  }
  return labels[status] || '未知'
}

const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    registered: 'primary',
    checked_in: 'success',
    cancelled: 'info'
  }
  return types[status] || 'default'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    registered: '已报名',
    checked_in: '已签到',
    cancelled: '已取消'
  }
  return labels[status] || '未知'
}

const formatTime = (time: string) => {
  const timeStr = time.endsWith('Z') || time.includes('+') ? time : time + 'Z'
  return dayjs(timeStr).format('YYYY-MM-DD HH:mm')
}

const goToDetail = (activityId: number) => {
  router.push(`/activities/${activityId}`)
}

const handleCancel = async (activityId: number) => {
  try {
    await ElMessageBox.confirm('确定要取消报名吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await registrationApi.cancelRegistration(activityId)
    ElMessage.success('取消成功')
    loadRegistrations()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '取消失败')
    }
  }
}
</script>

<style scoped>
.my-activities-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.container {
  max-width: 1200px;
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

.activities-list {
  margin-top: 24px;
}

.activity-item {
  margin-bottom: 16px;
}

.item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-info {
  flex: 1;
}

.item-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  cursor: pointer;
  transition: color 0.3s;
}

.item-info h3:hover {
  color: #409eff;
}

.meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #909399;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
