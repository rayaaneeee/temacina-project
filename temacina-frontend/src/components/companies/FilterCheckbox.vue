<template>
  <label class="flex items-center gap-2 cursor-pointer group">
    <input
      type="checkbox"
      :checked="checked"
      @change="$emit('toggle')"
      class="w-3.5 h-3.5 rounded border-gray-300 text-orange-500
             focus:ring-orange-400 focus:ring-offset-0 cursor-pointer"
    />
    <span class="text-xs text-gray-600 group-hover:text-gray-900 leading-none">{{ label }}</span>
  </label>
</template>

<script setup>
defineProps({ label: String, checked: Boolean })
defineEmits(['toggle'])
</script>