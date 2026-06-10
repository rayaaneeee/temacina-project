<template>
  <div class="p-6 max-w-6xl mx-auto">

    <!-- Page title + back -->
    <div class="flex items-center gap-3 mb-6">
      <button
        @click="$router.back()"
        class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
      >
        <ArrowLeft class="w-4 h-4" />
        Back
      </button>
      <h1 class="text-xl font-bold text-gray-800">Company Profile</h1>
    </div>

    <!-- Not found -->
    <div v-if="!company" class="flex flex-col items-center justify-center py-24 text-gray-400">
      <Building2 class="w-12 h-12 mb-4 opacity-25" />
      <p class="text-sm">Company not found.</p>
    </div>

    <template v-else>
      <div class="grid grid-cols-3 gap-5">

        <!-- ── Left 2 cols ───────────────────────────────────── -->
        <div class="col-span-2 space-y-5">

          <!-- Company header card -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <div class="flex items-start gap-4">
              <!-- Logo / Initial -->
              <div class="w-14 h-14 rounded-xl bg-orange-100 text-orange-600 font-black text-2xl
                          flex items-center justify-center flex-shrink-0">
                {{ company.legal_name.charAt(0) }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <h2 class="text-lg font-bold text-gray-900 leading-tight">{{ company.legal_name }}</h2>
                    <p class="text-sm text-gray-500 mt-0.5">
                      {{ company.addresses[0]?.city }}, {{ company.addresses[0]?.country }}
                    </p>
                  </div>
                  <!-- Verified badge -->
                  <div class="flex items-center gap-1.5 bg-green-50 border border-green-200 text-green-700
                              text-xs font-semibold px-2.5 py-1 rounded-full flex-shrink-0">
                    <BadgeCheck class="w-3.5 h-3.5" />
                    Verified Entity
                  </div>
                </div>
                <!-- Sector tags -->
                <div class="flex flex-wrap gap-1.5 mt-2">
                  <span
                    v-for="s in company.sectors"
                    :key="s"
                    class="text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 font-medium"
                  >{{ s }}</span>
                </div>
              </div>
            </div>

            <!-- Tabs -->
            <div class="flex gap-1 mt-5 border-b border-gray-100">
              <button
                v-for="tab in tabs"
                :key="tab"
                @click="activeTab = tab"
                :class="activeTab === tab
                  ? 'border-b-2 border-orange-500 text-orange-600 font-semibold'
                  : 'text-gray-500 hover:text-gray-700'"
                class="px-4 py-2 text-sm transition-colors -mb-px"
              >{{ tab }}</button>
            </div>

            <!-- Tab: Overview -->
            <div v-if="activeTab === 'Overview'" class="pt-4 space-y-4">
              <!-- Description -->
              <div v-if="company.descriptions[0]">
                <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                  Company Description
                </h4>
                <p class="text-sm text-gray-700 leading-relaxed">
                  {{ company.descriptions[0].description }}
                </p>
              </div>

              <!-- Two-col facts -->
              <div class="grid grid-cols-2 gap-4 mt-4">
                <!-- Digital Presence -->
                <div class="border border-gray-100 rounded-lg p-3">
                  <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2 flex items-center gap-1">
                    <Monitor class="w-3.5 h-3.5" /> Digital Presence
                  </p>
                  <div class="space-y-1">
                    <a
                      v-for="w in company.websites"
                      :key="w.url"
                      :href="w.url"
                      target="_blank"
                      class="block text-xs text-orange-500 hover:underline truncate"
                    >{{ w.url.replace('https://', '') }}</a>
                    <p v-if="!company.websites.length" class="text-xs text-gray-400">No website</p>
                  </div>
                </div>

                <!-- Historical Data -->
                <div class="border border-gray-100 rounded-lg p-3">
                  <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2 flex items-center gap-1">
                    <Clock class="w-3.5 h-3.5" /> Historical Data
                  </p>
                  <div class="text-xs text-gray-600 space-y-1">
                    <div class="flex justify-between">
                      <span class="text-gray-400">Trade Shows</span>
                      <span class="font-medium">{{ company.trade_shows.join(', ') || '—' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">Years Active</span>
                      <span class="font-medium">{{ company.trade_shows.length }} Cycles</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Active Insights -->
              <div class="grid grid-cols-2 gap-3 mt-1">
                <div class="rounded-lg border border-blue-100 bg-blue-50 p-3 flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                    <Users class="w-4 h-4 text-blue-500" />
                  </div>
                  <div>
                    <p class="text-lg font-bold text-gray-800">{{ company.contacts.length }}</p>
                    <p class="text-xs text-gray-500">Detected Contacts</p>
                  </div>
                </div>
                <div class="rounded-lg border border-purple-100 bg-purple-50 p-3 flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
                    <FileText class="w-4 h-4 text-purple-500" />
                  </div>
                  <div>
                    <p class="text-lg font-bold text-gray-800">{{ company.trade_shows.length }}</p>
                    <p class="text-xs text-gray-500">Trade Documents</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tab: Contacts -->
            <div v-if="activeTab === 'Contacts'" class="pt-4">
              <div v-if="company.contacts.length" class="space-y-3">
                <div
                  v-for="(c, i) in company.contacts"
                  :key="i"
                  class="flex items-center gap-3 p-3 rounded-lg border border-gray-100"
                >
                  <div class="w-8 h-8 rounded-full bg-orange-100 text-orange-600 font-bold text-sm
                              flex items-center justify-center">
                    {{ c.name.charAt(0) }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-800">{{ c.name }}</p>
                    <p class="text-xs text-gray-500">{{ c.role }}</p>
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-gray-400 py-4">No contacts available.</p>
            </div>

            <!-- Tab: Data Ledger -->
            <div v-if="activeTab === 'Data Ledger'" class="pt-4">
              <div class="space-y-2">
                <div
                  v-for="(email, i) in company.emails"
                  :key="'e'+i"
                  class="flex items-center gap-3 text-sm p-2 rounded-lg hover:bg-gray-50"
                >
                  <Mail class="w-4 h-4 text-gray-400" />
                  <a :href="`mailto:${email.address}`" class="text-orange-500 hover:underline">
                    {{ email.address }}
                  </a>
                  <span class="ml-auto text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">
                    {{ email.is_professional ? 'Professional' : 'Personal' }}
                  </span>
                </div>
                <div
                  v-for="(ph, i) in company.phones"
                  :key="'p'+i"
                  class="flex items-center gap-3 text-sm p-2 rounded-lg hover:bg-gray-50"
                >
                  <Phone class="w-4 h-4 text-gray-400" />
                  <span class="text-gray-700">{{ ph.number }}</span>
                  <span class="ml-auto text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">{{ ph.type }}</span>
                </div>
              </div>
              <p v-if="!company.emails.length && !company.phones.length" class="text-sm text-gray-400 py-4">
                No data available.
              </p>
            </div>

            <!-- Tab: Documents -->
            <div v-if="activeTab === 'Documents'" class="pt-4">
              <div v-if="company.trade_shows.length" class="space-y-2">
                <div
                  v-for="ts in company.trade_shows"
                  :key="ts"
                  class="flex items-center gap-3 p-3 rounded-lg border border-gray-100 text-sm"
                >
                  <FileText class="w-4 h-4 text-orange-400 flex-shrink-0" />
                  <span class="text-gray-700 font-medium">{{ ts }}</span>
                  <span class="ml-auto text-xs text-gray-400">Trade Show Document</span>
                </div>
              </div>
              <p v-else class="text-sm text-gray-400 py-4">No documents available.</p>
            </div>
          </div>
        </div>

        <!-- ── Right col · Data Provenance ───────────────── -->
        <div class="col-span-1 space-y-4">

          <!-- Confidence Score -->
          <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
              Safex Confidence Score
            </p>
            <p class="text-4xl font-black text-gray-800">84<span class="text-lg font-bold text-gray-400">/100</span></p>
            <div class="mt-2 w-full bg-gray-100 rounded-full h-2">
              <div class="bg-orange-500 h-2 rounded-full" style="width: 84%"></div>
            </div>
          </div>

          <!-- Data Provenance -->
          <div class="bg-white rounded-xl border border-gray-200 p-4">
            <h4 class="text-xs font-bold text-gray-700 uppercase tracking-wide mb-3">Data Provenance</h4>

            <!-- Verifying Source -->
            <div class="mb-3">
              <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Verifying Source</p>
              <div class="border border-green-200 rounded-lg p-2.5 bg-green-50">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-xs font-semibold text-green-700">Canton Fair Official Directory</span>
                  <span class="text-[10px] text-green-600 bg-green-100 px-1.5 py-0.5 rounded font-medium">99.4% Match</span>
                </div>
                <p class="text-[10px] text-green-600">2024 • Page 128</p>
                <div class="mt-1.5 bg-green-200 rounded-full h-1.5">
                  <div class="bg-green-500 h-1.5 rounded-full" style="width: 99.4%"></div>
                </div>
              </div>
            </div>

            <!-- Raw Extraction -->
            <div class="mb-3">
              <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Raw Extraction</p>
              <div class="bg-gray-50 rounded-lg p-2.5 text-xs text-gray-600 font-mono leading-relaxed">
                <span class="text-orange-500">{{ company.emails[0]?.address ?? 'N/A' }}</span>
                {{ ' was identified in the contact directory block under ' }}
                <span class="text-gray-800 font-semibold">{{ company.legal_name }}</span>
                {{ ' via Safex OCR v4.' }}
              </div>
            </div>

            <!-- Historical Context -->
            <div>
              <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Historical Context</p>
              <div class="space-y-2">
                <div
                  v-for="(ts, i) in company.trade_shows.slice(0, 3)"
                  :key="i"
                  class="flex items-start gap-2"
                >
                  <div class="w-1.5 h-1.5 rounded-full bg-orange-400 mt-1.5 flex-shrink-0"></div>
                  <div>
                    <p class="text-xs font-medium text-gray-700">{{ ts }}</p>
                    <p class="text-[10px] text-gray-400">Exhibition Cycle</p>
                  </div>
                </div>
              </div>
              <button class="mt-3 text-xs text-orange-500 hover:text-orange-700 font-medium flex items-center gap-1">
                <FileText class="w-3 h-3" /> View Full Log
              </button>
            </div>
          </div>

          <!-- Export action -->
          <button
            class="w-full flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600
                   text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
          >
            <Download class="w-4 h-4" />
            Export Company Data
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowLeft, Building2, BadgeCheck, Users, FileText, Mail,
  Phone, Monitor, Clock, Download,
} from 'lucide-vue-next'
import { useCompaniesStore } from '@/stores/companies'

const route = useRoute()
const store = useCompaniesStore()

const company = computed(() =>
  store.allCompanies.find(c => c.id === Number(route.params.id))
  ?? store.selectedCompany
)

const tabs = ['Overview', 'Contacts', 'Data Ledger', 'Documents']
const activeTab = ref('Overview')
</script>