<template>
  <div class="flex h-full overflow-hidden">

    <!-- ── Column 1 · Filters ──────────────────────────────────── -->
    <aside class="w-56 flex-shrink-0 border-r border-gray-200 bg-white overflow-y-auto flex flex-col">

      <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Filters</span>
        <button
          v-if="store.activeFiltersCount > 0"
          @click="store.resetFilters()"
          class="text-xs text-orange-500 hover:text-orange-600 font-medium"
        >Reset</button>
      </div>

      <div class="flex-1 px-3 py-3 space-y-5">

        <!-- Sector -->
        <FilterGroup label="1 Sector of Activity" :badge="store.filters.sector_id ? 1 : 0">
          <FilterCheckbox
            v-for="s in store.sectors"
            :key="s.id"
            :label="s.title"
            :checked="store.filters.sector_id === s.id"
            @toggle="store.setFilter('sector_id', store.filters.sector_id === s.id ? null : s.id)"
          />
        </FilterGroup>

        <!-- Exhibition Year -->
        <FilterGroup label="2 Exhibition Year" :badge="store.filters.year ? 1 : 0">
          <FilterCheckbox
            v-for="y in years"
            :key="y"
            :label="String(y)"
            :checked="store.filters.year === y"
            @toggle="store.setFilter('year', store.filters.year === y ? null : y)"
          />
        </FilterGroup>

        <!-- Trade Show -->
        <FilterGroup label="3 Trade Show" :badge="store.filters.trade_show_id ? 1 : 0">
          <FilterCheckbox
            v-for="ts in store.tradeShows"
            :key="ts.id"
            :label="`${ts.name} ${ts.exhibition_year}`"
            :checked="store.filters.trade_show_id === ts.id"
            @toggle="store.setFilter('trade_show_id', store.filters.trade_show_id === ts.id ? null : ts.id)"
          />
        </FilterGroup>

        <!-- Country -->
        <FilterGroup label="4 Country" :badge="store.filters.country ? 1 : 0">
          <div class="mt-1">
            <input
              :value="store.filters.country"
              @input="store.setFilter('country', $event.target.value)"
              type="text"
              placeholder="e.g. France"
              class="w-full text-xs border border-gray-200 rounded px-2 py-1.5
                     focus:outline-none focus:ring-1 focus:ring-orange-400"
            />
          </div>
          <FilterCheckbox
            v-for="c in store.countries.slice(0, 8)"
            :key="c"
            :label="c"
            :checked="store.filters.country === c"
            @toggle="store.setFilter('country', store.filters.country === c ? '' : c)"
          />
        </FilterGroup>

      </div>

      <!-- Action buttons -->
      <div class="px-3 pb-4 space-y-2 border-t border-gray-100 pt-3">
        <button
          @click="store.fetchCompanies()"
          class="w-full flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600
                 text-white text-sm font-semibold py-2 rounded-lg transition-colors"
        >
          <Search class="w-4 h-4" />
          Search
        </button>
        <button
          @click="store.resetFilters()"
          class="w-full flex items-center justify-center gap-2 border border-gray-200
                 text-gray-600 hover:bg-gray-50 text-sm font-medium py-2 rounded-lg transition-colors"
        >
          <RotateCcw class="w-4 h-4" />
          Reset
        </button>
      </div>
    </aside>

    <!-- ── Column 2 + 3 wrapper ───────────────────────────────── -->
    <div class="flex-1 flex flex-col overflow-hidden">

      <!-- Top bar -->
      <div class="bg-white border-b border-gray-200 px-5 py-3 flex items-center gap-4 flex-shrink-0">
        <div class="relative flex-1 max-w-sm">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="store.filters.search"
            @keyup.enter="store.fetchCompanies()"
            type="text"
            placeholder="Search companies..."
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg
                   focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
          />
        </div>

        <div class="flex items-center gap-4 text-sm">
          <div class="flex items-center gap-1.5">
            <Building2 class="w-4 h-4 text-orange-500" />
            <span class="font-bold text-gray-800">{{ store.pagination.total.toLocaleString() }}</span>
            <span class="text-gray-500">companies</span>
          </div>
        </div>

        <div class="ml-auto flex items-center gap-2">
          <!-- Export button -->
          <button
            @click="showExportModal = true"
            class="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white
                   text-sm font-semibold px-3 py-1.5 rounded-lg transition-colors"
          >
            <Download class="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      <!-- Filter summary bar -->
      <div
        v-if="store.filterSummary.length"
        class="bg-orange-50 border-b border-orange-100 px-5 py-2 text-xs text-gray-600 flex flex-wrap gap-x-3 gap-y-1"
      >
        <span v-for="part in store.filterSummary" :key="part.label">
          <span class="font-semibold text-gray-700">{{ part.label }}:</span>
          {{ part.value }}
        </span>
      </div>

      <!-- Table + detail -->
      <div class="flex flex-1 overflow-hidden">

        <!-- ── Column 2 · Company Table ───────────────────── -->
        <div class="flex-1 overflow-y-auto bg-gray-50">

          <div v-if="store.loading" class="flex items-center justify-center h-32">
            <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          </div>

          <template v-else>
            <!-- Table header with sorting -->
            <div class="sticky top-0 bg-white border-b border-gray-200 z-10">
              <div class="flex items-center px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                <span class="w-8">#</span>
                <SortableHeader class="flex-1"   field="legal_name" label="Company Name"    :ordering="store.filters.ordering" @sort="store.setOrdering" />
                <SortableHeader class="w-32 hidden md:block" field="contacts__first_name" label="Contact" :ordering="store.filters.ordering" @sort="store.setOrdering" />
                <SortableHeader class="w-28 hidden lg:block" field="addresses__city"      label="City"    :ordering="store.filters.ordering" @sort="store.setOrdering" />
                <SortableHeader class="w-24 hidden lg:block" field="addresses__country"   label="Country" :ordering="store.filters.ordering" @sort="store.setOrdering" />
                <span class="w-16 text-right">Action</span>
              </div>
            </div>

            <!-- Rows -->
            <div
              v-for="(company, idx) in store.companies"
              :key="company.id"
              @click="store.selectCompany(company)"
              :class="[
                'flex items-center px-4 py-3 border-b border-gray-100 cursor-pointer transition-colors text-sm',
                store.selectedCompany?.id === company.id
                  ? 'bg-orange-50 border-l-2 border-l-orange-500'
                  : 'bg-white hover:bg-gray-50'
              ]"
            >
              <span class="w-8 text-gray-400 text-xs">
                {{ (store.pagination.page - 1) * store.pagination.pageSize + idx + 1 }}
              </span>

              <div class="flex-1 min-w-0 flex items-center gap-2">
                <div class="w-7 h-7 rounded-md bg-orange-100 text-orange-600 font-bold text-xs
                            flex items-center justify-center flex-shrink-0">
                  {{ company.legal_name.charAt(0) }}
                </div>
                <span class="font-medium text-gray-800 truncate">{{ company.legal_name }}</span>
                <span
                  v-for="s in (company.sectors ?? []).slice(0, 1)"
                  :key="s.id ?? s"
                  class="hidden sm:inline-flex text-[10px] px-1.5 py-0.5 rounded-full bg-orange-100 text-orange-600 font-medium"
                >{{ s.title ?? s }}</span>
              </div>

              <span class="w-32 hidden md:block text-gray-600 truncate">
                {{ contactName(company) }}
              </span>
              <span class="w-28 hidden lg:block text-gray-500 truncate">
                {{ company.addresses?.[0]?.city ?? '—' }}
              </span>
              <span class="w-24 hidden lg:block text-gray-500 truncate">
                {{ company.country ?? company.addresses?.[0]?.country ?? '—' }}
              </span>

              <div class="w-16 flex justify-end">
                <button
                  @click.stop="store.selectCompany(company)"
                  class="text-xs text-orange-500 hover:text-orange-700 font-medium"
                >View</button>
              </div>
            </div>

            <!-- Empty -->
            <div v-if="!store.companies.length" class="flex flex-col items-center justify-center py-16 text-gray-400">
              <Building2 class="w-10 h-10 mb-3 opacity-30" />
              <p class="text-sm">No companies match your filters.</p>
              <button @click="store.resetFilters()" class="mt-2 text-orange-500 text-sm hover:underline">Clear filters</button>
            </div>

            <!-- Pagination -->
            <div v-if="store.pagination.totalPages > 1"
              class="flex items-center justify-between px-5 py-3 border-t border-gray-200 bg-white text-sm">
              <span class="text-gray-500 text-xs">
                Showing {{ (store.pagination.page - 1) * store.pagination.pageSize + 1 }}–{{
                  Math.min(store.pagination.page * store.pagination.pageSize, store.pagination.total)
                }} of {{ store.pagination.total }}
              </span>
              <div class="flex items-center gap-1">
                <button
                  @click="store.setPage(store.pagination.page - 1)"
                  :disabled="store.pagination.page === 1"
                  class="px-2 py-1 rounded border border-gray-200 text-gray-500
                         hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed text-xs"
                >&lsaquo;</button>

                <template v-for="p in visiblePages" :key="p">
                  <span v-if="p === '...'" class="px-2 text-gray-400 text-xs">…</span>
                  <button
                    v-else
                    @click="store.setPage(p)"
                    :class="p === store.pagination.page
                      ? 'bg-orange-500 text-white border-orange-500'
                      : 'border-gray-200 text-gray-600 hover:bg-gray-50'"
                    class="w-7 h-7 rounded border text-xs font-medium transition-colors"
                  >{{ p }}</button>
                </template>

                <button
                  @click="store.setPage(store.pagination.page + 1)"
                  :disabled="store.pagination.page === store.pagination.totalPages"
                  class="px-2 py-1 rounded border border-gray-200 text-gray-500
                         hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed text-xs"
                >&rsaquo;</button>

                <select
                  :value="store.pagination.pageSize"
                  @change="store.setPageSize(+$event.target.value)"
                  class="ml-2 border border-gray-200 rounded text-xs py-1 px-1 text-gray-600 focus:outline-none"
                >
                  <option v-for="n in [5, 10, 25, 50]" :key="n" :value="n">{{ n }} / page</option>
                </select>
              </div>
            </div>
          </template>
        </div>

        <!-- ── Column 3 · Company Detail Panel ──────────── -->
        <div class="w-80 flex-shrink-0 border-l border-gray-200 bg-white overflow-y-auto flex flex-col">

          <!-- No selection -->
          <div v-if="!store.selectedCompany"
            class="flex-1 flex flex-col items-center justify-center text-gray-400 px-6 text-center">
            <Building2 class="w-10 h-10 mb-3 opacity-25" />
            <p class="text-sm font-medium">Select a company</p>
            <p class="text-xs mt-1 text-gray-300">Click any row to see company details</p>
          </div>

          <template v-else>
            <!-- Header -->
            <div class="px-4 py-3 border-b border-gray-100 flex items-start gap-3">
              <div class="w-10 h-10 rounded-xl bg-orange-100 text-orange-600 font-bold text-base
                          flex items-center justify-center flex-shrink-0">
                {{ store.selectedCompany.legal_name.charAt(0) }}
              </div>
              <div class="min-w-0 flex-1">
                <h3 class="font-bold text-gray-800 text-sm leading-tight">
                  {{ store.selectedCompany.legal_name }}
                </h3>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span
                    v-for="s in (store.selectedCompany.sectors ?? [])"
                    :key="s.id ?? s"
                    class="text-[10px] px-1.5 py-0.5 rounded-full bg-orange-100 text-orange-600 font-medium"
                  >{{ s.title ?? s }}</span>
                </div>
              </div>
              <RouterLink
                :to="{ name: 'company-profile', params: { id: store.selectedCompany.id } }"
                class="ml-auto flex-shrink-0 text-orange-500 hover:text-orange-700"
                title="Open full profile"
              >
                <ExternalLink class="w-4 h-4" />
              </RouterLink>
            </div>

            <!-- Detail loading spinner -->
            <div v-if="detailLoading" class="flex justify-center py-6">
              <div class="w-5 h-5 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
            </div>

            <div v-else class="px-4 py-3 space-y-4 text-sm flex-1">

              <!-- Description -->
              <div v-if="description" class="bg-gray-50 rounded-lg p-3">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">About</p>
                <p class="text-xs text-gray-600 leading-relaxed">{{ description }}</p>
              </div>

              <!-- Address -->
              <DetailRow icon="MapPin" label="Address">
                <span v-if="store.selectedCompany.addresses?.[0]">
                  {{ store.selectedCompany.addresses[0].street }}<br />
                  {{ store.selectedCompany.addresses[0].postal_code }}
                  {{ store.selectedCompany.addresses[0].city }}<br />
                  {{ store.selectedCompany.addresses[0].country }}
                </span>
                <span v-else>—</span>
              </DetailRow>

              <!-- Contacts -->
              <div v-if="store.selectedCompany.contacts?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Contacts</p>
                <div class="space-y-3">
                  <div
                    v-for="(c, i) in store.selectedCompany.contacts"
                    :key="i"
                    class="border border-gray-100 rounded-lg p-2.5 space-y-1.5"
                  >
                    <div class="flex items-center gap-2">
                      <div class="w-6 h-6 rounded-full bg-orange-100 text-orange-600 text-[10px] font-bold flex items-center justify-center">
                        {{ (c.first_name ?? c.name ?? '?').charAt(0) }}
                      </div>
                      <div>
                        <p class="text-xs font-semibold text-gray-700">
                          {{ c.first_name && c.last_name ? `${c.first_name} ${c.last_name}` : (c.name ?? '—') }}
                        </p>
                        <p v-if="c.role" class="text-[10px] text-gray-400">{{ c.role }}</p>
                      </div>
                    </div>
                    <div v-if="c.phones?.length" class="flex items-center gap-1.5 text-[11px] text-gray-500">
                      <Phone class="w-3 h-3 text-orange-400" />
                      {{ c.phones[0].full_phone_number ?? c.phones[0].number }}
                    </div>
                    <div v-if="c.emails?.length" class="flex items-center gap-1.5 text-[11px] text-gray-500 truncate">
                      <Mail class="w-3 h-3 text-orange-400" />
                      <a :href="`mailto:${c.emails[0].email_address ?? c.emails[0].address}`" class="text-orange-500 hover:underline truncate">
                        {{ c.emails[0].email_address ?? c.emails[0].address }}
                      </a>
                    </div>
                  </div>
                </div>
              </div>
              <DetailRow v-else icon="User" label="Contact">
                {{ store.selectedCompany.contacts?.[0]
                    ? (store.selectedCompany.contacts[0].first_name + ' ' + store.selectedCompany.contacts[0].last_name).trim() || '—'
                    : '—' }}
              </DetailRow>

              <!-- Phones -->
              <div v-if="store.selectedCompany.phones?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Phone Numbers</p>
                <div class="space-y-1">
                  <div
                    v-for="(p, i) in store.selectedCompany.phones"
                    :key="i"
                    class="flex items-center gap-2 text-xs text-gray-700"
                  >
                    <Phone class="w-3.5 h-3.5 text-orange-400 flex-shrink-0" />
                    <span>{{ p.full_phone_number ?? p.number }}</span>
                    <span v-if="p.type" class="text-[10px] text-gray-400">({{ p.type }})</span>
                  </div>
                </div>
              </div>

              <!-- Emails -->
              <div v-if="store.selectedCompany.emails?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Email Addresses</p>
                <div class="space-y-1">
                  <div
                    v-for="(e, i) in store.selectedCompany.emails"
                    :key="i"
                    class="flex items-center gap-2 text-xs truncate"
                  >
                    <Mail class="w-3.5 h-3.5 text-orange-400 flex-shrink-0" />
                    <a :href="`mailto:${e.email_address ?? e.address}`" class="text-orange-500 hover:underline truncate">
                      {{ e.email_address ?? e.address }}
                    </a>
                    <span v-if="e.is_professional" class="text-[10px] text-green-500 flex-shrink-0">Pro</span>
                  </div>
                </div>
              </div>

              <!-- Website -->
              <DetailRow icon="Link" label="Website">
                <a
                  v-if="store.selectedCompany.websites?.[0]?.url"
                  :href="store.selectedCompany.websites[0].url"
                  target="_blank"
                  class="text-orange-500 hover:underline truncate block"
                >{{ store.selectedCompany.websites[0].url.replace(/^https?:\/\//, '') }}</a>
                <span v-else>—</span>
              </DetailRow>

              <!-- Social Networks -->
              <div v-if="store.selectedCompany.social_networks?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Social Networks</p>
                <div class="space-y-1">
                  <div
                    v-for="(sn, i) in store.selectedCompany.social_networks"
                    :key="i"
                    class="flex items-center gap-2 text-xs"
                  >
                    <Share2 class="w-3.5 h-3.5 text-orange-400 flex-shrink-0" />
                    <span class="font-medium text-gray-600 capitalize">{{ sn.platform ?? sn.social_network_type ?? '' }}</span>
                    <a
                      v-if="sn.profile_url"
                      :href="sn.profile_url"
                      target="_blank"
                      class="text-orange-500 hover:underline truncate"
                    >{{ sn.account_value }}</a>
                    <span v-else class="text-gray-500 truncate">{{ sn.account_value }}</span>
                  </div>
                </div>
              </div>

              <!-- Trade Shows -->
              <div v-if="store.selectedCompany.trade_shows?.length">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Trade Shows</p>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="(ts, i) in store.selectedCompany.trade_shows"
                    :key="i"
                    class="text-[10px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 font-medium"
                  >{{ ts }}</span>
                </div>
              </div>

            </div>

            <!-- Export selected -->
            <div class="px-4 pb-4 border-t border-gray-100 pt-3 flex gap-2">
              <button
                @click="showExportModal = true"
                class="flex-1 flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600
                       text-white text-sm font-semibold py-2 rounded-lg transition-colors"
              >
                <Download class="w-4 h-4" />
                Export
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- ── Export Modal ──────────────────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="showExportModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
        @click.self="showExportModal = false"
      >
        <div class="bg-white rounded-2xl shadow-2xl w-80 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-gray-800 text-base">Export Companies</h3>
            <button @click="showExportModal = false" class="text-gray-400 hover:text-gray-600">
              <X class="w-5 h-5" />
            </button>
          </div>

          <p class="text-xs text-gray-500 mb-5">
            Export the current filtered result
            <span class="font-semibold text-gray-700">({{ store.pagination.total }} companies)</span>
            in your preferred format.
          </p>

          <div class="space-y-3">
            <button
              @click="doExport('csv')"
              class="w-full flex items-center gap-3 border-2 border-gray-200 hover:border-orange-400
                     rounded-xl px-4 py-3 transition-colors group"
            >
              <div class="w-9 h-9 rounded-lg bg-green-100 text-green-600 flex items-center justify-center group-hover:bg-green-200 transition-colors">
                <FileText class="w-5 h-5" />
              </div>
              <div class="text-left">
                <p class="font-semibold text-sm text-gray-800">CSV File</p>
                <p class="text-xs text-gray-400">Comma-separated, works everywhere</p>
              </div>
            </button>

            <button
              @click="doExport('excel')"
              class="w-full flex items-center gap-3 border-2 border-gray-200 hover:border-orange-400
                     rounded-xl px-4 py-3 transition-colors group"
            >
              <div class="w-9 h-9 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                <Table2 class="w-5 h-5" />
              </div>
              <div class="text-left">
                <p class="font-semibold text-sm text-gray-800">Excel File</p>
                <p class="text-xs text-gray-400">Opens directly in Microsoft Excel</p>
              </div>
            </button>
          </div>

          <button
            @click="showExportModal = false"
            class="mt-4 w-full text-center text-xs text-gray-400 hover:text-gray-600"
          >Cancel</button>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import {
  Search, RotateCcw, Building2, Download,
  ExternalLink, Phone, Mail, Share2, FileText, Table2, X,
} from '@lucide/vue'
import { useCompaniesStore } from '@/stores/companies'
import FilterGroup    from '@/components/companies/FilterGroup.vue'
import FilterCheckbox from '@/components/companies/FilterCheckbox.vue'
import DetailRow      from '@/components/companies/DetailRow.vue'
import SortableHeader from '@/components/companies/SortableHeader.vue'

const store = useCompaniesStore()

const showExportModal = ref(false)
const detailLoading   = ref(false)

const years = [2026, 2025, 2024, 2023, 2022]

// Helper: resolve contact display name from list or detail shape
function contactName(company) {
  const c = company.contacts?.[0]
  if (!c) return '—'
  if (c.first_name || c.last_name) return `${c.first_name ?? ''} ${c.last_name ?? ''}`.trim()
  return c.name ?? '—'
}

// Description from nested array or string
const description = computed(() => {
  const d = store.selectedCompany?.descriptions?.[0]
  if (!d) return null
  return d.description ?? d.text ?? d
})

// Pagination pages
const visiblePages = computed(() => {
  const { page, totalPages } = store.pagination
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
  const pages = []
  if (page > 3) { pages.push(1); if (page > 4) pages.push('...') }
  for (let p = Math.max(1, page - 1); p <= Math.min(totalPages, page + 1); p++) pages.push(p)
  if (page < totalPages - 2) { if (page < totalPages - 3) pages.push('...'); pages.push(totalPages) }
  return pages
})

function doExport(format) {
  if (format === 'csv')   store.exportCsv()
  if (format === 'excel') store.exportExcel()
  showExportModal.value = false
}
</script>
