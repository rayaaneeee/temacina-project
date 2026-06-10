<template>
  <div>
    <button
      @click="open = !open"
      class="w-full flex items-center justify-between py-1 text-left"
    >
      <span class="text-[11px] font-bold text-gray-700 uppercase tracking-wide">{{ label }}</span>
      <div class="flex items-center gap-1">
        <span
          v-if="badge > 0"
          class="text-[10px] bg-orange-500 text-white font-bold rounded-full w-4 h-4
                 flex items-center justify-center"
        >{{ badge }}</span>
        <ChevronDown
          :class="open ? 'rotate-180' : ''"
          class="w-3.5 h-3.5 text-gray-400 transition-transform"
        />
      </div>
    </button>
    <div v-show="open" class="mt-1.5 space-y-1">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

defineProps({ label: String, badge: { type: Number, default: 0 } })
const open = ref(true)
</script>