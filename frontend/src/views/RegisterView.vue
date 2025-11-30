<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <span>用户注册</span>
        </div>
      </template>
      
      <el-form ref="registerFormRef" :model="registerForm" :rules="rules" label-width="80px" class="register-form">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名" 
            prefix-icon="User"
            clearable
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="registerForm.email" 
            type="email" 
            placeholder="请输入邮箱" 
            prefix-icon="Message"
            clearable
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码（至少6位）" 
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码" 
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="agreement">我已阅读并同意<a href="#" class="agreement-link">用户协议</a>和<a href="#" class="agreement-link">隐私政策</a></el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" class="register-button" @click="handleRegister">注册</el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-footer">
        <span>已有账号？</span>
        <el-link type="primary" @click="navigateToLogin">立即登录</el-link>
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
const registerFormRef = ref<FormInstance>()

// 注册表单数据
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 同意协议
const agreement = ref(false)

// 表单验证规则
const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' },
    // 密码强度检查
    {
      validator: (rule, value, callback) => {
        if (value && !/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
          callback(new Error('密码必须包含大小写字母和数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
})

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  // 检查是否同意协议
  if (!agreement.value) {
    ElMessage.warning('请阅读并同意用户协议和隐私政策')
    return
  }
  
  try {
    await registerFormRef.value.validate()
    
    // 显示加载状态
    ElMessage.loading('注册中...', { duration: 0 })
    
    // 调用注册方法
    await authStore.register(registerForm.username, registerForm.email, registerForm.password)
    
    // 注册成功
    ElMessage.success('注册成功，请登录')
    
    // 重定向到登录页面
    router.push('/login')
    
  } catch (error: any) {
    ElMessage.error(error?.message || '注册失败，请稍后重试')
    console.error('Register error:', error)
  } finally {
    // 关闭加载状态
    ElMessage.closeAll()
  }
}

// 导航到登录页面
const navigateToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 450px;
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

.register-form {
  padding: 0 20px 20px;
}

.register-button {
  width: 100%;
  margin-top: 10px;
}

.register-footer {
  text-align: center;
  padding: 10px 0 20px;
  color: #606266;
}

.register-footer .el-link {
  margin-left: 5px;
}

.agreement-link {
  color: #409eff;
  text-decoration: none;
}

.agreement-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .register-card {
    width: 100%;
    margin: 0 10px;
  }
}
</style>