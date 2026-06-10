<template>
  <div class="p-6 space-y-5">

    <div>
      <h1 class="text-lg font-bold text-gray-800">Exports</h1>
      <p class="text-xs text-gray-400 mt-0.5">Download data in various formats</p>
    </div>

    <!-- Export cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

      <!-- Companies CSV -->
      <div class="bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
            <FileSpreadsheet class="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">Companies — CSV</p>
            <p class="text-xs text-gray-400">All companies with addresses & sectors</p>
          </div>
        </div>
        <button @click="exportCompanies('csv')" :disabled="busy.companiesCsv"
          class="mt-auto flex items-center justify-center gap-2 w-full py-2 rounded-lg bg-green-500 text-white text-sm font-semibold hover:bg-green-600 transition-colors disabled:opacity-60">
          <span v-if="busy.companiesCsv" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          <Download v-else class="w-4 h-4" />
          {{ busy.companiesCsv ? 'Preparing…' : 'Download CSV' }}
        </button>
      </div>

      <!-- Companies JSON -->
      <div class="bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-yellow-100 flex items-center justify-center">
            <FileJson class="w-5 h-5 text-yellow-600" />
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">Companies — JSON</p>
            <p class="text-xs text-gray-400">Machine-readable full export</p>
          </div>
        </div>
        <button @click="exportCompanies('json')" :disabled="busy.companiesJson"
          class="mt-auto flex items-center justify-center gap-2 w-full py-2 rounded-lg bg-yellow-500 text-white text-sm font-semibold hover:bg-yellow-600 transition-colors disabled:opacity-60">
          <span v-if="busy.companiesJson" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          <Download v-else class="w-4 h-4" />
          {{ busy.companiesJson ? 'Preparing…' : 'Download JSON' }}
        </button>
      </div>

      <!-- Trade shows CSV -->
      <div class="bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
            <CalendarDays class="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">Trade Shows — CSV</p>
            <p class="text-xs text-gray-400">All trade shows with stats</p>
          </div>
        </div>
        <button @click="exportTradeShows()" :disabled="busy.tradeShows"
          class="mt-auto flex items-center justify-center gap-2 w-full py-2 rounded-lg bg-blue-500 text-white text-sm font-semibold hover:bg-blue-600 transition-colors disabled:opacity-60">
          <span v-if="busy.tradeShows" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          <Download v-else class="w-4 h-4" />
          {{ busy.tradeShows ? 'Preparing…' : 'Download CSV' }}
        </button>
      </div>

    </div>

    <!-- Success / error toast -->
    <Transition enter-from-class="opacity-0 translate-y-2" enter-active-class="transition duration-200"
      leave-to-class="opacity-0 translate-y-2" leave-active-class="transition duration-200">
      <div v-if="toast" :class="[
        'fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
        toast.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      ]">
        <CheckCircle v-if="toast.type === 'success'" class="w-4 h-4" />
        <AlertCircle v-else class="w-4 h-4" />
        {{ toast.message }}
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Download, FileSpreadsheet, FileJson, CalendarDays, CheckCircle, AlertCircle } from '@lucide/vue'
import api from '@/services/api'

const busy  = ref({ companiesCsv: false, companiesJson: false, tradeShows: false })
const toast = ref(null)

function showToast(type, message) {
  toast.value = { type, message }
  setTimeout(() => (toast.value = null), 3500)
}

function triggerDownload(content, filename, mime) {
  const blob = new Blob([content], { type: mime })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

async function exportCompanies(format) {
  const key = format === 'csv' ? 'companiesCsv' : 'companiesJson'
  busy.value[key] = true
  try {
    const res = await api.get('/companies/', { params: { page_size: 5000 } })
    const rows = res?.data ?? []

    if (format === 'json') {
      triggerDownload(JSON.stringify(rows, null, 2), 'companies.json', 'application/json')
    } else {
      const headers = ['id', 'legal_name', 'sector', 'country', 'city', 'phone', 'email', 'website']
      const csvRows = [
        headers.join(','),
        ...rows.map(c => [
          c.id,
          `"${(c.legal_name ?? '').replace(/"/g, '""')}"`,
          `"${(c.sectors?.[0]?.title ?? '').replace(/"/g, '""')}"`,
          `"${(c.addresses?.[0]?.country ?? '').replace(/"/g, '""')}"`,
          `"${(c.addresses?.[0]?.city ?? '').replace(/"/g, '""')}"`,
          `"${(c.phones?.[0]?.full_phone_number ?? '').replace(/"/g, '""')}"`,
          `"${(c.emails?.[0]?.email_address ?? '').replace(/"/g, '""')}"`,
          `"${(c.website ?? '').replace(/"/g, '""')}"`,
        ].join(','))
      ]
      triggerDownload(csvRows.join('\n'), 'companies.csv', 'text/csv')
    }
    showToast('success', `${rows.length} companies exported`)
  } catch {
    showToast('error', 'Export failed. Please try again.')
  } finally {
    busy.value[key] = false
  }
}

async function exportTradeShows() {
  busy.value.tradeShows = true
  try {
    const res  = await api.get('/trade-shows/', { params: { page_size: 500 } })
    const rows = res?.data ?? []
    const headers = ['id', 'name', 'exhibition_year', 'country', 'city', 'start_date', 'end_date']
    const csvRows = [
      headers.join(','),
      ...rows.map(t => [
        t.id,
        `"${(t.name ?? '').replace(/"/g, '""')}"`,
        t.exhibition_year ?? '',
        `"${(t.country ?? '').replace(/"/g, '""')}"`,
        `"${(t.city ?? '').replace(/"/g, '""')}"`,
        t.start_date ?? '',
        t.end_date ?? '',
      ].join(','))
    ]
    triggerDownload(csvRows.join('\n'), 'trade-shows.csv', 'text/csv')
    showToast('success', `${rows.length} trade shows exported`)
  } catch {
    showToast('error', 'Export failed. Please try again.')
  } finally {
    busy.value.tradeShows = false
  }
}
</script>
