<template>
  <div ref="wrap" class="tsbar-wrap">
    <canvas ref="canvas" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  /**
   * [{ name: string, year: number|string, count: number }]
   */
  data: { type: Array, default: () => [] },
})

const wrap   = ref(null)
const canvas = ref(null)
let chart    = null

// Lazy-load Chart.js from CDN to keep the bundle light
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

  const labels = props.data.map(d => `${d.name}\n${d.year}`)
  const counts  = props.data.map(d => d.count)

  if (chart) chart.destroy()

  chart = new Chart(canvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Entreprises',
        data: counts,
        backgroundColor: counts.map((_, i) =>
          i % 2 === 0 ? '#F4652A' : '#FDBA74'
        ),
        borderRadius: 5,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => {
              const d = props.data[items[0].dataIndex]
              return `${d.name} ${d.year}`
            },
            label: (item) => `  ${item.raw.toLocaleString('fr-DZ')} entreprises`,
          },
          backgroundColor: '#111827',
          titleFont: { size: 12, weight: '600' },
          bodyFont: { size: 12 },
          padding: 10,
          cornerRadius: 8,
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            font: { size: 10 },
            color: '#9CA3AF',
            maxRotation: 30,
            callback(val, idx) {
              const d = props.data[idx]
              return d ? `${d.name.split(' ')[0]} ${d.year}` : val
            },
          },
        },
        y: {
          grid: { color: '#F3F4F6' },
          ticks: { font: { size: 10 }, color: '#9CA3AF' },
          border: { display: false },
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
.tsbar-wrap {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>
