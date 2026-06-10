<template>
  <span :class="classes">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  role: { type: String, required: true },
  size: { type: String, default: 'md' }, // 'sm' | 'md'
})

const CONFIG = {
  superadmin: { label: 'Super Admin', classes: 'bg-purple-100 text-purple-700 border-purple-200' },
  admin:      { label: 'Admin',       classes: 'bg-orange-100 text-orange-600 border-orange-200' },
  manager:    { label: 'Manager',     classes: 'bg-blue-100 text-blue-700 border-blue-200' },
  analyst:    { label: 'Analyste',    classes: 'bg-teal-100 text-teal-700 border-teal-200' },
  viewer:     { label: 'Lecteur',     classes: 'bg-gray-100 text-gray-600 border-gray-200' },
}

const cfg     = computed(() => CONFIG[props.role] ?? CONFIG.viewer)
const label   = computed(() => cfg.value.label)
const classes = computed(() => [
  'inline-block border font-semibold rounded-full',
  props.size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-0.5 text-xs',
  cfg.value.classes,
])
</script>