<template>
  <div class="flex h-screen overflow-hidden bg-gray-50">
    <AppSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <AppHeader />
      <main class="flex-1 overflow-y-auto">
        <RouterView />
      </main>
      <AppFooter />
    </div>
  </div>
</template>

<script setup>
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader  from '@/components/layout/AppHeader.vue'
import AppFooter  from '@/components/layout/AppFooter.vue'
</script>