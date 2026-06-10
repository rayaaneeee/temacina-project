<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="open && user" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')" />

        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm overflow-hidden">

          <!-- Title bar -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                <ShieldCheck class="w-4 h-4 text-blue-500" />
              </div>
              <h2 class="font-semibold text-gray-900 text-base">Changer le rôle</h2>
            </div>
            <button class="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition" @click="$emit('close')">
              <X class="w-4 h-4" />
            </button>
          </div>

          <div class="px-6 py-5">
            <!-- Target user info -->
            <div class="flex items-center gap-3 mb-5 pb-4 border-b border-gray-100">
              <UserAvatar :first-name="user.first_name" :last-name="user.last_name" :role="user.role" size="md" />
              <div>
                <p class="text-sm font-medium text-gray-800">{{ user.first_name }} {{ user.last_name }}</p>
                <div class="flex items-center gap-1.5 mt-0.5">
                  <span class="text-xs text-gray-400">Actuellement :</span>
                  <UserRoleBadge :role="user.role" size="sm" />
                </div>
              </div>
            </div>

            <!-- Role picker -->
            <div class="space-y-2 mb-5">
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Sélectionner le nouveau rôle</p>
              <button
                v-for="r in assignableRoles"
                :key="r.id ?? r.name"
                type="button"
                :class="[
                  'w-full flex items-center justify-between px-4 py-3 rounded-xl border text-sm font-medium transition',
                  selectedRole === r.name
                    ? 'border-blue-400 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-blue-200 hover:bg-blue-50 text-gray-700',
                  r.name === user.role ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'
                ]"
                :disabled="r.name === user.role"
                @click="selectedRole = r.name"
              >
                <span>{{ ROLE_LABELS[r.name] ?? r.name }}</span>
                <span class="text-xs font-normal text-gray-400">{{ ROLE_DESC[r.name] }}</span>
              </button>
            </div>

            <!-- Error -->
            <div v-if="error" class="flex items-center gap-2 text-xs text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-4">
              <AlertCircle class="w-3.5 h-3.5 flex-shrink-0" />
              {{ error }}
            </div>

            <div class="flex justify-end gap-2">
              <button class="btn-ghost" @click="$emit('close')">Annuler</button>
              <button
                class="btn-primary bg-blue-500 hover:bg-blue-600"
                :disabled="!selectedRole || selectedRole === user.role || loading"
                @click="$emit('submit', { userId: user.id, role: selectedRole })"
              >
                <span v-if="loading" class="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                Confirmer
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ShieldCheck, X, AlertCircle } from '@lucide/vue'
import UserAvatar from './avatar.vue'
import UserRoleBadge from './rolebadge.vue'

const ROLE_LABELS = {
  viewer: 'Lecteur', analyst: 'Analyste', manager: 'Manager',
  admin: 'Admin', superadmin: 'Super Admin',
}
const ROLE_DESC = {
  viewer: 'lecture seule', analyst: 'lecture + exports',
  manager: 'gère son équipe', admin: 'gestion complète', superadmin: 'accès total',
}

const props = defineProps({
  open:            { type: Boolean, default: false },
  user:            { type: Object,  default: null },
  loading:         { type: Boolean, default: false },
  error:           { type: String,  default: '' },
  assignableRoles: { type: Array,   default: () => [] },
})

defineEmits(['close', 'submit'])

const selectedRole = ref('')

watch(() => props.open, (val) => { if (val) selectedRole.value = '' })
</script>

<style scoped>
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 150ms ease; }
.modal-fade-enter-from,  .modal-fade-leave-to      { opacity: 0; }
</style>