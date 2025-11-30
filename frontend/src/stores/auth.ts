import { defineStore } from 'pinia'
import apiClient from '../utils/axios'
import type { AxiosError } from 'axios'

interface User {
  id: number
  username: string
  email: string
}

interface LoginResponse {
  user: User
  access_token: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoggedIn: boolean
  loading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('token'),
    isLoggedIn: !!localStorage.getItem('token'),
    loading: false
  }),

  actions: {
    // 设置认证信息
    setAuth(user: User, token: string): void {
      this.user = user
      this.token = token
      this.isLoggedIn = true
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },

    // 清除认证信息
    clearAuth(): void {
      this.user = null
      this.token = null
      this.isLoggedIn = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    // 登录
    async login(email: string, password: string): Promise<{ success: boolean; message?: string }> {
      try {
        this.loading = true
        const response = await apiClient.post<LoginResponse>('/auth/login', { email, password })
        this.setAuth(response.user, response.access_token)
        return { success: true }
      } catch (error) {
        const axiosError = error as AxiosError<{ message?: string }>
        return { 
          success: false, 
          message: axiosError.response?.data?.message || '登录失败，请稍后重试' 
        }
      } finally {
        this.loading = false
      }
    },

    // 注册
    async register(username: string, email: string, password: string): Promise<{ success: boolean; message?: string }> {
      try {
        this.loading = true
        await apiClient.post('/auth/register', { username, email, password })
        return { success: true }
      } catch (error) {
        const axiosError = error as AxiosError<{ message?: string }>
        return { 
          success: false, 
          message: axiosError.response?.data?.message || '注册失败，请稍后重试' 
        }
      } finally {
        this.loading = false
      }
    },

    // 登出
    logout(): void {
      this.clearAuth()
    },

    // 检查认证状态
    checkAuth(): void {
      const token = localStorage.getItem('token')
      const userStr = localStorage.getItem('user')
      
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr)
          this.setAuth(user, token)
        } catch (error) {
          this.clearAuth()
        }
      } else {
        this.clearAuth()
      }
    }
  }
})