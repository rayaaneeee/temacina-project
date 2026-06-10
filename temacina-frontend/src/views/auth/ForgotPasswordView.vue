<template>
  <div>
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Forgot password?</h2>
      <p class="text-gray-500 text-sm mt-1">
        Enter your email to receive recovery instructions.
      </p>
    </div>

    <!-- Success state -->
    <div v-if="sent" class="text-center py-4">
      <div class="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <CheckCircle2 class="w-7 h-7 text-green-500" />
      </div>
      <h3 class="font-semibold text-gray-800 mb-1">Check your email</h3>
      <p class="text-sm text-gray-500 mb-5">
        If this email is registered, you'll receive a reset link shortly.
      </p>
      <RouterLink :to="{ name: 'login' }" class="btn-primary inline-flex mx-auto">
        Back to Login
      </RouterLink>
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="handleSubmit" class="space-y-5">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Email Address</label>
        <div class="relative">
          <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="email"
            type="email"
            placeholder="name@company.com"
            class="form-input pl-9"
          />
        </div>
        <p class="text-xs text-gray-400 mt-1">We'll never share your email with third parties.</p>
      </div>

      <button type="submit" :disabled="loading" class="btn-primary w-full justify-center py-2.5">
        <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
        <span>{{ loading ? 'Sending...' : 'Send reset link' }}</span>
        <ArrowRight v-if="!loading" class="w-4 h-4" />
      </button>

      <!-- Pro tip -->
      <div class="flex gap-2 text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
        <Info class="w-4 h-4 flex-shrink-0 mt-0.5" />
        <span>Pro-tip: If you don't see the email within 2 minutes, check your Spam or Promotions tab.</span>
      </div>

      <RouterLink :to="{ name: 'login' }"
        class="flex items-center justify-center gap-1 text-sm text-orange-500
               hover:text-orange-600 font-medium mt-2">
        <ArrowLeft class="w-4 h-4" /> Back to Login
      </RouterLink>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Mail, CheckCircle2, Loader2, ArrowRight, ArrowLeft, Info } from '@lucide/vue'

const authStore = useAuthStore()
const email     = ref('')
const loading   = ref(false)
const sent      = ref(false)

async function handleSubmit() {
  if (!email.value) return
  loading.value = true
  try {
    await authStore.requestPasswordReset(email.value)
  } finally {
    sent.value    = true
    loading.value = false
  }
}
</script>