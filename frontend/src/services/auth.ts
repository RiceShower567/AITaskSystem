import apiClient from '../utils/axios'

// 登录请求参数接口
export interface LoginRequest {
  username: string
  password: string
}

// 注册请求参数接口
export interface RegisterRequest {
  username: string
  email: string
  password: string
}

// 用户信息接口
export interface UserInfo {
  id: number
  username: string
  email: string
  created_at: string
}

// 登录响应接口
export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: UserInfo
}

// 注册响应接口
export interface RegisterResponse {
  message: string
  user: UserInfo
}

/**
 * 用户登录
 * @param credentials 登录凭据
 * @returns 登录响应数据
 */
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  return apiClient.post('/auth/login', credentials)
}

/**
 * 用户注册
 * @param userData 用户注册数据
 * @returns 注册响应数据
 */
export const register = async (userData: RegisterRequest): Promise<RegisterResponse> => {
  return apiClient.post('/auth/register', userData)
}

/**
 * 获取当前用户信息
 * @returns 用户信息
 */
export const getCurrentUser = async (): Promise<UserInfo> => {
  return apiClient.get('/auth/me')
}

/**
 * 用户登出
 */
export const logout = async (): Promise<void> => {
  return apiClient.post('/auth/logout')
}