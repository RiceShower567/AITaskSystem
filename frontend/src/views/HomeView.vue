<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用AI智能任务管理系统</span>
        </div>
      </template>
      
      <div class="welcome-content">
        <h2>你好，{{ user?.username }}！</h2>
        <p>今天是 {{ today }}，让我们开始高效地管理你的任务吧！</p>
        
        <div class="stats-container">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-number">{{ pendingDynamicTasks }}</div>
                  <div class="stat-label">待完成动态任务</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-number">{{ regularTasksCount }}</div>
                  <div class="stat-label">常规任务</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-number">{{ todayTasks }}</div>
                  <div class="stat-label">今日任务</div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div class="quick-actions">
          <el-button type="primary" @click="navigateTo('/tasks')" size="large">
            <el-icon><List /></el-icon>
            管理任务
          </el-button>
          <el-button @click="navigateTo('/calendar')" size="large">
            <el-icon><Calendar /></el-icon>
            查看日历
          </el-button>
        </div>
      </div>
    </el-card>
    
    <el-card class="upcoming-tasks-card">
      <template #header>
        <div class="card-header">
          <span>即将到来的任务</span>
          <el-button type="text" @click="navigateTo('/tasks')">查看全部</el-button>
        </div>
      </template>
      
      <div v-if="upcomingTasks.length > 0" class="tasks-list">
        <div v-for="task in upcomingTasks" :key="task.id" class="task-item">
          <div class="task-info">
            <h3>{{ task.title }}</h3>
            <p class="task-meta">
              <span v-if="task.type === 'regular'">
                <el-icon><Clock /></el-icon>
                {{ formatTimeRange(task.start_time, task.end_time) }}
                <span v-if="task.location" class="location">
                  <el-icon><Position /></el-icon>
                  {{ task.location }}
                </span>
              </span>
              <span v-else>
                <el-icon><Timer /></el-icon>
                预计用时: {{ task.estimated_time }}分钟
                <span v-if="task.deadline" class="deadline">
                  <el-icon><Warning /></el-icon>
                  截止: {{ formatDate(task.deadline) }}
                </span>
              </span>
            </p>
          </div>
          <div class="task-actions">
            <el-button 
              v-if="task.type === 'dynamic' && !task.completed" 
              type="success" 
              size="small"
              @click="completeTask(task.id)"
            >
              <el-icon><Check /></el-icon>
              完成
            </el-button>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <el-empty description="暂无即将到来的任务" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useTasksStore } from '../stores/tasks'
import { List, Calendar, Clock, Position, Timer, Warning, Check } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const tasksStore = useTasksStore()
const today = ref('')

// 计算属性
const user = computed(() => authStore.user)
const pendingDynamicTasks = computed(() => {
  return tasksStore.dynamicTasks.filter(task => !task.completed).length
})
const regularTasksCount = computed(() => tasksStore.regularTasks.length)
const todayTasks = computed(() => {
  const todayStr = new Date().toISOString().split('T')[0]
  return [...tasksStore.regularTasks.filter(task => task.start_time.startsWith(todayStr)),
          ...tasksStore.dynamicTasks.filter(task => !task.completed && task.deadline?.startsWith(todayStr))].length
})

// 获取即将到来的任务（混合常规任务和动态任务，按时间排序）
const upcomingTasks = computed(() => {
  const regularTasksWithType = tasksStore.regularTasks.map(task => ({ ...task, type: 'regular' }))
  const pendingDynamicTasksWithType = tasksStore.dynamicTasks
    .filter(task => !task.completed)
    .map(task => ({ ...task, type: 'dynamic' }))
  
  const allTasks = [...regularTasksWithType, ...pendingDynamicTasksWithType]
  
  return allTasks
    .sort((a, b) => {
      const dateA = a.type === 'regular' ? new Date(a.start_time) : new Date(a.deadline || 0)
      const dateB = b.type === 'regular' ? new Date(b.start_time) : new Date(b.deadline || 0)
      return dateA.getTime() - dateB.getTime()
    })
    .slice(0, 5)
})

// 方法
const navigateTo = (path: string) => {
  router.push(path)
}

const formatTimeRange = (start: string, end: string) => {
  const startDate = new Date(start)
  const endDate = new Date(end)
  return `${startDate.getHours().toString().padStart(2, '0')}:${startDate.getMinutes().toString().padStart(2, '0')} - ${endDate.getHours().toString().padStart(2, '0')}:${endDate.getMinutes().toString().padStart(2, '0')}`
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

const completeTask = async (taskId: number) => {
  await tasksStore.markTaskAsCompleted(taskId, true)
}

// 生命周期
onMounted(() => {
  // 格式化今天日期
  const now = new Date()
  today.value = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
  
  // 加载任务数据
  tasksStore.fetchRegularTasks()
  tasksStore.fetchDynamicTasks()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-content {
  text-align: center;
  padding: 20px 0;
}

.welcome-content h2 {
  margin-bottom: 10px;
  color: #303133;
}

.welcome-content p {
  color: #606266;
  margin-bottom: 30px;
}

.stats-container {
  margin: 30px 0;
}

.stat-card {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.quick-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.upcoming-tasks-card {
  margin-bottom: 20px;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  transition: all 0.3s;
}

.task-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.task-info h3 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 16px;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #909399;
  font-size: 12px;
  margin: 0;
}

.location, .deadline {
  display: flex;
  align-items: center;
  gap: 5px;
}

.task-actions {
  display: flex;
  gap: 10px;
}

.empty-state {
  padding: 40px 0;
}
</style>