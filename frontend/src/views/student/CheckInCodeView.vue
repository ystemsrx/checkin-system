<template>
  <div class="checkin-code-view">
    <app-header />
    
    <div class="container">
      <el-card class="checkin-card">
        <template #header>
          <h2>签到</h2>
        </template>

        <el-alert
          title="温馨提示"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <p>1. 下拉框中只显示您已报名且正在进行中的活动</p>
          <p>2. 签到码由组织者在活动现场提供（6位数字）</p>
          <p>3. 如果找不到活动，请确认活动是否已开始</p>
        </el-alert>

        <div class="checkin-form">
          <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
            <el-form-item label="选择活动" prop="activityId">
              <el-select
                v-model="form.activityId"
                placeholder="请选择已报名的活动"
                filterable
                style="width: 100%"
                @focus="loadMyActivities"
                :loading="loadingActivities"
              >
                <el-option
                  v-for="activity in myActivities"
                  :key="activity.id"
                  :label="`${activity.title} (ID: ${activity.id})`"
                  :value="activity.id"
                >
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>{{ activity.title }}</span>
                    <el-tag :type="getStatusType(activity.status)" size="small">
                      {{ getStatusLabel(activity.status) }}
                    </el-tag>
                  </div>
                </el-option>
                <template v-if="!loadingActivities && myActivities.length === 0" #empty>
                  <div style="padding: 20px; text-align: center; color: #909399;">
                    <p>暂无正在进行中的活动</p>
                    <el-link type="primary" @click="router.push('/activities')">
                      去活动列表报名 →
                    </el-link>
                  </div>
                </template>
              </el-select>
              <div class="form-tip">
                <el-link type="primary" @click="router.push('/my-activities')">
                  去"我的活动"查看 →
                </el-link>
              </div>
            </el-form-item>

            <el-form-item label="签到码" prop="code">
              <el-input
                v-model="form.code"
                placeholder="请输入6位签到码"
                maxlength="6"
                show-word-limit
                clearable
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
                :loading="submitting"
                @click="handleCheckIn"
                style="width: 100%"
              >
                <el-icon><CircleCheck /></el-icon>
                <span>签到</span>
              </el-button>
            </el-form-item>
          </el-form>

          <el-divider>或</el-divider>

          <el-button
            type="success"
            size="large"
            :icon="View"
            @click="router.push('/student/checkin')"
            style="width: 100%"
          >
            扫描二维码签到
          </el-button>
        </div>
      </el-card>

      <!-- 签到成功提示 -->
      <el-dialog
        v-model="successDialogVisible"
        title="签到成功"
        width="400px"
        :show-close="false"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
      >
        <div class="success-content">
          <el-result
            icon="success"
            title="签到成功！"
            :sub-title="`活动：${checkedActivity?.title || ''}`"
          >
            <template #extra>
              <div class="checkin-info">
                <p><strong>签到时间：</strong>{{ formatTime(checkInTime) }}</p>
                <p><strong>签到方式：</strong>签到码</p>
              </div>
            </template>
          </el-result>
        </div>
        <template #footer>
          <el-button type="primary" @click="handleCloseSuccess">
            确定
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { checkinApi } from '@/api/checkin'
import { activityApi } from '@/api/activity'
import { registrationApi } from '@/api/registration'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import dayjs from 'dayjs'
import { Key, CircleCheck, View } from '@element-plus/icons-vue'
import type { Activity } from '@/types'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const successDialogVisible = ref(false)
const checkInTime = ref('')
const checkedActivity = ref<Activity | null>(null)
const myActivities = ref<Activity[]>([])
const loadingActivities = ref(false)

const form = reactive({
  activityId: null as number | null,
  code: ''
})

const rules: FormRules = {
  activityId: [
    { required: true, message: '请输入活动ID', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入签到码', trigger: 'blur' },
    { len: 6, message: '签到码必须是6位数字', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '签到码必须是6位数字', trigger: 'blur' }
  ]
}

const handleCheckIn = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        // 先获取活动信息
        try {
          const activityResponse = await activityApi.getActivityById(form.activityId!)
          checkedActivity.value = activityResponse.data.data
        } catch (error: any) {
          ElMessage.error('活动不存在，请检查活动ID是否正确')
          submitting.value = false
          return
        }

        // 执行签到
        const response = await checkinApi.checkInWithCode({
          activityId: form.activityId!,
          code: form.code
        })

        checkInTime.value = response.data.data.checkedInAt
        successDialogVisible.value = true

        // 清空表单
        form.activityId = null
        form.code = ''
        formRef.value?.resetFields()
      } catch (error: any) {
        // 处理不同的错误情况
        const errorMsg = error.response?.data?.message || error.message || '签到失败'
        
        if (errorMsg.includes('未报名')) {
          ElMessage.error('您还未报名该活动，请先报名后再签到')
        } else if (errorMsg.includes('已经签到')) {
          ElMessage.warning('您已经签到过了')
        } else if (errorMsg.includes('签到码无效')) {
          ElMessage.error('签到码无效，请检查是否输入正确')
        } else if (errorMsg.includes('签到码已过期')) {
          ElMessage.error('签到码已过期，请联系组织者重新生成')
        } else {
          ElMessage.error(errorMsg)
        }
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleCloseSuccess = () => {
  successDialogVisible.value = false
  router.push('/student/my-activities')
}

const formatTime = (time: string) => {
  // 后端返回的UTC时间字符串已经带'Z'后缀，浏览器会自动转换为本地时间
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const loadMyActivities = async () => {
  if (loadingActivities.value || myActivities.value.length > 0) return
  
  loadingActivities.value = true
  try {
    const response = await registrationApi.getMyRegistrations({ pageSize: 100 })
    // 只显示正在进行中的活动
    myActivities.value = response.data.data.items.filter((item: any) => {
      return item.activity && item.activity.status === 'ongoing'
    }).map((item: any) => item.activity)
  } catch (error: any) {
    console.error('加载活动列表失败:', error)
  } finally {
    loadingActivities.value = false
  }
}

const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    upcoming: 'warning',
    ongoing: 'success',
    completed: 'info',
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
</script>

<style scoped>
.checkin-code-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
}

.container {
  max-width: 600px;
  margin: 0 auto;
  padding-top: 60px;
}

.checkin-card {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.checkin-card h2 {
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.checkin-form {
  padding: 24px;
}

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.success-content {
  text-align: center;
}

.checkin-info {
  margin-top: 16px;
  text-align: left;
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
}

.checkin-info p {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}
</style>
