/**
 * src/stores/analytics.js
 * Pinia store for the Analytics page.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import AnalyticsService from '@/services/analytics.service'

export const useAnalyticsStore = defineStore('analytics', () => {

  // ── Raw data ────────────────────────────────────────────────
  const overview       = ref(null)   // { total_companies, total_contacts, … }
  const bySector       = ref([])     // [{ sector, count }]
  const byCountry      = ref([])     // [{ country, count }]
  const byTradeShow    = ref([])     // [{ name, year, company_count }]
  const tradeShows     = ref([])     // all editions for selector
  const selectedShowStats = ref(null)

  // ── UI state ────────────────────────────────────────────────
  const loading        = ref({
    overview:   false,
    charts:     false,
    tradeShows: false,
    showStats:  false,
  })
  const error          = ref(null)
  const selectedShowId = ref(null)

  // ── Derived / shaped data for charts ────────────────────────

  /** Top N sectors sorted by count */
  const topSectors = computed(() =>
    [...bySector.value]
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
  )

  /** Top N countries sorted by count */
  const topCountries = computed(() =>
    [...byCountry.value]
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
  )

  /**
   * Normalise the raw by-trade-show data
   * (Django returns long field names from .values() calls)
   */
  const tradeShowSeries = computed(() =>
    byTradeShow.value.map(row => ({
      name:  row.documents__trade_show__name  ?? row.name  ?? '—',
      year:  row.documents__trade_show__exhibition_year ?? row.year ?? '',
      count: row.company_count ?? 0,
    }))
  )

  // ── Actions ─────────────────────────────────────────────────

  /** Load everything needed for the page in parallel. */
  async function loadAll() {
    error.value = null
    loading.value.overview = true
    loading.value.charts   = true

    try {
      const [ov, sector, country, show, shows] = await Promise.all([
        AnalyticsService.getOverview(),
        AnalyticsService.getBySector(),
        AnalyticsService.getByCountry(),
        AnalyticsService.getByTradeShow(),
        AnalyticsService.getAllTradeShows(),
      ])
      overview.value    = ov
      bySector.value    = Array.isArray(sector)  ? sector  : sector?.results  ?? []
      byCountry.value   = Array.isArray(country) ? country : country?.results ?? []
      byTradeShow.value = Array.isArray(show)    ? show    : show?.results    ?? []
      tradeShows.value  = Array.isArray(shows)   ? shows   : shows?.results   ?? []
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value.overview = false
      loading.value.charts   = false
    }
  }

  /** Load stats for one trade show edition. */
  async function loadTradeShowStats(id) {
    if (!id) { selectedShowStats.value = null; return }
    selectedShowId.value = id
    loading.value.showStats = true
    try {
      selectedShowStats.value = await AnalyticsService.getTradeShowStats(id)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value.showStats = false
    }
  }

  return {
    // state
    overview, bySector, byCountry, byTradeShow, tradeShows,
    selectedShowStats, selectedShowId, loading, error,
    // computed
    topSectors, topCountries, tradeShowSeries,
    // actions
    loadAll, loadTradeShowStats,
  }
})