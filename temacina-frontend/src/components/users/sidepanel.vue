<template>
  <!-- Slide-in overlay (no backdrop — it sits beside the table) -->
  <Transition name="slide">
    <div
      v-if="user"
      class="w-80 bg-white border-l border-gray-200 flex flex-col flex-shrink-0 overflow-y-auto"
    >

      <!-- ── Header ─────────────────────────────────────────── -->
      <div class="px-5 pt-5 pb-4 border-b border-gray-100">
        <div class="flex items-start justify-between mb-4">
          <UserAvatar
            :first-name="user.first_name"
            :last-name="user.last_name"
            :role="user.role"
            size="lg"
          />
          <button
            class="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition"
            @click="$emit('close')"
          >
            <X class="w-4 h-4" />
          </button>
        </div>

        <h2 class="font-semibold text-gray-900 text-base leading-tight">
          {{ user.first_name }} {{ user.last_name }}
        </h2>
        <p class="text-xs text-gray-400 mt-0.5 mb-3">{{ user.email }}</p>

        <div class="flex flex-wrap gap-1.5">
          <UserRoleBadge :role="user.role" />
          <UserStatusBadge :active="user.is_active" />
        </div>
      </div>

      <!-- ── Details ────────────────────────────────────────── -->
      <div class="flex-1 px-5 py-4 space-y-5">

        <!-- Info rows -->
        <div class="space-y-3">
          <DetailRow icon="phone" label="Téléphone">
            {{ user.phone || '—' }}
          </DetailRow>
          <DetailRow icon="building" label="Secteur">
            {{ user.sector?.name || '—' }}
          </DetailRow>
          <DetailRow icon="user" label="Manager">
            {{ managerName }}
          </DetailRow>
          <DetailRow icon="calendar" label="Ajouté le">
            {{ formatDate(user.created_at) }}
          </DetailRow>
        </div>

        <!-- Divider -->
        <div class="border-t border-gray-100" />

        <!-- Actions -->
        <div v-if="canAct" class="space-y-2">
          <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Actions</p>

          <button
            class="action-btn text-gray-700 hover:bg-orange-50 hover:text-orange-600"
            @click="$emit('edit', user)"
          >
            <Pencil class="w-4 h-4" />
            Modifier le profil
          </button>

          <button
            class="action-btn text-gray-700 hover:bg-blue-50 hover:text-blue-600"
            @click="$emit('change-role', user)"
          >
            <ShieldCheck class="w-4 h-4" />
            Changer le rôle
          </button>

          <button
            class="action-btn hover:bg-amber-50"
            :class="user.is_active ? 'text-amber-600 hover:text-amber-700' : 'text-green-600 hover:text-green-700'"
            @click="$emit('toggle-status', user)"
          >
            <component :is="user.is_active ? UserX : UserCheck" class="w-4 h-4" />
            {{ user.is_active ? 'Désactiver le compte' : 'Réactiver le compte' }}
          </button>

          <button
            class="action-btn text-red-500 hover:bg-red-50 hover:text-red-600"
            @click="$emit('delete', user)"
          >
            <Trash2 class="w-4 h-4" />
            Supprimer l'utilisateur
          </button>
        </div>

        <!-- Read-only note for non-manageable users -->
        <p v-else class="text-xs text-gray-400 italic">
          Vous ne pouvez pas modifier cet utilisateur.
        </p>
      </div>

    </div>
  </Transition>
</template>

<script setup>
import { computed, defineComponent, h } from 'vue'
import { X, Pencil, ShieldCheck, Trash2, UserX, UserCheck, Phone, Building2, User, Calendar } from 'lucide-vue-next'
import UserAvatar from './avatar.vue'
import UserRoleBadge from './rolebadge.vue'
import UserStatusBadge from './statusbadge.vue'
import dayjs from 'dayjs'

const props = defineProps({
  user:    { type: Object, default: null },
  canAct:  { type: Boolean, default: true },
})

defineEmits(['close', 'edit', 'change-role', 'toggle-status', 'delete'])

const ICON_MAP = { phone: Phone, building: Building2, user: User, calendar: Calendar }

// Simple inline sub-component for each detail row
const DetailRow = defineComponent({
  props: { icon: String, label: String },
  setup(props, { slots }) {
    return () => h('div', { class: 'flex items-start gap-3' }, [
      h('div', { class: 'w-7 h-7 rounded-lg bg-gray-50 border border-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5' }, [
        h(ICON_MAP[props.icon] ?? User, { class: 'w-3.5 h-3.5 text-gray-400' }),
      ]),
      h('div', [
        h('p', { class: 'text-xs text-gray-400' }, props.label),
        h('p', { class: 'text-sm text-gray-700 font-medium mt-0.5' }, slots.default?.()),
      ]),
    ])
  },
})

const HIERARCHY = ['viewer', 'analyst', 'manager', 'admin', 'superadmin']

function rankOf(role) { return HIERARCHY.indexOf(role) }

const managerName = computed(() => {
  if (!props.user?.manager) return '—'
  const m = props.user.manager
  return typeof m === 'object' ? `${m.first_name} ${m.last_name}` : '—'
})

function formatDate(iso) {
  return iso ? dayjs(iso).format('DD MMMM YYYY') : '—'
}
</script>

<style scoped>
.action-btn {
  @apply w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium
         transition-colors duration-150 text-left;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 200ms ease, opacity 200ms ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(24px);
  opacity: 0;
}
</style>