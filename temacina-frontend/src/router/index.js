import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import AuthLayout from '@/layouts/AuthLayout.vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import LoginView from '@/views/auth/LoginView.vue'
import ForgotPasswordView from '@/views/auth/ForgotPasswordView.vue'
import ResetPasswordView from '@/views/auth/ResetPasswordView.vue'

const routes = [
  {
    path: '/',
    component: AuthLayout,
    children: [
      { path: '', redirect: '/app/help' },
      { path: 'login', name: 'login', component: LoginView, meta: { guestOnly: true } },
      { path: 'forgot-password', name: 'forgot-password', component: ForgotPasswordView, meta: { guestOnly: true } },
      { path: 'reset-password', name: 'reset-password', component: ResetPasswordView, meta: { guestOnly: true } },
    ],
  },
  {
    path: '/app',
    component: DashboardLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/app/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'profile', name: 'profile', component: () => import('@/views/ProfileView.vue') },

      { path: 'users-management', name: 'users-management', component: () => import('@/views/UsersManagementView.vue') },
      { path: 'help', name: 'help', component: () => import('@/views/HelpView.vue') },
      //{ path: 'trade-shows', name: 'trade-shows', component: () => import('@/views/TradeShowsView.vue') },
      //{ path: 'documentation', name: 'documentation', component: () => import('@/views/DocumentsPageView.vue') }
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

const HIERARCHY = ['viewer', 'analyst', 'manager', 'admin', 'superadmin']

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.guestOnly && auth.isAuthenticated) return next({ name: 'dashboard' })
  if (to.meta.requiresAuth && !auth.isAuthenticated) return next({ name: 'login', query: { redirect: to.fullPath } })

  if (auth.isAuthenticated && !auth.user) {
    try { await auth.fetchMe() }
    catch { auth.logout(); return next({ name: 'login' }) }
  }

  next()
})

export default router