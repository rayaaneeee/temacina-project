<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <!-- Card wrapper -->
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="flex items-center justify-center gap-3 mb-8">
        <div class="w-12 h-12 bg-orange-500 rounded-2xl flex items-center justify-center shadow-lg">
          <span class="text-white font-black text-xl">T</span>
        </div>
        <div>
          <div class="text-xl font-bold text-gray-800 leading-none">Temacina</div>
          <div class="text-xs text-gray-400">.com</div>
        </div>
      </div>

      <!-- Auth form card -->
      <div class="bg-white rounded-2xl shadow-panel border border-gray-100 p-8">
        <RouterView />
      </div>

      <!-- Footer -->
      <p class="text-center text-xs text-gray-400 mt-6">
        © {{ year }} Safex Directory Inc. · Privacy · Security Center
      </p>
    </div>
  </div>
</template>

<script setup>
const year = new Date().getFullYear()
</script>