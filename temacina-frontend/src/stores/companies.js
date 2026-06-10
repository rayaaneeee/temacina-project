import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { mockCompanies, mockTradeShows, mockKpis } from '@/data/mockData'

export const useCompaniesStore = defineStore('companies', () => {
  // ── Filter state ─────────────────────────────────────────────
  const filters = ref({
    sectors:     [],
    years:       [],
    trade_shows: [],
    supports:    [],
    countries:   [],
    search:      '',
  })

  // ── Pagination ───────────────────────────────────────────────
  const pagination = ref({
    page:       1,
    pageSize:   10,
    total:      0,
    totalPages: 0,
  })

  // ── Data ─────────────────────────────────────────────────────
  const allCompanies    = ref(mockCompanies)
  const companies       = ref([])
  const selectedCompany = ref(null)
  const loading         = ref(false)
  const tradeShows      = ref(mockTradeShows)
  const kpis            = ref(mockKpis)

  // ── Getters ──────────────────────────────────────────────────
  const activeFiltersCount = computed(() => {
    const f = filters.value
    return (
      f.sectors.length + f.years.length + f.trade_shows.length +
      f.supports.length + f.countries.length + (f.search ? 1 : 0)
    )
  })

  const filterSummary = computed(() => {
    const f = filters.value
    const parts = []
    if (f.sectors.length)     parts.push({ label: 'Secteurs',  value: f.sectors.join(', ') })
    if (f.years.length)       parts.push({ label: 'Années',    value: f.years.join(', ') })
    if (f.trade_shows.length) parts.push({ label: 'Salons',    value: f.trade_shows.join(', ') })
    if (f.supports.length)    parts.push({ label: 'Supports',  value: f.supports.join(', ') })
    if (f.countries.length)   parts.push({ label: 'Pays',      value: f.countries.join(', ') })
    if (f.search)             parts.push({ label: 'Recherche', value: f.search })
    return parts
  })

  // ── Actions ──────────────────────────────────────────────────
  function fetchCompanies() {
    loading.value = true
    setTimeout(() => {
      let result = [...allCompanies.value]
      const f = filters.value

      if (f.sectors.length)
        result = result.filter(c => c.sectors.some(s => f.sectors.includes(s)))
      if (f.countries.length)
        result = result.filter(c =>
          c.addresses.some(a => f.countries.includes(a.country)))
      if (f.trade_shows.length)
        result = result.filter(c =>
          c.trade_shows.some(ts => f.trade_shows.includes(ts)))
      if (f.search)
        result = result.filter(c =>
          c.legal_name.toLowerCase().includes(f.search.toLowerCase()))

      pagination.value.total      = result.length
      pagination.value.totalPages = Math.ceil(result.length / pagination.value.pageSize)

      const start = (pagination.value.page - 1) * pagination.value.pageSize
      companies.value = result.slice(start, start + pagination.value.pageSize)
      loading.value   = false
    }, 300)
  }

  function selectCompany(company) {
    selectedCompany.value = company
  }

  function toggleFilterItem(key, item) {
    const arr = filters.value[key]
    const idx = arr.indexOf(item)
    if (idx > -1) arr.splice(idx, 1)
    else arr.push(item)
    pagination.value.page = 1
  }

  function setFilter(key, value) {
    filters.value[key]    = value
    pagination.value.page = 1
  }

  function resetFilters() {
    filters.value = {
      sectors: [], years: [], trade_shows: [],
      supports: [], countries: [], search: '',
    }
    pagination.value.page = 1
    fetchCompanies()
  }

  function setPage(page) {
    pagination.value.page = page
    fetchCompanies()
  }

  function setPageSize(size) {
    pagination.value.pageSize = size
    pagination.value.page     = 1
    fetchCompanies()
  }

  function exportCsv() {
    const headers = ['ID', 'Nom', 'Secteur', 'Ville', 'Pays', 'Téléphone', 'Email']
    const rows = companies.value.map(c => [
      c.id,
      c.legal_name,
      c.sectors.join('/'),
      c.addresses[0]?.city ?? '',
      c.addresses[0]?.country ?? '',
      c.phones[0]?.number ?? '',
      c.emails[0]?.address ?? '',
    ])
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `temacina_export_${Date.now()}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Auto-fetch when filters change
  watch(filters, fetchCompanies, { deep: true })

  // Initialize
  fetchCompanies()

  return {
    filters, pagination, companies, selectedCompany,
    loading, tradeShows, kpis, activeFiltersCount, filterSummary,
    allCompanies,
    fetchCompanies, selectCompany, toggleFilterItem,
    setFilter, resetFilters, setPage, setPageSize, exportCsv,
  }
})