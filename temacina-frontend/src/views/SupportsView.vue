<template>
  <div class="p-6 space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-bold text-gray-800">Documents</h1>
        <p class="text-xs text-gray-400 mt-0.5">{{ store.pagination.total }} total documents</p>
      </div>
    </div>

    <!-- Filters bar -->
    <div class="bg-white rounded-xl border border-gray-200 px-4 py-3 flex flex-wrap items-center gap-3">
      <div class="relative flex-1 min-w-48">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input v-model="searchInput" @input="onSearch"
          placeholder="Search documents..."
          class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
      </div>
      <select v-model="store.filters.year" @change="store.setFilter('year', store.filters.year || null)"
        class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
        <option value="">All Years</option>
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
      <select v-model="store.filters.status" @change="store.setFilter('status', store.filters.status)"
        class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
        <option value="">All Statuses</option>
        <option value="done">Done</option>
        <option value="pending">Pending</option>
        <option value="processing">Processing</option>
        <option value="error">Error</option>
      </select>
      <select v-model="store.filters.doc_type" @change="store.setFilter('doc_type', store.filters.doc_type)"
        class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
        <option value="">All Types</option>
        <option value="Annuaire">Annuaire</option>
        <option value="Catalogue">Catalogue</option>
        <option value="Brochure">Brochure</option>
      </select>
      <button @click="store.resetFilters(); searchInput = ''"
        class="text-sm text-gray-500 hover:text-orange-500 flex items-center gap-1 transition-colors">
        <X class="w-3.5 h-3.5" /> Reset
      </button>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">#</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">File Name</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Trade Show</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Type</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Pages</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Status</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Ingested</th>
            <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-if="store.loading">
            <td colspan="8" class="px-4 py-12 text-center">
              <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            </td>
          </tr>
          <tr v-else-if="!store.documents.length">
            <td colspan="8" class="px-4 py-12 text-center text-sm text-gray-400">
              <FileText class="w-10 h-10 mx-auto mb-2 opacity-20" />
              No documents found
            </td>
          </tr>
          <tr v-else v-for="(doc, i) in store.documents" :key="doc.id"
            class="hover:bg-orange-50/30 transition-colors">
            <td class="px-4 py-3 text-xs text-gray-400">{{ (offset + i + 1).toString().padStart(3, '0') }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <FileText class="w-3.5 h-3.5 text-blue-500" />
                </div>
                <span class="text-xs font-medium text-gray-800 truncate max-w-xs">{{ doc.file_name }}</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <div class="text-xs text-gray-700 font-medium">{{ doc.trade_show?.name ?? '—' }}</div>
              <div class="text-[10px] text-gray-400">{{ doc.trade_show?.exhibition_year }}</div>
            </td>
            <td class="px-4 py-3">
              <span class="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 font-medium">
                {{ doc.document_type ?? '—' }}
              </span>
            </td>
            <td class="px-4 py-3 text-xs text-gray-600">{{ doc.page_count ?? '—' }}</td>
            <td class="px-4 py-3">
              <span :class="[
                'text-[10px] px-2 py-0.5 rounded-full font-semibold',
                doc.ingestion_status === 'done'       ? 'bg-green-100 text-green-700' :
                doc.ingestion_status === 'pending'    ? 'bg-yellow-100 text-yellow-700' :
                doc.ingestion_status === 'processing' ? 'bg-blue-100 text-blue-700' :
                'bg-red-100 text-red-700'
              ]">{{ doc.ingestion_status ?? 'unknown' }}</span>
            </td>
            <td class="px-4 py-3 text-xs text-gray-400">{{ doc.ingested_at ? formatDate(doc.ingested_at) : '—' }}</td>
            <td class="px-4 py-3">
              <button @click="store.openPreview(doc)"
                class="text-xs text-orange-500 hover:text-orange-700 font-medium flex items-center gap-1 transition-colors">
                <Eye class="w-3.5 h-3.5" /> Preview
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="store.pagination.total > 0"
        class="px-4 py-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
        <span>Showing {{ offset + 1 }}–{{ Math.min(offset + store.pagination.pageSize, store.pagination.total) }} of {{ store.pagination.total }}</span>
        <div class="flex items-center gap-1">
          <button @click="store.setPage(store.pagination.page - 1)" :disabled="store.pagination.page <= 1"
            class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">Previous</button>
          <button v-for="p in visiblePages" :key="p" @click="p !== '...' && store.setPage(p)"
            :class="['px-3 py-1.5 rounded-lg border transition-colors',
              p === store.pagination.page ? 'bg-orange-500 text-white border-orange-500'
              : p === '...' ? 'border-transparent cursor-default' : 'border-gray-200 hover:bg-gray-50']">
            {{ p }}
          </button>
          <button @click="store.setPage(store.pagination.page + 1)" :disabled="store.pagination.page >= store.pagination.totalPages"
            class="px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">Next</button>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <Teleport to="body">
      <div v-if="store.preview" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="store.closePreview()" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg z-10 overflow-hidden">
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-blue-100 flex items-center justify-center">
                <FileText class="w-4 h-4 text-blue-500" />
              </div>
              <div>
                <p class="text-sm font-bold text-gray-800 truncate max-w-xs">{{ store.preview.file_name }}</p>
                <p class="text-xs text-gray-400">{{ store.preview.document_type }}</p>
              </div>
            </div>
            <button @click="store.closePreview()" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400">
              <X class="w-4 h-4" />
            </button>
          </div>
          <div class="p-5 space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-gray-50 rounded-xl p-3">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Trade Show</p>
                <p class="text-sm font-semibold text-gray-800">{{ store.preview.trade_show?.name ?? '—' }}</p>
                <p class="text-xs text-gray-500">{{ store.preview.trade_show?.exhibition_year }}</p>
              </div>
              <div class="bg-gray-50 rounded-xl p-3">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Pages</p>
                <p class="text-2xl font-black text-gray-800">{{ store.preview.page_count ?? '—' }}</p>
              </div>
              <div class="bg-gray-50 rounded-xl p-3">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Status</p>
                <span :class="['text-xs px-2 py-0.5 rounded-full font-semibold',
                  store.preview.ingestion_status === 'done'    ? 'bg-green-100 text-green-700' :
                  store.preview.ingestion_status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-blue-100 text-blue-700']">
                  {{ store.preview.ingestion_status }}
                </span>
              </div>
              <div class="bg-gray-50 rounded-xl p-3">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">Ingested At</p>
                <p class="text-sm font-semibold text-gray-800">
                  {{ store.preview.ingested_at ? formatDate(store.preview.ingested_at) : '—' }}
                </p>
              </div>
            </div>
            <div class="bg-gray-50 rounded-xl p-3">
              <div class="flex items-center justify-between mb-2">
                <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Ingestion Progress</p>
                <span class="text-xs font-bold text-gray-700">
                  {{ store.preview.ingestion_status === 'done' ? '100%' : store.preview.ingestion_status === 'pending' ? '0%' : '50%' }}
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="h-2 rounded-full transition-all"
                  :class="store.preview.ingestion_status === 'done' ? 'bg-green-500' : store.preview.ingestion_status === 'pending' ? 'bg-yellow-400' : 'bg-blue-400'"
                  :style="{ width: store.preview.ingestion_status === 'done' ? '100%' : store.preview.ingestion_status === 'pending' ? '0%' : '50%' }">
                </div>
              </div>
            </div>
          </div>
          <div class="px-5 py-4 border-t border-gray-100 flex justify-end">
            <button @click="store.closePreview()"
              class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 font-medium">Close</button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { Search, FileText, Eye, X } from '@lucide/vue'
import { useDocumentsStore } from '@/stores/documents'

const store = useDocumentsStore()
const searchInput = ref('')

onMounted(() => store.fetchDocuments())

const onSearch = useDebounceFn(() => store.setFilter('search', searchInput.value), 350)

const years = [2026, 2025, 2024, 2023, 2022, 2021, 2020]

const offset = computed(() => (store.pagination.page - 1) * store.pagination.pageSize)

const visiblePages = computed(() => {
  const { page, totalPages } = store.pagination
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
  const pages = [1]
  if (page > 3) pages.push('...')
  for (let p = Math.max(2, page - 1); p <= Math.min(totalPages - 1, page + 1); p++) pages.push(p)
  if (page < totalPages - 2) pages.push('...')
  pages.push(totalPages)
  return pages
})

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>
