<template>
  <div class="p-6 space-y-6">

    <!-- KPI Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="kpi in kpiCards" :key="kpi.label"
           class="bg-white rounded-xl border border-gray-200 shadow-card p-5 flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
             :class="kpi.bg">
          <component :is="kpi.icon" class="w-6 h-6" :class="kpi.color" />
        </div>
        <div>
          <div class="text-2xl font-black text-gray-900">
            {{ kpi.value.toLocaleString('en-US') }}
          </div>
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            {{ kpi.label }}
          </div>
        </div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

      <!-- Companies by year -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-card p-5">
        <h3 class="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
          <BarChart3 class="w-4 h-4 text-orange-500" />
          Companies by year
        </h3>
        <div class="space-y-3">
          <div v-for="item in store.kpis.companies_by_year"
               :key="item.documents__trade_show__exhibition_year"
               class="flex items-center gap-3">
            <span class="text-xs font-semibold text-gray-500 w-10">
              {{ item.documents__trade_show__exhibition_year }}
            </span>
            <div class="flex-1 bg-gray-100 rounded-full h-2.5 overflow-hidden">
              <div class="h-full bg-orange-500 rounded-full transition-all duration-500"
                   :style="{ width: `${(item.count / maxYearCount) * 100}%` }">
              </div>
            </div>
            <span class="text-xs font-bold text-gray-700 w-10 text-right">
              {{ item.count }}
            </span>
          </div>
        </div>
      </div>

      <!-- Companies by sector -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-card p-5">
        <h3 class="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
          <PieChart class="w-4 h-4 text-orange-500" />
          Companies by sector
        </h3>
        <div class="space-y-3">
          <div v-for="item in store.kpis.companies_by_sector"
               :key="item.sectors__title"
               class="flex items-center gap-3">
            <span class="text-xs font-semibold text-gray-500 w-24 truncate">
              {{ item.sectors__title }}
            </span>
            <div class="flex-1 bg-gray-100 rounded-full h-2.5 overflow-hidden">
              <div class="h-full rounded-full transition-all duration-500"
                   :class="sectorColors[item.sectors__title] || 'bg-gray-400'"
                   :style="{ width: `${(item.count / maxSectorCount) * 100}%` }">
              </div>
            </div>
            <span class="text-xs font-bold text-gray-700 w-10 text-right">
              {{ item.count }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Companies by country + recent companies -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

      <!-- Top countries -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-card p-5">
        <h3 class="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
          <Globe class="w-4 h-4 text-orange-500" />
          Top countries
        </h3>
        <div class="space-y-2">
          <div v-for="(item, idx) in store.kpis.companies_by_country"
               :key="item.addresses__country"
               class="flex items-center justify-between py-1.5 border-b border-gray-50">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-orange-100 text-orange-600
                           text-xs font-black flex items-center justify-center">
                {{ idx + 1 }}
              </span>
              <span class="text-sm text-gray-700">{{ item.addresses__country }}</span>
            </div>
            <span class="text-sm font-bold text-gray-900">
              {{ item.count.toLocaleString('en-US') }}
            </span>
          </div>
        </div>
      </div>

      <!-- Recent companies -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-card p-5">
        <h3 class="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
          <Building2 class="w-4 h-4 text-orange-500" />
          Recent companies
        </h3>
        <div class="space-y-2">
          <div v-for="company in recentCompanies" :key="company.id"
               class="flex items-center justify-between py-1.5 border-b border-gray-50
                      cursor-pointer hover:bg-orange-50 rounded-lg px-2 transition"
               @click="router.push({ name: 'companies' })">
            <div>
              <div class="text-sm font-semibold text-gray-800">{{ company.legal_name }}</div>
              <div class="text-xs text-gray-400">{{ company.addresses[0]?.city }}</div>
            </div>
            <span class="badge-sector text-[10px]">{{ company.sectors[0] }}</span>
          </div>
        </div>
        <button @click="router.push({ name: 'companies' })"
          class="mt-3 w-full text-center text-xs text-orange-500 hover:text-orange-600
                 font-semibold py-2 border border-orange-200 rounded-lg hover:bg-orange-50 transition">
          View all companies →
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCompaniesStore } from '@/stores/companies'
import { Building2, FileText, Mail, BarChart3, PieChart, Globe } from '@lucide/vue'

const store  = useCompaniesStore()
const router = useRouter()

const kpiCards = computed(() => [
  { label: 'Companies',   value: store.kpis.total_companies,   icon: Building2, bg: 'bg-orange-100', color: 'text-orange-500' },
  { label: 'Trade Shows', value: store.kpis.total_trade_shows, icon: BarChart3, bg: 'bg-blue-100',   color: 'text-blue-500'   },
  { label: 'Documents',   value: store.kpis.total_documents,   icon: FileText,  bg: 'bg-green-100',  color: 'text-green-500'  },
  { label: 'Emails',      value: store.kpis.total_emails,      icon: Mail,      bg: 'bg-purple-100', color: 'text-purple-500' },
])

const maxYearCount    = computed(() => Math.max(...store.kpis.companies_by_year.map(i => i.count)))
const maxSectorCount  = computed(() => Math.max(...store.kpis.companies_by_sector.map(i => i.count)))
const recentCompanies = computed(() => store.allCompanies.slice(0, 5))

const sectorColors = {
  'Industrie':    'bg-orange-500',
  'Agriculture':  'bg-green-500',
  'Construction': 'bg-blue-500',
  'ITech':        'bg-purple-500',
  'Others':       'bg-gray-400',
}
</script>