<template>
  <div class="p-6 space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-bold text-gray-800">Contacts</h1>
        <p class="text-xs text-gray-400 mt-0.5">{{ pagination.total }} companies with contact information</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl border border-gray-200 px-4 py-3 flex flex-wrap items-center gap-3">
      <div class="relative flex-1 min-w-48">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input v-model="searchInput" @input="onSearch" placeholder="Search by name or country…"
          class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
      </div>
      <select v-model="sectorFilter" @change="applyFilter"
        class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
        <option value="">All Sectors</option>
        <option v-for="s in sectors" :key="s" :value="s">{{ s }}</option>
      </select>
      <button @click="resetFilters" class="text-sm text-gray-500 hover:text-orange-500 flex items-center gap-1 transition-colors">
        <X class="w-3.5 h-3.5" /> Reset
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else>
      <!-- Grid of contact cards -->
      <div v-if="companies.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div v-for="c in companies" :key="c.id"
          class="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md hover:border-orange-200 transition-all cursor-pointer"
          @click="openDetail(c)">

          <!-- Avatar + name -->
          <div class="flex items-start gap-3 mb-3">
            <div class="w-10 h-10 rounded-xl bg-orange-100 text-orange-600 font-black text-sm flex items-center justify-center flex-shrink-0">
              {{ c.legal_name?.charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-gray-800 leading-tight truncate">{{ c.legal_name }}</p>
              <p class="text-[10px] text-gray-400 mt-0.5">{{ c.sectors?.[0]?.title ?? '—' }}</p>
            </div>
          </div>

          <!-- Info rows -->
          <div class="space-y-1.5">
            <div class="flex items-center gap-2 text-[11px] text-gray-500">
              <Globe class="w-3 h-3 flex-shrink-0 text-gray-300" />
              <span class="truncate">{{ c.country ?? '—' }}</span>
            </div>
          </div>

          <!-- Footer -->
          <div class="mt-3 pt-3 border-t border-gray-50 flex items-center justify-between">
            <span class="text-[10px] text-gray-400">ID #{{ c.id }}</span>
            <RouterLink :to="`/app/companies/${c.id}`" @click.stop
              class="text-[10px] text-orange-500 hover:text-orange-700 font-semibold flex items-center gap-1">
              View Profile <ArrowRight class="w-3 h-3" />
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="bg-white rounded-xl border border-gray-200 py-16 flex flex-col items-center text-gray-400">
        <Users class="w-10 h-10 mb-2 opacity-20" />
        <p class="text-sm">No contacts found</p>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total > 0"
        class="bg-white rounded-xl border border-gray-200 px-4 py-3 flex items-center justify-between text-xs text-gray-500">
        <span>Showing {{ offset + 1 }}–{{ Math.min(offset + pagination.pageSize, pagination.total) }} of {{ pagination.total }}</span>
        <div class="flex items-center gap-1">
          <button @click="changePage(pagination.page - 1)" :disabled="pagination.page <= 1"
            class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">Previous</button>
          <button v-for="p in visiblePages" :key="p" @click="p !== '...' && changePage(p)"
            :class="['px-3 py-1.5 rounded-lg border transition-colors',
              p === pagination.page ? 'bg-orange-500 text-white border-orange-500'
              : p === '...' ? 'border-transparent cursor-default' : 'border-gray-200 hover:bg-gray-50']">
            {{ p }}
          </button>
          <button @click="changePage(pagination.page + 1)" :disabled="pagination.page >= pagination.totalPages"
            class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">Next</button>
        </div>
      </div>
    </template>

    <!-- Detail slide-over -->
    <Teleport to="body">
      <Transition enter-from-class="opacity-0" enter-active-class="transition duration-150"
        leave-to-class="opacity-0" leave-active-class="transition duration-150">
        <div v-if="selected" class="fixed inset-0 z-50 flex">
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="selected = null; detail = null" />
          <div class="relative ml-auto w-full max-w-sm bg-white h-full shadow-2xl flex flex-col overflow-hidden z-10">

            <!-- Panel header -->
            <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-orange-100 text-orange-600 font-black text-sm flex items-center justify-center flex-shrink-0">
                  {{ selected.legal_name?.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="text-sm font-bold text-gray-800 truncate max-w-48">{{ selected.legal_name }}</p>
                  <p class="text-xs text-gray-400">{{ selected.sectors?.[0]?.title ?? '—' }}</p>
                </div>
              </div>
              <button @click="selected = null; detail = null" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400">
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- Loading detail -->
            <div v-if="detailLoading" class="flex-1 flex items-center justify-center">
              <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
            </div>

            <div v-else class="flex-1 overflow-y-auto p-5 space-y-5">

              <!-- Address -->
              <div v-if="detail?.addresses?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Address</p>
                <div v-for="a in detail.addresses" :key="a.id" class="flex items-start gap-2 text-xs text-gray-600">
                  <MapPin class="w-3.5 h-3.5 text-gray-300 flex-shrink-0 mt-0.5" />
                  <span>{{ [a.street, a.city, a.country].filter(Boolean).join(', ') }}</span>
                </div>
              </div>

              <!-- Phones -->
              <div v-if="detail?.phones?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Phone Numbers</p>
                <div class="space-y-1.5">
                  <div v-for="p in detail.phones" :key="p.id"
                    class="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2">
                    <div class="flex items-center gap-2">
                      <Phone class="w-3.5 h-3.5 text-gray-400" />
                      <span class="text-xs font-medium text-gray-700">{{ p.full_phone_number }}</span>
                    </div>
                    <span class="text-[10px] text-gray-400 bg-white border border-gray-200 px-1.5 py-0.5 rounded">{{ p.type }}</span>
                  </div>
                </div>
              </div>

              <!-- Emails -->
              <div v-if="detail?.emails?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Emails</p>
                <div class="space-y-1.5">
                  <div v-for="e in detail.emails" :key="e.id"
                    class="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2">
                    <Mail class="w-3.5 h-3.5 text-gray-400" />
                    <span class="text-xs font-medium text-gray-700 break-all">{{ e.email_address }}</span>
                  </div>
                </div>
              </div>

              <!-- Websites -->
              <div v-if="detail?.websites?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Websites</p>
                <div class="space-y-1.5">
                  <div v-for="w in detail.websites" :key="w.id"
                    class="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2">
                    <Link class="w-3.5 h-3.5 text-gray-400" />
                    <a :href="w.url" target="_blank" class="text-xs text-orange-500 hover:underline break-all">{{ w.url }}</a>
                  </div>
                </div>
              </div>

              <!-- Trade Shows -->
              <div v-if="detail?.trade_shows?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Trade Shows</p>
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="ts in detail.trade_shows" :key="ts"
                    class="text-[10px] bg-orange-50 text-orange-600 border border-orange-200 px-2 py-0.5 rounded-full font-medium">
                    {{ ts }}
                  </span>
                </div>
              </div>

              <!-- No contact info -->
              <div v-if="detail && !detail.phones?.length && !detail.emails?.length && !detail.websites?.length"
                class="flex flex-col items-center py-8 text-gray-400">
                <PhoneOff class="w-8 h-8 mb-2 opacity-30" />
                <p class="text-xs">No contact information available</p>
              </div>

            </div>

            <!-- Panel footer -->
            <div class="border-t border-gray-100 p-4">
              <RouterLink :to="`/app/companies/${selected.id}`"
                class="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-orange-500 text-white text-sm font-semibold hover:bg-orange-600 transition-colors">
                View Full Profile
                <ArrowRight class="w-4 h-4" />
              </RouterLink>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { Search, Users, Globe, Phone, Mail, Link, MapPin, X, ArrowRight, PhoneOff } from '@lucide/vue'
import api from '@/services/api'

// ── State ────────────────────────────────────────────────────
const companies   = ref([])
const loading     = ref(true)
const searchInput = ref('')
const sectorFilter = ref('')
const sectors     = ref([])
const pagination  = ref({ page: 1, pageSize: 20, total: 0, totalPages: 1 })

const selected     = ref(null)
const detail       = ref(null)
const detailLoading = ref(false)

// ── Fetch ────────────────────────────────────────────────────
async function fetchCompanies(page = 1) {
  loading.value = true
  try {
    const params = { page, page_size: pagination.value.pageSize }
    if (searchInput.value) params.search = searchInput.value
    if (sectorFilter.value) params.sector = sectorFilter.value

    const res = await api.get('/companies/', { params })
    // Handle double-wrapped or single-wrapped response
    const data = res?.data ?? res ?? []
    const meta = res?.meta ?? {}
    companies.value = Array.isArray(data) ? data : []
    pagination.value = {
      page:       meta.page       ?? page,
      pageSize:   meta.page_size  ?? 20,
      total:      meta.total      ?? companies.value.length,
      totalPages: meta.total_pages ?? 1,
    }
    // Collect unique sectors for filter
    const sectorSet = new Set()
    companies.value.forEach(c => c.sectors?.forEach(s => sectorSet.add(s.title)))
    if (sectorSet.size > sectors.value.length) sectors.value = [...sectorSet].sort()
  } catch {
    companies.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchCompanies())

// ── Filters ──────────────────────────────────────────────────
const onSearch = useDebounceFn(() => fetchCompanies(1), 350)

function applyFilter() { fetchCompanies(1) }

function resetFilters() {
  searchInput.value  = ''
  sectorFilter.value = ''
  fetchCompanies(1)
}

function changePage(p) {
  if (p < 1 || p > pagination.value.totalPages) return
  fetchCompanies(p)
}

// ── Detail slide-over ────────────────────────────────────────
async function openDetail(company) {
  selected.value     = company
  detail.value       = null
  detailLoading.value = true
  try {
    const res = await api.get(`/companies/${company.id}/`)
    detail.value = res?.data ?? res
  } catch {
    detail.value = null
  } finally {
    detailLoading.value = false
  }
}

// ── Helpers ──────────────────────────────────────────────────
const offset = computed(() => (pagination.value.page - 1) * pagination.value.pageSize)

const visiblePages = computed(() => {
  const { page, totalPages } = pagination.value
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
  const pages = [1]
  if (page > 3) pages.push('...')
  for (let p = Math.max(2, page - 1); p <= Math.min(totalPages - 1, page + 1); p++) pages.push(p)
  if (page < totalPages - 2) pages.push('...')
  pages.push(totalPages)
  return pages
})
</script>
