<template>
  <div class="statistics-view">
    <app-header />
    
    <div class="container">
      <el-button :icon="ArrowLeft" @click="router.back()" class="back-btn">返回</el-button>

      <el-card v-loading="loading">
        <template #header>
          <div class="card-header">
            <h2>活动统计</h2>
            <el-button type="primary" :icon="Download" @click="handleExport">导出报表</el-button>
          </div>
        </template>

        <el-descriptions :column="2" border style="margin-bottom: 24px">
          <el-descriptions-item label="活动名称">{{ statistics?.activityTitle }}</el-descriptions-item>
          <el-descriptions-item label="总报名数">{{ statistics?.totalRegistrations }}</el-descriptions-item>
          <el-descriptions-item label="总签到数">{{ statistics?.totalCheckIns }}</el-descriptions-item>
          <el-descriptions-item label="签到率">{{ statistics?.checkInRate }}%</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h3 style="margin-bottom: 16px">报名学生列表</h3>
        <el-table v-loading="loadingRegistrations" :data="registrations" style="width: 100%">
          <el-table-column prop="userName" label="姓名" width="120" />
          <el-table-column prop="userEmail" label="学号" width="150" />
          <el-table-column prop="subItem" label="项目" width="120">
            <template #default="{ row }">
              {{ row.subItem || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'checked_in' ? 'success' : 'primary'">
                {{ row.status === 'checked_in' ? '已签到' : '已报名' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="registeredAt" label="报名时间" width="160">
            <template #default="{ row }">{{ formatTime(row.registeredAt) }}</template>
          </el-table-column>
          <el-table-column prop="checkedInAt" label="签到时间" width="160">
            <template #default="{ row }">
              {{ row.checkedInAt ? formatTime(row.checkedInAt) : '-' }}
            </template>
          </el-table-column>
        </el-table>

        <div v-if="pagination.total > 0" class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            layout="total, prev, pager, next"
            @current-change="loadRegistrations"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { statisticsApi } from '@/api/statistics'
import { registrationApi } from '@/api/registration'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import { ArrowLeft, Download } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import type { ActivityStatistics, Registration } from '@/types'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const loadingRegistrations = ref(false)
const statistics = ref<ActivityStatistics | null>(null)
const registrations = ref<Registration[]>([])
const pagination = ref({ total: 0, page: 1, pageSize: 20 })
const activityId = Number(route.params.id)

onMounted(() => {
  loadStatistics()
  loadRegistrations()
})

const loadStatistics = async () => {
  loading.value = true
  try {
    const response = await statisticsApi.getActivityStatistics(activityId)
    statistics.value = response.data.data
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const loadRegistrations = async () => {
  loadingRegistrations.value = true
  try {
    const response = await registrationApi.getActivityRegistrations(activityId, {
      page: pagination.value.page,
      pageSize: pagination.value.pageSize
    })
    const data = response.data.data
    registrations.value = data.items
    pagination.value.total = data.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载报名列表失败')
  } finally {
    loadingRegistrations.value = false
  }
}

const formatTime = (time: string) => {
  const timeStr = time.endsWith('Z') || time.includes('+') ? time : time + 'Z'
  return dayjs(timeStr).format('YYYY-MM-DD HH:mm')
}

const handleExport = async () => {
  try {
    const response = await statisticsApi.exportStatistics(activityId)
    
    // Create a blob from the response
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Extract filename from Content-Disposition header or use default
    const contentDisposition = response.headers['content-disposition']
    let filename = `活动统计_${activityId}_${new Date().getTime()}.xlsx`
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
        // Decode if it's URL encoded
        try {
          filename = decodeURIComponent(filename)
        } catch (e) {
          // Keep original filename if decode fails
        }
      }
    }
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    
    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  }
}
</script>

<style scoped>
.statistics-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.back-btn {
  margin-bottom: 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}
h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}
h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
