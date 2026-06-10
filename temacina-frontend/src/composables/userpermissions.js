/**
 * src/composables/usePermissions.js
 * Role-based access helpers.
 *
 * Usage:
 *   const { isAdmin, isAbove, canManage } = usePermissions()
 *   if (!isAdmin.value) router.replace('/app/dashboard')
 */
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ROLE_HIERARCHY } from '@/stores/users'

export function usePermissions() {
  const auth = useAuthStore()

  const myRole  = computed(() => auth.userRole ?? 'viewer')
  const myRank  = computed(() => ROLE_HIERARCHY.indexOf(myRole.value))

  const isAdmin      = computed(() => myRank.value >= ROLE_HIERARCHY.indexOf('admin'))
  const isSuperAdmin = computed(() => myRole.value === 'superadmin')
  const isManager    = computed(() => myRank.value >= ROLE_HIERARCHY.indexOf('manager'))

  /**
   * Can the current user perform actions on `targetRoleName`?
   * Actor must be strictly above the target.
   */
  function isAbove(targetRoleName) {
    return myRank.value > ROLE_HIERARCHY.indexOf(targetRoleName)
  }

  /**
   * Can the current user manage (edit/delete/change-role) a given user object?
   * - superadmin → everyone below superadmin
   * - admin      → everyone below admin
   * - manager    → only their direct reports (manager_id === me)
   */
  function canManage(targetUser) {
    if (!targetUser) return false
    if (isSuperAdmin.value) return targetUser.role !== 'superadmin'
    if (isAdmin.value)      return isAbove(targetUser.role)
    return false  // managers only see their reports — handled at route/component level
  }

  /**
   * Can the current user assign `roleName` to someone?
   * Actor must be strictly above that role.
   */
  function canAssignRole(roleName) {
    return isAbove(roleName)
  }

  /**
   * Returns the list of roles that the current user is allowed to assign.
   * Used to populate the role dropdown in InviteUserModal / ChangeRoleModal.
   */
  function assignableRoles(allRoles) {
    return allRoles.filter(r => canAssignRole(r.name))
  }

  return {
    myRole,
    isAdmin,
    isSuperAdmin,
    isManager,
    isAbove,
    canManage,
    canAssignRole,
    assignableRoles,
  }
}