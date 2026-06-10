<template>
  <span :class="classes">
    <span :class="dotClass" class="w-1.5 h-1.5 rounded-full" />
    {{ active ? 'Actif' : 'Inactif' }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  active: { type: Boolean, required: true },
})

const classes = computed(() => [
  'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border',
  props.active
    ? 'bg-green-50 text-green-700 border-green-200'
    : 'bg-gray-100 text-gray-500 border-gray-200',
])

const dotClass = computed(() =>
  props.active ? 'bg-green-500' : 'bg-gray-400'
)
</script>