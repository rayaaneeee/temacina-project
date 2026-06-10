<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')" />

        <!-- Dialog -->
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">

          <!-- Title bar -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center">
                <UserPlus class="w-4 h-4 text-orange-500" />
              </div>
              <h2 class="font-semibold text-gray-900 text-base">Inviter un utilisateur</h2>
            </div>
            <button class="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition" @click="$emit('close')">
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Form -->
          <form class="px-6 py-5 space-y-4" @submit.prevent="handleSubmit">

            <!-- Name row -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="form-label">Prénom <span class="text-red-400">*</span></label>
                <input v-model="form.first_name" type="text" class="form-input" placeholder="Yasmine" required />
              </div>
              <div>
                <label class="form-label">Nom <span class="text-red-400">*</span></label>
                <input v-model="form.last_name" type="text" class="form-input" placeholder="Benali" required />
              </div>
            </div>

            <!-- Email -->
            <div>
              <label class="form-label">Adresse e-mail <span class="text-red-400">*</span></label>
              <input v-model="form.email" type="email" class="form-input" placeholder="yasmine@temacina.com" required />
            </div>

            <!-- Role -->
            <div>
              <label class="form-label">Rôle <span class="text-red-400">*</span></label>
              <select v-model="form.role_id" class="form-input" required>
                <option value="" disabled>Sélectionner un rôle</option>
                <option
                  v-for="r in assignableRoles"
                  :key="r.id ?? r.name"
                  :value="r.id ?? r.name"
                >
                  {{ ROLE_LABELS[r.name] ?? r.name }}
                </option>
              </select>
            </div>

            <!-- Sector -->
            <div>
              <label class="form-label">Secteur</label>
              <select v-model="form.sector_id" class="form-input">
                <option value="">Aucun</option>
                <option v-for="s in sectors" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>

            <!-- Phone -->
            <div>
              <label class="form-label">Téléphone</label>
              <input v-model="form.phone" type="tel" class="form-input" placeholder="+213 xx xx xx xx" />
            </div>

            <!-- Error -->
            <div v-if="error" class="flex items-center gap-2 text-xs text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
              <AlertCircle class="w-3.5 h-3.5 flex-shrink-0" />
              {{ error }}
            </div>

            <!-- Footer -->
            <div class="flex justify-end gap-2 pt-1">
              <button type="button" class="btn-ghost" :disabled="loading" @click="$emit('close')">
                Annuler
              </button>
              <button type="submit" class="btn-primary" :disabled="loading">
                <span v-if="loading" class="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                <UserPlus v-else class="w-4 h-4" />
                Envoyer l'invitation
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { UserPlus, X, AlertCircle } from '@lucide/vue'

const ROLE_LABELS = {
  viewer:     'Lecteur',
  analyst:    'Analyste',
  manager:    'Manager',
  admin:      'Admin',
  superadmin: 'Super Admin',
}

const props = defineProps({
  open:            { type: Boolean, default: false },
  loading:         { type: Boolean, default: false },
  error:           { type: String,  default: '' },
  sectors:         { type: Array,   default: () => [] },
  assignableRoles: { type: Array,   default: () => [] }, // roles the actor is allowed to assign
})

const emit = defineEmits(['close', 'submit'])

const EMPTY_FORM = () => ({
  first_name: '', last_name: '', email: '',
  role_id: '', sector_id: '', phone: '',
})

const form = ref(EMPTY_FORM())

// Reset on open
watch(() => props.open, (val) => {
  if (val) form.value = EMPTY_FORM()
})

function handleSubmit() {
  emit('submit', { ...form.value })
}
</script>

<style scoped>
.form-label { @apply block text-xs font-semibold text-gray-500 mb-1; }

.modal-fade-enter-active,
.modal-fade-leave-active { transition: opacity 150ms ease; }
.modal-fade-enter-from,
.modal-fade-leave-to   { opacity: 0; }
</style>