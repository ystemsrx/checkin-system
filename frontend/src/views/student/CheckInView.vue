<template>
  <div class="checkin-view">
    <app-header />
    
    <div class="container">
      <div class="page-header">
        <h1>活动签到</h1>
        <p>输入签到码进行签到</p>
      </div>

      <el-card class="checkin-card">
        <div class="tab-content">
              <el-form :model="codeForm" label-position="top" style="max-width: 500px; margin: 0 auto">
                <el-form-item label="活动">
                  <el-select
                    v-model="codeForm.activityId"
                    placeholder="请选择活动"
                    style="width: 100%"
                    filterable
                  >
                    <el-option
                      v-for="activity in myActivities"
                      :key="activity.id"
                      :label="activity.title"
                      :value="activity.id"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item label="签到码">
                  <el-input
                    v-model="codeForm.code"
                    placeholder="请输入6位签到码"
                    maxlength="6"
                    show-word-limit
                    size="large"
                  >
                    <template #prepend>
                      <el-icon><Key /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    size="large"
                    style="width: 100%"
                    :loading="checking"
                    @click="handleCodeCheckIn"
                  >
                    确认签到
                  </el-button>
                </el-form-item>
              </el-form>

              <div class="tips">
                <el-alert
                  title="提示"
                  type="info"
                  :closable="false"
                  show-icon
                >
                  <p>请向活动组织者获取签到码</p>
                </el-alert>
              </div>
        </div>
      </el-card>

      <!-- Recent Check-ins -->
      <el-card class="recent-card">
        <template #header>
          <div class="card-header">
            <span>最近签到</span>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="item in recentCheckIns"
            :key="item.id"
            :timestamp="formatTime(item.checkedInAt)"
            placement="top"
          >
            <el-card>
              <h4>{{ item.activityTitle || '未知活动' }}</h4>
              <p>签到方式: 签到码</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { checkinApi } from '@/api/checkin'
import { registrationApi } from '@/api/registration'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import dayjs from 'dayjs'
import { Key } from '@element-plus/icons-vue'
import type { Activity, CheckIn } from '@/types'

const checking = ref(false)
const myActivities = ref<Activity[]>([])
const recentCheckIns = ref<CheckIn[]>([])

const codeForm = reactive({
  activityId: null as number | null,
  code: ''
})


onMounted(async () => {
  await loadMyActivities()
  await loadRecentCheckIns()
})


const loadMyActivities = async () => {
  try {
    const response = await registrationApi.getMyRegistrations({ pageSize: 100 })
    // Filter to get only registered activities that are ongoing
    const registrations = response.data.data.items.filter(
      (r: any) => r.status === 'registered' && r.activity && r.activity.status === 'ongoing'
    )
    // Extract activity data from registrations
    myActivities.value = registrations.map((r: any) => r.activity)
  } catch (error) {
    console.error('Load activities error:', error)
    ElMessage.error('加载活动列表失败')
  }
}

const loadRecentCheckIns = async () => {
  try {
    const response = await checkinApi.getMyRecentCheckIns()
    recentCheckIns.value = response.data.data
  } catch (error) {
    console.error('Load recent check-ins error:', error)
    // 不显示错误消息，因为这不是关键功能
  }
}


const handleCodeCheckIn = async () => {
  if (!codeForm.activityId) {
    ElMessage.warning('请选择活动')
    return
  }
  if (!codeForm.code || codeForm.code.length !== 6) {
    ElMessage.warning('请输入6位签到码')
    return
  }

  checking.value = true
  try {
    await checkinApi.checkInWithCode({
      activityId: codeForm.activityId,
      code: codeForm.code
    })
    ElMessage.success('签到成功')
    codeForm.code = ''
    // 刷新最近签到列表
    await loadRecentCheckIns()
  } catch (error: any) {
    // 提取后端返回的错误消息
    const errorMessage = error.response?.data?.message || error.message || '签到失败'
    ElMessage.error(errorMessage)
  } finally {
    checking.value = false
  }
}

const formatTime = (time: string) => {
  // 后端返回的UTC时间字符串已经带'Z'后缀，浏览器会自动转换为本地时间
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}
</script>

<style scoped>
.checkin-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.container {
  max-width: 1000px;
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

.checkin-card {
  margin-bottom: 24px;
}

.tab-content {
  padding: 24px 0;
}


.tips {
  max-width: 500px;
  margin: 0 auto;
}

.recent-card {
  margin-top: 24px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}
</style>
