import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useDocumentsStore = defineStore('documents', () => {
  const documents    = ref([])
  const loading      = ref(false)
  const preview      = ref(null) // document being previewed

  const pagination = ref({ page: 1, pageSize: 15, total: 0, totalPages: 0 })
  const filters    = ref({ trade_show_id: null, year: null, status: '', doc_type: '', search: '' })

  async function fetchDocuments() {
    loading.value = true
    try {
      const params = {
        page:      pagination.value.page,
        page_size: pagination.value.pageSize,
      }
      if (filters.value.trade_show_id) params.trade_show_id = filters.value.trade_show_id
      if (filters.value.year)          params.year          = filters.value.year
      if (filters.value.status)        params.status        = filters.value.status
      if (filters.value.doc_type)      params.doc_type      = filters.value.doc_type
      if (filters.value.search)        params.search        = filters.value.search

      const res = await api.get('/documents/', { params })
      documents.value             = res?.data  ?? []
      pagination.value.total      = res?.meta?.total      ?? 0
      pagination.value.totalPages = res?.meta?.total_pages ?? 0
    } catch {
      documents.value = []
    } finally {
      loading.value = false
    }
  }

  function setFilter(key, value) {
    filters.value[key]    = value
    pagination.value.page = 1
    fetchDocuments()
  }

  function resetFilters() {
    filters.value = { trade_show_id: null, year: null, status: '', doc_type: '', search: '' }
    pagination.value.page = 1
    fetchDocuments()
  }

  function setPage(page) {
    pagination.value.page = page
    fetchDocuments()
  }

  function openPreview(doc)  { preview.value = doc }
  function closePreview()    { preview.value = null }

  return {
    documents, loading, preview, pagination, filters,
    fetchDocuments, setFilter, resetFilters, setPage,
    openPreview, closePreview,
  }
})
