<template>
  <div class="registrations-view">
    <app-header />
    
    <div class="container">
      <el-button :icon="ArrowLeft" @click="router.back()" class="back-btn">返回</el-button>

      <el-card>
        <template #header>
          <div class="card-header">
            <h2>报名列表</h2>
            <el-button type="primary" :icon="Download" @click="handleExport">导出</el-button>
          </div>
        </template>

        <el-table v-loading="loading" :data="registrations" style="width: 100%">
          <el-table-column prop="userName" label="姓名" width="120" />
          <el-table-column prop="userEmail" label="学号" width="150" />
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
import { registrationApi } from '@/api/registration'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import dayjs from 'dayjs'
import { ArrowLeft, Download } from '@element-plus/icons-vue'
import type { Registration } from '@/types'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const registrations = ref<Registration[]>([])
const pagination = ref({ total: 0, page: 1, pageSize: 20 })
const activityId = Number(route.params.id)

onMounted(() => loadRegistrations())

const loadRegistrations = async () => {
  loading.value = true
  try {
    const response = await registrationApi.getActivityRegistrations(activityId, {
      page: pagination.value.page,
      pageSize: pagination.value.pageSize
    })
    const data = response.data.data
    registrations.value = data.items
    pagination.value.total = data.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (time: string) => {
  // 后端返回的UTC时间字符串已经带'Z'后缀，浏览器会自动转换为本地时间
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}
</script>

<style scoped>
.registrations-view {
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
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
