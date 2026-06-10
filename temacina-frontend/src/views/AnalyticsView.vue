<template>
  <div class="p-6 space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-bold text-gray-800">Analytics</h1>
        <p class="text-xs text-gray-400 mt-0.5">Overview of all indexed data</p>
      </div>
      <button @click="store.loadAll()"
        class="flex items-center gap-2 text-sm text-gray-500 hover:text-orange-500 transition-colors">
        <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': store.loading.overview }" />
        Refresh
      </button>
    </div>

    <!-- Error -->
    <div v-if="store.error" class="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
      {{ store.error }}
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      <KpiCard label="Companies"   :value="store.overview?.total_companies"   :icon="Building2"   :loading="store.loading.overview" />
      <KpiCard label="Trade Shows" :value="store.overview?.total_trade_shows" :icon="CalendarDays" :loading="store.loading.overview" iconBg="#EFF6FF" iconColor="#3B82F6" />
      <KpiCard label="Documents"   :value="store.overview?.total_documents"   :icon="FileText"    :loading="store.loading.overview" iconBg="#F0FDF4" iconColor="#22C55E" />
      <KpiCard label="Emails"      :value="store.overview?.total_emails"      :icon="Mail"        :loading="store.loading.overview" iconBg="#FDF4FF" iconColor="#A855F7" />
      <KpiCard label="Phones"      :value="store.overview?.total_phones"      :icon="Phone"       :loading="store.loading.overview" iconBg="#FFFBEB" iconColor="#F59E0B" />
    </div>

    <!-- Charts row 1 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <ChartCard title="Companies by Sector" subtitle="Distribution across industry sectors"
        :loading="store.loading.charts" :empty="!store.topSectors.length">
        <HorizontalBarChart :data="store.topSectors" color="#F4652A" />
      </ChartCard>
      <ChartCard title="Companies by Country" subtitle="Geographic distribution"
        :loading="store.loading.charts" :empty="!store.topCountries.length">
        <HorizontalBarChart :data="store.topCountries" color="#3B82F6" />
      </ChartCard>
    </div>

    <!-- Charts row 2 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div class="lg:col-span-2">
        <ChartCard title="Companies by Year" subtitle="Exhibition year breakdown"
          :loading="store.loading.charts" :empty="!store.tradeShowSeries.length">
          <TradeShowBarChart :data="store.tradeShowSeries" />
        </ChartCard>
      </div>
      <ChartCard title="Sector Share" subtitle="Proportion of companies per sector"
        :loading="store.loading.charts" :empty="!store.topSectors.length">
        <DonutChart :data="store.topSectors" centerLabel="companies" />
      </ChartCard>
    </div>

    <!-- Trade Show drill-down -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-sm font-bold text-gray-800">Trade Show Deep-Dive</h3>
          <p class="text-xs text-gray-400 mt-0.5">Select a trade show to see detailed stats</p>
        </div>
        <select v-model="selectedId" @change="store.loadTradeShowStats(selectedId)"
          class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white max-w-xs">
          <option :value="null">— Select a trade show —</option>
          <option v-for="ts in store.tradeShows" :key="ts.id" :value="ts.id">
            {{ ts.name }} ({{ ts.exhibition_year }})
          </option>
        </select>
      </div>

      <div v-if="store.loading.showStats" class="flex justify-center py-10">
        <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
      <TradeShowStatsPanel
        v-else-if="store.selectedShowStats"
        :stats="store.selectedShowStats"
        @close="selectedId = null; store.loadTradeShowStats(null)"
      />
      <div v-else class="flex flex-col items-center justify-center py-10 text-gray-400">
        <CalendarDays class="w-10 h-10 mb-2 opacity-20" />
        <p class="text-sm">Choose a trade show above to view its analytics</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Building2, CalendarDays, FileText, Mail, Phone, RefreshCw } from '@lucide/vue'
import { useAnalyticsStore } from '@/stores/analytics'
import KpiCard             from '@/components/analytics/KpiCard.vue'
import ChartCard           from '@/components/analytics/ChartCard.vue'
import HorizontalBarChart  from '@/components/analytics/HorizontalBarChart.vue'
import TradeShowBarChart   from '@/components/analytics/TradeShowBarChart.vue'
import DonutChart          from '@/components/analytics/DonutChart.vue'
import TradeShowStatsPanel from '@/components/analytics/TradeShowStatsPanel.vue'

const store      = useAnalyticsStore()
const selectedId = ref(null)

onMounted(() => store.loadAll())
</script>
