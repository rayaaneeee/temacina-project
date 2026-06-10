import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import UsersService from '@/services/user.services'

const ROLE_HIERARCHY = ['viewer', 'analyst', 'manager', 'admin', 'superadmin']

export const useUsersStore = defineStore('users', () => {

  // ── State ────────────────────────────────────────────────────────
  const users       = ref([])
  const roles       = ref([])
  const sectors     = ref([])
  const loading     = ref(false)
  const error       = ref(null)

  const pagination  = ref({ page: 1, pageSize: 15, total: 0, totalPages: 0 })
  const filters     = ref({ role: '', sector_id: '', search: '' })
  const modal       = ref({ type: null, user: null, open: false })

  // ── Getters ──────────────────────────────────────────────────────

  const activeFilters = computed(() =>
    Object.values(filters.value).filter(Boolean).length
  )

  const rankOf = (roleName) => ROLE_HIERARCHY.indexOf(roleName)

  // ── Actions ──────────────────────────────────────────────────────

  async function fetchUsers() {
    loading.value = true
    error.value   = null
    try {
      const params = {
        page:      pagination.value.page,
        page_size: pagination.value.pageSize,
        ...(filters.value.role      && { role:      filters.value.role }),
        ...(filters.value.sector_id && { sector_id: filters.value.sector_id }),
        ...(filters.value.search    && { search:    filters.value.search }),
      }
      const res = await UsersService.getAll(params)
      // Handle both standard paginated { data: [...], meta: {...} } and plain array
      const list = res?.data ?? (Array.isArray(res) ? res : [])
      const meta = res?.meta ?? {}
      users.value                 = list
      pagination.value.total      = meta.total      ?? list.length
      pagination.value.totalPages = meta.total_pages ?? Math.ceil(list.length / pagination.value.pageSize)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchReferenceData() {
    const [rolesData, sectorsData] = await Promise.all([
      UsersService.getRoles().catch(() => []),
      UsersService.getSectors().catch(() => []),
    ])
    roles.value   = Array.isArray(rolesData)   ? rolesData   : (rolesData?.data   ?? [])
    sectors.value = Array.isArray(sectorsData) ? sectorsData : (sectorsData?.data ?? [])
  }

  async function inviteUser(formData) {
    loading.value = true
    error.value   = null
    try {
      const newUser = await UsersService.inviteUser(formData)
      users.value.unshift(newUser)
      pagination.value.total += 1
      closeModal()
      return newUser
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateUser(userId, data) {
    loading.value = true
    error.value   = null
    try {
      const updated = await UsersService.updateUser(userId, data)
      _replaceInList(updated)
      closeModal()
      return updated
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function changeRole(userId, roleName) {
    loading.value = true
    error.value   = null
    try {
      const updated = await UsersService.changeRole(userId, roleName)
      _replaceInList(updated)
      closeModal()
      return updated
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function toggleStatus(user) {
    const updated = await UsersService.setStatus(user.id, !user.is_active)
    _replaceInList(updated)
    return updated
  }

  async function deactivateUser(userId) {
    loading.value = true
    error.value   = null
    try {
      await UsersService.deactivateUser(userId)
      users.value = users.value.filter(u => u.id !== userId)
      pagination.value.total -= 1
      closeModal()
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  function setFilter(key, value) {
    filters.value[key]    = value
    pagination.value.page = 1
    fetchUsers()
  }

  function resetFilters() {
    filters.value = { role: '', sector_id: '', search: '' }
    pagination.value.page = 1
    fetchUsers()
  }

  function setPage(page) {
    pagination.value.page = page
    fetchUsers()
  }

  function openModal(type, user = null) {
    modal.value = { type, user, open: true }
  }

  function closeModal() {
    modal.value = { type: null, user: null, open: false }
  }

  function _replaceInList(updated) {
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) users.value[idx] = updated
  }

  return {
    users, roles, sectors, loading, error, pagination, filters, modal,
    activeFilters, rankOf,
    fetchUsers, fetchReferenceData,
    inviteUser, updateUser, changeRole, toggleStatus, deactivateUser,
    setFilter, resetFilters, setPage,
    openModal, closeModal,
  }
})
