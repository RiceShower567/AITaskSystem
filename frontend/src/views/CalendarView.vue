<template>
  <div class="calendar-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务日历</span>
          <el-radio-group v-model="calendarView" size="small" style="margin-left: 20px;">
            <el-radio-button label="month">月</el-radio-button>
            <el-radio-button label="week">周</el-radio-button>
            <el-radio-button label="day">日</el-radio-button>
          </el-radio-group>
          <el-checkbox v-model="showRegularTasks" style="margin-left: 20px;">显示常规任务</el-checkbox>
          <el-checkbox v-model="showDynamicTasks" style="margin-left: 10px;">显示动态任务</el-checkbox>
        </div>
      </template>

      <div class="calendar-wrapper">
        <!-- 日历导航 -->
        <div class="calendar-nav">
          <el-button @click="prevDate" size="small"><el-icon><ArrowLeft /></el-icon></el-button>
          <span class="current-date">{{ currentDateTitle }}</span>
          <el-button @click="today" size="small">今天</el-button>
          <el-button @click="nextDate" size="small"><el-icon><ArrowRight /></el-icon></el-button>
        </div>

        <!-- 月视图 -->
        <div v-if="calendarView === 'month'" class="month-view">
          <!-- 星期标题行 -->
          <div class="calendar-weekdays">
            <div class="weekday" v-for="weekday in weekdays" :key="weekday">{{ weekday }}</div>
          </div>

          <!-- 日期网格 -->
          <div class="calendar-days">
            <div 
              v-for="day in monthDays" 
              :key="day.date"
              class="calendar-day"
              :class="{
                'other-month': !day.isCurrentMonth,
                'today': day.isToday,
                'has-tasks': day.tasks.length > 0
              }"
              @click="selectDay(day)"
            >
              <span class="day-number">{{ day.day }}</span>
              <div class="day-tasks">
                <div 
                  v-for="(task, index) in day.tasks.slice(0, 3)" 
                  :key="index"
                  class="task-item"
                  :class="task.type"
                  :title="task.title"
                >
                  {{ task.title }}
                </div>
                <div v-if="day.tasks.length > 3" class="more-tasks">
                  +{{ day.tasks.length - 3 }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 周视图 -->
        <div v-else-if="calendarView === 'week'" class="week-view">
          <!-- 时间列和任务单元格 -->
          <div class="week-view-grid">
            <!-- 时间列 -->
            <div class="time-column">
              <div v-for="hour in 24" :key="hour" class="time-slot">
                <span>{{ formatTime(hour) }}</span>
              </div>
            </div>
            
            <!-- 星期几列 -->
            <div class="week-days-column">
              <div class="week-days-header">
                <div 
                  v-for="(day, index) in weekDays" 
                  :key="index"
                  class="week-day-header"
                  :class="{ 'today': day.isToday }"
                >
                  <div class="week-day-name">{{ day.weekday }}</div>
                  <div class="week-day-date">{{ day.day }}</div>
                </div>
              </div>
              
              <!-- 任务网格 -->
              <div class="tasks-grid">
                <div 
                  v-for="(day, index) in weekDays" 
                  :key="index"
                  class="day-column"
                >
                  <div class="time-slots">
                    <div 
                      v-for="task in getTasksForDay(day)" 
                      :key="task.id || task.title + task.startTime"
                      class="task-slot"
                      :class="task.type"
                      :style="getTaskSlotStyle(task)"
                      :title="task.title"
                    >
                      {{ task.title }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 日视图 -->
        <div v-else-if="calendarView === 'day'" class="day-view">
          <!-- 日期标题 -->
          <div class="day-view-header">
            <h3>{{ selectedDateTitle }}</h3>
          </div>
          
          <!-- 时间线和任务 -->
          <div class="day-view-grid">
            <div class="time-column">
              <div v-for="hour in 24" :key="hour" class="time-slot">
                <span>{{ formatTime(hour) }}</span>
              </div>
            </div>
            
            <div class="tasks-column">
              <div class="time-slots">
                <div 
                  v-for="task in dayTasks" 
                  :key="task.id || task.title + task.startTime"
                  class="task-slot"
                  :class="task.type"
                  :style="getTaskSlotStyle(task)"
                  :title="task.title"
                >
                  <div class="task-time">{{ formatTaskTimeRange(task) }}</div>
                  <div class="task-title">{{ task.title }}</div>
                  <div v-if="task.location" class="task-location">{{ task.location }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 任务详情对话框 -->
    <el-dialog v-model="showTaskDetails" title="任务详情" width="400px">
      <div v-if="selectedTask" class="task-details">
        <h3>{{ selectedTask.title }}</h3>
        <div class="detail-item">
          <strong>类型：</strong>
          <el-tag :type="selectedTask.type === 'regular' ? 'primary' : 'success'">
            {{ selectedTask.type === 'regular' ? '常规任务' : '动态任务' }}
          </el-tag>
        </div>
        <div v-if="selectedTask.type === 'regular'" class="detail-item">
          <strong>任务类型：</strong>{{ getTaskTypeName(selectedTask.original.type) }}
        </div>
        <div v-if="selectedTask.type === 'regular' && selectedTask.location" class="detail-item">
          <strong>地点：</strong>{{ selectedTask.location }}
        </div>
        <div class="detail-item">
          <strong>时间：</strong>{{ selectedTask.startTime }} - {{ selectedTask.endTime }}
        </div>
        <div v-if="selectedTask.type === 'regular'" class="detail-item">
          <strong>重复规则：</strong>{{ getRepeatRuleText(selectedTask.original.repeat_rule) }}
        </div>
        <div v-if="selectedTask.type === 'dynamic'" class="detail-item">
          <strong>优先级：</strong>
          <el-tag :type="getPriorityColor(selectedTask.original.priority)">
            {{ getPriorityText(selectedTask.original.priority) }}
          </el-tag>
        </div>
        <div v-if="selectedTask.type === 'dynamic'" class="detail-item">
          <strong>预计耗时：</strong>{{ selectedTask.original.estimated_time }} 分钟
        </div>
        <div v-if="selectedTask.type === 'dynamic' && selectedTask.original.tags && selectedTask.original.tags.length > 0" class="detail-item">
          <strong>标签：</strong>
          <el-tag size="small" v-for="tag in selectedTask.original.tags" :key="tag" class="tag-item">
            {{ tag }}
          </el-tag>
        </div>
        <div v-if="selectedTask.type === 'dynamic'" class="detail-item">
          <strong>完成状态：</strong>
          <el-switch
            v-model="taskCompletionStatus"
            active-text="已完成"
            inactive-text="未完成"
            @change="updateTaskCompletion"
          />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTaskDetails = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { useTasksStore } from '../stores/tasks'

interface Task {
  id?: number;
  title: string;
  type: string; // 'regular' or 'dynamic'
  startTime: string;
  endTime: string;
  location?: string;
  original: any; // 原始任务数据
}

interface CalendarDay {
  date: string;
  day: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  tasks: Task[];
}

// 状态管理
const tasksStore = useTasksStore()
const calendarView = ref('month')
const showRegularTasks = ref(true)
const showDynamicTasks = ref(true)
const currentDate = ref(new Date())
const selectedDay = ref<CalendarDay | null>(null)
const showTaskDetails = ref(false)
const selectedTask = ref<Task | null>(null)
const taskCompletionStatus = ref(false)

// 常量
const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

// 计算属性：当前日期标题
const currentDateTitle = computed(() => {
  if (calendarView.value === 'month') {
    return `${currentDate.value.getFullYear()}年${currentDate.value.getMonth() + 1}月`
  } else if (calendarView.value === 'week') {
    const weekStart = getWeekStart(currentDate.value)
    const weekEnd = getWeekEnd(currentDate.value)
    return `${weekStart.getMonth() + 1}月${weekStart.getDate()}日 - ${weekEnd.getMonth() + 1}月${weekEnd.getDate()}日`
  } else {
    return `${currentDate.value.getFullYear()}年${currentDate.value.getMonth() + 1}月${currentDate.value.getDate()}日`
  }
})

// 计算属性：选中日期标题
const selectedDateTitle = computed(() => {
  if (selectedDay.value) {
    const date = new Date(selectedDay.value.date)
    return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 ${weekdays[date.getDay()]}`
  }
  return `${currentDate.value.getFullYear()}年${currentDate.value.getMonth() + 1}月${currentDate.value.getDate()}日 ${weekdays[currentDate.value.getDay()]}`
})

// 计算属性：月视图的天数数组
const monthDays = computed((): CalendarDay[] => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const days: CalendarDay[] = []
  
  // 获取当月第一天
  const firstDay = new Date(year, month, 1)
  // 获取当月最后一天
  const lastDay = new Date(year, month + 1, 0)
  
  // 获取当月第一天是星期几
  const firstDayWeek = firstDay.getDay()
  
  // 获取上个月需要显示的天数
  const prevMonthDays = firstDayWeek
  const prevMonthLastDay = new Date(year, month, 0)
  
  // 获取下个月需要显示的天数
  const totalCells = 42 // 6行7列
  const nextMonthDays = totalCells - (prevMonthDays + lastDay.getDate())
  
  // 添加上个月的天数
  for (let i = prevMonthDays - 1; i >= 0; i--) {
    const day = prevMonthLastDay.getDate() - i
    const dateStr = new Date(year, month - 1, day).toISOString().split('T')[0]
    days.push({
      date: dateStr,
      day,
      isCurrentMonth: false,
      isToday: isToday(new Date(year, month - 1, day)),
      tasks: getTasksForDate(dateStr)
    })
  }
  
  // 添加当月的天数
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const dateStr = new Date(year, month, day).toISOString().split('T')[0]
    days.push({
      date: dateStr,
      day,
      isCurrentMonth: true,
      isToday: isToday(new Date(year, month, day)),
      tasks: getTasksForDate(dateStr)
    })
  }
  
  // 添加下个月的天数
  for (let day = 1; day <= nextMonthDays; day++) {
    const dateStr = new Date(year, month + 1, day).toISOString().split('T')[0]
    days.push({
      date: dateStr,
      day,
      isCurrentMonth: false,
      isToday: isToday(new Date(year, month + 1, day)),
      tasks: getTasksForDate(dateStr)
    })
  }
  
  return days
})

// 计算属性：周视图的天数组
const weekDays = computed(() => {
  const days = []
  const weekStart = getWeekStart(currentDate.value)
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart)
    date.setDate(weekStart.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]
    days.push({
      date: dateStr,
      day: date.getDate(),
      weekday: weekdays[i],
      isToday: isToday(date)
    })
  }
  
  return days
})

// 计算属性：日视图的任务
const dayTasks = computed(() => {
  if (selectedDay.value) {
    return getTasksForDate(selectedDay.value.date)
  }
  const today = new Date().toISOString().split('T')[0]
  return getTasksForDate(today)
})

// 方法
const isToday = (date: Date): boolean => {
  const today = new Date()
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear()
}

const getWeekStart = (date: Date): Date => {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day
  const start = new Date(d.setDate(diff))
  start.setHours(0, 0, 0, 0)
  return start
}

const getWeekEnd = (date: Date): Date => {
  const start = getWeekStart(date)
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  end.setHours(23, 59, 59, 999)
  return end
}

const formatTime = (hour: number): string => {
  return `${hour.toString().padStart(2, '0')}:00`
}

const formatTaskTimeRange = (task: Task): string => {
  const start = new Date(task.startTime)
  const end = new Date(task.endTime)
  return `${start.getHours().toString().padStart(2, '0')}:${start.getMinutes().toString().padStart(2, '0')} - ${end.getHours().toString().padStart(2, '0')}:${end.getMinutes().toString().padStart(2, '0')}`
}

const getTasksForDate = (dateStr: string): Task[] => {
  const tasks: Task[] = []
  
  // 添加常规任务
  if (showRegularTasks.value) {
    tasksStore.regularTasks.forEach(regularTask => {
      // 检查任务是否应该在这一天显示（基于重复规则）
      if (shouldShowRegularTaskOnDate(regularTask, dateStr)) {
        tasks.push({
          id: regularTask.id,
          title: regularTask.title,
          type: 'regular',
          startTime: `${dateStr}T${regularTask.start_time.split('T')[1]}`,
          endTime: `${dateStr}T${regularTask.end_time.split('T')[1]}`,
          location: regularTask.location,
          original: regularTask
        })
      }
    })
  }
  
  // 添加动态任务
  if (showDynamicTasks.value) {
    tasksStore.dynamicTasks.forEach(dynamicTask => {
      // 动态任务显示在截止日期当天
      if (dynamicTask.deadline && dynamicTask.deadline.split('T')[0] === dateStr) {
        tasks.push({
          id: dynamicTask.id,
          title: dynamicTask.title,
          type: 'dynamic',
          startTime: `${dateStr}T09:00:00`, // 默认开始时间
          endTime: `${dateStr}T10:00:00`, // 默认结束时间
          original: dynamicTask
        })
      }
    })
  }
  
  // 按开始时间排序
  return tasks.sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime())
}

const getTasksForDay = (day: { date: string }) => {
  return getTasksForDate(day.date)
}

const shouldShowRegularTaskOnDate = (task: any, dateStr: string): boolean => {
  const taskDate = new Date(task.start_time)
  const targetDate = new Date(dateStr)
  
  // 如果是单次任务，只在指定日期显示
  if (task.repeat_rule === 'once') {
    return taskDate.toISOString().split('T')[0] === dateStr
  }
  // 如果是每日任务，所有日期都显示
  else if (task.repeat_rule === 'daily') {
    return true
  }
  // 如果是每周任务，只在相同星期几显示
  else if (task.repeat_rule === 'weekly') {
    return taskDate.getDay() === targetDate.getDay()
  }
  
  return false
}

const getTaskSlotStyle = (task: Task) => {
  const start = new Date(task.startTime)
  const end = new Date(task.endTime)
  
  const startMinutes = start.getHours() * 60 + start.getMinutes()
  const endMinutes = end.getHours() * 60 + end.getMinutes()
  const duration = endMinutes - startMinutes
  
  return {
    top: `${startMinutes * (100 / (24 * 60))}%`,
    height: `${duration * (100 / (24 * 60))}%`
  }
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

const selectDay = (day: CalendarDay) => {
  selectedDay.value = day
  
  // 如果有任务，显示第一个任务的详情
  if (day.tasks.length > 0) {
    selectedTask.value = day.tasks[0]
    if (selectedTask.value.type === 'dynamic') {
      taskCompletionStatus.value = selectedTask.value.original.is_completed
    }
    showTaskDetails.value = true
  }
}

const updateTaskCompletion = async () => {
  if (selectedTask.value?.type === 'dynamic' && selectedTask.value.id) {
    try {
      await tasksStore.markTaskAsCompleted(selectedTask.value.id, taskCompletionStatus.value)
      ElMessage.success(taskCompletionStatus.value ? '任务已完成' : '任务已标记为未完成')
      
      // 更新原始任务数据
      if (selectedTask.value.original) {
        selectedTask.value.original.completed = taskCompletionStatus.value
      }
    } catch (error: any) {
      ElMessage.error(error?.message || '更新失败')
      // 回滚状态
      taskCompletionStatus.value = !taskCompletionStatus.value
    }
  }
}

const prevDate = () => {
  if (calendarView.value === 'month') {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
  } else if (calendarView.value === 'week') {
    const newDate = new Date(currentDate.value)
    newDate.setDate(currentDate.value.getDate() - 7)
    currentDate.value = newDate
  } else {
    const newDate = new Date(currentDate.value)
    newDate.setDate(currentDate.value.getDate() - 1)
    currentDate.value = newDate
  }
}

const nextDate = () => {
  if (calendarView.value === 'month') {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
  } else if (calendarView.value === 'week') {
    const newDate = new Date(currentDate.value)
    newDate.setDate(currentDate.value.getDate() + 7)
    currentDate.value = newDate
  } else {
    const newDate = new Date(currentDate.value)
    newDate.setDate(currentDate.value.getDate() + 1)
    currentDate.value = newDate
  }
}

const today = () => {
  currentDate.value = new Date()
}

// 生命周期
onMounted(() => {
  // 加载任务数据
  tasksStore.fetchRegularTasks()
  tasksStore.fetchDynamicTasks()
  
  // 初始选中今天
  const today = new Date().toISOString().split('T')[0]
  const todayDay = monthDays.value.find(day => day.date === today)
  if (todayDay) {
    selectedDay.value = todayDay
  }
})

// 监听视图切换
watch(calendarView, () => {
  // 切换视图时重置选中的日期
  const today = new Date().toISOString().split('T')[0]
  const todayDay = monthDays.value.find(day => day.date === today)
  if (todayDay) {
    selectedDay.value = todayDay
  }
})
</script>

<style scoped>
.calendar-container {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.calendar-wrapper {
  margin-top: 20px;
}

.calendar-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  gap: 15px;
}

.current-date {
  font-size: 18px;
  font-weight: bold;
}

/* 月视图样式 */
.month-view {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.weekday {
  padding: 10px;
  text-align: center;
  font-weight: bold;
  color: #606266;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, 120px);
}

.calendar-day {
  padding: 8px;
  border-right: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  overflow: hidden;
  position: relative;
}

.calendar-day:nth-child(7n) {
  border-right: none;
}

.calendar-day.other-month {
  background-color: #f9f9f9;
  color: #c0c4cc;
}

.calendar-day.today {
  background-color: #ecf5ff;
}

.calendar-day.today .day-number {
  background-color: #409eff;
  color: white;
  border-radius: 50%;
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
}

.day-number {
  font-weight: bold;
  margin-bottom: 5px;
}

.day-tasks {
  margin-top: 5px;
}

.task-item {
  padding: 2px 4px;
  margin-bottom: 2px;
  border-radius: 2px;
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-item.regular {
  background-color: #ecf5ff;
  color: #409eff;
}

.task-item.dynamic {
  background-color: #f0f9eb;
  color: #67c23a;
}

.more-tasks {
  font-size: 11px;
  color: #909399;
  text-align: center;
  margin-top: 2px;
}

/* 周视图样式 */
.week-view-grid {
  display: flex;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.time-column {
  width: 60px;
  border-right: 1px solid #ebeef5;
  background-color: #f5f7fa;
}

.time-slot {
  height: 60px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #909399;
}

.week-days-column {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.week-days-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.week-day-header {
  padding: 8px;
  text-align: center;
  border-right: 1px solid #ebeef5;
}

.week-day-header:last-child {
  border-right: none;
}

.week-day-header.today {
  background-color: #ecf5ff;
}

.week-day-name {
  font-weight: bold;
  font-size: 14px;
}

.week-day-date {
  font-size: 12px;
  color: #909399;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  height: calc(24 * 60px);
}

.day-column {
  border-right: 1px solid #ebeef5;
  position: relative;
}

.day-column:last-child {
  border-right: none;
}

.time-slots {
  height: 100%;
  position: relative;
}

.task-slot {
  position: absolute;
  left: 2px;
  right: 2px;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 12px;
  overflow: hidden;
  cursor: pointer;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.task-slot.regular {
  background-color: #ecf5ff;
  color: #409eff;
  border: 1px solid #409eff;
}

.task-slot.dynamic {
  background-color: #f0f9eb;
  color: #67c23a;
  border: 1px solid #67c23a;
}

/* 日视图样式 */
.day-view-header {
  text-align: center;
  margin-bottom: 20px;
}

.day-view-grid {
  display: flex;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.tasks-column {
  flex: 1;
  position: relative;
}

.task-time {
  font-size: 11px;
  margin-bottom: 2px;
}

.task-title {
  font-weight: bold;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-location {
  font-size: 11px;
  opacity: 0.8;
}

/* 任务详情对话框 */
.task-details {
  padding: 10px 0;
}

.detail-item {
  margin-bottom: 12px;
}

.tag-item {
  margin-right: 5px;
  margin-bottom: 5px;
}
</style>