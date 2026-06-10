<template>
  <button
    @click="$emit('sort', field)"
    class="flex items-center gap-1 hover:text-gray-800 transition-colors text-left"
    :class="$attrs.class"
  >
    {{ label }}
    <span class="flex flex-col leading-none ml-0.5">
      <ChevronUp
        class="w-2.5 h-2.5 -mb-0.5"
        :class="ordering === field ? 'text-orange-500' : 'text-gray-300'"
      />
      <ChevronDown
        class="w-2.5 h-2.5"
        :class="ordering === `-${field}` ? 'text-orange-500' : 'text-gray-300'"
      />
    </span>
  </button>
</template>

<script setup>
import { ChevronUp, ChevronDown } from '@lucide/vue'

defineProps({ field: String, label: String, ordering: String })
defineEmits(['sort'])
</script>
