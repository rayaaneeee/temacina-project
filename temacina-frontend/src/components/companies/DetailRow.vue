<template>
  <div class="flex gap-3">
    <div class="w-4 h-4 mt-0.5 flex-shrink-0 text-orange-400">
      <component :is="iconComponent" class="w-4 h-4" />
    </div>
    <div class="min-w-0 flex-1">
      <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-0.5">{{ label }}</p>
      <div class="text-sm text-gray-700 leading-snug">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  User, Briefcase, MapPin, Globe, Hash,
  Phone, Mail, Link, FileText, Share2, Users,
} from '@lucide/vue'

const props = defineProps({ icon: String, label: String })

const iconMap = {
  User, Briefcase, MapPin, Globe, Hash,
  Phone, Mail, Link, FileText, Share2, Users,
  Linkedin: Share2, Twitter: Share2, Facebook: Share2, Instagram: Share2,
}
const iconComponent = computed(() => iconMap[props.icon] ?? User)
</script>
