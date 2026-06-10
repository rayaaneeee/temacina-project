<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center
                 justify-between px-6 flex-shrink-0">
    <h1 class="text-base font-semibold text-gray-800">{{ pageTitle }}</h1>

    <div class="flex items-center gap-3">
      <!-- Bell -->
      <button class="relative p-2 rounded-lg hover:bg-gray-100 transition">
        <Bell class="w-5 h-5 text-gray-500" />
        <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-orange-500 rounded-full"></span>
      </button>

      <!-- User -->
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50">
        <div class="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center">
          <span class="text-white font-bold text-sm">{{ initial }}</span>
        </div>
        <div class="hidden sm:block text-left">
          <div class="text-sm font-semibold text-gray-800 leading-none">{{ authStore.userName }}</div>
          <div class="text-xs text-gray-400 capitalize leading-tight">{{ authStore.userRole }}</div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Bell } from '@lucide/vue'

const authStore = useAuthStore()
const route     = useRoute()

const initial   = computed(() =>
  authStore.userName ? authStore.userName.charAt(0).toUpperCase() : 'U'
)
const pageTitle = computed(() => {
  const titles = {
    dashboard:    'Tableau de bord',
    companies:    'Entreprises',
    contacts:     'Contacts',
    'trade-shows':'Salons d\'exposition',
    supports:     'Supports',
    countries:    'Pays',
    analytics:    'Analyses',
    exports:      'Exports',
    settings:     'Paramètres',
    profile:      'Mon Profil',
  }
  return titles[route.name] ?? 'Temacina'
})
</script>