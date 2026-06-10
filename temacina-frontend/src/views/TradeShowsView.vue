<template>
  <div class="flex h-full overflow-hidden">

    <!-- ── Left: Trade Show List ─────────────────────────────── -->
    <div class="w-72 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col">

      <!-- Header -->
      <div class="px-4 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 class="text-sm font-bold text-gray-800">Trade Exhibitions</h2>
        <button @click="showFilters = !showFilters"
          class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors">
          <SlidersHorizontal class="w-4 h-4" />
        </button>
      </div>

      <!-- Filters dropdown -->
      <div v-if="showFilters" class="px-4 py-3 border-b border-gray-100 space-y-2 bg-gray-50">
        <select v-model="store.filters.year" @change="store.setFilter('year', store.filters.year)"
          class="w-full text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-orange-400">
          <option :value="null">All Years</option>
          <option v-for="y in store.years" :key="y" :value="y">{{ y }}</option>
        </select>
        <input v-model="countryInput" @input="store.setFilter('country', countryInput)"
          placeholder="Filter by country..."
          class="w-full text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-orange-400" />
      </div>

      <!-- Search -->
      <div class="px-4 py-3 border-b border-gray-100">
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input v-model="searchInput" @input="onSearch"
            placeholder="Filter shows..."
            class="w-full text-xs pl-8 pr-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
        </div>
      </div>

      <!-- List -->
      <div class="flex-1 overflow-y-auto">
        <!-- Loading skeleton -->
        <div v-if="store.loading" class="p-4 space-y-3">
          <div v-for="i in 6" :key="i" class="animate-pulse">
            <div class="h-4 bg-gray-100 rounded w-3/4 mb-1"></div>
            <div class="h-3 bg-gray-100 rounded w-1/2"></div>
          </div>
        </div>

        <div v-else>
          <button
            v-for="ts in store.tradeShows"
            :key="ts.id"
            @click="store.selectShow(ts)"
            :class="[
              'w-full text-left px-4 py-3 border-b border-gray-50 transition-colors',
              store.selectedShow?.id === ts.id
                ? 'bg-orange-50 border-l-2 border-l-orange-500'
                : 'hover:bg-gray-50'
            ]"
          >
            <div class="flex items-center justify-between">
              <p :class="['text-sm font-semibold truncate pr-2', store.selectedShow?.id === ts.id ? 'text-orange-600' : 'text-gray-800']">
                {{ ts.name }}
              </p>
              <span class="text-[10px] font-bold text-orange-500 flex-shrink-0 bg-orange-50 px-1.5 py-0.5 rounded">
                {{ ts.exhibition_year }}
              </span>
            </div>
            <div class="flex items-center gap-3 mt-1 text-xs text-gray-400">
              <span v-if="ts.city || ts.country" class="flex items-center gap-1">
                <MapPin class="w-3 h-3" />
                {{ [ts.city, ts.country].filter(Boolean).join(', ') }}
              </span>
            </div>
          </button>

          <p v-if="!store.tradeShows.length" class="text-center text-xs text-gray-400 py-8">
            No trade shows found
          </p>
        </div>
      </div>

      <!-- Pagination -->
      <div class="px-4 py-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-400">
        <span>{{ store.pagination.total }} exhibitions</span>
        <div class="flex gap-1">
          <button @click="store.setPage(store.pagination.page - 1)"
            :disabled="store.pagination.page <= 1"
            class="px-2 py-1 rounded hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed">‹</button>
          <span class="px-2 py-1 text-gray-600 font-medium">{{ store.pagination.page }}</span>
          <button @click="store.setPage(store.pagination.page + 1)"
            :disabled="store.pagination.page >= store.pagination.totalPages"
            class="px-2 py-1 rounded hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed">›</button>
        </div>
      </div>
    </div>

    <!-- ── Right: Detail Panel ────────────────────────────────── -->
    <div class="flex-1 overflow-y-auto bg-gray-50">

      <!-- Empty state -->
      <div v-if="!store.selectedShow" class="flex flex-col items-center justify-center h-full text-gray-400">
        <CalendarDays class="w-14 h-14 mb-4 opacity-20" />
        <p class="text-sm font-medium">Select a trade show</p>
        <p class="text-xs mt-1">Click any exhibition on the left to view details</p>
      </div>

      <!-- Detail loading -->
      <div v-else-if="store.detailLoading" class="p-6 space-y-4">
        <div class="animate-pulse space-y-3">
          <div class="h-6 bg-gray-200 rounded w-1/3"></div>
          <div class="h-4 bg-gray-200 rounded w-1/4"></div>
          <div class="grid grid-cols-4 gap-4 mt-6">
            <div v-for="i in 4" :key="i" class="h-24 bg-gray-200 rounded-xl"></div>
          </div>
        </div>
      </div>

      <!-- Detail content -->
      <template v-else-if="store.selectedShow">
        <div class="p-6 space-y-6">

          <!-- Header -->
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="text-xs font-bold text-orange-500 bg-orange-50 px-2 py-0.5 rounded">
                  {{ store.selectedShow.exhibition_year }}
                </span>
              </div>
              <h1 class="text-2xl font-black text-gray-900">{{ store.selectedShow.name }}</h1>
              <div class="flex items-center gap-4 mt-1 text-sm text-gray-500">
                <span v-if="store.selectedShow.city || store.selectedShow.country" class="flex items-center gap-1">
                  <MapPin class="w-3.5 h-3.5" />
                  {{ store.selectedShow.venue_name ? store.selectedShow.venue_name + ', ' : '' }}
                  {{ [store.selectedShow.city, store.selectedShow.country].filter(Boolean).join(', ') }}
                </span>
              </div>
            </div>
            <button @click="exportCompanies"
              class="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-colors">
              <Download class="w-4 h-4" />
              Export Data
            </button>
          </div>

          <!-- KPI Cards -->
          <div class="grid grid-cols-4 gap-4">
            <div class="bg-white rounded-xl border border-gray-200 p-4">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center">
                  <Building2 class="w-4 h-4 text-orange-500" />
                </div>
                <p class="text-xs text-gray-500">Companies Indexed</p>
              </div>
              <p class="text-2xl font-black text-gray-900">{{ store.showStats?.company_count ?? 0 }}</p>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-4">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                  <FileText class="w-4 h-4 text-blue-500" />
                </div>
                <p class="text-xs text-gray-500">Documents</p>
              </div>
              <p class="text-2xl font-black text-gray-900">{{ store.showStats?.document_count ?? 0 }}</p>
              <p class="text-xs text-gray-400 mt-0.5">All active</p>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-4">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center">
                  <Users class="w-4 h-4 text-green-500" />
                </div>
                <p class="text-xs text-gray-500">Contact Leads</p>
              </div>
              <p class="text-2xl font-black text-gray-900">{{ contactLeads }}</p>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-4">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
                  <RefreshCw class="w-4 h-4 text-purple-500" />
                </div>
                <p class="text-xs text-gray-500">Ingestion</p>
              </div>
              <p class="text-2xl font-black text-gray-900">{{ ingestionPct }}%</p>
              <p class="text-xs text-gray-400 mt-0.5">Completion</p>
            </div>
          </div>

          <!-- Ingestion Progress Bar (if docs exist) -->
          <div v-if="store.showStats?.ingestion_status?.length" class="bg-white rounded-xl border border-gray-200 p-4">
            <h3 class="text-sm font-bold text-gray-700 mb-3">Ingestion Status</h3>
            <div class="space-y-2">
              <div v-for="s in store.showStats.ingestion_status" :key="s.ingestion_status" class="flex items-center gap-3">
                <span class="text-xs text-gray-500 w-20 capitalize">{{ s.ingestion_status }}</span>
                <div class="flex-1 bg-gray-100 rounded-full h-2">
                  <div class="h-2 rounded-full transition-all"
                    :class="s.ingestion_status === 'done' ? 'bg-green-500' : s.ingestion_status === 'pending' ? 'bg-yellow-400' : 'bg-red-400'"
                    :style="{ width: store.showStats.document_count ? (s.count / store.showStats.document_count * 100) + '%' : '0%' }">
                  </div>
                </div>
                <span class="text-xs font-bold text-gray-700 w-6 text-right">{{ s.count }}</span>
              </div>
            </div>
          </div>

          <!-- Exhibition Intelligence: Companies Table -->
          <div class="bg-white rounded-xl border border-gray-200">
            <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between gap-4">
              <div>
                <h3 class="text-sm font-bold text-gray-800">Exhibition Intelligence</h3>
                <p class="text-xs text-gray-400 mt-0.5">B2B entities identified from {{ store.selectedShow.name }}</p>
              </div>
              <div class="relative flex-shrink-0">
                <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
                <input :value="store.companiesSearch"
                  @input="store.searchCompanies($event.target.value)"
                  placeholder="Filter list..."
                  class="pl-8 pr-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400 w-44" />
              </div>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead class="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide w-12">#</th>
                    <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Company Name</th>
                    <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Sector</th>
                    <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Location</th>
                    <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Contact</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  <tr v-if="store.showCompanies.length === 0">
                    <td colspan="5" class="px-4 py-10 text-center text-sm text-gray-400">
                      No companies indexed for this trade show yet
                    </td>
                  </tr>
                  <tr v-for="(c, i) in store.showCompanies" :key="c.id"
                    class="hover:bg-orange-50/30 transition-colors cursor-pointer"
                    @click="$router.push(`/app/companies/${c.id}`)">
                    <td class="px-4 py-3 text-xs text-gray-400">
                      {{ (companiesOffset + i + 1).toString().padStart(4, '0') }}
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex items-center gap-2">
                        <div class="w-7 h-7 rounded-lg bg-orange-100 text-orange-600 font-bold text-xs
                                    flex items-center justify-center flex-shrink-0">
                          {{ c.legal_name?.charAt(0) }}
                        </div>
                        <span class="font-semibold text-gray-800 text-xs">{{ c.legal_name }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <span v-if="c.sectors?.length"
                        class="text-[10px] px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 font-medium">
                        {{ c.sectors[0]?.title ?? c.sectors[0] }}
                      </span>
                      <span v-else class="text-xs text-gray-400">—</span>
                    </td>
                    <td class="px-4 py-3 text-xs text-gray-600">
                      {{ c.addresses?.[0]?.country ?? c.country ?? '—' }}
                    </td>
                    <td class="px-4 py-3 text-xs text-gray-400">
                      {{ c.contacts?.[0] ? `${c.contacts[0].first_name ?? ''} ${c.contacts[0].last_name ?? ''}`.trim() || '—' : '—' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Table pagination -->
            <div v-if="store.companiesPagination.totalPages > 1"
              class="px-4 py-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
              <span>Showing {{ companiesOffset + 1 }}–{{ Math.min(companiesOffset + store.companiesPagination.pageSize, store.companiesPagination.total) }} of {{ store.companiesPagination.total }}</span>
              <div class="flex items-center gap-1">
                <button @click="store.setCompaniesPage(store.companiesPagination.page - 1)"
                  :disabled="store.companiesPagination.page <= 1"
                  class="px-2.5 py-1 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">
                  Previous
                </button>
                <button
                  v-for="p in visiblePages"
                  :key="p"
                  @click="p !== '...' && store.setCompaniesPage(p)"
                  :class="[
                    'px-2.5 py-1 rounded-lg border transition-colors',
                    p === store.companiesPagination.page
                      ? 'bg-orange-500 text-white border-orange-500'
                      : p === '...' ? 'border-transparent cursor-default' : 'border-gray-200 hover:bg-gray-50'
                  ]">
                  {{ p }}
                </button>
                <button @click="store.setCompaniesPage(store.companiesPagination.page + 1)"
                  :disabled="store.companiesPagination.page >= store.companiesPagination.totalPages"
                  class="px-2.5 py-1 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">
                  Next
                </button>
              </div>
            </div>
          </div>

        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import {
  Search, SlidersHorizontal, MapPin, CalendarDays,
  Building2, FileText, Users, RefreshCw, Download,
} from '@lucide/vue'
import { useTradeShowsStore } from '@/stores/tradeShows'

const store = useTradeShowsStore()

const showFilters  = ref(false)
const countryInput = ref('')
const searchInput  = ref('')

onMounted(() => store.fetchTradeShows())

const onSearch = useDebounceFn(() => {
  store.setFilter('search', searchInput.value)
}, 350)

// KPI computed
const contactLeads = computed(() => {
  if (!store.showStats) return 0
  // Sum contacts from ingestion data — approximate from company count
  return store.showStats.company_count ? store.showStats.company_count * 2 : 0
})

const ingestionPct = computed(() => {
  const s = store.showStats
  if (!s || !s.document_count) return 0
  const done = s.ingestion_status?.find(x => x.ingestion_status === 'done')?.count ?? 0
  return Math.round((done / s.document_count) * 100)
})

const companiesOffset = computed(() =>
  (store.companiesPagination.page - 1) * store.companiesPagination.pageSize
)

const visiblePages = computed(() => {
  const { page, totalPages } = store.companiesPagination
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
  const pages = [1]
  if (page > 3) pages.push('...')
  for (let p = Math.max(2, page - 1); p <= Math.min(totalPages - 1, page + 1); p++) pages.push(p)
  if (page < totalPages - 2) pages.push('...')
  pages.push(totalPages)
  return pages
})

function exportCompanies() {
  if (!store.showCompanies.length) return
  const headers = ['Company', 'Sector', 'Country']
  const rows = store.showCompanies.map(c => [
    c.legal_name,
    c.sectors?.[0]?.title ?? '',
    c.addresses?.[0]?.country ?? c.country ?? '',
  ])
  const csv = [headers, ...rows].map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a'); a.href = url
  a.download = `${store.selectedShow.name}_companies.csv`; a.click()
  URL.revokeObjectURL(url)
}
</script>
