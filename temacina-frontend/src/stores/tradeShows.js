import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useTradeShowsStore = defineStore('tradeShows', () => {
  // ── State ─────────────────────────────────────────────────────
  const tradeShows      = ref([])
  const selectedShow    = ref(null)
  const showStats       = ref(null)
  const showCompanies   = ref([])
  const loading         = ref(false)
  const detailLoading   = ref(false)

  const pagination = ref({ page: 1, pageSize: 15, total: 0, totalPages: 0 })
  const filters    = ref({ year: null, country: '', search: '' })

  const companiesPagination = ref({ page: 1, pageSize: 10, total: 0, totalPages: 0 })
  const companiesSearch     = ref('')

  // ── Getters ───────────────────────────────────────────────────
  const years = computed(() => {
    const s = new Set(tradeShows.value.map(ts => ts.exhibition_year).filter(Boolean))
    return [...s].sort((a, b) => b - a)
  })

  // ── Actions ───────────────────────────────────────────────────
  async function fetchTradeShows() {
    loading.value = true
    try {
      const params = {
        page:      pagination.value.page,
        page_size: pagination.value.pageSize,
      }
      if (filters.value.year)    params.year    = filters.value.year
      if (filters.value.country) params.country = filters.value.country
      if (filters.value.search)  params.search  = filters.value.search

      const res = await api.get('/trade-shows/', { params })
      tradeShows.value               = res?.data  ?? []
      pagination.value.total         = res?.meta?.total      ?? 0
      pagination.value.totalPages    = res?.meta?.total_pages ?? 0
    } catch {
      tradeShows.value = []
    } finally {
      loading.value = false
    }
  }

  async function selectShow(ts) {
    selectedShow.value  = ts
    showStats.value     = null
    showCompanies.value = []
    companiesPagination.value.page = 1
    companiesSearch.value = ''
    detailLoading.value = true
    try {
      const [stats] = await Promise.all([
        api.get(`/trade-shows/${ts.id}/stats/`),
        fetchShowCompanies(ts.id),
      ])
      showStats.value = stats
    } catch {
      showStats.value = null
    } finally {
      detailLoading.value = false
    }
  }

  async function fetchShowCompanies(showId) {
    const params = {
      trade_show_id: showId,
      page:          companiesPagination.value.page,
      page_size:     companiesPagination.value.pageSize,
    }
    if (companiesSearch.value) params.search = companiesSearch.value
    const res = await api.get('/companies/', { params })
    showCompanies.value                  = res?.data  ?? []
    companiesPagination.value.total      = res?.meta?.total      ?? 0
    companiesPagination.value.totalPages = res?.meta?.total_pages ?? 0
  }

  function setFilter(key, value) {
    filters.value[key]    = value
    pagination.value.page = 1
    fetchTradeShows()
  }

  function setPage(page) {
    pagination.value.page = page
    fetchTradeShows()
  }

  function setCompaniesPage(page) {
    companiesPagination.value.page = page
    if (selectedShow.value) fetchShowCompanies(selectedShow.value.id)
  }

  function searchCompanies(q) {
    companiesSearch.value          = q
    companiesPagination.value.page = 1
    if (selectedShow.value) fetchShowCompanies(selectedShow.value.id)
  }

  return {
    tradeShows, selectedShow, showStats, showCompanies,
    loading, detailLoading, pagination, filters, years,
    companiesPagination, companiesSearch,
    fetchTradeShows, selectShow, setFilter, setPage,
    setCompaniesPage, searchCompanies, fetchShowCompanies,
  }
})
