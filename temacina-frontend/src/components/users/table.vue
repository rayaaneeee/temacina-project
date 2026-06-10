<template>
  <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">

    <!-- Loading skeleton -->
    <div v-if="loading">
      <div v-for="i in 6" :key="i" class="flex items-center gap-4 px-5 py-3.5 border-b border-gray-100 last:border-0 animate-pulse">
        <div class="w-9 h-9 rounded-full bg-gray-100 flex-shrink-0" />
        <div class="flex-1 space-y-1.5">
          <div class="h-3 bg-gray-100 rounded w-40" />
          <div class="h-2.5 bg-gray-100 rounded w-56" />
        </div>
        <div class="h-5 bg-gray-100 rounded-full w-16" />
        <div class="h-5 bg-gray-100 rounded-full w-20 hidden md:block" />
        <div class="h-5 bg-gray-100 rounded-full w-12" />
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="users.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400">
      <Users class="w-12 h-12 mb-3 opacity-30" />
      <p class="text-sm font-medium text-gray-500">Aucun utilisateur trouvé</p>
      <p class="text-xs mt-1">Ajustez les filtres ou invitez un nouvel utilisateur.</p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="th">Utilisateur</th>
            <th class="th">Rôle</th>
            <th class="th">Secteur</th>
            <th class="th">Manager</th>
            <th class="th">Statut</th>
            <th class="th">Ajouté le</th>
            <th class="th text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="group">
          <UserTableRow
            v-for="user in users"
            :key="user.id"
            :user="user"
            :selected="selectedId === user.id"
            :can-act="canActOn(user)"
            @select="$emit('select', $event)"
            @edit="$emit('edit', $event)"
            @change-role="$emit('change-role', $event)"
            @toggle-status="$emit('toggle-status', $event)"
            @delete="$emit('delete', $event)"
          />
        </tbody>
      </table>
    </div>

    <!-- Footer: count + pagination -->
    <div
      v-if="!loading && users.length > 0"
      class="flex items-center justify-between px-5 py-3 border-t border-gray-100 text-xs text-gray-400"
    >
      <span>
        Affichage
        <span class="font-medium text-gray-600">{{ rangeStart }}–{{ rangeEnd }}</span>
        sur
        <span class="font-medium text-gray-600">{{ total }}</span>
      </span>

      <div class="flex items-center gap-1">
        <button
          :disabled="page <= 1"
          class="pagination-btn"
          @click="$emit('page', page - 1)"
        >
          <ChevronLeft class="w-3.5 h-3.5" />
        </button>

        <template v-for="p in visiblePages" :key="p">
          <span v-if="p === '…'" class="px-1 text-gray-300">…</span>
          <button
            v-else
            :class="[
              'pagination-btn font-medium',
              p === page ? 'bg-orange-500 text-white border-orange-500' : ''
            ]"
            @click="$emit('page', p)"
          >
            {{ p }}
          </button>
        </template>

        <button
          :disabled="page >= totalPages"
          class="pagination-btn"
          @click="$emit('page', page + 1)"
        >
          <ChevronRight class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Users, ChevronLeft, ChevronRight } from '@lucide/vue'
import UserTableRow from './tablerow.vue'

const props = defineProps({
  users:      { type: Array,  default: () => [] },
  loading:    { type: Boolean, default: false },
  selectedId: { type: Number,  default: null },
  page:       { type: Number,  default: 1 },
  pageSize:   { type: Number,  default: 15 },
  total:      { type: Number,  default: 0 },
  totalPages: { type: Number,  default: 1 },
  myRank:     { type: Number,  default: 0 },   // rank of the logged-in actor
  myRole:     { type: String,  default: '' },
})

defineEmits(['select', 'edit', 'change-role', 'toggle-status', 'delete', 'page'])

const HIERARCHY = ['viewer', 'analyst', 'manager', 'admin', 'superadmin']

function rankOf(role) { return HIERARCHY.indexOf(role) }

/** Actor can manage a row only if their rank > the target's rank. */
function canActOn(user) {
  return props.myRank > rankOf(user.role)
}

const rangeStart = computed(() => (props.page - 1) * props.pageSize + 1)
const rangeEnd   = computed(() => Math.min(props.page * props.pageSize, props.total))

/** Build a compact page list: 1 … 4 [5] 6 … 20 */
const visiblePages = computed(() => {
  const { page, totalPages } = props
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
  const pages = new Set([1, totalPages, page, page - 1, page + 1].filter(p => p >= 1 && p <= totalPages))
  const sorted = [...pages].sort((a, b) => a - b)
  const result = []
  sorted.forEach((p, i) => {
    if (i > 0 && p - sorted[i - 1] > 1) result.push('…')
    result.push(p)
  })
  return result
})
</script>

<style scoped>
.th {
  @apply px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap;
}
.pagination-btn {
  @apply w-7 h-7 flex items-center justify-center rounded-lg border border-gray-200
         text-gray-500 hover:border-orange-300 hover:text-orange-500 hover:bg-orange-50
         disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent
         disabled:hover:text-gray-500 disabled:hover:border-gray-200 transition text-xs;
}
</style>