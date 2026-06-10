<template>
  <div>
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Reset your password</h2>
      <p class="text-gray-500 text-sm mt-1">
        Please enter your new credentials to secure your account.
      </p>
    </div>

    <!-- No token -->
    <div v-if="!token" class="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
      Invalid or expired link. Please request a new password reset.
    </div>

    <!-- Success -->
    <div v-else-if="success" class="text-center py-4">
      <div class="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <CheckCircle2 class="w-7 h-7 text-green-500" />
      </div>
      <h3 class="font-semibold text-gray-800 mb-1">Password reset!</h3>
      <p class="text-sm text-gray-500 mb-5">You can now sign in with your new password.</p>
      <RouterLink :to="{ name: 'login' }" class="btn-primary inline-flex mx-auto">
        Back to Login
      </RouterLink>
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="handleSubmit" class="space-y-5">
      <!-- New password -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">New Password</label>
        <div class="relative">
          <KeyRound class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="form.password"
            :type="show.password ? 'text' : 'password'"
            placeholder="••••••••"
            class="form-input pl-9 pr-10"
          />
          <button type="button" @click="show.password = !show.password"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
            <Eye v-if="!show.password" class="w-4 h-4" />
            <EyeOff v-else class="w-4 h-4" />
          </button>
        </div>
        <!-- Security level bar -->
        <div class="mt-2">
          <div class="flex justify-between text-xs mb-1">
            <span class="text-gray-400 uppercase tracking-wide font-medium">Security Level</span>
            <span :class="strengthColor" class="font-semibold">{{ strengthLabel }}</span>
          </div>
          <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div :class="strengthBg" class="h-full rounded-full transition-all duration-300"
                 :style="{ width: strengthWidth }"></div>
          </div>
        </div>
        <!-- Rules -->
        <div class="grid grid-cols-2 gap-1 mt-2">
          <div v-for="rule in passwordRules" :key="rule.text"
               :class="rule.valid ? 'text-green-600' : 'text-gray-400'"
               class="flex items-center gap-1 text-xs">
            <CheckCircle2 v-if="rule.valid" class="w-3 h-3" />
            <Circle v-else class="w-3 h-3" />
            {{ rule.text }}
          </div>
        </div>
      </div>

      <!-- Confirm password -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Confirm Password</label>
        <div class="relative">
          <ShieldCheck class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="form.confirm"
            :type="show.confirm ? 'text' : 'password'"
            placeholder="••••••••"
            class="form-input pl-9 pr-10"
          />
          <button type="button" @click="show.confirm = !show.confirm"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
            <Eye v-if="!show.confirm" class="w-4 h-4" />
            <EyeOff v-else class="w-4 h-4" />
          </button>
        </div>
      </div>

      <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

      <button type="submit" :disabled="loading" class="btn-primary w-full justify-center py-2.5">
        <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
        Reset Password
      </button>

      <!-- Security note -->
      <div class="flex gap-2 text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
        <Info class="w-4 h-4 flex-shrink-0 mt-0.5" />
        <div>
          <span class="font-semibold text-gray-600">Security Note: </span>
          Choosing a strong, unique password helps protect your data from unauthorized access.
        </div>
      </div>

      <RouterLink :to="{ name: 'login' }"
        class="flex items-center justify-center gap-1 text-sm text-orange-500
               hover:text-orange-600 font-medium">
        <ArrowLeft class="w-4 h-4" /> Back to login
      </RouterLink>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { KeyRound, Eye, EyeOff, CheckCircle2, Circle, ShieldCheck,
         Loader2, ArrowLeft, Info } from '@lucide/vue'

const route     = useRoute()
const authStore = useAuthStore()
const token     = route.query.token
const loading   = ref(false)
const success   = ref(false)
const errorMsg  = ref('')
const form      = ref({ password: '', confirm: '' })
const show      = ref({ password: false, confirm: false })

const passwordRules = computed(() => [
  { text: 'Min. 8 characters',   valid: form.value.password.length >= 8 },
  { text: 'Uppercase letter',    valid: /[A-Z]/.test(form.value.password) },
  { text: 'At least one number', valid: /\d/.test(form.value.password) },
  { text: 'Special character',   valid: /[!@#$%^&*]/.test(form.value.password) },
])

const strengthScore = computed(() => passwordRules.value.filter(r => r.valid).length)
const strengthLabel = computed(() => ['', 'Very Weak', 'Weak', 'Fair', 'Strong'][strengthScore.value])
const strengthColor = computed(() => ['', 'text-red-500', 'text-orange-400', 'text-yellow-500', 'text-green-500'][strengthScore.value])
const strengthBg    = computed(() => ['', 'bg-red-400', 'bg-orange-400', 'bg-yellow-400', 'bg-green-500'][strengthScore.value])
const strengthWidth = computed(() => ['0%', '25%', '50%', '75%', '100%'][strengthScore.value])

async function handleSubmit() {
  errorMsg.value = ''
  if (!passwordRules.value.every(r => r.valid)) {
    errorMsg.value = 'Password does not meet requirements.'
    return
  }
  if (form.value.password !== form.value.confirm) {
    errorMsg.value = 'Passwords do not match.'
    return
  }
  loading.value = true
  try {
    await authStore.confirmPasswordReset(token, form.value.password)
    success.value = true
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}
</script>