<template>
  <div class="p-6 space-y-5">

    <div>
      <h1 class="text-lg font-bold text-gray-800">Countries</h1>
      <p class="text-xs text-gray-400 mt-0.5">Geographic distribution of indexed companies</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else>
      <!-- Summary cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Countries</p>
          <p class="text-2xl font-black text-gray-800">{{ countries.length }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Total Companies</p>
          <p class="text-2xl font-black text-gray-800">{{ totalCompanies }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Top Country</p>
          <p class="text-sm font-bold text-gray-800 truncate">{{ countries[0]?.label ?? '—' }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Top Share</p>
          <p class="text-2xl font-black text-orange-500">
            {{ totalCompanies ? Math.round((countries[0]?.count / totalCompanies) * 100) : 0 }}%
          </p>
        </div>
      </div>

      <!-- Search -->
      <div class="bg-white rounded-xl border border-gray-200 px-4 py-3">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input v-model="search" placeholder="Filter countries..."
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">#</th>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Country</th>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Companies</th>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide w-64">Share</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-if="!filtered.length">
              <td colspan="4" class="px-4 py-12 text-center text-sm text-gray-400">
                <Globe class="w-10 h-10 mx-auto mb-2 opacity-20" />
                No countries found
              </td>
            </tr>
            <tr v-for="(c, i) in filtered" :key="c.label" class="hover:bg-orange-50/30 transition-colors">
              <td class="px-4 py-3 text-xs text-gray-400">{{ (i + 1).toString().padStart(2, '0') }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold flex-shrink-0">
                    {{ c.label?.substring(0, 2).toUpperCase() }}
                  </div>
                  <span class="text-xs font-medium text-gray-800">{{ c.label }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-xs font-bold text-gray-700">{{ c.count.toLocaleString() }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="flex-1 bg-gray-100 rounded-full h-1.5">
                    <div class="h-1.5 rounded-full bg-orange-400 transition-all"
                      :style="{ width: `${Math.round((c.count / totalCompanies) * 100)}%` }"></div>
                  </div>
                  <span class="text-xs text-gray-500 w-8 text-right">
                    {{ Math.round((c.count / totalCompanies) * 100) }}%
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Globe } from '@lucide/vue'
import api from '@/services/api'

const countries = ref([])
const loading   = ref(true)
const search    = ref('')

onMounted(async () => {
  try {
    const data = await api.get('/dashboard/kpis/')
    const raw  = data?.companies_by_country ?? []
    countries.value = raw
      .map(r => ({
        label: r.addresses__country ?? r.country ?? r.label ?? '—',
        count: r.count ?? 0,
      }))
      .filter(c => c.label && c.label !== '—')
      .sort((a, b) => b.count - a.count)
  } catch { countries.value = [] }
  finally  { loading.value = false }
})

const totalCompanies = computed(() => countries.value.reduce((s, c) => s + c.count, 0))

const filtered = computed(() => {
  if (!search.value) return countries.value
  const q = search.value.toLowerCase()
  return countries.value.filter(c => c.label.toLowerCase().includes(q))
})
</script>
