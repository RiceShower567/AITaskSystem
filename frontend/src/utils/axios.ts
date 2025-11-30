import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api', // 与Vite配置中的代理路径匹配
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 直接从localStorage获取token
    const token = localStorage.getItem('token')
    
    // 如果有token，添加到请求头
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error: AxiosError<{ message?: string; error?: string }>) => {
    const { response } = error
    
    if (response) {
      switch (response.status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          // 直接清除localStorage中的token，而不是使用store
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          ElMessage.error('登录已过期，请重新登录')
          router.push('/login')
          break
          
        case 403:
          ElMessage.error('没有权限访问此资源')
          break
          
        case 404:
          ElMessage.error('请求的资源不存在')
          break
          
        case 500:
          ElMessage.error('服务器错误')
          break
          
        default:
          // 尝试获取响应中的错误消息
          const errorMsg = response.data?.message || response.data?.error || '请求失败'
          ElMessage.error(String(errorMsg))
      }
    } else {
      // 网络错误等情况
      ElMessage.error('网络连接失败，请检查您的网络设置')
    }
    
    return Promise.reject(error)
  }
)

export default apiClient