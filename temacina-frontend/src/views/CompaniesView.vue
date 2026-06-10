<template>
  <div class="flex h-full overflow-hidden">

    <!-- ── Column 1 · Filters ──────────────────────────────────── -->
    <aside class="w-56 flex-shrink-0 border-r border-gray-200 bg-white overflow-y-auto flex flex-col">

      <!-- Filter header -->
      <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Filters</span>
        <button
          v-if="store.activeFiltersCount > 0"
          @click="store.resetFilters()"
          class="text-xs text-orange-500 hover:text-orange-600 font-medium"
        >Reset</button>
      </div>

      <div class="flex-1 px-3 py-3 space-y-5">

        <!-- Sector of Activity -->
        <FilterGroup label="1 Sector of Activity" :badge="store.filters.sectors.length">
          <FilterCheckbox
            v-for="s in sectors"
            :key="s"
            :label="s"
            :checked="store.filters.sectors.includes(s)"
            @toggle="store.toggleFilterItem('sectors', s)"
          />
        </FilterGroup>

        <!-- Exhibition Year -->
        <FilterGroup label="2 Exhibition Year" :badge="store.filters.years.length">
          <FilterCheckbox
            v-for="y in years"
            :key="y"
            :label="String(y)"
            :checked="store.filters.years.includes(y)"
            @toggle="store.toggleFilterItem('years', y)"
          />
        </FilterGroup>

        <!-- Trade Show Name -->
        <FilterGroup label="3 Trade Show Name" :badge="store.filters.trade_shows.length">
          <FilterCheckbox
            v-for="ts in tradeShowNames"
            :key="ts"
            :label="ts"
            :checked="store.filters.trade_shows.includes(ts)"
            @toggle="store.toggleFilterItem('trade_shows', ts)"
          />
        </FilterGroup>

        <!-- Support Type -->
        <FilterGroup label="4 Support Type" :badge="store.filters.supports.length">
          <FilterCheckbox
            v-for="sp in supports"
            :key="sp"
            :label="sp"
            :checked="store.filters.supports.includes(sp)"
            @toggle="store.toggleFilterItem('supports', sp)"
          />
        </FilterGroup>

      </div>

      <!-- Search + Buttons -->
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

      <!-- Top bar: search + stats + export -->
      <div class="bg-white border-b border-gray-200 px-5 py-3 flex items-center gap-4 flex-shrink-0">
        <!-- Search input -->
        <div class="relative flex-1 max-w-sm">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="store.filters.search"
            type="text"
            placeholder="Search companies, sectors, countries..."
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg
                   focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
          />
        </div>

        <!-- Stats pills -->
        <div class="flex items-center gap-4 text-sm">
          <div class="flex items-center gap-1.5">
            <Building2 class="w-4 h-4 text-orange-500" />
            <span class="font-bold text-gray-800">{{ store.pagination.total.toLocaleString() }}</span>
            <span class="text-gray-500">companies</span>
          </div>
          <div class="flex items-center gap-1.5">
            <Globe class="w-4 h-4 text-orange-500" />
            <span class="font-bold text-gray-800">28</span>
            <span class="text-gray-500">countries</span>
          </div>
          <div class="flex items-center gap-1.5">
            <Users class="w-4 h-4 text-orange-500" />
            <span class="font-bold text-gray-800">12,840</span>
            <span class="text-gray-500">contacts</span>
          </div>
        </div>

        <div class="ml-auto flex items-center gap-2">
          <!-- View toggle -->
          <div class="flex border border-gray-200 rounded-lg overflow-hidden">
            <button
              @click="viewMode = 'table'"
              :class="viewMode === 'table'
                ? 'bg-orange-500 text-white'
                : 'bg-white text-gray-500 hover:bg-gray-50'"
              class="px-2.5 py-1.5 transition-colors"
            ><List class="w-4 h-4" /></button>
            <button
              @click="viewMode = 'grid'"
              :class="viewMode === 'grid'
                ? 'bg-orange-500 text-white'
                : 'bg-white text-gray-500 hover:bg-gray-50'"
              class="px-2.5 py-1.5 transition-colors"
            ><LayoutGrid class="w-4 h-4" /></button>
          </div>

          <!-- Export -->
          <button
            @click="store.exportCsv()"
            class="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white
                   text-sm font-semibold px-3 py-1.5 rounded-lg transition-colors"
          >
            <Download class="w-4 h-4" />
            Export (CSV)
          </button>
        </div>
      </div>

      <!-- Filter summary bar -->
      <div
        v-if="store.filterSummary.length"
        class="bg-orange-50 border-b border-orange-100 px-5 py-2 text-xs text-gray-600 flex flex-wrap gap-x-3 gap-y-1"
      >
        <span
          v-for="part in store.filterSummary"
          :key="part.label"
        >
          <span class="font-semibold text-gray-700">{{ part.label }}:</span>
          {{ part.value }}
        </span>
      </div>

      <!-- Main content: table + detail panel -->
      <div class="flex flex-1 overflow-hidden">

        <!-- ── Column 2 · Company Table ───────────────────── -->
        <div class="flex-1 overflow-y-auto bg-gray-50">

          <!-- Loading -->
          <div v-if="store.loading" class="flex items-center justify-center h-32">
            <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          </div>

          <template v-else>
            <!-- Table header -->
            <div class="sticky top-0 bg-white border-b border-gray-200 z-10">
              <div class="flex items-center px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                <span class="w-8">#</span>
                <span class="flex-1">Company Name</span>
                <span class="w-32 hidden md:block">Contact Person</span>
                <span class="w-28 hidden lg:block">City</span>
                <span class="w-24 hidden lg:block">Country</span>
                <span class="w-32 hidden xl:block">Phone</span>
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
              <!-- Company -->
              <div class="flex-1 min-w-0 flex items-center gap-2">
                <div class="w-7 h-7 rounded-md bg-orange-100 text-orange-600 font-bold text-xs
                            flex items-center justify-center flex-shrink-0">
                  {{ company.legal_name.charAt(0) }}
                </div>
                <span class="font-medium text-gray-800 truncate">{{ company.legal_name }}</span>
                <span
                  v-for="s in company.sectors.slice(0,1)"
                  :key="s"
                  class="hidden sm:inline-flex text-[10px] px-1.5 py-0.5 rounded-full bg-orange-100 text-orange-600 font-medium"
                >{{ s }}</span>
              </div>
              <!-- Contact -->
              <span class="w-32 hidden md:block text-gray-600 truncate">
                {{ company.contacts[0]?.name ?? '—' }}
              </span>
              <!-- City -->
              <span class="w-28 hidden lg:block text-gray-500 truncate">
                {{ company.addresses[0]?.city ?? '—' }}
              </span>
              <!-- Country -->
              <span class="w-24 hidden lg:block text-gray-500 truncate">
                {{ company.addresses[0]?.country ?? '—' }}
              </span>
              <!-- Phone -->
              <span class="w-32 hidden xl:block text-gray-500 text-xs truncate">
                {{ company.phones[0]?.number ?? '—' }}
              </span>
              <!-- Action -->
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
                  <option v-for="n in [5,10,25,50]" :key="n" :value="n">{{ n }} / page</option>
                </select>
              </div>
            </div>
          </template>
        </div>

        <!-- ── Column 3 · Company Detail Panel ──────────── -->
        <div class="w-72 flex-shrink-0 border-l border-gray-200 bg-white overflow-y-auto flex flex-col">

          <!-- No selection placeholder -->
          <div v-if="!store.selectedCompany"
            class="flex-1 flex flex-col items-center justify-center text-gray-400 px-6 text-center">
            <Building2 class="w-10 h-10 mb-3 opacity-25" />
            <p class="text-sm font-medium">Select a company</p>
            <p class="text-xs mt-1 text-gray-300">Click any row to see company details</p>
          </div>

          <!-- Selected company detail -->
          <template v-else>
            <!-- Header -->
            <div class="px-4 py-3 border-b border-gray-100 flex items-start gap-3">
              <div class="w-10 h-10 rounded-xl bg-orange-100 text-orange-600 font-bold text-base
                          flex items-center justify-center flex-shrink-0">
                {{ store.selectedCompany.legal_name.charAt(0) }}
              </div>
              <div class="min-w-0">
                <h3 class="font-bold text-gray-800 text-sm leading-tight">
                  {{ store.selectedCompany.legal_name }}
                </h3>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span
                    v-for="s in store.selectedCompany.sectors"
                    :key="s"
                    class="text-[10px] px-1.5 py-0.5 rounded-full bg-orange-100 text-orange-600 font-medium"
                  >{{ s }}</span>
                </div>
              </div>
              <!-- Open profile link -->
              <RouterLink
                :to="{ name: 'company-profile', params: { id: store.selectedCompany.id } }"
                class="ml-auto flex-shrink-0 text-orange-500 hover:text-orange-700"
                title="Open full profile"
              >
                <ExternalLink class="w-4 h-4" />
              </RouterLink>
            </div>

            <!-- Details -->
            <div class="px-4 py-3 space-y-4 text-sm flex-1">

              <!-- Contact Name -->
              <DetailRow icon="User" label="Contact Name">
                {{ store.selectedCompany.contacts[0]?.name ?? '—' }}
              </DetailRow>

              <!-- Job Function -->
              <DetailRow icon="Briefcase" label="Job Function">
                {{ store.selectedCompany.contacts[0]?.role ?? '—' }}
              </DetailRow>

              <!-- Address -->
              <DetailRow icon="MapPin" label="Street Address">
                {{ store.selectedCompany.addresses[0]?.street ?? '—' }}
              </DetailRow>

              <!-- Country & City -->
              <DetailRow icon="Globe" label="Country & City">
                {{ store.selectedCompany.addresses[0]?.country ?? '' }}
                <span v-if="store.selectedCompany.addresses[0]?.city">, {{ store.selectedCompany.addresses[0].city }}</span>
              </DetailRow>

              <!-- Postal code -->
              <DetailRow icon="Hash" label="Postal Code">
                {{ store.selectedCompany.addresses[0]?.postal_code ?? '—' }}
              </DetailRow>

              <!-- Phone -->
              <DetailRow icon="Phone" label="Phone Number">
                {{ store.selectedCompany.phones[0]?.number ?? '—' }}
              </DetailRow>

              <!-- Email -->
              <DetailRow icon="Mail" label="Email Address">
                <a
                  v-if="store.selectedCompany.emails[0]?.address"
                  :href="`mailto:${store.selectedCompany.emails[0].address}`"
                  class="text-orange-500 hover:underline truncate block"
                >{{ store.selectedCompany.emails[0].address }}</a>
                <span v-else>—</span>
              </DetailRow>

              <!-- Website -->
              <DetailRow icon="Link" label="Official Website">
                <a
                  v-if="store.selectedCompany.websites[0]?.url"
                  :href="store.selectedCompany.websites[0].url"
                  target="_blank"
                  class="text-orange-500 hover:underline truncate block"
                >{{ store.selectedCompany.websites[0].url.replace('https://', '') }}</a>
                <span v-else>—</span>
              </DetailRow>

            </div>

            <!-- Export selected company -->
            <div class="px-4 pb-4 border-t border-gray-100 pt-3">
              <button
                @click="store.exportCsv()"
                class="w-full flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600
                       text-white text-sm font-semibold py-2 rounded-lg transition-colors"
              >
                <Download class="w-4 h-4" />
                Export (CSV)
              </button>
            </div>
          </template>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import {
  Search, RotateCcw, Building2, Globe, Users, List, LayoutGrid,
  Download, ExternalLink, User, Briefcase, MapPin, Phone, Mail,
  Link, Hash,
} from 'lucide-vue-next'
import { useCompaniesStore } from '@/stores/companies'
import FilterGroup    from '@/components/companies/FilterGroup.vue'
import FilterCheckbox from '@/components/companies/FilterCheckbox.vue'
import DetailRow      from '@/components/companies/DetailRow.vue'

const store = useCompaniesStore()

const viewMode = ref('table')

// ── Static filter options ────────────────────────────────────────
const sectors      = ['Industrie', 'Agriculture', 'Construction', 'ITech', 'Services']
const years        = [2026, 2025, 2024, 2023, 2022]
const tradeShowNames = computed(() => store.tradeShows.map(ts => ts.name))
const supports     = ['Business Card', 'Catalogues', 'Directory', 'Magazine', 'Flyer']

// ── Pagination helper ────────────────────────────────────────────
const visiblePages = computed(() => {
  const { page, totalPages } = store.pagination
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
  const pages = []
  if (page > 3) { pages.push(1); if (page > 4) pages.push('...') }
  for (let p = Math.max(1, page - 1); p <= Math.min(totalPages, page + 1); p++) pages.push(p)
  if (page < totalPages - 2) { if (page < totalPages - 3) pages.push('...'); pages.push(totalPages) }
  return pages
})
</script>
