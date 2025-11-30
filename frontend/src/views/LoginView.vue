<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>用户登录</span>
        </div>
      </template>
      
      <el-form ref="loginFormRef" :model="loginForm" :rules="rules" label-width="80px" class="login-form">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名或邮箱" 
            prefix-icon="User"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码" 
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <el-button type="primary" class="login-button" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <span>还没有账号？</span>
        <el-link type="primary" @click="navigateToRegister">立即注册</el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref<FormInstance>()

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 记住我状态
const rememberMe = ref(false)

// 表单验证规则
const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
})

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    
    // 显示加载状态
    ElMessage.loading('登录中...', { duration: 0 })
    
    // 调用登录方法
    await authStore.login(loginForm.username, loginForm.password)
    
    // 登录成功
    ElMessage.success('登录成功')
    
    // 如果用户之前尝试访问其他页面，重定向到那里，否则到首页
    const redirectPath = sessionStorage.getItem('redirectPath') || '/'
    sessionStorage.removeItem('redirectPath')
    router.replace(redirectPath)
    
  } catch (error: any) {
    ElMessage.error(error?.message || '登录失败，请检查用户名和密码')
    console.error('Login error:', error)
  } finally {
    // 关闭加载状态
    ElMessage.closeAll()
  }
}

// 导航到注册页面
const navigateToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  max-width: 100%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.card-header span {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.login-form {
  padding: 0 20px 20px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
}

.login-footer {
  text-align: center;
  padding: 10px 0 20px;
  color: #606266;
}

.login-footer .el-link {
  margin-left: 5px;
}

@media (max-width: 768px) {
  .login-card {
    width: 100%;
    margin: 0 10px;
  }
}
</style>