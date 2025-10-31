<template>
  <el-card class="activity-card" shadow="hover" @click="handleClick">
    <div class="card-cover">
      <el-image 
        :src="activity.coverImage ? getImageUrl(activity.coverImage) : defaultCoverImage" 
        fit="cover"
        class="cover-image"
      >
        <template #error>
          <div class="image-slot">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
    </div>
    
    <div class="card-header">
      <el-tag :type="categoryType">{{ categoryLabel }}</el-tag>
      <el-tag :type="statusType" effect="plain">{{ statusLabel }}</el-tag>
    </div>

    <h3 class="activity-title">{{ activity.title }}</h3>
    
    <div class="activity-info">
      <div class="info-item">
        <el-icon><Clock /></el-icon>
        <span>{{ formatTime(activity.startTime) }}</span>
      </div>
      <div class="info-item">
        <el-icon><Location /></el-icon>
        <span>{{ activity.location }}</span>
      </div>
      <div class="info-item">
        <el-icon><User /></el-icon>
        <span>{{ activity.currentParticipants }}/{{ activity.maxParticipants }}</span>
      </div>
      <div class="info-item">
        <el-icon><UserFilled /></el-icon>
        <span>{{ activity.organizerName }}</span>
      </div>
    </div>

    <div class="activity-description">
      {{ truncateText(activity.description, 100) }}
    </div>

    <div class="activity-footer">
      <el-progress
        :percentage="participantPercentage"
        :status="participantPercentage >= 100 ? 'success' : undefined"
        :stroke-width="6"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Activity } from '@/types'
import dayjs from 'dayjs'
import { Clock, Location, User, UserFilled, Picture } from '@element-plus/icons-vue'

interface Props {
  activity: Activity
}

const props = defineProps<Props>()
const router = useRouter()

const categoryType = computed(() => {
  const types: Record<string, any> = {
    academic: 'primary',
    cultural: 'success',
    sports: 'warning',
    volunteer: 'info',
    other: 'default'
  }
  return types[props.activity.category] || 'default'
})

const categoryLabel = computed(() => {
  const labels: Record<string, string> = {
    academic: '学术',
    cultural: '文艺',
    sports: '体育',
    volunteer: '志愿',
    other: '其他'
  }
  return labels[props.activity.category] || '其他'
})

const statusType = computed(() => {
  const types: Record<string, any> = {
    upcoming: 'info',
    ongoing: 'success',
    completed: 'default',
    cancelled: 'danger'
  }
  return types[props.activity.status] || 'default'
})

const statusLabel = computed(() => {
  const labels: Record<string, string> = {
    upcoming: '未开始',
    ongoing: '进行中',
    completed: '已结束',
    cancelled: '已取消'
  }
  return labels[props.activity.status] || '未知'
})

const participantPercentage = computed(() => {
  return Math.round((props.activity.currentParticipants / props.activity.maxParticipants) * 100)
})

const formatTime = (time: string) => {
  // 后端返回的是UTC时间字符串，需要转换为本地时间显示
  const timeStr = time.endsWith('Z') || time.includes('+') ? time : time + 'Z'
  return dayjs(timeStr).format('YYYY-MM-DD HH:mm')
}

// 默认封面图片
const defaultCoverImage = '/default-cover.svg'

const truncateText = (text: string, length: number) => {
  return text.length > length ? text.substring(0, length) + '...' : text
}

// 缓存 base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
const BASE_URL_WITHOUT_API = API_BASE_URL.replace('/api', '')

const getImageUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) {
    return url
  }
  // 如果 URL 以 /api 开头，说明是完整的 API 路径，需要去掉 /api 前缀
  if (url.startsWith('/api/')) {
    return BASE_URL_WITHOUT_API + url
  }
  // 否则直接拼接
  return API_BASE_URL + url
}

const handleClick = () => {
  router.push(`/activities/${props.activity.id}`)
}
</script>

<style scoped>
.activity-card {
  cursor: pointer;
  transition: transform 0.3s;
  height: 100%;
  overflow: hidden;
}

.card-cover {
  margin: -20px -20px 16px -20px;
  height: 180px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}

.activity-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.activity-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #606266;
}

.info-item .el-icon {
  color: #909399;
}

.activity-description {
  font-size: 14px;
  color: #909399;
  line-height: 1.6;
  margin-bottom: 16px;
  min-height: 44px;
}

.activity-footer {
  margin-top: auto;
}
</style>
