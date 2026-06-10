<template>
  <div class="ts-panel">

    <!-- header -->
    <div class="ts-panel-header">
      <div>
        <div class="ts-eyebrow">Analyse par édition</div>
        <h3 class="ts-panel-title">{{ stats.name }} — {{ stats.year }}</h3>
        <p class="ts-meta">{{ stats.city }}, {{ stats.country }}</p>
      </div>
      <button class="ts-close" @click="$emit('close')">
        <X class="w-4 h-4" />
      </button>
    </div>

    <!-- mini KPIs -->
    <div class="ts-kpis">
      <div class="ts-kpi">
        <span class="ts-kpi-val">{{ stats.company_count?.toLocaleString('fr-DZ') ?? '—' }}</span>
        <span class="ts-kpi-label">Entreprises</span>
      </div>
      <div class="ts-kpi-divider" />
      <div class="ts-kpi">
        <span class="ts-kpi-val">{{ stats.document_count?.toLocaleString('fr-DZ') ?? '—' }}</span>
        <span class="ts-kpi-label">Documents</span>
      </div>
    </div>

    <!-- charts row -->
    <div class="ts-charts">
      <!-- docs by type -->
      <ChartCard
        title="Documents par type"
        :loading="false"
        :empty="!stats.docs_by_type?.length"
        :height="220"
      >
        <DonutChart
          :data="normalisedDocTypes"
          center-label="docs"
        />
      </ChartCard>

      <!-- ingestion status -->
      <ChartCard
        title="Statut d'ingestion"
        :loading="false"
        :empty="!stats.ingestion_status?.length"
        :height="220"
      >
        <DonutChart
          :data="normalisedIngestion"
          center-label="docs"
        />
      </ChartCard>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { X } from 'lucide-vue-next'
import ChartCard from './ChartCard.vue'
import DonutChart from './DonutChart.vue'

const props = defineProps({
  stats: { type: Object, required: true },
})

defineEmits(['close'])

const INGESTION_LABELS = {
  pending:    'En attente',
  processing: 'En cours',
  completed:  'Terminé',
  failed:     'Échec',
}

const normalisedDocTypes = computed(() =>
  (props.stats.docs_by_type ?? []).map(d => ({
    label: d.document_type__label ?? d.label ?? '—',
    count: d.count ?? 0,
  }))
)

const normalisedIngestion = computed(() =>
  (props.stats.ingestion_status ?? []).map(d => ({
    label: INGESTION_LABELS[d.ingestion_status] ?? d.ingestion_status ?? '—',
    count: d.count ?? 0,
  }))
)
</script>

<style scoped>
.ts-panel {
  background: #fff;
  border: 0.5px solid #E5E7EB;
  border-radius: 14px;
  overflow: hidden;
}

.ts-panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 0.5px solid #F3F4F6;
}

.ts-eyebrow {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #F4652A;
  margin-bottom: 4px;
}

.ts-panel-title {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 2px;
}

.ts-meta {
  font-size: 12px;
  color: #9CA3AF;
  margin: 0;
}

.ts-close {
  padding: 6px;
  border: none;
  background: #F3F4F6;
  border-radius: 8px;
  cursor: pointer;
  color: #6B7280;
  display: flex;
  align-items: center;
}

.ts-close:hover { background: #E5E7EB; }

.ts-kpis {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 14px 20px;
  border-bottom: 0.5px solid #F3F4F6;
}

.ts-kpi {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ts-kpi-val {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  font-variant-numeric: tabular-nums;
}

.ts-kpi-label {
  font-size: 11px;
  color: #9CA3AF;
  font-weight: 500;
}

.ts-kpi-divider {
  width: 1px;
  height: 32px;
  background: #E5E7EB;
  margin: 0 24px;
}

.ts-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}

.ts-charts > :first-child {
  border-right: 0.5px solid #F3F4F6;
  border-radius: 0;
  border: none;
  border-right: 0.5px solid #F3F4F6;
}

.ts-charts > :last-child {
  border-radius: 0;
  border: none;
}
</style>
