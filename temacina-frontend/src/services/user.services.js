/**
 * users.service.js
 * All HTTP calls for the /api/v1/users/ namespace.
 *
 * Every method returns the unwrapped `data` field from the standard
 * envelope { success, data, errors } — the Axios interceptor in api.js
 * already strips the envelope, so you get plain objects / arrays.
 */
import api from './api'

const BASE = '/users'

const UsersService = {
  // ── List & detail ──────────────────────────────────────────────────

  /**
   * Fetch a paginated, filtered list of users.
   * @param {Object} params  – { role, sector_id, manager_id, page, page_size }
   * @returns {Promise<{ results: User[], count: number }>}
   */
  getAll(params = {}) {
    return api.get(`${BASE}/`, { params })
  },

  /**
   * Fetch a single user by id.
   * @param {number} userId
   * @returns {Promise<User>}
   */
  getById(userId) {
    return api.get(`${BASE}/${userId}/`)
  },

  /**
   * Fetch the currently authenticated user's own profile.
   * @returns {Promise<User>}
   */
  getMe() {
    return api.get(`${BASE}/me/`)
  },

  // ── Create / Invite ────────────────────────────────────────────────

  /**
   * Invite (create) a new user. Admin+ only.
   * The backend will send them an e-mail with a set-password link.
   *
   * @param {Object} data – { email, first_name, last_name, role_id,
   *                          sector_id?, manager_id?, phone? }
   * @returns {Promise<User>}
   */
  inviteUser(data) {
    return api.post(`${BASE}/invite/`, data)
  },

  // ── Update ─────────────────────────────────────────────────────────

  /**
   * Partial update (PATCH) — only the fields you pass are changed.
   * Admins can also update role_id and is_active.
   *
   * @param {number} userId
   * @param {Object} data – any subset of { first_name, last_name, phone,
   *                         sector_id, manager_id, role_id, is_active }
   * @returns {Promise<User>}
   */
  updateUser(userId, data) {
    return api.patch(`${BASE}/${userId}/`, data)
  },

  // ── Role ───────────────────────────────────────────────────────────

  /**
   * Change a user's role. Actor must be above the target role.
   * @param {number} userId
   * @param {string} roleName – one of viewer|analyst|manager|admin|superadmin
   * @returns {Promise<User>}
   */
  changeRole(userId, roleName) {
    return api.patch(`${BASE}/${userId}/role/`, { role: roleName })
  },

  // ── Status ─────────────────────────────────────────────────────────

  /**
   * Toggle a user's is_active status.
   * Convenience wrapper around updateUser.
   * @param {number} userId
   * @param {boolean} isActive
   * @returns {Promise<User>}
   */
  setStatus(userId, isActive) {
    return api.patch(`${BASE}/${userId}/`, { is_active: isActive })
  },

  // ── Deactivate / Delete ────────────────────────────────────────────

  /**
   * Soft-delete (deactivate) a user. Admin+ only.
   * Sets is_active=false; the row is kept in the DB for audit purposes.
   * @param {number} userId
   * @returns {Promise<void>}
   */
  deactivateUser(userId) {
    return api.delete(`${BASE}/${userId}/`)
  },

  // ── Reference data ─────────────────────────────────────────────────

  /**
   * Fetch all available roles (viewer, analyst, manager, admin, superadmin).
   * Used to populate the role selector in invite / edit modals.
   * @returns {Promise<Role[]>}
   */
  getRoles() {
    return api.get(`${BASE}/roles/`)
  },

  /**
   * Fetch all user sectors (for the sector dropdown).
   * @returns {Promise<UserSector[]>}
   */
  getSectors() {
    return api.get(`${BASE}/sectors/`)
  },

  /**
   * Fetch direct reports for a given manager.
   * @param {number} managerId
   * @returns {Promise<User[]>}
   */
  getDirectReports(managerId) {
    return api.get(`${BASE}/${managerId}/reports/`)
  },
}

export default UsersService