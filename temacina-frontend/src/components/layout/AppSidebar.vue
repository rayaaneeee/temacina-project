<template>
  <aside class="w-52 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col h-full">

    <!-- Logo -->
    <div class="flex items-center gap-2 px-4 py-4 border-b border-gray-100">
      <div class="w-full shrink-0 flex items-center justify-center">
         <img src="@/assets/temacina.png" />
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 py-4 px-3 overflow-y-auto">
      <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-widest px-2 mb-2">
        Main Menu
      </p>
      <div class="space-y-0.5">
        <RouterLink
          v-for="item in navItems"
          :key="item.label"
          :to="item.to"
          custom
          v-slot="{ isActive, navigate }"
        >
          <button
            @click="navigate"
            :class="[
              'flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm transition-colors',
              isActive
                ? 'bg-orange-500 text-white font-semibold'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            ]"
          >
            <component :is="item.icon" class="w-4 h-4 flex-shrink-0" />
            <span class="truncate">{{ item.label }}</span>
          </button>
        </RouterLink>
      </div>
    </nav>

    <!-- Bottom: Profile + Logout -->
    <div class="border-t border-gray-100 p-3 space-y-0.5">
      <RouterLink to="/app/profile"
        class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm
               text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors">
        <User class="w-4 h-4 flex-shrink-0" />
        <span>Profile</span>
      </RouterLink>
      <button
        @click="handleLogout"
        class="flex items-center gap-3 px-3 py-2 rounded-lg w-full text-sm
               text-gray-500 hover:bg-red-50 hover:text-red-500 transition-colors">
        <LogOut class="w-4 h-4" />
        <span>Logout</span>
      </button>
    </div>

  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard, Building2, Users, CalendarDays,
  FileText, Globe, BarChart3, Download, Settings, LogOut, User,
  Users2,
  HelpCircle,
} from '@lucide/vue'

const authStore = useAuthStore()
const router    = useRouter()

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}

const navItems = [
  { label: 'Dashboard',   to: '/app/dashboard',   icon: LayoutDashboard },
  { label: 'Companies',   to: '/app/companies',   icon: Building2 },
  { label: 'Contacts',    to: '/app/contacts',    icon: Users },
  { label: 'Trade Shows', to: '/app/trade-shows', icon: CalendarDays },
  { label: 'Documents',   to: '/app/supports',    icon: FileText },
  { label: 'Countries',   to: '/app/countries',   icon: Globe },
  { label: 'Analytics',   to: '/app/analytics',   icon: BarChart3 },
  { label: 'Exports',     to: '/app/exports',     icon: Download },
  { label: 'Settings',    to: '/app/settings',    icon: Settings },
]

const navItems = computed(() =>
  ALL_ITEMS.filter(item => authStore.hasRole(item.minRole))
)
</script>