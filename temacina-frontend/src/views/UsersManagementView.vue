<template>
  <div class="min-h-screen bg-gray-50 p-6">

    <!-- ── Page header ───────────────────────────────────────────── -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestion des utilisateurs</h1>
        <p class="text-sm text-gray-500 mt-0.5">
          {{ pagination.total }} utilisateur{{ pagination.total !== 1 ? 's' : '' }} au total
        </p>
      </div>
      <button class="btn-primary" @click="openModal('invite')">
        <UserPlus class="w-4 h-4" />
        Inviter un utilisateur
      </button>
    </div>

    <!-- ── Filter / search bar ───────────────────────────────────── -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-5 flex flex-wrap gap-3 items-center shadow-card">
      <!-- Search -->
      <div class="relative flex-1 min-w-48">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Nom, e-mail…"
          class="form-input pl-9"
          @input="debouncedSearch"
        />
      </div>

      <!-- Role filter -->
      <select
        v-model="filters.role"
        class="form-input w-44"
        @change="store.setFilter('role', filters.role)"
      >
        <option value="">Tous les rôles</option>
        <option v-for="r in roles" :key="r.name" :value="r.name">
          {{ roleLabel(r.name) }}
        </option>
      </select>

      <!-- Sector filter -->
      <select
        v-model="filters.sector_id"
        class="form-input w-44"
        @change="store.setFilter('sector_id', filters.sector_id)"
      >
        <option value="">Tous les secteurs</option>
        <option v-for="s in sectors" :key="s.id" :value="s.id">
          {{ s.name }}
        </option>
      </select>

      <!-- Reset -->
      <button
        v-if="activeFilters > 0"
        class="btn-ghost text-orange-500 border-orange-200"
        @click="store.resetFilters(); searchQuery = ''"
      >
        <X class="w-4 h-4" />
        Réinitialiser
      </button>
    </div>

    <!-- ── Table ─────────────────────────────────────────────────── -->
    <div class="bg-white border border-gray-200 rounded-xl shadow-card overflow-hidden">

      <!-- Loading overlay -->
      <div v-if="loading" class="flex items-center justify-center h-64">
        <div class="w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin" />
      </div>

      <!-- Empty state -->
      <div v-else-if="users.length === 0" class="flex flex-col items-center justify-center h-64 text-gray-400">
        <Users class="w-12 h-12 mb-3 opacity-40" />
        <p class="text-sm font-medium">Aucun utilisateur trouvé</p>
        <p class="text-xs mt-1">Ajustez les filtres ou invitez un nouvel utilisateur.</p>
      </div>

      <!-- Data table -->
      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-5 py-3 font-semibold text-gray-500 uppercase tracking-wide text-xs">Utilisateur</th>
            <th class="text-left px-5 py-3 font-semibold text-gray-500 uppercase tracking-wide text-xs">Rôle</th>
            <th class="text-left px-5 py-3 font-semibold text-gray-500 uppercase tracking-wide text-xs">Secteur</th>
            <th class="text-left px-5 py-3 font-semibold text-gray-500 uppercase tracking-wide text-xs">Statut</th>
            <th class="text-left px-5 py-3 font-semibold text-gray-500 uppercase tracking-wide text-xs">Ajouté le</th>
            <th class="px-5 py-3" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in users"
            :key="user.id"
            class="table-row-base"
          >
            <!-- Avatar + name + email -->
            <td class="px-5 py-3.5">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center font-semibold text-sm flex-shrink-0">
                  {{ initials(user) }}
                </div>
                <div>
                  <p class="font-medium text-gray-800">{{ user.first_name }} {{ user.last_name }}</p>
                  <p class="text-xs text-gray-400">{{ user.email }}</p>
                </div>
              </div>
            </td>

            <!-- Role badge -->
            <td class="px-5 py-3.5">
              <span :class="roleBadgeClass(user.role)">
                {{ roleLabel(user.role) }}
              </span>
            </td>

            <!-- Sector -->
            <td class="px-5 py-3.5 text-gray-600">
              {{ user.sector?.name ?? '—' }}
            </td>

            <!-- Status toggle -->
            <td class="px-5 py-3.5">
              <button
                v-if="canManage(user)"
                :class="user.is_active
                  ? 'bg-green-100 text-green-700 hover:bg-green-200'
                  : 'bg-gray-100 text-gray-500 hover:bg-gray-200'"
                class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition"
                @click="store.toggleStatus(user)"
              >
                <span :class="user.is_active ? 'bg-green-500' : 'bg-gray-400'" class="w-1.5 h-1.5 rounded-full" />
                {{ user.is_active ? 'Actif' : 'Inactif' }}
              </button>
              <span v-else :class="user.is_active ? 'text-green-600' : 'text-gray-400'" class="text-xs font-semibold">
                {{ user.is_active ? 'Actif' : 'Inactif' }}
              </span>
            </td>

            <!-- Created at -->
            <td class="px-5 py-3.5 text-gray-400 text-xs">
              {{ formatDate(user.created_at) }}
            </td>

            <!-- Actions menu -->
            <td class="px-5 py-3.5 text-right">
              <div v-if="canManage(user)" class="flex items-center justify-end gap-1">
                <!-- Edit -->
                <button
                  class="p-1.5 rounded-lg text-gray-400 hover:text-orange-500 hover:bg-orange-50 transition"
                  title="Modifier"
                  @click="openModal('edit', user)"
                >
                  <Pencil class="w-4 h-4" />
                </button>
                <!-- Change role -->
                <button
                  class="p-1.5 rounded-lg text-gray-400 hover:text-orange-500 hover:bg-orange-50 transition"
                  title="Changer le rôle"
                  @click="openModal('changeRole', user)"
                >
                  <ShieldCheck class="w-4 h-4" />
                </button>
                <!-- Deactivate -->
                <button
                  class="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition"
                  title="Désactiver"
                  @click="openModal('confirm', user)"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div
        v-if="pagination.totalPages > 1"
        class="flex items-center justify-between px-5 py-3 border-t border-gray-100 text-sm text-gray-500"
      >
        <span>Page {{ pagination.page }} sur {{ pagination.totalPages }}</span>
        <div class="flex gap-1">
          <button
            :disabled="pagination.page === 1"
            class="px-3 py-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-orange-50 hover:text-orange-500 hover:border-orange-200 transition"
            @click="store.setPage(pagination.page - 1)"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          <button
            :disabled="pagination.page === pagination.totalPages"
            class="px-3 py-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-orange-50 hover:text-orange-500 hover:border-orange-200 transition"
            @click="store.setPage(pagination.page + 1)"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════════════════
         MODALS
    ═════════════════════════════════════════════════════════════ -->

    <!-- Invite user modal -->
    <Teleport to="body">
      <div v-if="modal.open" class="fixed inset-0 z-50 flex items-center justify-center">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="store.closeModal()" />

        <!-- Invite -->
        <div v-if="modal.type === 'invite'" class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-4">Inviter un utilisateur</h2>
          <form class="space-y-4" @submit.prevent="submitInvite">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1">Prénom *</label>
                <input v-model="inviteForm.first_name" type="text" class="form-input" required />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1">Nom *</label>
                <input v-model="inviteForm.last_name" type="text" class="form-input" required />
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Adresse e-mail *</label>
              <input v-model="inviteForm.email" type="email" class="form-input" required />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Rôle *</label>
              <select v-model="inviteForm.role_id" class="form-input" required>
                <option value="" disabled>Sélectionner un rôle</option>
                <option
                  v-for="r in assignableRoles(roles)"
                  :key="r.id"
                  :value="r.id"
                >
                  {{ roleLabel(r.name) }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Secteur</label>
              <select v-model="inviteForm.sector_id" class="form-input">
                <option value="">Aucun</option>
                <option v-for="s in sectors" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
            <div v-if="error" class="text-red-500 text-xs bg-red-50 rounded-lg px-3 py-2">{{ error }}</div>
            <div class="flex justify-end gap-2 pt-2">
              <button type="button" class="btn-ghost" @click="store.closeModal()">Annuler</button>
              <button type="submit" class="btn-primary" :disabled="loading">
                <span v-if="loading" class="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                Envoyer l'invitation
              </button>
            </div>
          </form>
        </div>

        <!-- Edit user modal -->
        <div v-if="modal.type === 'edit' && modal.user" class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-1">Modifier l'utilisateur</h2>
          <p class="text-sm text-gray-400 mb-4">{{ modal.user.email }}</p>
          <form class="space-y-4" @submit.prevent="submitEdit">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1">Prénom</label>
                <input v-model="editForm.first_name" type="text" class="form-input" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1">Nom</label>
                <input v-model="editForm.last_name" type="text" class="form-input" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Téléphone</label>
              <input v-model="editForm.phone" type="tel" class="form-input" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Secteur</label>
              <select v-model="editForm.sector_id" class="form-input">
                <option value="">Aucun</option>
                <option v-for="s in sectors" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
            <div v-if="error" class="text-red-500 text-xs bg-red-50 rounded-lg px-3 py-2">{{ error }}</div>
            <div class="flex justify-end gap-2 pt-2">
              <button type="button" class="btn-ghost" @click="store.closeModal()">Annuler</button>
              <button type="submit" class="btn-primary" :disabled="loading">
                <span v-if="loading" class="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                Enregistrer
              </button>
            </div>
          </form>
        </div>

        <!-- Change role modal -->
        <div v-if="modal.type === 'changeRole' && modal.user" class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-1">Changer le rôle</h2>
          <p class="text-sm text-gray-400 mb-4">
            {{ modal.user.first_name }} {{ modal.user.last_name }} — actuellement
            <span class="font-semibold text-orange-500">{{ roleLabel(modal.user.role) }}</span>
          </p>
          <div class="space-y-2 mb-5">
            <button
              v-for="r in assignableRoles(roles)"
              :key="r.id"
              :class="[
                'w-full text-left px-4 py-3 rounded-xl border transition text-sm font-medium',
                selectedRole === r.name
                  ? 'border-orange-400 bg-orange-50 text-orange-600'
                  : 'border-gray-200 hover:border-orange-200 hover:bg-orange-50 text-gray-700'
              ]"
              @click="selectedRole = r.name"
            >
              {{ roleLabel(r.name) }}
              <span class="text-xs font-normal text-gray-400 ml-1">{{ roleDescription(r.name) }}</span>
            </button>
          </div>
          <div v-if="error" class="text-red-500 text-xs bg-red-50 rounded-lg px-3 py-2 mb-3">{{ error }}</div>
          <div class="flex justify-end gap-2">
            <button class="btn-ghost" @click="store.closeModal()">Annuler</button>
            <button
              class="btn-primary"
              :disabled="!selectedRole || loading"
              @click="submitChangeRole"
            >
              <span v-if="loading" class="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              Confirmer
            </button>
          </div>
        </div>

        <!-- Confirm deactivate modal -->
        <div v-if="modal.type === 'confirm' && modal.user" class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 p-6">
          <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <AlertTriangle class="w-6 h-6 text-red-500" />
          </div>
          <h2 class="text-lg font-bold text-gray-900 mb-2">Désactiver l'utilisateur ?</h2>
          <p class="text-sm text-gray-500 mb-5">
            <span class="font-semibold text-gray-700">{{ modal.user.first_name }} {{ modal.user.last_name }}</span>
            ne pourra plus se connecter. Cette action est réversible.
          </p>
          <div class="flex justify-end gap-2">
            <button class="btn-ghost" @click="store.closeModal()">Annuler</button>
            <button
              class="inline-flex items-center gap-2 px-4 py-2 bg-red-500 text-white font-semibold rounded-lg text-sm hover:bg-red-600 transition"
              :disabled="loading"
              @click="store.deactivateUser(modal.user.id)"
            >
              <span v-if="loading" class="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              Désactiver
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import {
  UserPlus, Search, X, Users, Pencil, ShieldCheck, Trash2,
  ChevronLeft, ChevronRight, AlertTriangle,
} from '@lucide/vue'
import { useUsersStore } from '@/stores/users'
import { usePermissions } from '@/composables/userpermissions'
import dayjs from 'dayjs'

