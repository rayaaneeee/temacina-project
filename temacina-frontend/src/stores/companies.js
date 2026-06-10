import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useCompaniesStore = defineStore('companies', () => {
  // ── Filter state ─────────────────────────────────────────────
  const filters = ref({
    sector_id:      null,
    year:           null,
    trade_show_id:  null,
    country:        '',
    search:         '',
    ordering:       'legal_name',
  })

  // ── Pagination ───────────────────────────────────────────────
  const pagination = ref({
    page:       1,
    pageSize:   10,
    total:      0,
    totalPages: 0,
  })

  // ── Data ─────────────────────────────────────────────────────
  const companies       = ref([])
  const selectedCompany = ref(null)
  const loading         = ref(false)
  const sectors         = ref([])
  const tradeShows      = ref([])
  const countries       = ref([])

  // ── Getters ──────────────────────────────────────────────────
  const activeFiltersCount = computed(() => {
    const f = filters.value
    return (
      (f.sector_id     ? 1 : 0) +
      (f.year          ? 1 : 0) +
      (f.trade_show_id ? 1 : 0) +
      (f.country       ? 1 : 0) +
      (f.search        ? 1 : 0)
    )
  })

  const filterSummary = computed(() => {
    const f   = filters.value
    const parts = []
    if (f.sector_id) {
      const s = sectors.value.find(x => x.id === f.sector_id)
      if (s) parts.push({ label: 'Sector', value: s.title })
    }
    if (f.year)          parts.push({ label: 'Year',       value: f.year })
    if (f.trade_show_id) {
      const ts = tradeShows.value.find(x => x.id === f.trade_show_id)
      if (ts) parts.push({ label: 'Trade Show', value: ts.name })
    }
    if (f.country)       parts.push({ label: 'Country',    value: f.country })
    if (f.search)        parts.push({ label: 'Search',     value: f.search })
    return parts
  })

  // ── Actions ──────────────────────────────────────────────────
  async function fetchSectors() {
    try {
      const res = await api.get('/sectors/')
      sectors.value = res?.data ?? (Array.isArray(res) ? res : [])
    } catch {}
  }

  async function fetchTradeShows() {
    try {
      const res = await api.get('/trade-shows/')
      tradeShows.value = res?.data ?? (Array.isArray(res) ? res : [])
    } catch {}
  }

  async function fetchCompanies() {
    loading.value = true
    try {
      const f      = filters.value
      const params = {
        page:      pagination.value.page,
        page_size: pagination.value.pageSize,
        ordering:  f.ordering,
      }
      if (f.sector_id)     params.sector_id     = f.sector_id
      if (f.year)          params.year           = f.year
      if (f.trade_show_id) params.trade_show_id  = f.trade_show_id
      if (f.country)       params.country        = f.country
      if (f.search)        params.search         = f.search

      const res = await api.get('/companies/', { params })

      // Backend wraps paginated responses as { data: [...], meta: { total, total_pages, ... } }
      const list = res?.data ?? (Array.isArray(res) ? res : [])
      const meta = res?.meta ?? {}

      pagination.value.total      = meta.total      ?? list.length
      pagination.value.totalPages = meta.total_pages ?? Math.ceil(list.length / pagination.value.pageSize)
      companies.value             = list

      // Build distinct country list from results
      const seen = new Set(countries.value)
      list.forEach(c => { if (c.country) seen.add(c.country) })
      countries.value = [...seen].sort()
    } catch {
      companies.value = []
    } finally {
      loading.value = false
    }
  }

  async function selectCompany(company) {
    // Always fetch full detail from API
    selectedCompany.value = company // optimistic
    try {
      const detail = await api.get(`/companies/${company.id}/`)
      selectedCompany.value = detail
    } catch {}
  }

  function setFilter(key, value) {
    filters.value[key]    = value
    pagination.value.page = 1
    fetchCompanies()
  }

  function resetFilters() {
    filters.value = {
      sector_id:     null,
      year:          null,
      trade_show_id: null,
      country:       '',
      search:        '',
      ordering:      'legal_name',
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

  function setOrdering(field) {
    filters.value.ordering =
      filters.value.ordering === field ? `-${field}` : field
    pagination.value.page  = 1
    fetchCompanies()
  }

  function exportCsv() {
    const headers = ['ID', 'Company', 'Sector', 'Country', 'Phone', 'Email']
    const rows = companies.value.map(c => [
      c.id,
      c.legal_name,
      Array.isArray(c.sectors) ? c.sectors.map(s => s.title ?? s).join('/') : '',
      c.country ?? c.addresses?.[0]?.country ?? '',
      c.phones?.[0]?.full_phone_number ?? c.phones?.[0]?.number ?? '',
      c.emails?.[0]?.email_address ?? c.emails?.[0]?.address ?? '',
    ])
    const csv = [headers, ...rows].map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n')
    downloadBlob(csv, 'text/csv', `temacina_companies_${Date.now()}.csv`)
  }

  function exportExcel() {
    // Build minimal XLSX-compatible XML (SpreadsheetML)
    const headers = ['ID', 'Company', 'Sector', 'Country', 'Phone', 'Email']
    const rows = companies.value.map(c => [
      c.id,
      c.legal_name,
      Array.isArray(c.sectors) ? c.sectors.map(s => s.title ?? s).join('/') : '',
      c.country ?? c.addresses?.[0]?.country ?? '',
      c.phones?.[0]?.full_phone_number ?? c.phones?.[0]?.number ?? '',
      c.emails?.[0]?.email_address ?? c.emails?.[0]?.address ?? '',
    ])

    const esc = v => String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    const toRow = cells =>
      `<Row>${cells.map(c => `<Cell><Data ss:Type="String">${esc(c)}</Data></Cell>`).join('')}</Row>`

    const xml = `<?xml version="1.0"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
          xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
  <Worksheet ss:Name="Companies">
    <Table>
      ${toRow(headers)}
      ${rows.map(toRow).join('\n      ')}
    </Table>
  </Worksheet>
</Workbook>`
    downloadBlob(xml, 'application/vnd.ms-excel', `temacina_companies_${Date.now()}.xls`)
  }

  function downloadBlob(content, mime, filename) {
    const blob = new Blob([content], { type: mime })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  // Initialize
  fetchSectors()
  fetchTradeShows()
  fetchCompanies()

  return {
    filters, pagination, companies, selectedCompany,
    loading, sectors, tradeShows, countries,
    activeFiltersCount, filterSummary,
    fetchCompanies, fetchSectors, fetchTradeShows,
    selectCompany, setFilter, resetFilters,
    setPage, setPageSize, setOrdering,
    exportCsv, exportExcel,
  }
})
