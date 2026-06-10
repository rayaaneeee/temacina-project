<template>
  <div class="hbar-wrap">
    <div
      v-for="(item, i) in normalised"
      :key="item.label"
      class="hbar-row"
    >
      <!-- Label -->
      <div class="hbar-label" :title="item.label">{{ item.label }}</div>

      <!-- Track + fill -->
      <div class="hbar-track">
        <div
          class="hbar-fill"
          :style="{
            width: item.pct + '%',
            background: colorAt(i),
            transitionDelay: (i * 40) + 'ms',
          }"
        />
      </div>

      <!-- Value -->
      <div class="hbar-value">{{ item.count.toLocaleString('fr-DZ') }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /**
   * [{ label: string, count: number }]
   */
  data:     { type: Array,  default: () => [] },
  maxItems: { type: Number, default: 10 },
  color:    { type: String, default: '#F4652A' },   // main accent
})

// Palette: accent → muted variants
const PALETTE = [
  '#F4652A', '#F48A65', '#FDBA74', '#FCD9C0',
  '#E0805A', '#C96840', '#FF9B6A', '#FFB896',
  '#EA6B30', '#D9622A',
]

function colorAt(i) {
  return i === 0 ? props.color : PALETTE[i % PALETTE.length]
}

const normalised = computed(() => {
  const items = [...props.data]
    .sort((a, b) => b.count - a.count)
    .slice(0, props.maxItems)
  const max = items[0]?.count ?? 1
  return items.map(item => ({
    label: item.label ?? item.sector ?? item.country ?? item.name ?? '—',
    count: item.count ?? 0,
    pct:   Math.round(((item.count ?? 0) / max) * 100),
  }))
})
</script>

<style scoped>
.hbar-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.hbar-row {
  display: grid;
  grid-template-columns: 140px 1fr 52px;
  align-items: center;
  gap: 10px;
}

.hbar-label {
  font-size: 12px;
  color: #374151;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hbar-track {
  height: 8px;
  background: #F3F4F6;
  border-radius: 99px;
  overflow: hidden;
}

.hbar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 600ms cubic-bezier(.4,0,.2,1);
  width: 0%;
}

.hbar-value {
  font-size: 11px;
  font-weight: 600;
  color: #6B7280;
  text-align: right;
  font-variant-numeric: tabular-nums;
}
</style>
