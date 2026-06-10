<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="open && user" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')" />

        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
          <!-- Icon -->
          <div class="w-12 h-12 bg-red-50 border border-red-100 rounded-xl flex items-center justify-center mb-4">
            <Trash2 class="w-5 h-5 text-red-500" />
          </div>

          <h2 class="font-semibold text-gray-900 text-base mb-1">Désactiver l'utilisateur ?</h2>
          <p class="text-sm text-gray-500 mb-5 leading-relaxed">
            <span class="font-semibold text-gray-700">{{ user.first_name }} {{ user.last_name }}</span>
            ne pourra plus se connecter. Le compte reste dans la base de données.
            Cette action est réversible.
          </p>

          <div v-if="error" class="flex items-center gap-2 text-xs text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-4">
            <AlertCircle class="w-3.5 h-3.5 flex-shrink-0" />
            {{ error }}
          </div>

          <div class="flex justify-end gap-2">
            <button class="btn-ghost" @click="$emit('close')">Annuler</button>
            <button
              class="inline-flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg text-sm transition"
              :disabled="loading"
              @click="$emit('confirm', user.id)"
            >
              <span v-if="loading" class="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              <Trash2 v-else class="w-4 h-4" />
              Désactiver
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { Trash2, AlertCircle } from 'lucide-vue-next'

defineProps({
  open:    { type: Boolean, default: false },
  user:    { type: Object,  default: null },
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: '' },
})

defineEmits(['close', 'confirm'])
</script>

<style scoped>
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 150ms ease; }
.modal-fade-enter-from,  .modal-fade-leave-to      { opacity: 0; }
</style>