const store = useUsersStore()
const { canManage, assignableRoles } = usePermissions()

// ── Store refs ──────────────────────────────────────────────────────
const { users, roles, sectors, loading, error, pagination, filters, modal } = store

// ── Local state ─────────────────────────────────────────────────────
const searchQuery  = ref('')
const selectedRole = ref('')

const inviteForm = ref({ first_name: '', last_name: '', email: '', role_id: '', sector_id: '' })
const editForm   = ref({ first_name: '', last_name: '', phone: '', sector_id: '' })

const activeFilters = computed(() => store.activeFilters)

// ── Lifecycle ───────────────────────────────────────────────────────
onMounted(async () => {
  await store.fetchReferenceData()
  await store.fetchUsers()
})

// Pre-fill edit form when modal opens
watch(() => modal.user, (user) => {
  if (modal.type === 'edit' && user) {
    editForm.value = {
      first_name: user.first_name,
      last_name:  user.last_name,
      phone:      user.phone ?? '',
      sector_id:  user.sector?.id ?? '',
    }
  }
  if (modal.type === 'changeRole' && user) {
    selectedRole.value = ''
  }
})

// ── Debounced search ─────────────────────────────────────────────────
const debouncedSearch = useDebounceFn(() => {
  store.setFilter('search', searchQuery.value)
}, 350)

