import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user         = ref(null)
  const loading      = ref(false)
  const error        = ref(null)

  const isAuthenticated = computed(() => !!sessionStorage.getItem('access_token'))
  const userRole        = computed(() => user.value?.role?.name ?? user.value?.role ?? null)
  const userName        = computed(() => {
    const u = user.value
    if (!u) return ''
    if (u.first_name || u.last_name) return `${u.first_name ?? ''} ${u.last_name ?? ''}`.trim()
    return u.full_name ?? u.email ?? ''
  })

  const HIERARCHY = ['viewer', 'analyst', 'manager', 'admin', 'superadmin']
  const hasRole = (required) => {
    if (!userRole.value) return false
    return HIERARCHY.indexOf(userRole.value) >= HIERARCHY.indexOf(required)
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const data = await api.post('/auth/login/', { email, password })
      sessionStorage.setItem('access_token', data.access)
      sessionStorage.setItem('refresh_token', data.refresh)
      user.value = data.user
      return data.user
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      const refresh = sessionStorage.getItem('refresh_token')
      if (refresh) await api.post('/auth/logout/', { refresh })
    } finally {
      sessionStorage.clear()
      user.value = null
    }
  }

  async function fetchMe() {
    const data = await api.get('/users/me/')
    user.value = data
    return data
  }

  async function requestPasswordReset(email) {
    return api.post('/auth/password/reset/', { email })
  }

  async function confirmPasswordReset(token, newPassword) {
    return api.post('/auth/password/reset/confirm/', {
      token,
      new_password: newPassword,
    })
  }

  async function changePassword(oldPassword, newPassword) {
    return api.post('/auth/password/change/', {
      old_password: oldPassword,
      new_password: newPassword,
    })
  }

  async function updateProfile(data) {
    const updated = await api.patch('/users/me/', data)
    user.value = { ...user.value, ...updated }
    return updated
  }

  return {
    user, loading, error,
    isAuthenticated, userRole, userName, hasRole,
    login, logout, fetchMe,
    requestPasswordReset, confirmPasswordReset,
    changePassword, updateProfile,
  }
})