import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AxiosError } from 'axios'
import {
  RegularTask,
  DynamicTask,
  CreateRegularTaskParams,
  CreateDynamicTaskParams,
  UpdateRegularTaskParams,
  UpdateDynamicTaskParams,
  RegularTaskFilter,
  DynamicTaskFilter,
  getRegularTasks,
  createRegularTask,
  updateRegularTask,
  deleteRegularTask,
  getDynamicTasks,
  createDynamicTask,
  updateDynamicTask,
  deleteDynamicTask,
  toggleTaskCompletion,
  batchCreateDynamicTasks
} from '../services/tasks'

export const useTasksStore = defineStore('tasks', () => {
  // 状态
  const regularTasks = ref<RegularTask[]>([])
  const dynamicTasks = ref<DynamicTask[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const pendingTasks = computed(() => {
    return dynamicTasks.value.filter(task => !task.completed)
  })

  const completedTasks = computed(() => {
    return dynamicTasks.value.filter(task => task.completed)
  })

  const highPriorityTasks = computed(() => {
    return dynamicTasks.value.filter(task => task.priority === 'high' && !task.completed)
  })

  // 常规任务相关方法
  async function fetchRegularTasks(filter?: RegularTaskFilter): Promise<void> {
    loading.value = true
    error.value = null
    try {
      regularTasks.value = await getRegularTasks(filter)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取常规任务失败'
      error.value = errorMessage
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function addRegularTask(task: CreateRegularTaskParams): Promise<RegularTask> {
    loading.value = true
    error.value = null
    try {
      const newTask = await createRegularTask(task)
      regularTasks.value.push(newTask)
      return newTask
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '添加常规任务失败'
      error.value = errorMessage
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateRegularTaskById(id: number, updates: UpdateRegularTaskParams): Promise<RegularTask> {
    loading.value = true
    error.value = null
    try {
      const updatedTask = await updateRegularTask(id, updates)
      const index = regularTasks.value.findIndex(task => task.id === id)
      if (index !== -1) {
        regularTasks.value[index] = updatedTask
      }
      return updatedTask
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '更新常规任务失败'
      error.value = errorMessage
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteRegularTaskById(id: number): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await deleteRegularTask(id)
      const index = regularTasks.value.findIndex(task => task.id === id)
      if (index !== -1) {
        regularTasks.value.splice(index, 1)
      }
      return true
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '删除常规任务失败'
      error.value = errorMessage
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 动态任务相关方法
  async function fetchDynamicTasks(filter?: DynamicTaskFilter): Promise<void> {
    loading.value = true
    error.value = null
    try {
      dynamicTasks.value = await getDynamicTasks(filter)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取动态任务失败'
      error.value = errorMessage
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function addDynamicTask(task: CreateDynamicTaskParams): Promise<DynamicTask> {
    loading.value = true
    error.value = null
    try {
      const newTask = await createDynamicTask(task)
      dynamicTasks.value.push(newTask)
      return newTask
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '添加动态任务失败'
      error.value = errorMessage
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateDynamicTaskById(id: number, updates: UpdateDynamicTaskParams): Promise<DynamicTask> {
    loading.value = true
    error.value = null
    try {
      const updatedTask = await updateDynamicTask(id, updates)
      const index = dynamicTasks.value.findIndex(task => task.id === id)
      if (index !== -1) {
        dynamicTasks.value[index] = updatedTask
      }
      return updatedTask
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '更新动态任务失败'
      error.value = errorMessage
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteDynamicTaskById(id: number): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await deleteDynamicTask(id)
      const index = dynamicTasks.value.findIndex(task => task.id === id)
      if (index !== -1) {
        dynamicTasks.value.splice(index, 1)
      }
      return true
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '删除动态任务失败'
      error.value = errorMessage
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function markTaskAsCompleted(id: number, completed: boolean): Promise<DynamicTask> {
    loading.value = true
    error.value = null
    try {
      const updatedTask = await toggleTaskCompletion(id, completed)
      const index = dynamicTasks.value.findIndex(task => task.id === id)
      if (index !== -1) {
        dynamicTasks.value[index] = updatedTask
      }
      return updatedTask
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '更新任务完成状态失败'
      error.value = errorMessage
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function batchAddDynamicTasks(tasks: Omit<CreateDynamicTaskParams, 'tags'>[]): Promise<DynamicTask[]> {
    loading.value = true
    error.value = null
    try {
      // 确保参数格式正确
      const newTasks = await batchCreateDynamicTasks({ tasks })
      dynamicTasks.value.push(...newTasks)
      return newTasks
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '批量添加动态任务失败'
      error.value = errorMessage
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    regularTasks,
    dynamicTasks,
    loading,
    error,
    
    // 计算属性
    pendingTasks,
    completedTasks,
    highPriorityTasks,
    
    // 方法
    fetchRegularTasks,
    addRegularTask,
    updateRegularTaskById,
    deleteRegularTaskById,
    fetchDynamicTasks,
    addDynamicTask,
    updateDynamicTaskById,
    deleteDynamicTaskById,
    markTaskAsCompleted,
    batchAddDynamicTasks
  }
})