// ── Modal helpers ────────────────────────────────────────────────────
function openModal(type, user = null) {
  store.openModal(type, user)
}

// ── Form submit handlers ─────────────────────────────────────────────
async function submitInvite() {
  await store.inviteUser({ ...inviteForm.value })
  inviteForm.value = { first_name: '', last_name: '', email: '', role_id: '', sector_id: '' }
}

async function submitEdit() {
  await store.updateUser(modal.user.id, { ...editForm.value })
}

async function submitChangeRole() {
  if (!selectedRole.value) return
  await store.changeRole(modal.user.id, selectedRole.value)
}

// ── Display helpers ──────────────────────────────────────────────────
function initials(user) {
  return `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}`.toUpperCase()
}

function formatDate(iso) {
  return iso ? dayjs(iso).format('DD/MM/YYYY') : '—'
}

const ROLE_LABELS = {
  viewer:     'Lecteur',
  analyst:    'Analyste',
  manager:    'Manager',
  admin:      'Admin',
  superadmin: 'Super Admin',
}

const ROLE_DESCRIPTIONS = {
  viewer:     'lecture seule',
  analyst:    'lecture + exports',
  manager:    'gère son équipe',
  admin:      'gestion complète',
  superadmin: 'accès total',
}

function roleLabel(roleName) {
  return ROLE_LABELS[roleName] ?? roleName
}

function roleDescription(roleName) {
  return ROLE_DESCRIPTIONS[roleName] ?? ''
}

const ROLE_BADGE = {
  superadmin: 'bg-purple-100 text-purple-700',
  admin:      'bg-orange-100 text-orange-600',
  manager:    'bg-blue-100 text-blue-700',
  analyst:    'bg-teal-100 text-teal-700',
  viewer:     'bg-gray-100 text-gray-600',
}

function roleBadgeClass(roleName) {
  return [
    'inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold',
    ROLE_BADGE[roleName] ?? 'bg-gray-100 text-gray-600',
  ]
}
</script>