<template>
  <el-card :class="['task-card', `task-priority-${task.priority}`]" shadow="hover">
    <div class="task-header">
      <h3 class="task-title">{{ task.name }}</h3>
      <el-tag :type="priorityType" size="small">
        {{ priorityText }}
      </el-tag>
    </div>
    
    <div class="task-info">
      <div class="info-item" v-if="task.estimated_time">
        <el-icon><Timer /></el-icon>
        <span>{{ formatEstimatedTime(task.estimated_time) }}</span>
      </div>
      
      <div class="info-item" v-if="task.deadline">
        <el-icon><Calendar /></el-icon>
        <span>{{ formatDeadline(task.deadline) }}</span>
      </div>
    </div>
    
    <div class="task-tags" v-if="task.tags && task.tags.length > 0">
      <el-tag size="small" v-for="tag in task.tags" :key="tag">
        {{ tag }}
      </el-tag>
    </div>
    
    <div class="task-actions">
      <el-button
        type="primary"
        :icon="task.completed ? 'Check' : 'Check'"
        :disabled="task.completed"
        @click="handleComplete"
        size="small"
      >
        {{ task.completed ? '已完成' : '完成' }}
      </el-button>
      <el-button
        type="info"
        :icon="'Edit'"
        @click="handleEdit"
        size="small"
      >
        编辑
      </el-button>
      <el-button
        type="danger"
        :icon="'Delete'"
        @click="handleDelete"
        size="small"
      >
        删除
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Timer, Calendar, Check, Edit, Delete } from '@element-plus/icons-vue'
import { DynamicTask } from '../services/tasks'
import { useTasksStore } from '../stores/tasks'

const props = defineProps<{
  task: DynamicTask
}>()

const emit = defineEmits<{
  edit: [task: DynamicTask]
  delete: [taskId: number]
}>()

const tasksStore = useTasksStore()

// 计算属性
const priorityType = computed(() => {
  switch (props.task.priority) {
    case 'high':
      return 'danger'
    case 'medium':
      return 'warning'
    case 'low':
      return 'success'
    default:
      return 'info'
  }
})

const priorityText = computed(() => {
  switch (props.task.priority) {
    case 'high':
      return '高优先级'
    case 'medium':
      return '中优先级'
    case 'low':
      return '低优先级'
    default:
      return props.task.priority
  }
})

// 方法
const formatEstimatedTime = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes} 分钟`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours} 小时 ${mins} 分钟` : `${hours} 小时`
}

const formatDeadline = (deadline: string): string => {
  const date = new Date(deadline)
  const now = new Date()
  const tomorrow = new Date(now)
  tomorrow.setDate(now.getDate() + 1)
  tomorrow.setHours(0, 0, 0, 0)
  
  // 今天
  if (date.toDateString() === now.toDateString()) {
    return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  
  // 明天
  if (date.toDateString() === tomorrow.toDateString()) {
    return `明天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  
  // 本周
  const diffDays = Math.floor((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  if (diffDays < 7 && diffDays > 0) {
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return `${weekdays[date.getDay()]} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  
  // 其他日期
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const handleComplete = async () => {
  try {
    await tasksStore.markTaskAsCompleted(props.task.id, true)
    ElMessage.success('任务已标记为完成')
  } catch (error) {
    ElMessage.error('更新任务状态失败')
  }
}

const handleEdit = () => {
  emit('edit', props.task)
}

const handleDelete = async () => {
  try {
    await tasksStore.deleteDynamicTaskById(props.task.id)
    ElMessage.success('任务已删除')
    emit('delete', props.task.id)
  } catch (error) {
    ElMessage.error('删除任务失败')
  }
}
</script>

<style scoped>
.task-card {
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.task-info {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  color: #606266;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.task-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.task-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* 优先级样式 */
.task-priority-high .el-card__header {
  border-left: 4px solid #f56c6c;
}

.task-priority-medium .el-card__header {
  border-left: 4px solid #e6a23c;
}

.task-priority-low .el-card__header {
  border-left: 4px solid #67c23a;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .task-info {
    flex-direction: column;
    gap: 8px;
  }
  
  .task-actions {
    justify-content: stretch;
  }
  
  .task-actions .el-button {
    flex: 1;
  }
}
</style>