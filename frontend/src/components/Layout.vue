<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <el-header class="layout-header">
      <div class="header-left">
        <el-button
          type="text"
          class="sidebar-toggle"
          @click="toggleSidebar"
          :icon="isSidebarCollapse ? 'Menu' : 'Close'"
        />
        <div class="logo">AI任务管理系统</div>
      </div>
      <div class="header-right">
        <el-dropdown trigger="click">
          <span class="user-info">
            <el-avatar :size="32" :src="userAvatar">
              {{ userInitial }}
            </el-avatar>
            <span class="username">{{ user?.username }}</span>
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="showUserProfile">
                <el-icon><User /></el-icon>
                <span>个人资料</span>
              </el-dropdown-item>
              <el-dropdown-item @click="logout" danger>
                <el-icon><SwitchButton /></el-icon>
                <span>退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 主体内容区 -->
    <div class="layout-main">
      <!-- 侧边栏 -->
      <el-aside
        class="layout-sidebar"
        :width="isSidebarCollapse ? '64px' : '200px'"
        :class="{ 'sidebar-collapse': isSidebarCollapse }"
      >
        <el-menu
          :default-active="activeRoute"
          class="sidebar-menu"
          router
          :collapse="isSidebarCollapse"
          :collapse-transition="false"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><List /></el-icon>
            <template #title>任务管理</template>
          </el-menu-item>
          <el-menu-item index="/calendar">
          <el-icon><Calendar /></el-icon>
          <template #title>任务日历</template>
        </el-menu-item>
        <el-menu-item index="/ai-schedule">
          <el-icon><Cpu /></el-icon>
          <template #title>AI智能调度</template>
        </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 内容区 -->
      <el-main class="layout-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, HomeFilled, List, Calendar, User, SwitchButton, Menu, Close, Cpu } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 侧边栏状态
const isSidebarCollapse = ref(false)

// 计算属性
const user = computed(() => authStore.user)

// 用户头像和首字母
const userAvatar = computed(() => {
  // 实际项目中可能从用户资料获取头像
  return ''
})

const userInitial = computed(() => {
  if (!user.value?.username) return 'U'
  return user.value.username.charAt(0).toUpperCase()
})

// 当前激活的路由
const activeRoute = computed(() => {
  return route.path
})

// 方法
const toggleSidebar = () => {
  isSidebarCollapse.value = !isSidebarCollapse.value
}

const showUserProfile = () => {
  ElMessage.info('个人资料功能待实现')
}

const logout = async () => {
  try {
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.layout-header {
  height: 60px;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
}

.sidebar-toggle {
  font-size: 20px;
  margin-right: 20px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 10px;
  font-weight: 500;
}

/* 主体内容区 */
.layout-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 侧边栏 */
.layout-sidebar {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar-menu {
  height: 100%;
  background-color: transparent;
}

.sidebar-menu .el-menu-item {
  height: 60px;
  line-height: 60px;
  color: rgba(255, 255, 255, 0.65);
  border-right: none;
  font-size: 14px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #1890ff;
  color: #fff;
}

/* 内容区 */
.layout-content {
  flex: 1;
  padding: 0;
  background-color: #f5f7fa;
  overflow-y: auto;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .logo {
    font-size: 16px;
  }
  
  .username {
    display: none;
  }
  
  .layout-sidebar {
    width: 64px !important;
  }
  
  .sidebar-collapse {
    width: 0 !important;
  }
}
</style>