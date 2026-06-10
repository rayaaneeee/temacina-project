import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useDashboardStore = defineStore('dashboard', () => {
  const kpis = ref({
    total_companies:     0,
    total_trade_shows:   0,
    total_documents:     0,
    total_emails:        0,
    total_phones:        0,
    companies_by_year:   [],
    companies_by_sector: [],
    companies_by_country:[],
  })

  const recentCompanies = ref([])
  const loading         = ref(false)

  async function fetchKpis() {
    try {
      const data = await api.get('/dashboard/kpis/')
      kpis.value = data ?? kpis.value
    } catch {}
  }

  async function fetchRecentCompanies() {
    try {
      const res = await api.get('/companies/', { params: { page: 1, page_size: 5 } })
      recentCompanies.value = res?.data ?? (Array.isArray(res) ? res : [])
    } catch {}
  }

  async function init() {
    loading.value = true
    await Promise.all([fetchKpis(), fetchRecentCompanies()])
    loading.value = false
  }

  return { kpis, recentCompanies, loading, init, fetchKpis, fetchRecentCompanies }
})
