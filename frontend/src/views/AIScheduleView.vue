<template>
  <div class="ai-schedule-container">
    <el-card class="schedule-card">
      <template #header>
        <div class="card-header">
          <span>AI智能日程安排</span>
          <div class="header-actions">
            <el-date-picker
              v-model="selectedDate"
              type="date"
              placeholder="选择日期"
              style="width: 180px"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
            <el-button type="primary" @click="generateSchedule">
              <el-icon><Refresh /></el-icon>
              生成日程
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="error" class="error-container">
        <el-alert
          title="生成失败"
          :description="error"
          type="error"
          show-icon
          :closable="false"
        />
        <el-button type="primary" @click="generateSchedule" class="mt-4">重试</el-button>
      </div>

      <div v-else-if="schedule.length > 0" class="schedule-content">
        <div class="schedule-stats">
          <el-statistic title="总任务数" :value="schedule.length" />
          <el-statistic title="预计耗时" :value="totalDuration" suffix="分钟" />
        </div>

        <div class="schedule-timeline">
          <el-timeline>
            <el-timeline-item
              v-for="item in schedule"
              :key="item.task_id"
              :timestamp="formatTimeRange(item.start_time, item.end_time)"
              :type="getPriorityColor(item.priority_score)"
            >
              <div class="task-item">
                <h3 class="task-title">{{ item.title }}</h3>
                <div class="task-meta">
                  <el-tag :type="getPriorityColor(item.priority_score)">
                    {{ getPriorityLabel(item.priority_score) }}
                  </el-tag>
                  <el-tag type="info" effect="plain">
                    <el-icon><Timer /></el-icon>
                    {{ calculateDuration(item.start_time, item.end_time) }}分钟
                  </el-tag>
                  <el-tag v-if="item.confidence < 0.8" type="warning" effect="plain">
                    建议调整
                  </el-tag>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <div class="ai-recommendations">
          <el-collapse>
            <el-collapse-item title="AI优化建议" name="recommendations">
              <div v-if="loadingRecommendations" class="loading-recommendations">
                <el-skeleton :rows="3" animated />
              </div>
              <div v-else-if="recommendations" class="recommendations-content">
                <div class="markdown-body" v-html="formatRecommendations(recommendations)"></div>
              </div>
              <div v-else>
                <el-button type="primary" @click="fetchRecommendations">
                  <el-icon><ChatLineRound /></el-icon>
                  获取AI建议
                </el-button>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <div v-else class="empty-schedule">
        <el-empty description="暂无日程安排" />
        <el-button type="primary" @click="generateSchedule" class="mt-4">生成日程</el-button>
      </div>
    </el-card>

    <el-card class="weekly-schedule-card">
      <template #header>
        <div class="card-header">
          <span>周计划预览</span>
          <el-button type="primary" @click="showWeeklySchedule = !showWeeklySchedule">
            {{ showWeeklySchedule ? '隐藏' : '显示' }}周计划
          </el-button>
        </div>
      </template>

      <div v-if="showWeeklySchedule" class="weekly-content">
        <div v-if="weeklyLoading" class="loading-container">
          <el-skeleton :rows="10" animated />
        </div>
        <div v-else-if="weeklyError" class="error-container">
          <el-alert
            title="获取失败"
            :description="weeklyError"
            type="error"
            show-icon
            :closable="false"
          />
          <el-button type="primary" @click="fetchWeeklySchedule" class="mt-4">重试</el-button>
        </div>
        <div v-else-if="weeklySchedule && Object.keys(weeklySchedule).length > 0" class="weekly-grid">
          <div
            v-for="(daySchedule, date) in weeklySchedule"
            :key="date"
            class="day-column"
          >
            <div class="day-header">
              <div class="date">{{ formatDateHeader(date) }}</div>
              <div class="task-count">{{ daySchedule.length }}个任务</div>
            </div>
            <div class="day-tasks">
              <div
                v-for="task in daySchedule.slice(0, 3)"
                :key="task.task_id"
                class="mini-task"
                :class="`priority-${getPriorityLevel(task.priority_score)}`"
              >
                <div class="mini-task-title">{{ task.title }}</div>
                <div class="mini-task-time">{{ formatMiniTaskTime(task.start_time) }}</div>
              </div>
              <div v-if="daySchedule.length > 3" class="more-tasks">
                还有{{ daySchedule.length - 3 }}个任务...
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <el-button type="primary" @click="fetchWeeklySchedule">
            <el-icon><Calendar /></el-icon>
            获取周计划
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="work-patterns-card">
      <template #header>
        <div class="card-header">
          <span>工作模式分析</span>
          <el-button type="primary" @click="showWorkPatterns = !showWorkPatterns">
            {{ showWorkPatterns ? '隐藏' : '显示' }}分析
          </el-button>
        </div>
      </template>

      <div v-if="showWorkPatterns" class="work-patterns-content">
        <div v-if="patternsLoading" class="loading-container">
          <el-skeleton :rows="6" animated />
        </div>
        <div v-else-if="patternsError" class="error-container">
          <el-alert
            title="分析失败"
            :description="patternsError"
            type="error"
            show-icon
            :closable="false"
          />
          <el-button type="primary" @click="fetchWorkPatterns" class="mt-4">重试</el-button>
        </div>
        <div v-else-if="workPatterns" class="patterns-grid">
          <div class="pattern-item">
            <div class="pattern-title">完成任务</div>
            <div class="pattern-value">{{ workPatterns.total_completed }}</div>
          </div>
          <div class="pattern-item">
            <div class="pattern-title">完成率</div>
            <div class="pattern-value">{{ Math.round(workPatterns.completion_rate * 100) }}%</div>
          </div>
          <div class="pattern-item">
            <div class="pattern-title">高优先级</div>
            <div class="pattern-value">{{ workPatterns.tasks_by_priority.high }}</div>
          </div>
          <div class="pattern-item">
            <div class="pattern-title">中优先级</div>
            <div class="pattern-value">{{ workPatterns.tasks_by_priority.medium }}</div>
          </div>
          <div class="pattern-item">
            <div class="pattern-title">低优先级</div>
            <div class="pattern-value">{{ workPatterns.tasks_by_priority.low }}</div>
          </div>
        </div>
        <div v-else>
          <el-button type="primary" @click="fetchWorkPatterns">
            <el-icon><DataAnalysis /></el-icon>
            分析工作模式
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import {
  generateDailySchedule,
  getAIRecommendations,
  analyzeWorkPatterns,
  getWeeklySchedule,
  calculateDuration,
  formatTimeRange,
  getPriorityColor
} from '../services/aiScheduler';
import type { ScheduleItem } from '../services/aiScheduler';
import { Refresh, Timer, ChatLineRound, Calendar, DataAnalysis } from '@element-plus/icons-vue';

