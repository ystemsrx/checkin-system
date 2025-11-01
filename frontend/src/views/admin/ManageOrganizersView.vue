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

    <!-- Change Password Dialog -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="500px"
      @close="resetPasswordForm"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="组织者">
          <el-input
            :value="`${currentOrganizer?.name} (${currentOrganizer?.username})`"
            disabled
          />
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleChangePassword">
          确认修改
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
        <el-table-column prop="username" label="账号" width="150" />
        <el-table-column prop="name" label="姓名" width="150" />
        <el-table-column prop="email" label="邮箱" width="220" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.isActive ? 'success' : 'danger'">
              {{ scope.row.isActive ? '已启用' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button
              :type="scope.row.isActive ? 'warning' : 'success'"
              size="small"
              @click="handleToggleStatus(scope.row)"
            >
              {{ scope.row.isActive ? '停用' : '启用' }}
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="handleShowPasswordDialog(scope.row)"
            >
              修改密码
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import AppHeader from '@/components/layout/AppHeader.vue'

const authStore = useAuthStore()
const showCreateDialog = ref(false)
const showPasswordDialog = ref(false)
const loading = ref(false)
const loadingList = ref(false)
const formRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const organizers = ref<any[]>([])
const currentOrganizer = ref<any>(null)

const form = reactive({
  account: '',
  password: '',
  name: ''
})

const passwordForm = reactive({
  newPassword: '',
  confirmPassword: ''
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

const passwordRules: FormRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const resetForm = () => {
  form.account = ''
  form.password = ''
  form.name = ''
  formRef.value?.clearValidate()
}

const resetPasswordForm = () => {
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  currentOrganizer.value = null
  passwordFormRef.value?.clearValidate()
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

const handleToggleStatus = async (organizer: any) => {
  const action = organizer.isActive ? '停用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}组织者 ${organizer.name} (${organizer.username}) 吗？${
        organizer.isActive ? '\n停用后该组织者将立即退出登录并无法访问系统。' : ''
      }`,
      `${action}组织者`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await request.post('/auth/admin/toggle-organizer-status', {
      adminAccount: authStore.accountUser?.accountId,
      adminPassword: 'admin123',
      organizerId: organizer.id
    })

    if (response.data.success) {
      ElMessage.success(response.data.message)
      // 刷新列表
      fetchOrganizers()
    } else {
      ElMessage.error(response.data.msg || `${action}失败`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.msg || error.message || `${action}失败`
      ElMessage.error(errorMsg)
    }
  }
}

const handleShowPasswordDialog = (organizer: any) => {
  currentOrganizer.value = organizer
  showPasswordDialog.value = true
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await request.post('/auth/admin/change-organizer-password', {
          adminAccount: authStore.accountUser?.accountId,
          adminPassword: 'admin123',
          organizerId: currentOrganizer.value.id,
          newPassword: passwordForm.newPassword
        })

        if (response.data.success) {
          ElMessage.success('密码修改成功，该组织者需要重新登录')
          showPasswordDialog.value = false
          resetPasswordForm()
          // 刷新列表
          fetchOrganizers()
        } else {
          ElMessage.error(response.data.msg || '修改失败')
        }
      } catch (error: any) {
        const errorMsg = error.response?.data?.msg || error.message || '修改失败'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleDelete = async (organizer: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除组织者 ${organizer.name} (${organizer.username}) 吗？\n删除后：\n1. 该组织者将立即退出登录并无法访问系统\n2. 该组织者创建的活动将保留\n3. 可以创建同名的新组织者`,
      '删除组织者',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error',
        dangerouslyUseHTMLString: false
      }
    )

    const response = await request.post('/auth/admin/delete-organizer', {
      adminAccount: authStore.accountUser?.accountId,
      adminPassword: 'admin123',
      organizerId: organizer.id
    })

    if (response.data.success) {
      ElMessage.success('组织者已删除')
      // 刷新列表
      fetchOrganizers()
    } else {
      ElMessage.error(response.data.msg || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.msg || error.message || '删除失败'
      ElMessage.error(errorMsg)
    }
  }
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
