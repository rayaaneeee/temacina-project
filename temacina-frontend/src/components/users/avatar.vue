<template>
  <div :class="sizeClass" class="rounded-full flex items-center justify-center font-semibold flex-shrink-0" :style="{ background: bgColor, color: textColor }">
    {{ initials }}
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  firstName: { type: String, default: '' },
  lastName:  { type: String, default: '' },
  role:      { type: String, default: 'viewer' },
  size:      { type: String, default: 'md' }, // 'sm' | 'md' | 'lg'
})

const ROLE_COLORS = {
  superadmin: { bg: '#EDE9FE', text: '#6D28D9' },
  admin:      { bg: '#FFF0E8', text: '#C2410C' },
  manager:    { bg: '#DBEAFE', text: '#1D4ED8' },
  analyst:    { bg: '#CCFBF1', text: '#0F766E' },
  viewer:     { bg: '#F3F4F6', text: '#374151' },
}

const color    = computed(() => ROLE_COLORS[props.role] ?? ROLE_COLORS.viewer)
const bgColor  = computed(() => color.value.bg)
const textColor = computed(() => color.value.text)
const initials  = computed(() =>
  `${props.firstName?.[0] ?? ''}${props.lastName?.[0] ?? ''}`.toUpperCase()
)
const sizeClass = computed(() => ({
  sm: 'w-7 h-7 text-xs',
  md: 'w-9 h-9 text-sm',
  lg: 'w-14 h-14 text-xl',
}[props.size] ?? 'w-9 h-9 text-sm'))
</script>