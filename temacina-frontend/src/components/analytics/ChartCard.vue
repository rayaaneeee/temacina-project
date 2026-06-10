<template>
  <div class="chart-card">
    <div class="chart-card-header">
      <div>
        <h3 class="chart-title">{{ title }}</h3>
        <p v-if="subtitle" class="chart-subtitle">{{ subtitle }}</p>
      </div>
      <slot name="actions" />
    </div>

    <!-- loading -->
    <div v-if="loading" class="chart-loading">
      <div class="spinner" />
    </div>

    <!-- empty -->
    <div v-else-if="empty" class="chart-empty">
      <BarChart2 class="empty-icon" />
      <p>Aucune donnée disponible</p>
    </div>

    <!-- content -->
    <div v-else class="chart-body" :style="{ height: height + 'px' }">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { BarChart2 } from '@lucide/vue'

defineProps({
  title:    { type: String,  required: true },
  subtitle: { type: String,  default: '' },
  loading:  { type: Boolean, default: false },
  empty:    { type: Boolean, default: false },
  height:   { type: Number,  default: 280 },
})
</script>

<style scoped>
.chart-card {
  background: #fff;
  border: 0.5px solid #E5E7EB;
  border-radius: 14px;
  overflow: hidden;
}

.chart-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 0.5px solid #F3F4F6;
}

.chart-title {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 2px;
}

.chart-subtitle {
  font-size: 11px;
  color: #9CA3AF;
  margin: 0;
}

.chart-body {
  padding: 16px 20px 20px;
  position: relative;
}

.chart-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #F3F4F6;
  border-top-color: #F4652A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg) } }

.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #D1D5DB;
  gap: 10px;
  font-size: 13px;
}

.empty-icon {
  width: 32px;
  height: 32px;
  opacity: 0.5;
}
</style>
