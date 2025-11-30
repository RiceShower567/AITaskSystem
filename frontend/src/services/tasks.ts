import apiClient from '../utils/axios'

// 常规任务接口
export interface RegularTask {
  id: number
  title: string
  type: string
  location?: string
  start_time: string
  end_time: string
  repeat_type: 'daily' | 'weekly' | 'single'
  repeat_days?: number[] // 0-6，对应周日到周六
  created_at: string
  updated_at: string
}

// 动态任务接口
export interface DynamicTask {
  id: number
  title: string
  priority: 'high' | 'medium' | 'low'
  estimated_time: number // 预计耗时（分钟）
  deadline?: string
  tags?: string[]
  completed: boolean
  completed_at?: string
  created_at: string
  updated_at: string
}

// 创建常规任务参数
export interface CreateRegularTaskParams {
  title: string
  type: string
  location?: string
  start_time: string
  end_time: string
  repeat_type: 'daily' | 'weekly' | 'single'
  repeat_days?: number[]
}

// 创建动态任务参数
export interface CreateDynamicTaskParams {
  title: string
  priority: 'high' | 'medium' | 'low'
  estimated_time: number
  deadline?: string
  tags?: string[]
}

// 更新常规任务参数
export interface UpdateRegularTaskParams extends Partial<CreateRegularTaskParams> {
  // 部分更新参数
}

// 更新动态任务参数
export interface UpdateDynamicTaskParams extends Partial<CreateDynamicTaskParams> {
  completed?: boolean
  completed_at?: string
}

// 常规任务筛选参数
export interface RegularTaskFilter {
  start_date?: string
  end_date?: string
  type?: string
}

// 动态任务筛选参数
export interface DynamicTaskFilter {
  completed?: boolean
  priority?: 'high' | 'medium' | 'low'
  deadline?: string
  tag?: string
  sort_by?: 'created_at' | 'priority' | 'deadline'
  order?: 'asc' | 'desc'
}

// 批量创建动态任务参数
export interface BatchCreateDynamicTasksParams {
  tasks: Omit<CreateDynamicTaskParams, 'tags'>[]
}

/**
 * 获取常规任务列表
 * @param filter 筛选条件
 * @returns 常规任务列表
 */
export const getRegularTasks = async (filter?: RegularTaskFilter): Promise<RegularTask[]> => {
  return apiClient.get('/tasks/regular', { params: filter })
}

/**
 * 创建常规任务
 * @param taskData 任务数据
 * @returns 创建的任务
 */
export const createRegularTask = async (taskData: CreateRegularTaskParams): Promise<RegularTask> => {
  return apiClient.post('/tasks/regular', taskData)
}

/**
 * 更新常规任务
 * @param id 任务ID
 * @param taskData 更新数据
 * @returns 更新后的任务
 */
export const updateRegularTask = async (id: number, taskData: UpdateRegularTaskParams): Promise<RegularTask> => {
  return apiClient.put(`/tasks/regular/${id}`, taskData)
}

/**
 * 删除常规任务
 * @param id 任务ID
 */
export const deleteRegularTask = async (id: number): Promise<void> => {
  return apiClient.delete(`/tasks/regular/${id}`)
}

/**
 * 获取动态任务列表
 * @param filter 筛选条件
 * @returns 动态任务列表
 */
export const getDynamicTasks = async (filter?: DynamicTaskFilter): Promise<DynamicTask[]> => {
  return apiClient.get('/tasks/dynamic', { params: filter })
}

/**
 * 创建动态任务
 * @param taskData 任务数据
 * @returns 创建的任务
 */
export const createDynamicTask = async (taskData: CreateDynamicTaskParams): Promise<DynamicTask> => {
  return apiClient.post('/tasks/dynamic', taskData)
}

/**
 * 更新动态任务
 * @param id 任务ID
 * @param taskData 更新数据
 * @returns 更新后的任务
 */
export const updateDynamicTask = async (id: number, taskData: UpdateDynamicTaskParams): Promise<DynamicTask> => {
  return apiClient.put(`/tasks/dynamic/${id}`, taskData)
}

/**
 * 删除动态任务
 * @param id 任务ID
 */
export const deleteDynamicTask = async (id: number): Promise<void> => {
  return apiClient.delete(`/tasks/dynamic/${id}`)
}

/**
 * 标记动态任务完成状态
 * @param id 任务ID
 * @param completed 完成状态
 * @returns 更新后的任务
 */
export const toggleTaskCompletion = async (id: number, completed: boolean): Promise<DynamicTask> => {
  return apiClient.patch(`/tasks/dynamic/${id}/complete`, { completed })
}

/**
 * 批量创建动态任务
 * @param tasksData 任务数据数组
 * @returns 创建的任务列表
 */
export const batchCreateDynamicTasks = async (tasksData: BatchCreateDynamicTasksParams): Promise<DynamicTask[]> => {
  return apiClient.post('/tasks/dynamic/batch', tasksData)
}