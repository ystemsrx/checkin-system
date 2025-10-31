<template>
  <div class="activity-list-view">
    <app-header />
    
    <div class="container">
      <div class="page-header">
        <h1>活动列表</h1>
        <p>浏览并报名参加各类班级活动</p>
      </div>

      <!-- Filter Section -->
      <el-card class="filter-card" shadow="never">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="关键词">
            <el-input
              v-model="filterForm.keyword"
              placeholder="搜索活动名称"
              clearable
              :prefix-icon="Search"
              style="width: 200px"
            />
          </el-form-item>

          <el-form-item label="分类">
            <el-select
              v-model="filterForm.category"
              placeholder="选择分类"
              clearable
              style="width: 150px"
            >
              <el-option label="学术" value="academic" />
              <el-option label="文艺" value="cultural" />
              <el-option label="体育" value="sports" />
              <el-option label="志愿" value="volunteer" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>

          <el-form-item label="状态">
            <el-select
              v-model="filterForm.status"
              placeholder="选择状态"
              clearable
              style="width: 150px"
            >
              <el-option label="未开始" value="upcoming" />
              <el-option label="进行中" value="ongoing" />
              <el-option label="已结束" value="completed" />
            </el-select>
          </el-form-item>

          <el-form-item label="开始时间">
            <el-date-picker
              v-model="filterForm.startDate"
              type="date"
              placeholder="选择日期"
              clearable
              style="width: 180px"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :icon="Search" @click="handleSearch">
              搜索
            </el-button>
            <el-button :icon="RefreshLeft" @click="handleReset">
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Activity Grid -->
      <div v-loading="loading" class="activity-grid">
        <activity-card
          v-for="activity in activities"
          :key="activity.id"
          :activity="activity"
        />
      </div>

      <!-- Empty State -->
      <el-empty
        v-if="!loading && activities.length === 0"
        description="暂无活动"
      />

      <!-- Pagination -->
      <div v-if="pagination.total > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useActivityStore } from '@/stores/activity'
import { storeToRefs } from 'pinia'
import AppHeader from '@/components/layout/AppHeader.vue'
import ActivityCard from '@/components/ActivityCard.vue'
import { Search, RefreshLeft } from '@element-plus/icons-vue'
import type { ActivityFilter } from '@/types'

const activityStore = useActivityStore()
const { activities, pagination, loading } = storeToRefs(activityStore)

const filterForm = reactive<ActivityFilter & { startDate?: Date }>({
  keyword: '',
  category: undefined,
  status: undefined,
  startDate: undefined
})

onMounted(() => {
  loadActivities()
})

const loadActivities = async () => {
  const params: any = {
    page: pagination.value.page,
    pageSize: pagination.value.pageSize
  }

  if (filterForm.keyword) params.keyword = filterForm.keyword
  if (filterForm.category) params.category = filterForm.category
  if (filterForm.status) params.status = filterForm.status
  if (filterForm.startDate) {
    params.startDate = filterForm.startDate.toISOString().split('T')[0]
  }

  await activityStore.fetchActivities(params)
}

const handleSearch = () => {
  pagination.value.page = 1
  loadActivities()
}

const handleReset = () => {
  filterForm.keyword = ''
  filterForm.category = undefined
  filterForm.status = undefined
  filterForm.startDate = undefined
  pagination.value.page = 1
  loadActivities()
}

const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadActivities()
}

const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.page = 1
  loadActivities()
}
</script>

<style scoped>
.activity-list-view {
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

.filter-card {
  margin-bottom: 24px;
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}
</style>
