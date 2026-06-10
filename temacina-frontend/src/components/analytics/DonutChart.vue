<template>
  <div class="donut-wrap">
    <canvas ref="canvas" />
    <!-- central total -->
    <div class="donut-center">
      <span class="donut-total">{{ total.toLocaleString('fr-DZ') }}</span>
      <span class="donut-total-label">{{ centerLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'

const props = defineProps({
  /**
   * [{ label: string, count: number }]
   */
  data:        { type: Array,  default: () => [] },
  centerLabel: { type: String, default: 'total' },
})

const canvas = ref(null)
let chart = null

const COLORS = ['#F4652A', '#FDBA74', '#FCD9C0', '#F48A65', '#E0805A', '#C96840', '#FF9B6A']

const total = computed(() => props.data.reduce((s, d) => s + (d.count ?? 0), 0))

async function getChart() {
  if (window.Chart) return window.Chart
  return new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js'
    s.onload = () => resolve(window.Chart)
    s.onerror = reject
    document.head.appendChild(s)
  })
}

async function draw() {
  if (!canvas.value || !props.data.length) return
  const Chart = await getChart()

  if (chart) chart.destroy()

  chart = new Chart(canvas.value, {
    type: 'doughnut',
    data: {
      labels:   props.data.map(d => d.label ?? d.document_type__label ?? d.ingestion_status ?? '—'),
      datasets: [{
        data:            props.data.map(d => d.count ?? 0),
        backgroundColor: COLORS,
        borderWidth:     2,
        borderColor:     '#fff',
        hoverOffset:     4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { size: 11 },
            color: '#6B7280',
            padding: 14,
            usePointStyle: true,
            pointStyleWidth: 8,
          },
        },
        tooltip: {
          backgroundColor: '#111827',
          titleFont: { size: 11, weight: '600' },
          bodyFont: { size: 11 },
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (item) => `  ${item.label}: ${item.raw.toLocaleString('fr-DZ')}`,
          },
        },
      },
    },
  })
}

onMounted(() => nextTick(draw))
watch(() => props.data, () => nextTick(draw), { deep: true })
onBeforeUnmount(() => chart?.destroy())
</script>

<style scoped>
.donut-wrap {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-center {
  position: absolute;
  top: 38%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.donut-total {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.donut-total-label {
  display: block;
  font-size: 10px;
  color: #9CA3AF;
  margin-top: 3px;
}
</style>
