<template>
  <tr
    :class="[
      'border-b border-gray-100 transition-colors duration-100 cursor-pointer',
      selected ? 'bg-orange-50' : 'hover:bg-gray-50'
    ]"
    @click="$emit('select', user)"
  >
    <!-- User name + email -->
    <td class="px-5 py-3.5">
      <div class="flex items-center gap-3">
        <UserAvatar
          :first-name="user.first_name"
          :last-name="user.last_name"
          :role="user.role"
          size="md"
        />
        <div>
          <p class="font-medium text-gray-800 text-sm leading-tight">
            {{ user.first_name }} {{ user.last_name }}
          </p>
          <p class="text-xs text-gray-400 mt-0.5">{{ user.email }}</p>
        </div>
      </div>
    </td>

    <!-- Role -->
    <td class="px-5 py-3.5">
      <UserRoleBadge :role="user.role" />
    </td>

    <!-- Sector -->
    <td class="px-5 py-3.5 text-sm text-gray-600">
      {{ user.sector?.name ?? '—' }}
    </td>

    <!-- Manager -->
    <td class="px-5 py-3.5 text-sm text-gray-600">
      {{ managerName }}
    </td>

    <!-- Status -->
    <td class="px-5 py-3.5">
      <UserStatusBadge :active="user.is_active" />
    </td>

    <!-- Added date -->
    <td class="px-5 py-3.5 text-xs text-gray-400 whitespace-nowrap">
      {{ formatDate(user.created_at) }}
    </td>

    <!-- Actions -->
    <td class="px-5 py-3.5" @click.stop>
      <div v-if="canAct" class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <!-- Edit -->
        <button
          class="p-1.5 rounded-lg text-gray-400 hover:text-orange-500 hover:bg-orange-50 transition"
          title="Modifier"
          @click="$emit('edit', user)"
        >
          <Pencil class="w-3.5 h-3.5" />
        </button>
        <!-- Change role -->
        <button
          class="p-1.5 rounded-lg text-gray-400 hover:text-blue-500 hover:bg-blue-50 transition"
          title="Changer le rôle"
          @click="$emit('change-role', user)"
        >
          <ShieldCheck class="w-3.5 h-3.5" />
        </button>
        <!-- Toggle status -->
        <button
          class="p-1.5 rounded-lg text-gray-400 hover:text-amber-500 hover:bg-amber-50 transition"
          :title="user.is_active ? 'Désactiver' : 'Réactiver'"
          @click="$emit('toggle-status', user)"
        >
          <component :is="user.is_active ? UserX : UserCheck" class="w-3.5 h-3.5" />
        </button>
        <!-- Delete -->
        <button
          class="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition"
          title="Supprimer"
          @click="$emit('delete', user)"
        >
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>
    </td>
  </tr>
</template>
<script setup>

import { computed } from 'vue'
import { Pencil, ShieldCheck, Trash2, UserX, UserCheck } from '@lucide/vue'
import UserAvatar from './avatar.vue'
import UserRoleBadge from './rolebadge.vue'
import UserStatusBadge from './statusbadge.vue'
import dayjs from 'dayjs'

const props = defineProps({
  user:     { type: Object, required: true },
  selected: { type: Boolean, default: false },
  canAct:   { type: Boolean, default: true },   // false for rows the actor can't manage
})

defineEmits(['select', 'edit', 'change-role', 'toggle-status', 'delete'])

const managerName = computed(() => {
  if (!props.user.manager) return '—'
  const m = props.user.manager
  return typeof m === 'object'
    ? `${m.first_name} ${m.last_name}`
    : '—'
})

function formatDate(iso) {
  return iso ? dayjs(iso).format('DD/MM/YYYY') : '—'
}

</script>