<template>
  <div class="p-6 space-y-6">

    <div>
      <h1 class="text-lg font-bold text-gray-800">Settings</h1>
      <p class="text-xs text-gray-400 mt-0.5">Platform configuration and preferences</p>
    </div>

    <!-- Section: Appearance -->
    <section class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
      <div class="px-5 py-4 flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
          <Palette class="w-4 h-4 text-purple-600" />
        </div>
        <div>
          <p class="text-sm font-bold text-gray-800">Appearance</p>
          <p class="text-xs text-gray-400">Interface and display preferences</p>
        </div>
      </div>
      <div class="px-5 py-4 flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-700">Theme</p>
          <p class="text-xs text-gray-400">Choose your color scheme</p>
        </div>
        <div class="flex items-center gap-2">
          <button v-for="t in themes" :key="t.value" @click="theme = t.value"
            :class="['px-3 py-1.5 rounded-lg text-xs font-medium border transition-all',
              theme === t.value ? 'border-orange-400 bg-orange-50 text-orange-600' : 'border-gray-200 text-gray-500 hover:border-gray-300']">
            {{ t.label }}
          </button>
        </div>
      </div>
      <div class="px-5 py-4 flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-700">Language</p>
          <p class="text-xs text-gray-400">Dashboard display language</p>
        </div>
        <select v-model="language"
          class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
          <option value="en">English</option>
          <option value="fr">Français</option>
          <option value="ar">العربية</option>
        </select>
      </div>
    </section>

    <!-- Section: Notifications -->
    <section class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
      <div class="px-5 py-4 flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-yellow-100 flex items-center justify-center flex-shrink-0">
          <Bell class="w-4 h-4 text-yellow-600" />
        </div>
        <div>
          <p class="text-sm font-bold text-gray-800">Notifications</p>
          <p class="text-xs text-gray-400">Manage alert preferences</p>
        </div>
      </div>
      <ToggleRow v-for="n in notifications" :key="n.key" v-model="notifState[n.key]"
        :label="n.label" :description="n.description" />
    </section>

    <!-- Section: Data -->
    <section class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
      <div class="px-5 py-4 flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
          <Database class="w-4 h-4 text-green-600" />
        </div>
        <div>
          <p class="text-sm font-bold text-gray-800">Data & Privacy</p>
          <p class="text-xs text-gray-400">Manage how data is used</p>
        </div>
      </div>
      <ToggleRow v-for="d in dataPrefs" :key="d.key" v-model="dataState[d.key]"
        :label="d.label" :description="d.description" />
    </section>

    <!-- Section: About -->
    <section class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
      <div class="px-5 py-4 flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
          <Info class="w-4 h-4 text-gray-500" />
        </div>
        <div>
          <p class="text-sm font-bold text-gray-800">About</p>
          <p class="text-xs text-gray-400">Platform information</p>
        </div>
      </div>
      <div class="px-5 py-4 flex items-center justify-between">
        <p class="text-sm text-gray-600">Version</p>
        <span class="text-xs bg-orange-100 text-orange-600 font-semibold px-2 py-0.5 rounded-full">v1.0.0</span>
      </div>
      <div class="px-5 py-4 flex items-center justify-between">
        <p class="text-sm text-gray-600">Environment</p>
        <span class="text-xs bg-gray-100 text-gray-600 font-semibold px-2 py-0.5 rounded-full">Development</span>
      </div>
      <div class="px-5 py-4 flex items-center justify-between">
        <p class="text-sm text-gray-600">API Base URL</p>
        <code class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded font-mono">http://localhost:8000/api/v1</code>
      </div>
    </section>

    <!-- Save button -->
    <div class="flex justify-end">
      <button @click="save" :disabled="saved"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-orange-500 text-white text-sm font-semibold hover:bg-orange-600 transition-colors disabled:opacity-60">
        <Check v-if="saved" class="w-4 h-4" />
        <Save v-else class="w-4 h-4" />
        {{ saved ? 'Saved!' : 'Save Preferences' }}
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, defineComponent, h } from 'vue'
import { Palette, Bell, Database, Info, Check, Save } from '@lucide/vue'

// Inline toggle row component
const ToggleRow = defineComponent({
  props: { modelValue: Boolean, label: String, description: String },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('div', { class: 'px-5 py-4 flex items-center justify-between' }, [
      h('div', [
        h('p', { class: 'text-sm font-medium text-gray-700' }, props.label),
        h('p', { class: 'text-xs text-gray-400' }, props.description),
      ]),
      h('button', {
        onClick: () => emit('update:modelValue', !props.modelValue),
        class: [
          'relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200',
          props.modelValue ? 'bg-orange-500' : 'bg-gray-200'
        ].join(' ')
      }, [
        h('span', {
          class: [
            'inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200',
            props.modelValue ? 'translate-x-4' : 'translate-x-0'
          ].join(' ')
        })
      ])
    ])
  }
})

const theme    = ref('light')
const language = ref('en')
const saved    = ref(false)

const themes = [
  { value: 'light', label: '☀️ Light' },
  { value: 'dark',  label: '🌙 Dark' },
  { value: 'auto',  label: '🖥 Auto' },
]

const notifications = [
  { key: 'ingestion',    label: 'Ingestion Alerts',   description: 'Notify when document ingestion completes or fails' },
  { key: 'newCompany',   label: 'New Companies',      description: 'Notify when new companies are indexed' },
  { key: 'weeklyReport', label: 'Weekly Report',      description: 'Receive a weekly summary digest' },
]
const notifState = ref({ ingestion: true, newCompany: false, weeklyReport: true })

const dataPrefs = [
  { key: 'analytics', label: 'Usage Analytics',  description: 'Help improve the platform with anonymous usage data' },
  { key: 'cache',     label: 'Data Cache',        description: 'Cache API responses for faster navigation' },
]
const dataState = ref({ analytics: true, cache: true })

function save() {
  saved.value = true
  setTimeout(() => (saved.value = false), 2500)
}
</script>
