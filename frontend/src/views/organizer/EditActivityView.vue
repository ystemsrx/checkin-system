<template>
  <div class="edit-activity-view">
    <app-header />
    
    <div v-loading="loading" class="container">
      <el-button :icon="ArrowLeft" @click="router.back()" class="back-btn">
        返回
      </el-button>

      <el-card v-if="activity">
        <template #header>
          <h2>编辑活动</h2>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="120px"
          label-position="right"
        >
          <el-form-item label="活动名称" prop="title">
            <el-input
              v-model="form.title"
              placeholder="请输入活动名称"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="活动分类" prop="category">
            <el-select v-model="form.category" placeholder="请选择分类">
              <el-option label="学术" value="academic" />
              <el-option label="文艺" value="cultural" />
              <el-option label="体育" value="sports" />
              <el-option label="志愿" value="volunteer" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>

          <el-form-item label="活动地点" prop="location">
            <el-input
              v-model="form.location"
              placeholder="请输入活动地点"
              maxlength="200"
            />
          </el-form-item>

          <el-form-item label="开始时间" prop="startTime">
            <el-date-picker
              v-model="form.startTime"
              type="datetime"
              placeholder="选择开始时间"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="结束时间" prop="endTime">
            <el-date-picker
              v-model="form.endTime"
              type="datetime"
              placeholder="选择结束时间"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="报名截止" prop="registrationDeadline">
            <el-date-picker
              v-model="form.registrationDeadline"
              type="datetime"
              placeholder="选择报名截止时间"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="人数限制" prop="maxParticipants">
            <el-input-number
              v-model="form.maxParticipants"
              :min="activity.currentParticipants"
              :max="10000"
              style="width: 200px"
            />
            <span style="margin-left: 12px; color: #909399">
              当前已报名 {{ activity.currentParticipants }} 人
            </span>
          </el-form-item>

          <el-form-item label="活动描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="6"
              placeholder="请输入活动描述"
              maxlength="2000"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="活动图片">
            <div class="upload-section">
              <el-upload
                :action="uploadUrl"
                :headers="uploadHeaders"
                list-type="picture-card"
                :file-list="fileList"
                :on-success="handleUploadSuccess"
                :on-remove="handleRemove"
                :before-upload="beforeUpload"
                accept="image/*"
                multiple
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">
                <el-text type="info" size="small">第一张图片将作为封面显示，支持上传多张图片</el-text>
              </div>
            </div>
          </el-form-item>

          <el-form-item label="标签">
            <el-tag
              v-for="tag in form.tags"
              :key="tag"
              closable
              @close="handleRemoveTag(tag)"
              style="margin-right: 8px"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="tagInputVisible"
              ref="tagInputRef"
              v-model="tagInputValue"
              size="small"
              style="width: 120px"
              @keyup.enter="handleAddTag"
              @blur="handleAddTag"
            />
            <el-button
              v-else
              size="small"
              @click="showTagInput"
            >
              + 添加标签
            </el-button>
          </el-form-item>

          <el-form-item label="活动细分项目">
            <div style="width: 100%;">
              <el-table :data="form.subItems" style="width: 100%; margin-bottom: 12px;" v-if="form.subItems.length > 0">
                <el-table-column label="项目名称" width="200">
                  <template #default="{ row, $index }">
                    <el-input
                      v-if="editingSubItemIndex === $index"
                      v-model="editingSubItem.name"
                      :disabled="(row.currentParticipants || 0) > 0"
                      size="small"
                    />
                    <span v-else>{{ row.name }}</span>
                    <el-tag v-if="(row.currentParticipants || 0) > 0" type="warning" size="small" style="margin-left: 8px;">
                      已有{{ row.currentParticipants }}人报名
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="人数限制" width="200">
                  <template #default="{ row, $index }">
                    <el-input-number
                      v-if="editingSubItemIndex === $index"
                      v-model="editingSubItem.maxParticipants"
                      :min="row.currentParticipants || 1"
                      :max="1000"
                      size="small"
                    />
                    <span v-else>{{ row.maxParticipants }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="当前报名" width="100">
                  <template #default="{ row }">
                    {{ row.currentParticipants || 0 }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180">
                  <template #default="{ row, $index }">
                    <div v-if="editingSubItemIndex === $index" style="display: flex; gap: 4px;">
                      <el-button type="primary" size="small" @click="handleSaveSubItem($index)">保存</el-button>
                      <el-button size="small" @click="handleCancelEditSubItem">取消</el-button>
                    </div>
                    <div v-else style="display: flex; gap: 4px;">
                      <el-button type="primary" size="small" @click="handleEditSubItem($index)">编辑</el-button>
                      <el-button 
                        type="danger" 
                        size="small" 
                        :disabled="(row.currentParticipants || 0) > 0"
                        @click="handleRemoveSubItem($index)"
                      >
                        删除
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
              <div v-if="subItemInputVisible" style="display: flex; gap: 8px; margin-bottom: 8px;">
                <el-input
                  v-model="subItemForm.name"
                  placeholder="项目名称"
                  style="width: 200px;"
                />
                <el-input-number
                  v-model="subItemForm.maxParticipants"
                  :min="1"
                  :max="1000"
                  placeholder="人数限制"
                  style="width: 150px;"
                />
                <el-button type="primary" size="small" @click="handleAddSubItem">确认</el-button>
                <el-button size="small" @click="subItemInputVisible = false">取消</el-button>
              </div>
              <el-button
                v-if="!subItemInputVisible"
                size="small"
                @click="showSubItemInput"
              >
                + 添加细分项目
              </el-button>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="submitting"
              @click="handleSubmit"
            >
              保存修改
            </el-button>
            <el-button @click="router.back()">
              取消
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useActivityStore } from '@/stores/activity'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import type { Activity, ActivityCategory, ActivitySubItem } from '@/types'

const router = useRouter()
const route = useRoute()
const activityStore = useActivityStore()

const formRef = ref<FormInstance>()
const tagInputRef = ref()
const loading = ref(false)
const submitting = ref(false)
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const subItemInputVisible = ref(false)
const subItemForm = reactive({
  name: '',
  maxParticipants: 10
})
const editingSubItemIndex = ref<number | null>(null)
const editingSubItem = reactive({
  name: '',
  maxParticipants: 10
})
const activity = ref<Activity | null>(null)

const activityId = Number(route.params.id)

const form = reactive({
  title: '',
  category: '' as ActivityCategory | '',
  location: '',
  startTime: null as Date | null,
  endTime: null as Date | null,
  registrationDeadline: null as Date | null,
  maxParticipants: 50,
  description: '',
  images: [] as string[],
  tags: [] as string[],
  subItems: [] as ActivitySubItem[]
})

const fileList = ref<any[]>([])
const uploadUrl = ref(import.meta.env.VITE_API_BASE_URL + '/uploads/image')
const uploadHeaders = ref({
  Authorization: `Bearer ${localStorage.getItem('token')}`
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入活动名称', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择活动分类', trigger: 'change' }
  ],
  location: [
    { required: true, message: '请输入活动地点', trigger: 'blur' }
  ],
  startTime: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  endTime: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  registrationDeadline: [
    { required: true, message: '请选择报名截止时间', trigger: 'change' }
  ],
  maxParticipants: [
    { required: true, message: '请输入人数限制', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入活动描述', trigger: 'blur' }
  ]
}

onMounted(async () => {
  await loadActivity()
})

const loadActivity = async () => {
  loading.value = true
  const result = await activityStore.fetchActivityById(activityId)
  if (result.success && result.data) {
    activity.value = result.data
    // Populate form
    form.title = activity.value.title
    form.category = activity.value.category
    form.location = activity.value.location
    // 后端返回的是 UTC 时间字符串，需要转换为本地时间
    // 如果字符串不包含时区信息，需要添加 'Z' 表示 UTC
    const parseUTCTime = (timeStr: string) => {
      if (!timeStr.endsWith('Z') && !timeStr.includes('+')) {
        return new Date(timeStr + 'Z')
      }
      return new Date(timeStr)
    }
    form.startTime = parseUTCTime(activity.value.startTime)
    form.endTime = parseUTCTime(activity.value.endTime)
    form.registrationDeadline = parseUTCTime(activity.value.registrationDeadline)
    form.maxParticipants = activity.value.maxParticipants
    form.description = activity.value.description
    form.images = activity.value.images || []
    form.tags = activity.value.tags || []
    form.subItems = activity.value.subItems || []
    
    // 初始化文件列表
    if (activity.value.images && activity.value.images.length > 0) {
      fileList.value = activity.value.images.map((url, index) => ({
        name: `image-${index}`,
        url: url.startsWith('http') ? url : import.meta.env.VITE_API_BASE_URL + url
      }))
    }
  }
  loading.value = false
}

const showTagInput = () => {
  tagInputVisible.value = true
  nextTick(() => {
    tagInputRef.value?.focus()
  })
}

const handleAddTag = () => {
  const value = tagInputValue.value.trim()
  if (value && !form.tags.includes(value)) {
    form.tags.push(value)
  }
  tagInputVisible.value = false
  tagInputValue.value = ''
}

const handleRemoveTag = (tag: string) => {
  form.tags = form.tags.filter(t => t !== tag)
}

const showSubItemInput = () => {
  subItemForm.name = ''
  subItemForm.maxParticipants = 10
  subItemInputVisible.value = true
}

const handleAddSubItem = () => {
  const name = subItemForm.name.trim()
  if (!name) {
    ElMessage.warning('请输入项目名称')
    return
  }
  if (form.subItems.some(item => item.name === name)) {
    ElMessage.warning('项目名称已存在')
    return
  }
  form.subItems.push({
    name: name,
    maxParticipants: subItemForm.maxParticipants
  })
  subItemInputVisible.value = false
}

const handleEditSubItem = (index: number) => {
  const item = form.subItems[index]
  if (!item) return
  editingSubItemIndex.value = index
  editingSubItem.name = item.name
  editingSubItem.maxParticipants = item.maxParticipants
}

const handleSaveSubItem = (index: number) => {
  const item = form.subItems[index]
  if (!item) return
  
  const newName = editingSubItem.name.trim()
  
  // 验证名称
  if (!newName) {
    ElMessage.warning('请输入项目名称')
    return
  }
  
  // 如果有人报名，不能修改名称
  if ((item.currentParticipants || 0) > 0 && newName !== item.name) {
    ElMessage.error('该项目已有人报名，不能修改名称')
    return
  }
  
  // 检查名称是否重复
  if (newName !== item.name && form.subItems.some((si, i) => i !== index && si.name === newName)) {
    ElMessage.warning('项目名称已存在')
    return
  }
  
  // 验证人数不能少于当前报名人数
  if (editingSubItem.maxParticipants < (item.currentParticipants || 0)) {
    ElMessage.error(`人数限制不能少于当前报名人数（${item.currentParticipants}）`)
    return
  }
  
  form.subItems[index] = {
    ...item,
    name: newName,
    maxParticipants: editingSubItem.maxParticipants
  }
  
  editingSubItemIndex.value = null
  ElMessage.success('修改成功')
}

const handleCancelEditSubItem = () => {
  editingSubItemIndex.value = null
}

const handleRemoveSubItem = (index: number) => {
  const item = form.subItems[index]
  if (!item) return
  if ((item.currentParticipants || 0) > 0) {
    ElMessage.error('该项目已有人报名，不能删除')
    return
  }
  form.subItems.splice(index, 1)
}

const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (response: any, file: any) => {
  if (response.code === 200) {
    form.images.push(response.data.url)
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

const handleRemove = (file: any) => {
  const index = fileList.value.indexOf(file)
  if (index > -1) {
    form.images.splice(index, 1)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      // 验证子项目人数总和
      if (form.subItems.length > 0) {
        const subItemsTotal = form.subItems.reduce((sum, item) => sum + item.maxParticipants, 0)
        if (subItemsTotal !== form.maxParticipants) {
          ElMessage.error(`子项目人数总和（${subItemsTotal}）必须等于总人数（${form.maxParticipants}）`)
          return
        }
      }
      
      submitting.value = true
      
      // 将本地时间转换为 UTC 时间字符串（去掉 'Z' 后缀，让后端按 UTC 处理）
      const toUTCString = (date: Date) => {
        const isoString = date.toISOString()
        // 去掉 'Z' 后缀，因为后端期望不带时区的字符串
        return isoString.replace('Z', '')
      }
      
      const data = {
        title: form.title,
        category: form.category as ActivityCategory,
        location: form.location,
        startTime: toUTCString(form.startTime!),
        endTime: toUTCString(form.endTime!),
        registrationDeadline: toUTCString(form.registrationDeadline!),
        maxParticipants: form.maxParticipants,
        description: form.description,
        images: form.images.length > 0 ? form.images : undefined,
        tags: form.tags.length > 0 ? form.tags : undefined,
        subItems: form.subItems.length > 0 ? form.subItems : undefined
      }

      const result = await activityStore.updateActivity(activityId, data)
      submitting.value = false

      if (result.success) {
        ElMessage.success('保存成功')
        router.push('/organizer/activities')
      } else {
        ElMessage.error(result.message || '保存失败')
      }
    }
  })
}
</script>

<style scoped>
.edit-activity-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.back-btn {
  margin-bottom: 16px;
}

.upload-section {
  width: 100%;
}

.upload-tip {
  margin-top: 8px;
}

h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}
</style>
