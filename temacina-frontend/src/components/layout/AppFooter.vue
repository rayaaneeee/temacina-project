<template>
  <footer class="h-9 bg-white border-t border-gray-100 flex items-center
                 justify-center px-6 flex-shrink-0">
    <p class="text-xs text-gray-400">
      © {{ year }} <strong class="text-gray-600">TEMACINA.COM</strong>
      — Tous droits réservés.
    </p>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>