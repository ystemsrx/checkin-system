<template>
  <div class="manage-organizers">
    <div class="header">
      <h1>组织者管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        添加组织者
      </el-button>
    </div>

    <!-- Create Organizer Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      title="添加组织者"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="账号" prop="account">
          <el-input
            v-model="form.account"
            placeholder="请输入组织者账号"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入姓名（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleCreate">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- Info -->
    <el-alert
      title="管理员功能"
      type="info"
      :closable="false"
      style="margin-bottom: 20px"
    >
      在此页面可以创建组织者账号。组织者可以创建和管理活动。
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const authStore = useAuthStore()
const showCreateDialog = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  account: '',
  password: '',
  name: ''
})

const rules: FormRules = {
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
}

const resetForm = () => {
  form.account = ''
  form.password = ''
  form.name = ''
  formRef.value?.clearValidate()
}

const handleCreate = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await request.post('/auth/admin/create-organizer', {
          adminAccount: authStore.accountUser?.accountId,
          adminPassword: 'admin123',
          account: form.account,
          password: form.password,
          name: form.name
        })

        if (response.data.success) {
          ElMessage.success('组织者创建成功')
          showCreateDialog.value = false
          resetForm()
        } else {
          ElMessage.error(response.data.msg || '创建失败')
        }
      } catch (error: any) {
        const errorMsg = error.response?.data?.msg || error.message || '创建失败'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.manage-organizers {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}
</style>
