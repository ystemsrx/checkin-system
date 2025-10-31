<template>
  <div class="checkin-management-view">
    <app-header />
    
    <div class="container">
      <el-button :icon="ArrowLeft" @click="router.back()" class="back-btn">返回</el-button>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-card>
            <template #header><h3>生成签到二维码</h3></template>
            <div class="qr-section">
              <div v-if="qrData" class="qr-display">
                <div ref="qrCodeRef" class="qr-code"></div>
                <p>请让学生扫描此二维码签到</p>
              </div>
              <el-button v-else type="primary" @click="generateQRCode" :loading="generating">
                生成二维码
              </el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header><h3>生成签到码</h3></template>
            <div class="code-section">
              <div v-if="checkInCode" class="code-display">
                <h1>{{ checkInCode.code }}</h1>
                <p>有效期至: {{ formatTime(checkInCode.expiresAt) }}</p>
              </div>
              <el-button v-else type="primary" @click="generateCode" :loading="generating">
                生成签到码
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card style="margin-top: 24px">
        <template #header>
          <div class="card-header">
            <h3>签到统计</h3>
            <el-button type="primary" :icon="Refresh" @click="loadStats">刷新</el-button>
          </div>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="总报名人数">{{ stats.total }}</el-descriptions-item>
          <el-descriptions-item label="已签到人数">{{ stats.checkedIn }}</el-descriptions-item>
          <el-descriptions-item label="签到率">{{ stats.rate }}%</el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { checkinApi } from '@/api/checkin'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import dayjs from 'dayjs'
import { ArrowLeft, Refresh } from '@element-plus/icons-vue'
import type { CheckInCode } from '@/types'

const router = useRouter()
const route = useRoute()
const activityId = Number(route.params.id)
const generating = ref(false)
const qrData = ref('')
const qrCodeRef = ref()
const checkInCode = ref<CheckInCode | null>(null)
const stats = ref({ total: 0, checkedIn: 0, rate: 0 })

onMounted(() => loadStats())

const generateQRCode = async () => {
  generating.value = true
  try {
    const response = await checkinApi.generateQRCode(activityId)
    qrData.value = response.data.data.qrData
    // Would use QRCode library here to render
    ElMessage.success('二维码生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败')
  } finally {
    generating.value = false
  }
}

const generateCode = async () => {
  generating.value = true
  try {
    const response = await checkinApi.generateCode(activityId)
    checkInCode.value = response.data.data
    ElMessage.success('签到码生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败')
  } finally {
    generating.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await checkinApi.getCheckInStats(activityId)
    stats.value = response.data.data
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  }
}

const formatTime = (time: string) => {
  const timeStr = time.endsWith('Z') || time.includes('+') ? time : time + 'Z'
  return dayjs(timeStr).format('YYYY-MM-DD HH:mm')
}
</script>

<style scoped>
.checkin-management-view {
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
.qr-section, .code-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  min-height: 300px;
  justify-content: center;
}
.qr-display, .code-display {
  text-align: center;
}
.code-display h1 {
  font-size: 48px;
  font-weight: bold;
  color: #409eff;
  letter-spacing: 8px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header h3 {
  margin: 0;
}
</style>
