import api from '@/services/api'

const AnalyticsService = {
  /** KPIs + chart data — reuses the dashboard/kpis endpoint */
  async getOverview() {
    const data = await api.get('/dashboard/kpis/')
    return {
      total_companies:  data?.total_companies  ?? 0,
      total_trade_shows:data?.total_trade_shows ?? 0,
      total_documents:  data?.total_documents  ?? 0,
      total_emails:     data?.total_emails     ?? 0,
      total_phones:     data?.total_phones     ?? 0,
    }
  },

  async getBySector() {
    const data = await api.get('/dashboard/kpis/')
    return (data?.companies_by_sector ?? []).map(r => ({
      label: r.sectors__title ?? r.label ?? '—',
      count: r.count ?? 0,
    }))
  },

  async getByCountry() {
    const data = await api.get('/dashboard/kpis/')
    return (data?.companies_by_country ?? []).map(r => ({
      label: r.addresses__country ?? r.label ?? '—',
      count: r.count ?? 0,
    }))
  },

  async getByTradeShow() {
    const data = await api.get('/dashboard/kpis/')
    return (data?.companies_by_year ?? []).map(r => ({
      name:  String(r.documents__trade_show__exhibition_year ?? r.year ?? ''),
      year:  r.documents__trade_show__exhibition_year ?? r.year ?? '',
      count: r.count ?? 0,
    }))
  },

  async getAllTradeShows() {
    const res = await api.get('/trade-shows/', { params: { page_size: 99 } })
    return res?.data ?? []
  },

  async getTradeShowStats(id) {
    return api.get(`/trade-shows/${id}/stats/`)
  },
}

export default AnalyticsService
