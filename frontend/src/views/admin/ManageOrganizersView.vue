<template>
  <div class="manage-organizers-page">
    <app-header />
    
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

    <!-- Organizers List -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>组织者列表</span>
        </div>
      </template>
      
      <el-table
        :data="organizers"
        v-loading="loadingList"
        style="width: 100%"
      >
        <el-table-column prop="username" label="账号" width="180" />
        <el-table-column prop="name" label="姓名" width="180" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.createdAt) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import AppHeader from '@/components/layout/AppHeader.vue'

const authStore = useAuthStore()
const showCreateDialog = ref(false)
const loading = ref(false)
const loadingList = ref(false)
const formRef = ref<FormInstance>()
const organizers = ref<any[]>([])

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

const fetchOrganizers = async () => {
  loadingList.value = true
  try {
    const response = await request.get('/auth/admin/organizers', {
      params: {
        adminAccount: authStore.accountUser?.accountId,
        adminPassword: 'admin123'
      }
    })

    if (response.data.success) {
      organizers.value = response.data.data
    } else {
      ElMessage.error(response.data.msg || '获取组织者列表失败')
    }
  } catch (error: any) {
    const errorMsg = error.response?.data?.msg || error.message || '获取组织者列表失败'
    ElMessage.error(errorMsg)
  } finally {
    loadingList.value = false
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
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
          // 刷新列表
          fetchOrganizers()
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

onMounted(() => {
  fetchOrganizers()
})
</script>

<style scoped>
.manage-organizers-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
</style>
