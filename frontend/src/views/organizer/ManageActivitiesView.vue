<template>
  <div class="manage-activities-view">
    <app-header />
    
    <div class="container">
      <div class="page-header">
        <h1>管理活动</h1>
        <el-button
          type="primary"
          :icon="Plus"
          @click="router.push('/organizer/activities/create')"
        >
          创建活动
        </el-button>
      </div>

      <el-card>
        <el-table v-loading="loading" :data="activities" style="width: 100%">
          <el-table-column prop="title" label="活动名称" min-width="200" />
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
          <el-table-column prop="startTime" label="开始时间" width="160">
            <template #default="{ row }">
              {{ formatTime(row.startTime) }}
            </template>
          </el-table-column>
          <el-table-column prop="currentParticipants" label="报名人数" width="120">
            <template #default="{ row }">
              {{ row.currentParticipants }} / {{ row.maxParticipants }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="400" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button
                  type="primary"
                  size="small"
                  :icon="Edit"
                  :disabled="row.status === 'ongoing' || row.status === 'completed'"
                  @click="handleEdit(row.id)"
                >
                  编辑
                </el-button>
                <el-button
                  type="info"
                  size="small"
                  :icon="CircleCheck"
                  :disabled="row.status !== 'ongoing'"
                  :class="{ 'checkin-ongoing': row.status === 'ongoing' }"
                  @click="handleCheckIn(row.id)"
                >
                  签到
                </el-button>
                <el-button
                  type="warning"
                  size="small"
                  :icon="DataAnalysis"
                  @click="handleViewStatistics(row.id)"
                >
                  统计
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  :disabled="row.status === 'ongoing'"
                  @click="handleDelete(row.id)"
                >
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="pagination.total > 0" class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { activityApi } from '@/api/activity'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import dayjs from 'dayjs'
import { Plus, Edit, User, CircleCheck, DataAnalysis, Delete } from '@element-plus/icons-vue'
import type { Activity } from '@/types'

const router = useRouter()

const loading = ref(false)
const activities = ref<Activity[]>([])
const pagination = ref({
  total: 0,
  page: 1,
  pageSize: 10
})

onMounted(() => {
  loadActivities()
})

const loadActivities = async () => {
  loading.value = true
  try {
    const response = await activityApi.getMyActivities({
      page: pagination.value.page,
      pageSize: pagination.value.pageSize
    })
    const data = response.data.data
    activities.value = data.items
    pagination.value.total = data.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = () => {
  loadActivities()
}

const handleSizeChange = () => {
  pagination.value.page = 1
  loadActivities()
}

const handleEdit = (id: number) => {
  router.push(`/organizer/activities/${id}/edit`)
}

const handleCheckIn = (id: number) => {
  router.push(`/organizer/activities/${id}/checkin`)
}

const handleViewStatistics = (id: number) => {
  router.push(`/organizer/activities/${id}/statistics`)
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此活动吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await activityApi.deleteActivity(id)
    ElMessage.success('删除成功')
    loadActivities()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
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

const formatTime = (time: string) => {
  // 后端返回的是UTC时间字符串，需要转换为本地时间显示
  const timeStr = time.endsWith('Z') || time.includes('+') ? time : time + 'Z'
  return dayjs(timeStr).format('YYYY-MM-DD HH:mm')
}
</script>

<style scoped>
.manage-activities-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.action-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: nowrap;
}

/* 签到按钮进行中状态的淡紫色 */
.checkin-ongoing:not(.is-disabled) {
  background-color: #d4b5f7 !important;
  border-color: #d4b5f7 !important;
  color: white !important;
}

.checkin-ongoing:not(.is-disabled):hover {
  background-color: #c19ef5 !important;
  border-color: #c19ef5 !important;
}
</style>
