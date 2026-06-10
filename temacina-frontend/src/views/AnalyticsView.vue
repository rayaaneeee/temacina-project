<template>
  <div class="analytics-page">

    <!-- ── Page header ──────────────────────────────────────────── -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Analytiques</h1>
        <p class="page-sub">Vue d'ensemble de la base de données Temacina</p>
      </div>

      <!-- Trade show drill-down selector -->
      <div class="show-selector-wrap">
        <label class="selector-label">Analyser une édition</label>
        <select
          v-model="selectedShowId"
          class="show-selector"
          @change="onShowSelect"
        >
          <option value="">Toutes les éditions</option>
          <option
            v-for="show in tradeShows"
            :key="show.id"
            :value="show.id"
          >
            {{ show.name }} {{ show.exhibition_year }}
          </option>
        </select>
      </div>
    </div>

    <!-- ── Global error ─────────────────────────────────────────── -->
    <div v-if="error" class="error-bar">
      <AlertCircle class="w-4 h-4 flex-shrink-0" />
      {{ error }}
    </div>

    <!-- ── KPI row ──────────────────────────────────────────────── -->
    <div class="kpi-grid">
      <KpiCard
        label="Entreprises"
        :value="overview?.total_companies ?? null"
        sub="dans la base"
        :icon="Building2"
        icon-bg="#FFF0E8"
        icon-color="#F4652A"
        :loading="loading.overview"
      />
      <KpiCard
        label="Contacts"
        :value="overview?.total_contacts ?? null"
        sub="personnes référencées"
        :icon="Users"
        icon-bg="#EFF6FF"
        icon-color="#3B82F6"
        :loading="loading.overview"
      />
      <KpiCard
        label="E-mails"
        :value="overview?.total_emails ?? null"
        sub="adresses collectées"
        :icon="Mail"
        icon-bg="#F0FDF4"
        icon-color="#22C55E"
        :loading="loading.overview"
      />
      <KpiCard
        label="Téléphones"
        :value="overview?.total_phones ?? null"
        sub="numéros collectés"
        :icon="Phone"
        icon-bg="#FDF4FF"
        icon-color="#A855F7"
        :loading="loading.overview"
      />
      <KpiCard
        label="Sites web"
        :value="overview?.total_websites ?? null"
        sub="URLs référencées"
        :icon="Globe"
        icon-bg="#FFFBEB"
        icon-color="#F59E0B"
        :loading="loading.overview"
      />
      <KpiCard
        label="Éditions"
        :value="overview?.total_trade_shows ?? null"
        sub="salons couverts"
        :icon="CalendarDays"
        icon-bg="#FFF1F2"
        icon-color="#F43F5E"
        :loading="loading.overview"
      />
    </div>

    <!-- ── Trade show drill-down panel ─────────────────────────── -->
    <Transition name="fade-slide">
      <TradeShowStatsPanel
        v-if="selectedShowStats && !loading.showStats"
        :stats="selectedShowStats"
        @close="clearShowSelection"
      />
    </Transition>

    <!-- Loading placeholder for show stats -->
    <div v-if="loading.showStats" class="ts-loading-placeholder">
      <div class="spinner" />
      <span>Chargement de l'édition…</span>
    </div>

    <!-- ── Main charts grid ─────────────────────────────────────── -->
    <div class="charts-grid">

      <!-- Enterprises per trade show (full width) -->
      <div class="col-span-2">
        <ChartCard
          title="Entreprises par édition de salon"
          subtitle="Nombre d'entreprises distinctes référencées par édition"
          :loading="loading.charts"
          :empty="!tradeShowSeries.length"
          :height="260"
        >
          <TradeShowBarChart :data="tradeShowSeries" />
        </ChartCard>
      </div>

      <!-- By sector -->
      <ChartCard
        title="Répartition par secteur"
        :subtitle="`Top ${topSectors.length} secteurs`"
        :loading="loading.charts"
        :empty="!topSectors.length"
        :height="topSectors.length * 36 + 16"
      >
        <HorizontalBarChart
          :data="topSectors"
          :max-items="10"
        />
      </ChartCard>

      <!-- By country -->
      <ChartCard
        title="Répartition par pays"
        :subtitle="`Top ${topCountries.length} pays`"
        :loading="loading.charts"
        :empty="!topCountries.length"
        :height="topCountries.length * 36 + 16"
      >
        <HorizontalBarChart
          :data="topCountries"
          :max-items="10"
          color="#3B82F6"
        />
      </ChartCard>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import {
  Building2, Users, Mail, Phone, Globe,
  CalendarDays, AlertCircle,
} from 'lucide-vue-next'
import { useAnalyticsStore } from '@/stores/analytics'
import KpiCard from '@/components/analytics/KpiCard.vue'
import ChartCard from '@/components/analytics/ChartCard.vue'
import HorizontalBarChart from '@/components/analytics/HorizontalBarChart.vue'
import TradeShowBarChart from '@/components/analytics/TradeShowBarChart.vue'
import TradeShowStatsPanel from '@/components/analytics/TradeShowStatsPanel.vue'
import DonutChart from '@/components/analytics/DonutChart.vue'

const store = useAnalyticsStore()
const {
  overview, tradeShows, tradeShowSeries,
  topSectors, topCountries,
  selectedShowStats, loading, error,
} = storeToRefs(store)

const selectedShowId = ref('')

onMounted(() => store.loadAll())

function onShowSelect() {
  if (selectedShowId.value) {
    store.loadTradeShowStats(selectedShowId.value)
  } else {
    clearShowSelection()
  }
}

function clearShowSelection() {
  selectedShowId.value = ''
  store.selectedShowStats = null
}
</script>

<style scoped>
.analytics-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Header ─────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 4px;
}

.page-sub {
  font-size: 13px;
  color: #9CA3AF;
  margin: 0;
}

.show-selector-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.selector-label {
  font-size: 11px;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.show-selector {
  padding: 8px 12px;
  border: 0.5px solid #D1D5DB;
  border-radius: 9px;
  font-size: 13px;
  color: #111827;
  background: #fff;
  cursor: pointer;
  min-width: 220px;
}

.show-selector:focus {
  outline: none;
  border-color: #F4652A;
  box-shadow: 0 0 0 3px rgba(244,101,42,0.12);
}

/* ── Error ──────────────────────────────────────────────── */
.error-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #FEF2F2;
  border: 0.5px solid #FECACA;
  border-radius: 10px;
  font-size: 13px;
  color: #DC2626;
}

/* ── KPI grid ───────────────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 14px;
}

/* ── Trade show loading placeholder ────────────────────── */
.ts-loading-placeholder {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #fff;
  border: 0.5px solid #E5E7EB;
  border-radius: 14px;
  font-size: 13px;
  color: #9CA3AF;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #F3F4F6;
  border-top-color: #F4652A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg) } }

/* ── Charts grid ────────────────────────────────────────── */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.col-span-2 {
  grid-column: 1 / -1;
}

@media (max-width: 900px) {
  .charts-grid { grid-template-columns: 1fr; }
  .col-span-2  { grid-column: auto; }
  .kpi-grid    { grid-template-columns: repeat(2, 1fr); }
}

/* ── Transitions ────────────────────────────────────────── */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
