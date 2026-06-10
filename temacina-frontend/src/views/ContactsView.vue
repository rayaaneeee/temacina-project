<template>
  <div class="p-6 space-y-5">

    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-bold text-gray-800">Contacts</h1>
        <p class="text-xs text-gray-400 mt-0.5">All contacts extracted from trade show directories</p>
      </div>
    </div>

    <!-- Search -->
    <div class="bg-white rounded-xl border border-gray-200 px-4 py-3 flex items-center gap-3">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input v-model="search" placeholder="Search by name, role or company..."
          class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">#</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Name</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Role</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Company</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Phone</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Email</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-if="!filtered.length">
            <td colspan="6" class="px-4 py-12 text-center text-sm text-gray-400">
              <Users class="w-10 h-10 mx-auto mb-2 opacity-20" />
              No contacts found
            </td>
          </tr>
          <tr v-for="(c, i) in filtered" :key="i" class="hover:bg-orange-50/30 transition-colors">
            <td class="px-4 py-3 text-xs text-gray-400">{{ (i + 1).toString().padStart(3, '0') }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-orange-100 text-orange-600 font-bold text-xs flex items-center justify-center flex-shrink-0">
                  {{ c.first_name?.charAt(0) ?? '?' }}
                </div>
                <span class="font-medium text-gray-800 text-xs">{{ c.first_name }} {{ c.last_name }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-xs text-gray-500">{{ c.role || '—' }}</td>
            <td class="px-4 py-3">
              <RouterLink :to="`/app/companies/${c.company_id}`"
                class="text-xs text-orange-500 hover:underline font-medium">
                {{ c.company_name }}
              </RouterLink>
            </td>
            <td class="px-4 py-3 text-xs text-gray-500">{{ c.phones?.[0]?.full_phone_number || '—' }}</td>
            <td class="px-4 py-3 text-xs text-gray-500">{{ c.emails?.[0]?.email_address || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Users } from '@lucide/vue'
import api from '@/services/api'

const contacts = ref([])
const loading  = ref(true)
const search   = ref('')

onMounted(async () => {
  try {
    // Fetch all companies with detail to extract contacts
    const res = await api.get('/companies/', { params: { page_size: 100 } })
    const companies = res?.data ?? []
    // Fetch detail for companies that likely have contacts
    const details = await Promise.all(
      companies.slice(0, 20).map(c => api.get(`/companies/${c.id}/`).catch(() => null))
    )
    contacts.value = details
      .filter(Boolean)
      .flatMap(c => (c.contacts ?? []).map(ct => ({
        ...ct,
        company_id:   c.id,
        company_name: c.legal_name,
      })))
  } catch { contacts.value = [] }
  finally  { loading.value = false }
})

const filtered = computed(() => {
  if (!search.value) return contacts.value
  const q = search.value.toLowerCase()
  return contacts.value.filter(c =>
    `${c.first_name} ${c.last_name}`.toLowerCase().includes(q) ||
    c.role?.toLowerCase().includes(q) ||
    c.company_name?.toLowerCase().includes(q)
  )
})
</script>