// 响应式数据
const selectedDate = ref(new Date().toISOString().split('T')[0]);
const schedule = ref<ScheduleItem[]>([]);
const recommendations = ref<string>('');
const workPatterns = ref<any>(null);
const weeklySchedule = ref<Record<string, ScheduleItem[]>>({});
// 加载状态
const loading = ref(false);
const loadingRecommendations = ref(false);
const patternsLoading = ref(false);
const weeklyLoading = ref(false);
// 错误处理
const error = ref('');
const weeklyError = ref('');
const patternsError = ref('');
// UI控制
const showWeeklySchedule = ref(false);
const showWorkPatterns = ref(false);

// 计算属性
const totalDuration = computed(() => {
  return schedule.value.reduce((total, item) => {
    return total + calculateDuration(item.start_time, item.end_time);
  }, 0);
});

// 方法
const generateSchedule = async () => {
  loading.value = true;
  error.value = '';
  recommendations.value = '';
  
  try {
    const result = await generateDailySchedule(selectedDate.value);
    if (result.success) {
      schedule.value = result.schedule || [];
      ElMessage.success('日程生成成功');
    } else {
      error.value = result.error || '生成失败';
      ElMessage.error('生成日程失败: ' + error.value);
    }
  } catch (err: any) {
    error.value = err?.message || '生成失败';
    console.error('生成日程失败:', err);
    ElMessage.error('生成日程失败，请检查网络连接或稍后重试');
  } finally {
    loading.value = false;
  }
};

const fetchRecommendations = async () => {
  loadingRecommendations.value = true;
  
  try {
    const result = await getAIRecommendations(selectedDate.value);
    if (result.success) {
      recommendations.value = result.recommendations;
      ElMessage.success('获取AI建议成功');
    }
  } catch (err) {
    ElMessage.error('获取AI建议失败');
    console.error('获取AI建议失败:', err);
  } finally {
    loadingRecommendations.value = false;
  }
};

