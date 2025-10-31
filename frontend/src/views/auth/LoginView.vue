<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <el-icon :size="48" color="#409eff"><Calendar /></el-icon>
        <h2>班级活动报名系统</h2>
        <p>欢迎登录</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        size="large"
      >
        <el-form-item label="账号（学号）" prop="account">
          <el-input
            v-model="form.account"
            placeholder="请输入学号"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Calendar } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  account: '',
  password: ''
})

const rules: FormRules = {
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      const result = await authStore.login(form)
      loading.value = false

      if (result.success) {
        // Show welcome message with user name
        ElMessage.success(`欢迎回来，${result.userName}！`)
        
        // Redirect based on role
        let defaultRedirect = '/activities'
        if (authStore.isAdmin) {
          defaultRedirect = '/admin/manage-organizers'
        } else if (authStore.isOrganizer) {
          defaultRedirect = '/organizer/dashboard'
        }
        
        const redirect = (route.query.redirect as string) || defaultRedirect
        router.push(redirect)
      } else {
        // 显示明确的错误提示，不清空输入框
        const errorMsg = result.message || '登录失败'
        // 如果包含"账号"或"密码"或"错误"等关键词，直接显示；否则显示通用错误
        if (errorMsg.includes('账号') || errorMsg.includes('密码') || errorMsg.includes('错误') || errorMsg.includes('不存在')) {
          ElMessage.error(errorMsg)
        } else {
          ElMessage.error('账号或密码错误，请检查后重试')
        }
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%);
  position: relative;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(96, 165, 250, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 20%, rgba(147, 197, 253, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.login-box {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 
    0 8px 32px rgba(59, 130, 246, 0.15),
    0 2px 8px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h2 {
  margin: 16px 0 8px;
  font-size: 24px;
  color: #303133;
}

.login-header p {
  color: #909399;
  font-size: 14px;
}

.login-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #606266;
}

.login-footer span {
  margin-right: 8px;
}
</style>
