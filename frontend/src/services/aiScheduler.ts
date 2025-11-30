import apiClient from '../utils/axios';

export interface ScheduleItem {
  task_id: number;
  title: string;
  start_time: string;
  end_time: string;
  priority_score: number;
  confidence: number;
}

export interface GenerateScheduleResponse {
  success: boolean;
  date: string;
  schedule: ScheduleItem[];
  total_tasks: number;
  error?: string;
}

export interface RecommendationsResponse {
  success: boolean;
  date: string;
  recommendations: string;
  ai_success: boolean;
  error?: string;
}

export interface WorkPatternsResponse {
  success: boolean;
  patterns: {
    total_completed: number;
    completion_rate: number;
    tasks_by_priority: {
      high: number;
      medium: number;
      low: number;
    };
    average_completion_time: number;
    preferred_time_slots: Record<string, number>;
  };
  error?: string;
}

export interface WeeklyScheduleResponse {
  success: boolean;
  start_date: string;
  end_date: string;
  weekly_schedule: Record<string, ScheduleItem[]>;
  total_tasks: number;
  error?: string;
}

/**
 * 生成每日日程表
 * @param date 日期，格式：YYYY-MM-DD
 * @returns 日程表数据
 */
export async function generateDailySchedule(date: string): Promise<GenerateScheduleResponse> {
  try {
    const response = await apiClient.post<GenerateScheduleResponse>('/api/ai/generate-schedule', {
      date
    });
    return response.data;
  } catch (error) {
    console.error('生成日程表失败:', error);
    throw error;
  }
}

/**
 * 获取AI日程优化建议
 * @param date 日期，格式：YYYY-MM-DD
 * @returns AI建议
 */
export async function getAIRecommendations(date: string): Promise<RecommendationsResponse> {
  try {
    const response = await apiClient.post<RecommendationsResponse>('/api/ai/get-recommendations', {
      date
    });
    return response.data;
  } catch (error) {
    console.error('获取AI建议失败:', error);
    throw error;
  }
}

/**
 * 分析工作模式
 * @returns 工作模式分析数据
 */
export async function analyzeWorkPatterns(): Promise<WorkPatternsResponse> {
  try {
    const response = await apiClient.get<WorkPatternsResponse>('/api/ai/analyze-work-patterns');
    return response.data;
  } catch (error) {
    console.error('分析工作模式失败:', error);
    throw error;
  }
}

/**
 * 获取周计划
 * @param startDate 开始日期，格式：YYYY-MM-DD
 * @returns 周计划数据
 */
export async function getWeeklySchedule(startDate: string): Promise<WeeklyScheduleResponse> {
  try {
    const response = await apiClient.post<WeeklyScheduleResponse>('/api/ai/get-weekly-schedule', {
      start_date: startDate
    });
    return response.data;
  } catch (error) {
    console.error('获取周计划失败:', error);
    throw error;
  }
}

/**
 * 计算任务持续时间（分钟）
 * @param startTime 开始时间
 * @param endTime 结束时间
 * @returns 持续时间（分钟）
 */
export function calculateDuration(startTime: string, endTime: string): number {
  const start = new Date(startTime);
  const end = new Date(endTime);
  return Math.round((end.getTime() - start.getTime()) / (1000 * 60));
}

/**
 * 格式化时间范围
 * @param startTime 开始时间
 * @param endTime 结束时间
 * @returns 格式化的时间范围字符串
 */
export function formatTimeRange(startTime: string, endTime: string): string {
  const start = new Date(startTime);
  const end = new Date(endTime);
  
  const formatTime = (date: Date) => {
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  };
  
  return `${formatTime(start)} - ${formatTime(end)}`;
}

/**
 * 获取任务优先级颜色
 * @param priorityScore 优先级分数
 * @returns 颜色类名
 */
export function getPriorityColor(priorityScore: number): string {
  if (priorityScore >= 1000) return 'primary'; // 常规任务
  if (priorityScore >= 200) return 'danger';  // 高优先级
  if (priorityScore >= 100) return 'warning'; // 中优先级
  return 'success'; // 低优先级
}
