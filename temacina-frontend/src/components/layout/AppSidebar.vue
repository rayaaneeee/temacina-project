<template>
  <aside class="w-48 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col h-full">

    <!-- Logo -->
    <div class="flex items-center gap-2 px-4 py-4 border-b border-gray-100">
      <div class="w-full shrink-0 flex items-center justify-center">
         <img src="@/assets/temacina.png" />
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
      <RouterLink
        v-for="item in navItems"
        :key="item.name"
        :to="item.to"
        custom
        v-slot="{ isActive, navigate }"
      >
        <button
          @click="navigate"
          :class="['nav-item w-full', isActive ? 'active' : '']"
        >
          <component :is="item.icon" class="w-4 h-4 flex-shrink-0" />
          <span class="truncate text-xs">{{ item.label }}</span>
        </button>
      </RouterLink>
    </nav>

    <!-- Bottom: user + logout -->
    <div class="border-t border-gray-100 p-3 space-y-1">
      <button
        @click="handleLogout"
        class="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-red-50
               text-gray-500 hover:text-red-500 w-full transition-colors">
        <LogOut class="w-4 h-4" />
        <span class="text-xs font-medium">Déconnexion</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
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

const initial = computed(() =>
  authStore.userName ? authStore.userName.charAt(0).toUpperCase() : 'U'
)

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}

const navItems = [
  { label: 'Tableau de bord',     to: '/app/dashboard',   icon: LayoutDashboard },
  { label: 'Entreprises',         to: '/app/companies',   icon: Building2 },
  { label: "Salons d'exposition", to: '/app/trade-shows', icon: CalendarDays },
  { label: 'Supports',            to: '/app/supports',    icon: FileText },
  { label: 'Analyses',            to: '/app/analytics',   icon: BarChart3 },
  { label: 'Profil',              to: '/app/profile',     icon: User },
  { label: 'Gestion utilisateurs',   to: '/app/users-management',     icon: Users  },
  { label: 'Aide',   to: '/app/help',     icon: HelpCircle  },
]
</script>