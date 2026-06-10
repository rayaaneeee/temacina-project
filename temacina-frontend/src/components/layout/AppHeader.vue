<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center
                 justify-between px-6 flex-shrink-0">
    <h1 class="text-base font-semibold text-gray-800">{{ pageTitle }}</h1>

    <!-- User — clicks to profile page -->
    <RouterLink to="/app/profile"
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50
             hover:bg-gray-100 transition cursor-pointer">
      <div class="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center">
        <span class="text-white font-bold text-sm">{{ initial }}</span>
      </div>
      <div class="hidden sm:block text-left">
        <div class="text-sm font-semibold text-gray-800 leading-none">{{ authStore.userName }}</div>
        <div class="text-xs text-gray-400 capitalize leading-tight">{{ authStore.userRole }}</div>
      </div>
    </RouterLink>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route     = useRoute()

const initial = computed(() =>
  authStore.userName ? authStore.userName.charAt(0).toUpperCase() : 'U'
)

const pageTitle = computed(() => {
  const titles = {
    dashboard:    'Dashboard',
    companies:    'Companies',
    contacts:     'Contacts',
    'trade-shows':'Trade Shows',
    supports:     'Documents',
    countries:    'Countries',
    analytics:    'Analytics',
    exports:      'Exports',
    settings:     'Settings',
    profile:      'My Profile',
  }
  return titles[route.name] ?? 'Temacina'
})
</script>