const fetchWorkPatterns = async () => {
  patternsLoading.value = true;
  patternsError.value = '';
  
  try {
    const result = await analyzeWorkPatterns();
    if (result.success) {
      workPatterns.value = result.patterns || null;
      ElMessage.success('工作模式分析成功');
    } else {
      patternsError.value = result.error || '分析失败';
      ElMessage.error('工作模式分析失败: ' + patternsError.value);
    }
  } catch (err: any) {
    patternsError.value = err?.message || '分析失败';
    console.error('分析工作模式失败:', err);
    ElMessage.error('工作模式分析失败，请稍后重试');
  } finally {
    patternsLoading.value = false;
  }
};

const fetchWeeklySchedule = async () => {
  weeklyLoading.value = true;
  weeklyError.value = '';
  
  try {
    // 计算本周一的日期
    const today = new Date(selectedDate.value);
    const dayOfWeek = today.getDay();
    const monday = new Date(today);
    monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));
    const mondayStr = monday.toISOString().split('T')[0];
    
    const result = await getWeeklySchedule(mondayStr);
    if (result.success) {
      weeklySchedule.value = result.weekly_schedule || {};
      ElMessage.success('获取周计划成功');
    } else {
      weeklyError.value = result.error || '获取失败';
      ElMessage.error('获取周计划失败: ' + weeklyError.value);
    }
  } catch (err: any) {
    weeklyError.value = err?.message || '获取失败';
    console.error('获取周计划失败:', err);
    ElMessage.error('获取周计划失败，请稍后重试');
  } finally {
    weeklyLoading.value = false;
  }
};

const getPriorityLabel = (score: number): string => {
  if (score >= 1000) return '常规任务';
  if (score >= 200) return '高优先级';
  if (score >= 100) return '中优先级';
  return '低优先级';
};

const getPriorityLevel = (score: number): string => {
  if (score >= 1000) return 'regular';
  if (score >= 200) return 'high';
  if (score >= 100) return 'medium';
  return 'low';
};

const formatDateHeader = (dateStr: string): string => {
  const date = new Date(dateStr);
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  return `${date.getMonth() + 1}月${date.getDate()}日 ${weekdays[date.getDay()]}`;
};

const formatMiniTaskTime = (timeStr: string): string => {
  const date = new Date(timeStr);
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const formatRecommendations = (text: string): string => {
  // 简单的Markdown渲染
  return text
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^- (.*$)/gm, '<li>$1</li>')
    .replace(/^(\d+\. )(.*$)/gm, '<li>$2</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
};

// 生命周期
onMounted(() => {
  generateSchedule();
});
</script>

<style scoped>
.ai-schedule-container {
  padding: 20px;
}

.schedule-card,
.weekly-schedule-card,
.work-patterns-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.loading-container {
  padding: 20px 0;
}

.error-container {
  text-align: center;
  padding: 20px 0;
}

.empty-schedule {
  text-align: center;
  padding: 40px 0;
}

.schedule-content {
  padding: 20px 0;
}

.schedule-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 30px;
}

.schedule-timeline {
  margin-bottom: 30px;
}

.task-item {
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
}

.task-title {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.task-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.ai-recommendations {
  margin-top: 20px;
}

.recommendations-content {
  padding: 10px 0;
}

.markdown-body {
  line-height: 1.6;
}

.markdown-body h1,
.markdown-body h2 {
  margin: 16px 0 8px 0;
  font-size: 18px;
}

.markdown-body ul {
  margin: 8px 0;
  padding-left: 20px;
}

.markdown-body li {
  margin: 4px 0;
}

.weekly-content,
.work-patterns-content {
  padding: 20px 0;
}

.weekly-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 15px;
}

.day-column {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.day-header {
  background-color: #f5f7fa;
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #ebeef5;
}

.date {
  font-weight: bold;
  margin-bottom: 4px;
}

.task-count {
  font-size: 12px;
  color: #909399;
}

.day-tasks {
  padding: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.mini-task {
  padding: 5px;
  margin-bottom: 5px;
  border-radius: 3px;
  font-size: 12px;
}

.mini-task.priority-regular {
  background-color: #ecf5ff;
}

.mini-task.priority-high {
  background-color: #fef0f0;
}

.mini-task.priority-medium {
  background-color: #fdf6ec;
}

.mini-task.priority-low {
  background-color: #f0f9eb;
}

.mini-task-title {
  font-weight: bold;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-task-time {
  color: #909399;
}

.more-tasks {
  text-align: center;
  color: #909399;
  font-size: 11px;
  margin-top: 5px;
}

.patterns-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

.pattern-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pattern-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.pattern-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}
</style>
