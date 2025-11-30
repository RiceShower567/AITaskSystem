<template>
  <div class="tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务管理</span>
          <el-radio-group v-model="activeTab" size="small">
            <el-radio-button label="regular">常规任务</el-radio-button>
            <el-radio-button label="dynamic">动态任务</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <!-- 常规任务管理 -->
      <div v-if="activeTab === 'regular'" class="regular-tasks-content">
        <!-- 搜索和添加 -->
        <div class="task-controls">
          <el-input
            v-model="regularSearchQuery"
            placeholder="搜索任务名称或地点"
            prefix-icon="Search"
            clearable
            style="width: 300px;"
          />
          <el-button type="primary" @click="showRegularTaskDialog = true">
            <el-icon><Plus /></el-icon>
            添加常规任务
          </el-button>
          <el-button @click="showImportDialog = true">
            <el-icon><Upload /></el-icon>
            导入课程表
          </el-button>
        </div>

        <!-- 任务列表 -->
        <el-table
          :data="filteredRegularTasks"
          style="width: 100%"
          stripe
          @selection-change="regularTaskSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="title" label="任务名称" min-width="180" />
          <el-table-column prop="type" label="任务类型" width="100">
            <template #default="scope">
              <el-tag size="small" :type="getTaskTypeColor(scope.row.type)">
                {{ getTaskTypeName(scope.row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="地点" width="120" />
          <el-table-column label="时间" width="200">
            <template #default="scope">
              {{ formatRegularTaskTime(scope.row.start_time, scope.row.end_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="repeat_rule" label="重复规则" width="120">
            <template #default="scope">
              {{ getRepeatRuleText(scope.row.repeat_rule) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" @click="editRegularTask(scope.row)">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="deleteRegularTask(scope.row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 批量操作 -->
        <div v-if="selectedRegularTasks.length > 0" class="batch-actions">
          <span>已选择 {{ selectedRegularTasks.length }} 个任务</span>
          <el-button type="danger" @click="batchDeleteRegularTasks">批量删除</el-button>
        </div>
      </div>

      <!-- 动态任务管理 -->
      <div v-else class="dynamic-tasks-content">
        <!-- 搜索和筛选 -->
        <div class="task-controls">
          <el-input
            v-model="dynamicSearchQuery"
            placeholder="搜索任务名称"
            prefix-icon="Search"
            clearable
            style="width: 250px;"
          />
          <el-select v-model="priorityFilter" placeholder="优先级" size="small" style="width: 120px; margin-left: 10px;">
            <el-option label="全部" value="" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
          <el-select v-model="completedFilter" placeholder="完成状态" size="small" style="width: 120px; margin-left: 10px;">
            <el-option label="全部" value="" />
            <el-option label="已完成" :value="true" />
            <el-option label="未完成" :value="false" />
          </el-select>
          <el-button type="primary" @click="showDynamicTaskDialog = true" style="margin-left: auto;">
            <el-icon><Plus /></el-icon>
            添加动态任务
          </el-button>
        </div>

        <!-- 任务列表 -->
        <el-table
          :data="filteredDynamicTasks"
          style="width: 100%"
          stripe
          @selection-change="dynamicTaskSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="title" label="任务名称" min-width="200" />
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="scope">
              <el-tag size="small" :type="getPriorityColor(scope.row.priority)">
                {{ getPriorityText(scope.row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="estimated_time" label="预计耗时(分钟)" width="120" />
          <el-table-column prop="deadline" label="截止日期" width="120" />
          <el-table-column prop="tags" label="标签" width="150">
            <template #default="scope">
              <el-tag size="small" v-for="tag in scope.row.tags" :key="tag" class="tag-item">
                {{ tag }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="completed" label="完成状态" width="100">
            <template #default="scope">
              <el-switch
                v-model="scope.row.completed"
                active-text="已完成"
                inactive-text="未完成"
                @change="updateTaskCompletion(scope.row.id, scope.row.completed)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" @click="editDynamicTask(scope.row)">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="deleteDynamicTask(scope.row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 批量操作 -->
        <div v-if="selectedDynamicTasks.length > 0" class="batch-actions">
          <span>已选择 {{ selectedDynamicTasks.length }} 个任务</span>
          <el-button type="success" @click="batchCompleteDynamicTasks">批量完成</el-button>
          <el-button type="danger" @click="batchDeleteDynamicTasks">批量删除</el-button>
        </div>
      </div>
    </el-card>

    <!-- 常规任务对话框 -->
    <el-dialog v-model="showRegularTaskDialog" :title="editingRegularTask ? '编辑常规任务' : '添加常规任务'" width="500px">
      <el-form ref="regularTaskFormRef" :model="regularTaskForm" :rules="regularTaskRules" label-width="100px">
        <el-form-item label="任务名称" prop="title">
          <el-input v-model="regularTaskForm.title" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="regularTaskForm.type" placeholder="请选择任务类型">
            <el-option label="课程" value="course" />
            <el-option label="例会" value="meeting" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="地点" prop="location">
          <el-input v-model="regularTaskForm.location" placeholder="请输入地点" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="regularTaskForm.start_time"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="regularTaskForm.end_time"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="重复规则" prop="repeat_rule">
          <el-select v-model="regularTaskForm.repeat_rule" placeholder="请选择重复规则">
            <el-option label="单次" value="once" />
            <el-option label="每日" value="daily" />
            <el-option label="每周" value="weekly" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRegularTaskDialog = false">取消</el-button>
          <el-button type="primary" @click="saveRegularTask">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 动态任务对话框 -->
    <el-dialog v-model="showDynamicTaskDialog" :title="editingDynamicTask ? '编辑动态任务' : '添加动态任务'" width="500px">
      <el-form ref="dynamicTaskFormRef" :model="dynamicTaskForm" :rules="dynamicTaskRules" label-width="100px">
        <el-form-item label="任务名称" prop="title">
          <el-input v-model="dynamicTaskForm.title" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="紧急程度" prop="priority">
          <el-select v-model="dynamicTaskForm.priority" placeholder="请选择紧急程度">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="预计耗时" prop="estimated_time">
          <el-input-number v-model="dynamicTaskForm.estimated_time" :min="1" :step="5" placeholder="分钟" />
        </el-form-item>
        <el-form-item label="截止日期" prop="deadline">
          <el-date-picker
            v-model="dynamicTaskForm.deadline"
            type="date"
            placeholder="选择日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="关联标签" prop="tags">
          <el-select
            v-model="dynamicTaskForm.tags"
            placeholder="请选择标签"
            multiple
            filterable
            allow-create
            default-first-option
          >
            <el-option v-for="tag in allTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDynamicTaskDialog = false">取消</el-button>
          <el-button type="primary" @click="saveDynamicTask">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入课程表" width="400px">
      <el-upload
        class="upload-demo"
        drag
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        :file-list="uploadFileList"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            请上传Excel或CSV格式的课程表文件
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showImportDialog = false">取消</el-button>
          <el-button type="primary" @click="importTasks" :disabled="!uploadFileList.length">导入</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { Plus, Search, Upload, UploadFilled } from '@element-plus/icons-vue'
import { useTasksStore } from '../stores/tasks'

// 状态管理
const tasksStore = useTasksStore()
const activeTab = ref('regular')

// 搜索和筛选
const regularSearchQuery = ref('')
const dynamicSearchQuery = ref('')
const priorityFilter = ref('')
const completedFilter = ref('')

// 任务选择
const selectedRegularTasks = ref<any[]>([])
const selectedDynamicTasks = ref<any[]>([])

// 对话框状态
const showRegularTaskDialog = ref(false)
const showDynamicTaskDialog = ref(false)
const showImportDialog = ref(false)
const editingRegularTask = ref(false)
const editingDynamicTask = ref(false)

// 表单引用
const regularTaskFormRef = ref<FormInstance>()
const dynamicTaskFormRef = ref<FormInstance>()

// 常规任务表单
const regularTaskForm = reactive({
  id: null,
  title: '',
  type: 'course',
  location: '',
  start_time: '',
  end_time: '',
  repeat_rule: 'weekly'
})

// 动态任务表单
const dynamicTaskForm = reactive({
  id: null,
  title: '',
  priority: 'medium',
  estimated_time: 30,
  deadline: '',
  tags: []
})

// 上传文件
const uploadFileList = ref<any[]>([])

// 所有标签（用于动态任务）
const allTags = ref(['学习', '工作', '生活', '健身', '其他'])

// 表单验证规则
const regularTaskRules = reactive<FormRules>({
  title: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' },
    {
      validator: (rule, value, callback) => {
        if (value && regularTaskForm.start_time && new Date(value) <= new Date(regularTaskForm.start_time)) {
          callback(new Error('结束时间必须晚于开始时间'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  repeat_rule: [
    { required: true, message: '请选择重复规则', trigger: 'change' }
  ]
})

const dynamicTaskRules = reactive<FormRules>({
  title: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择紧急程度', trigger: 'change' }
  ],
  estimated_time: [
    { required: true, message: '请输入预计耗时', trigger: 'blur' },
    { type: 'number', min: 1, message: '预计耗时至少为1分钟', trigger: 'blur' }
  ],
  deadline: [
    { required: true, message: '请选择截止日期', trigger: 'change' }
  ]
})

// 计算属性：过滤后的常规任务
const filteredRegularTasks = computed(() => {
  return tasksStore.regularTasks.filter(task => {
    const matchesSearch = !regularSearchQuery.value || 
      task.title.toLowerCase().includes(regularSearchQuery.value.toLowerCase()) ||
      (task.location && task.location.toLowerCase().includes(regularSearchQuery.value.toLowerCase()))
    return matchesSearch
  })
})

// 计算属性：过滤后的动态任务
const filteredDynamicTasks = computed(() => {
  return tasksStore.dynamicTasks.filter(task => {
    const matchesSearch = !dynamicSearchQuery.value || 
      task.title.toLowerCase().includes(dynamicSearchQuery.value.toLowerCase())
    const matchesPriority = !priorityFilter.value || task.priority === priorityFilter.value
    const matchesCompleted = completedFilter.value === '' || task.is_completed === completedFilter.value
    return matchesSearch && matchesPriority && matchesCompleted
  })
})

// 方法
const formatRegularTaskTime = (startTime: string, endTime: string) => {
  const startDate = new Date(startTime)
  const endDate = new Date(endTime)
  return `${startDate.getMonth() + 1}月${startDate.getDate()}日 ${startDate.getHours().toString().padStart(2, '0')}:${startDate.getMinutes().toString().padStart(2, '0')} - ${endDate.getHours().toString().padStart(2, '0')}:${endDate.getMinutes().toString().padStart(2, '0')}`
}

const getTaskTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    course: 'primary',
    meeting: 'success',
    other: 'info'
  }
  return colors[type] || 'info'
}

const getTaskTypeName = (type: string) => {
  const names: Record<string, string> = {
    course: '课程',
    meeting: '例会',
    other: '其他'
  }
  return names[type] || '其他'
}

const getRepeatRuleText = (rule: string) => {
  const texts: Record<string, string> = {
    once: '单次',
    daily: '每日',
    weekly: '每周'
  }
  return texts[rule] || '单次'
}

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return colors[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const texts: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || '中'
}

const regularTaskSelectionChange = (selection: any[]) => {
  selectedRegularTasks.value = selection
}

const dynamicTaskSelectionChange = (selection: any[]) => {
  selectedDynamicTasks.value = selection
}

const resetRegularTaskForm = () => {
  Object.assign(regularTaskForm, {
    id: null,
    title: '',
    type: 'course',
    location: '',
    start_time: '',
    end_time: '',
    repeat_rule: 'weekly'
  })
  editingRegularTask.value = false
  if (regularTaskFormRef.value) {
    regularTaskFormRef.value.resetFields()
  }
}

const resetDynamicTaskForm = () => {
  Object.assign(dynamicTaskForm, {
    id: null,
    title: '',
    priority: 'medium',
    estimated_time: 30,
    deadline: '',
    tags: []
  })
  editingDynamicTask.value = false
  if (dynamicTaskFormRef.value) {
    dynamicTaskFormRef.value.resetFields()
  }
}

const editRegularTask = (task: any) => {
  Object.assign(regularTaskForm, task)
  editingRegularTask.value = true
  showRegularTaskDialog.value = true
}

const editDynamicTask = (task: any) => {
  Object.assign(dynamicTaskForm, task)
  // 确保tags是数组
  if (!Array.isArray(dynamicTaskForm.tags)) {
    dynamicTaskForm.tags = []
  }
  editingDynamicTask.value = true
  showDynamicTaskDialog.value = true
}

const saveRegularTask = async () => {
  if (!regularTaskFormRef.value) return
  
  try {
    await regularTaskFormRef.value.validate()
    
    if (editingRegularTask.value) {
      // 更新任务
      await tasksStore.updateRegularTask(regularTaskForm)
      ElMessage.success('任务更新成功')
    } else {
      // 创建任务
      await tasksStore.createRegularTask(regularTaskForm)
      ElMessage.success('任务创建成功')
    }
    
    showRegularTaskDialog.value = false
    resetRegularTaskForm()
    
  } catch (error: any) {
    ElMessage.error(error?.message || '操作失败')
  }
}

const saveDynamicTask = async () => {
  if (!dynamicTaskFormRef.value) return
  
  try {
    await dynamicTaskFormRef.value.validate()
    
    if (editingDynamicTask.value) {
      // 更新任务
      await tasksStore.updateDynamicTask(dynamicTaskForm)
      ElMessage.success('任务更新成功')
    } else {
      // 创建任务
      await tasksStore.createDynamicTask(dynamicTaskForm)
      ElMessage.success('任务创建成功')
      
      // 更新标签列表
      dynamicTaskForm.tags.forEach((tag: string) => {
        if (!allTags.value.includes(tag)) {
          allTags.value.push(tag)
        }
      })
    }
    
    showDynamicTaskDialog.value = false
    resetDynamicTaskForm()
    
  } catch (error: any) {
    ElMessage.error(error?.message || '操作失败')
  }
}

const deleteRegularTask = async (taskId: number) => {
  try {
    await tasksStore.deleteRegularTask(taskId)
    ElMessage.success('任务删除成功')
  } catch (error: any) {
    ElMessage.error(error?.message || '删除失败')
  }
}

const deleteDynamicTask = async (taskId: number) => {
  try {
    await tasksStore.deleteDynamicTask(taskId)
    ElMessage.success('任务删除成功')
  } catch (error: any) {
    ElMessage.error(error?.message || '删除失败')
  }
}

const batchDeleteRegularTasks = async () => {
  if (selectedRegularTasks.value.length === 0) return
  
  try {
    const taskIds = selectedRegularTasks.value.map(task => task.id)
    await Promise.all(taskIds.map(id => tasksStore.deleteRegularTask(id)))
    ElMessage.success(`成功删除 ${taskIds.length} 个任务`)
    selectedRegularTasks.value = []
  } catch (error: any) {
    ElMessage.error(error?.message || '批量删除失败')
  }
}

const batchDeleteDynamicTasks = async () => {
  if (selectedDynamicTasks.value.length === 0) return
  
  try {
    const taskIds = selectedDynamicTasks.value.map(task => task.id)
    await Promise.all(taskIds.map(id => tasksStore.deleteDynamicTask(id)))
    ElMessage.success(`成功删除 ${taskIds.length} 个任务`)
    selectedDynamicTasks.value = []
  } catch (error: any) {
    ElMessage.error(error?.message || '批量删除失败')
  }
}

const batchCompleteDynamicTasks = async () => {
  if (selectedDynamicTasks.value.length === 0) return
  
  try {
    const taskIds = selectedDynamicTasks.value.map(task => task.id)
    await Promise.all(taskIds.map(id => tasksStore.completeDynamicTask(id)))
    ElMessage.success(`成功完成 ${taskIds.length} 个任务`)
    selectedDynamicTasks.value = []
  } catch (error: any) {
    ElMessage.error(error?.message || '批量完成失败')
  }
}

const updateTaskCompletion = async (taskId: number, completed: boolean) => {
  try {
    await tasksStore.markTaskAsCompleted(taskId, completed)
    ElMessage.success(completed ? '任务已完成' : '任务已标记为未完成')
  } catch (error: any) {
    ElMessage.error(error?.message || '更新失败')
    // 回滚UI状态
    const task = tasksStore.dynamicTasks.find(t => t.id === taskId)
    if (task) {
      task.is_completed = !isCompleted
    }
  }
}

const handleFileChange = (file: any, fileList: any[]) => {
  uploadFileList.value = fileList.slice(-1)
}

const importTasks = async () => {
  // 这里应该实现文件导入逻辑
  // 实际项目中需要使用FileReader API读取文件内容
  ElMessage.info('文件导入功能待实现')
  showImportDialog.value = false
  uploadFileList.value = []
}

// 生命周期
onMounted(() => {
  // 加载任务数据
  tasksStore.fetchRegularTasks()
  tasksStore.fetchDynamicTasks()
})

// 监听对话框关闭，重置表单
watch(showRegularTaskDialog, (newVal) => {
  if (!newVal) {
    resetRegularTaskForm()
  }
})

watch(showDynamicTaskDialog, (newVal) => {
  if (!newVal) {
    resetDynamicTaskForm()
  }
})
</script>

<style scoped>
.tasks-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-controls {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.tag-item {
  margin-right: 5px;
  margin-bottom: 5px;
}

.upload-demo {
  margin-bottom: 20px;
}
</style>