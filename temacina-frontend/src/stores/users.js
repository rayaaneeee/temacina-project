/**
 * src/stores/users.js
 * Pinia store for the User Management page.
 * Accessible only by admin / superadmin (enforced by the router guard
 * AND by every backend endpoint).
 */
import { storeToRefs } from 'pinia'

const store = useUsersStore()
const { users, roles, sectors, loading, error, pagination, filters, modal } = storeToRefs(store)
const { fetchUsers, fetchReferenceData, inviteUser, updateUser,
        changeRole, toggleStatus, deactivateUser,
        setFilter, resetFilters, setPage, openModal, closeModal } = store

export const useUsersStore = defineStore('users', () => {

  // ── State ────────────────────────────────────────────────────────
  const users       = ref([])
  const roles       = ref([])       // [{ id, name }]
  const sectors     = ref([])       // [{ id, name }]
  const loading     = ref(false)
  const error       = ref(null)

  // Pagination
  const pagination  = ref({ page: 1, pageSize: 15, total: 0, totalPages: 0 })

  // Filters
  const filters     = ref({ role: '', sector_id: '', search: '' })

  // Modal state
  const modal       = ref({
    type: null,   // 'invite' | 'edit' | 'changeRole' | 'confirm'
    user: null,   // target user object
    open: false,
  })

  // ── Getters ──────────────────────────────────────────────────────

  const activeFilters = computed(() =>
    Object.values(filters.value).filter(Boolean).length
  )

  const rankOf = (roleName) => ROLE_HIERARCHY.indexOf(roleName)

  // ── Actions ──────────────────────────────────────────────────────

  /** Load users with current filters + pagination. */
  async function fetchUsers() {
    loading.value = true
    error.value   = null
    try {
      const params = {
        page:      pagination.value.page,
        page_size: pagination.value.pageSize,
        ...(filters.value.role       && { role:      filters.value.role }),
        ...(filters.value.sector_id  && { sector_id: filters.value.sector_id }),
        ...(filters.value.search     && { search:    filters.value.search }),
      }
      const data = await UsersService.getAll(params)
      // Support both paginated { results, count } and plain array responses
      if (Array.isArray(data)) {
        users.value              = data
        pagination.value.total   = data.length
        pagination.value.totalPages = 1
      } else {
        users.value              = data.results ?? data.data ?? []
        pagination.value.total   = data.count   ?? data.meta?.total ?? 0
        pagination.value.totalPages =
          Math.ceil(pagination.value.total / pagination.value.pageSize)
      }
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  /** Load reference data (roles + sectors) once at mount. */
  async function fetchReferenceData() {
    const [rolesData, sectorsData] = await Promise.all([
      UsersService.getRoles().catch(() => []),
      UsersService.getSectors().catch(() => []),
    ])
    roles.value   = rolesData
    sectors.value = sectorsData
  }

  /** Invite (create) a new user. */
  async function inviteUser(formData) {
    loading.value = true
    error.value   = null
    try {
      const newUser = await UsersService.inviteUser(formData)
      // Prepend to list so it's visible immediately
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

  /** Patch arbitrary fields on a user (name, phone, sector, manager…). */
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

  /** Change a user's role. */
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

  /** Toggle active / inactive. */
  async function toggleStatus(user) {
    const updated = await UsersService.setStatus(user.id, !user.is_active)
    _replaceInList(updated)
    return updated
  }

  /** Soft-delete (deactivate) a user. */
  async function deactivateUser(userId) {
    loading.value = true
    error.value   = null
    try {
      await UsersService.deactivateUser(userId)
      // Remove from visible list (or re-fetch to reflect server state)
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

  // ── Filter & pagination helpers ──────────────────────────────────

  function setFilter(key, value) {
    filters.value[key] = value
    pagination.value.page = 1   // reset to page 1 on filter change
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

  // ── Modal helpers ────────────────────────────────────────────────

  function openModal(type, user = null) {
    modal.value = { type, user, open: true }
  }

  function closeModal() {
    modal.value = { type: null, user: null, open: false }
  }

  // ── Private ──────────────────────────────────────────────────────

  function _replaceInList(updated) {
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) users.value[idx] = updated
  }

  return {
    // state
    users, roles, sectors, loading, error, pagination, filters, modal,
    // getters
    activeFilters, rankOf,
    // actions
    fetchUsers, fetchReferenceData,
    inviteUser, updateUser, changeRole, toggleStatus, deactivateUser,
    setFilter, resetFilters, setPage,
    openModal, closeModal,
  }
})