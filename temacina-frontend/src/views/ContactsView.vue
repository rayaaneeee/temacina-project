<template>
  <div class="p-6 space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-bold text-gray-800">Contacts</h1>
        <p class="text-xs text-gray-400 mt-0.5">Person contacts and company phone numbers</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        :class="['flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
          activeTab === tab.key
            ? 'bg-white text-orange-600 shadow-sm'
            : 'text-gray-500 hover:text-gray-700']">
        <component :is="tab.icon" class="w-4 h-4" />
        {{ tab.label }}
        <span v-if="tab.key === 'phones' && phoneStats.total"
          class="text-[10px] bg-orange-100 text-orange-600 font-bold px-1.5 py-0.5 rounded-full">
          {{ phoneStats.total }}
        </span>
      </button>
    </div>

    <!-- ── TAB: Person Contacts ─────────────────────────── -->
    <template v-if="activeTab === 'contacts'">

      <!-- Search -->
      <div class="bg-white rounded-xl border border-gray-200 px-4 py-3">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input v-model="contactSearch" @input="onContactSearch" placeholder="Search by name, role or company…"
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
        </div>
      </div>

      <!-- Loading -->
      <div v-if="contactsLoading" class="flex justify-center py-16">
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
            <tr v-if="!contacts.length">
              <td colspan="6" class="px-4 py-16 text-center">
                <div class="flex flex-col items-center gap-3 text-gray-400">
                  <Users class="w-12 h-12 opacity-20" />
                  <div>
                    <p class="text-sm font-medium">No person contacts yet</p>
                    <p class="text-xs text-gray-300 mt-1">The contacts database will populate as directories are ingested</p>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-else v-for="(c, i) in contacts" :key="c.id" class="hover:bg-orange-50/30 transition-colors">
              <td class="px-4 py-3 text-xs text-gray-400">{{ String(i + 1).padStart(3, '0') }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-full bg-orange-100 text-orange-600 font-bold text-xs flex items-center justify-center flex-shrink-0">
                    {{ c.first_name?.charAt(0) ?? '?' }}
                  </div>
                  <span class="text-xs font-medium text-gray-800">{{ c.first_name }} {{ c.last_name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500">{{ c.role || '—' }}</td>
              <td class="px-4 py-3">
                <RouterLink :to="`/app/companies/${c.company_id}`"
                  class="text-xs text-orange-500 hover:underline font-medium">
                  {{ c.company_name }}
                </RouterLink>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500">
                {{ c.phones?.[0]?.full_phone_number || '—' }}
              </td>
              <td class="px-4 py-3 text-xs text-gray-500">
                <a v-if="c.emails?.[0]?.email_address" :href="`mailto:${c.emails[0].email_address}`"
                  class="text-orange-500 hover:underline">{{ c.emails[0].email_address }}</a>
                <span v-else>—</span>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination for contacts -->
        <div v-if="contactsMeta.total_pages > 1"
          class="px-4 py-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
          <span>{{ contactsMeta.total }} contact{{ contactsMeta.total !== 1 ? 's' : '' }}</span>
          <div class="flex items-center gap-1">
            <button @click="loadContacts(contactsMeta.page - 1)" :disabled="contactsMeta.page <= 1"
              class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40">Previous</button>
            <button @click="loadContacts(contactsMeta.page + 1)" :disabled="contactsMeta.page >= contactsMeta.total_pages"
              class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40">Next</button>
          </div>
        </div>
      </div>
    </template>

    <!-- ── TAB: Phone Book ──────────────────────────────── -->
    <template v-else>

      <!-- Filters -->
      <div class="bg-white rounded-xl border border-gray-200 px-4 py-3 flex flex-wrap items-center gap-3">
        <div class="relative flex-1 min-w-48">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input v-model="phoneSearch" @input="onPhoneSearch" placeholder="Search company or number…"
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
        </div>
        <select v-model="phoneTypeFilter" @change="applyPhoneFilter"
          class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
          <option value="">All Types</option>
          <option value="Mobile">Mobile</option>
          <option value="Fixe">Landline</option>
        </select>
        <button @click="resetPhoneFilters" class="text-sm text-gray-500 hover:text-orange-500 flex items-center gap-1">
          <X class="w-3.5 h-3.5" /> Reset
        </button>
      </div>

      <!-- Loading -->
      <div v-if="phonesLoading" class="flex justify-center py-16">
        <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <template v-else>
        <!-- Phone table -->
        <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">#</th>
                <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Company</th>
                <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Phone Number</th>
                <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Type</th>
                <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Country</th>
                <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Sector</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-if="!phoneRows.length">
                <td colspan="6" class="px-4 py-12 text-center text-sm text-gray-400">
                  <Phone class="w-10 h-10 mx-auto mb-2 opacity-20" />
                  No phone numbers found
                </td>
              </tr>
              <tr v-else v-for="(row, i) in phoneRows" :key="`${row.company_id}-${row.phone_id}`"
                class="hover:bg-orange-50/30 transition-colors">
                <td class="px-4 py-3 text-xs text-gray-400">{{ String(phoneOffset + i + 1).padStart(3, '0') }}</td>
                <td class="px-4 py-3">
                  <RouterLink :to="`/app/companies/${row.company_id}`"
                    class="text-xs font-semibold text-orange-500 hover:underline">
                    {{ row.company_name }}
                  </RouterLink>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <Phone class="w-3.5 h-3.5 text-orange-400 flex-shrink-0" />
                    <span class="text-xs font-medium text-gray-800">{{ row.full_phone_number }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold',
                    row.type === 'Mobile' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600']">
                    {{ row.type || '—' }}
                  </span>
                </td>
                <td class="px-4 py-3 text-xs text-gray-500">{{ row.country || '—' }}</td>
                <td class="px-4 py-3 text-xs text-gray-500">{{ row.sector || '—' }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination -->
          <div v-if="phonePagination.totalPages > 1"
            class="px-4 py-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
            <span>Showing {{ phoneOffset + 1 }}–{{ Math.min(phoneOffset + phonePagination.pageSize, phonePagination.total) }} of {{ phonePagination.total }}</span>
            <div class="flex items-center gap-1">
              <button @click="changePhonesPage(phonePagination.page - 1)" :disabled="phonePagination.page <= 1"
                class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40">Previous</button>
              <button v-for="p in phoneVisiblePages" :key="p" @click="p !== '...' && changePhonesPage(p)"
                :class="['px-3 py-1.5 rounded-lg border transition-colors',
                  p === phonePagination.page ? 'bg-orange-500 text-white border-orange-500'
                  : p === '...' ? 'border-transparent cursor-default' : 'border-gray-200 hover:bg-gray-50']">
                {{ p }}
              </button>
              <button @click="changePhonesPage(phonePagination.page + 1)" :disabled="phonePagination.page >= phonePagination.totalPages"
                class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40">Next</button>
            </div>
          </div>
        </div>
      </template>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { Search, Users, Phone, X } from '@lucide/vue'
import api from '@/services/api'

// ── Tabs ──────────────────────────────────────────────────────
const tabs = [
  { key: 'contacts', label: 'Person Contacts', icon: Users  },
  { key: 'phones',   label: 'Phone Book',       icon: Phone  },
]
const activeTab = ref('contacts')

// ─────────────────────────────────────────────────────────────
// TAB 1: PERSON CONTACTS (from /contacts/ endpoint)
// ─────────────────────────────────────────────────────────────
const contacts       = ref([])
const contactsLoading = ref(false)
const contactSearch  = ref('')
const contactsMeta   = ref({ page: 1, total: 0, total_pages: 1 })

async function loadContacts(page = 1) {
  contactsLoading.value = true
  try {
    const params = { page, page_size: 25 }
    if (contactSearch.value) params.search = contactSearch.value
    const res  = await api.get('/contacts/', { params })
    // double-wrapped: res = { data: [...], meta: {...} } or { data: { data: [...] } }
    const data = res?.data?.data ?? res?.data ?? []
    const meta = res?.data?.meta ?? res?.meta ?? {}
    contacts.value = Array.isArray(data) ? data : []
    contactsMeta.value = {
      page:        meta.page        ?? page,
      total:       meta.total       ?? contacts.value.length,
      total_pages: meta.total_pages ?? 1,
    }
  } catch {
    contacts.value = []
  } finally {
    contactsLoading.value = false
  }
}

const onContactSearch = useDebounceFn(() => loadContacts(1), 350)

// ─────────────────────────────────────────────────────────────
// TAB 2: PHONE BOOK (built from companies list + detail)
// ─────────────────────────────────────────────────────────────
const allPhoneRows   = ref([])   // flat: { company_id, company_name, phone_id, full_phone_number, type, country, sector }
const phonesLoading  = ref(false)
const phoneSearch    = ref('')
const phoneTypeFilter = ref('')
const phoneStats     = ref({ total: 0 })
const phonePagination = ref({ page: 1, pageSize: 30, total: 0, totalPages: 1 })

const filteredPhoneRows = computed(() => {
  let rows = allPhoneRows.value
  if (phoneSearch.value) {
    const q = phoneSearch.value.toLowerCase()
    rows = rows.filter(r =>
      r.company_name.toLowerCase().includes(q) ||
      r.full_phone_number.includes(q)
    )
  }
  if (phoneTypeFilter.value) {
    rows = rows.filter(r => r.type === phoneTypeFilter.value)
  }
  return rows
})

const phoneRows = computed(() => {
  const start = (phonePagination.value.page - 1) * phonePagination.value.pageSize
  return filteredPhoneRows.value.slice(start, start + phonePagination.value.pageSize)
})

const phoneOffset = computed(() => (phonePagination.value.page - 1) * phonePagination.value.pageSize)

watch(filteredPhoneRows, (rows) => {
  phonePagination.value.total      = rows.length
  phonePagination.value.totalPages = Math.ceil(rows.length / phonePagination.value.pageSize) || 1
  phonePagination.value.page       = 1
})

const phoneVisiblePages = computed(() => {
  const { page, totalPages } = phonePagination.value
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
  const pages = [1]
  if (page > 3) pages.push('...')
  for (let p = Math.max(2, page - 1); p <= Math.min(totalPages - 1, page + 1); p++) pages.push(p)
  if (page < totalPages - 2) pages.push('...')
  pages.push(totalPages)
  return pages
})

function changePhonesPage(p) {
  if (p < 1 || p > phonePagination.value.totalPages) return
  phonePagination.value.page = p
}

async function loadPhoneBook() {
  phonesLoading.value = true
  try {
    // Fetch all companies (up to 500 — they're lightweight)
    const res = await api.get('/companies/', { params: { page_size: 500 } })
    const companies = res?.data ?? []

    // Fetch details in batches of 10 to get phones
    const rows = []
    const batchSize = 10
    for (let i = 0; i < companies.length; i += batchSize) {
      const batch = companies.slice(i, i + batchSize)
      const details = await Promise.all(
        batch.map(c => api.get(`/companies/${c.id}/`).catch(() => null))
      )
      details.forEach(d => {
        if (!d) return
        const company = d?.data ?? d
        ;(company.phones ?? []).forEach(p => {
          rows.push({
            company_id:        company.id,
            company_name:      company.legal_name,
            phone_id:          p.id,
            full_phone_number: p.full_phone_number,
            type:              p.type ?? '',
            country:           company.addresses?.[0]?.country ?? '',
            sector:            company.sectors?.[0]?.title     ?? '',
          })
        })
      })
    }
    allPhoneRows.value       = rows
    phoneStats.value.total   = rows.length
    phonePagination.value.total      = rows.length
    phonePagination.value.totalPages = Math.ceil(rows.length / phonePagination.value.pageSize) || 1
  } catch {
    allPhoneRows.value = []
  } finally {
    phonesLoading.value = false
  }
}

const onPhoneSearch   = useDebounceFn(() => { phonePagination.value.page = 1 }, 300)
function applyPhoneFilter() { phonePagination.value.page = 1 }
function resetPhoneFilters() { phoneSearch.value = ''; phoneTypeFilter.value = ''; phonePagination.value.page = 1 }

// Load tabs on demand
watch(activeTab, (tab) => {
  if (tab === 'phones' && !allPhoneRows.value.length) loadPhoneBook()
})

onMounted(() => loadContacts())
</script>
