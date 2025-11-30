import { createRouter, createWebHistory } from 'vue-router'

// 定义路由
export const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/TasksView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/calendar',
    name: 'Calendar',
    component: () => import('../views/CalendarView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-schedule',
    name: 'AISchedule',
    component: () => import('../views/AIScheduleView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue')
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 直接从localStorage检查登录状态
  const token = localStorage.getItem('token')
  const isLoggedIn = !!token
  const requiresAuth = to.meta.requiresAuth as boolean
  
  // 如果路由需要认证且用户未登录，则跳转到登录页
  if (requiresAuth && !isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } 
  // 如果用户已登录且访问登录/注册页，则跳转到首页
  else if (!requiresAuth && isLoggedIn && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router