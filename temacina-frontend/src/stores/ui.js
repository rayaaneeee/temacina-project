import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const sidebarOpen   = ref(true)
  const globalLoading = ref(false)
  const activeModal   = ref(null)

  function toggleSidebar() { sidebarOpen.value = !sidebarOpen.value }
  function openModal(name)  { activeModal.value = name }
  function closeModal()     { activeModal.value = null }
  function setLoading(v)    { globalLoading.value = v }

  return { sidebarOpen, globalLoading, activeModal,
           toggleSidebar, openModal, closeModal, setLoading }
})