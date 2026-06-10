<template>
  <div class="kpi-card">
    <div class="kpi-icon-wrap" :style="{ background: iconBg }">
      <component :is="icon" class="kpi-icon" :style="{ color: iconColor }" />
    </div>
    <div class="kpi-body">
      <p class="kpi-label">{{ label }}</p>
      <p class="kpi-value">
        <span v-if="loading" class="kpi-skeleton" />
        <template v-else>{{ formattedValue }}</template>
      </p>
      <p v-if="sub" class="kpi-sub">{{ sub }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:      { type: String,  required: true },
  value:      { type: Number,  default: null },
  sub:        { type: String,  default: '' },
  icon:       { type: Object,  required: true },   // lucide component
  iconBg:     { type: String,  default: '#FFF0E8' },
  iconColor:  { type: String,  default: '#F4652A' },
  loading:    { type: Boolean, default: false },
})

const formattedValue = computed(() =>
  props.value == null ? '—'
  : props.value >= 1_000_000 ? `${(props.value / 1_000_000).toFixed(1)}M`
  : props.value >= 1_000     ? `${(props.value / 1_000).toFixed(1)}k`
  : props.value.toLocaleString('fr-DZ')
)
</script>

<style scoped>
.kpi-card {
  background: #fff;
  border: 0.5px solid #E5E7EB;
  border-radius: 14px;
  padding: 18px 20px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.kpi-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon {
  width: 18px;
  height: 18px;
}

.kpi-body {
  min-width: 0;
}

.kpi-label {
  font-size: 11px;
  font-weight: 600;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 4px;
}

.kpi-value {
  font-size: 26px;
  font-weight: 700;
  color: #111827;
  line-height: 1;
  margin: 0 0 4px;
  font-variant-numeric: tabular-nums;
}

.kpi-sub {
  font-size: 11px;
  color: #9CA3AF;
  margin: 0;
}

.kpi-skeleton {
  display: inline-block;
  width: 72px;
  height: 26px;
  background: #F3F4F6;
  border-radius: 6px;
  animation: pulse 1.4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1 }
  50% { opacity: 0.4 }
}
</style>
