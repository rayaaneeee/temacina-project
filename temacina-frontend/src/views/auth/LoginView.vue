<template>
  <div>
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Login</h2>
      <p class="text-gray-500 text-sm mt-1">Welcome back to Temacina Dashboard</p>
    </div>

    <!-- Error banner -->
    <div v-if="errorMsg"
         class="mb-4 px-4 py-3 rounded-lg bg-red-50 border border-red-200
                text-red-700 text-sm flex items-start gap-2">
      <AlertCircle class="w-4 h-4 mt-0.5 flex-shrink-0" />
      <span>{{ errorMsg }}</span>
    </div>

    <form @submit.prevent="handleLogin" class="space-y-5">
      <!-- Email -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
        <div class="relative">
          <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="form.email"
            type="email"
            placeholder="name@company.com"
            autocomplete="email"
            class="form-input pl-9"
            :class="{ 'border-red-400': v$.email.$error }"
          />
        </div>
        <p v-if="v$.email.$error" class="mt-1 text-xs text-red-500">
          {{ v$.email.$errors[0].$message }}
        </p>
      </div>

      <!-- Password -->
      <div>
        <div class="flex justify-between mb-1.5">
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <RouterLink :to="{ name: 'forgot-password' }"
            class="text-xs text-orange-500 hover:text-orange-600 font-medium">
            Forgot password?
          </RouterLink>
        </div>
        <div class="relative">
          <KeyRound class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="••••••••"
            autocomplete="current-password"
            class="form-input pl-9 pr-10"
            :class="{ 'border-red-400': v$.password.$error }"
          />
          <button type="button"
            @click="showPassword = !showPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
            <Eye v-if="!showPassword" class="w-4 h-4" />
            <EyeOff v-else class="w-4 h-4" />
          </button>
        </div>
        <p v-if="v$.password.$error" class="mt-1 text-xs text-red-500">
          {{ v$.password.$errors[0].$message }}
        </p>
      </div>

      <!-- Remember -->
      <label class="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" v-model="form.remember"
          class="w-4 h-4 rounded border-gray-300 text-orange-500" />
        <span class="text-sm text-gray-600">Remember this device for 30 days</span>
      </label>

      <!-- Submit -->
      <button type="submit" :disabled="authStore.loading"
        class="btn-primary w-full justify-center py-2.5">
        <Loader2 v-if="authStore.loading" class="w-4 h-4 animate-spin" />
        <span>{{ authStore.loading ? 'Signing in...' : 'Sign in' }}</span>
        <ArrowRight v-if="!authStore.loading" class="w-4 h-4" />
      </button>
    </form>

    <!-- Restricted access note -->
    <div class="mt-5 p-3 rounded-lg bg-gray-50 border border-gray-200 flex gap-2">
      <ShieldAlert class="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
      <div>
        <p class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Restricted Access</p>
        <p class="text-xs text-gray-500 mt-0.5">
          Temacina is an invite-only platform for authorized enterprise employees.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useVuelidate } from '@vuelidate/core'
import { required, email as emailRule, minLength, helpers } from '@vuelidate/validators'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { Mail, KeyRound, Eye, EyeOff, AlertCircle, Loader2, ArrowRight, ShieldAlert } from '@lucide/vue'

const authStore    = useAuthStore()
const router       = useRouter()
const route        = useRoute()
const toast        = useToast()
const showPassword = ref(false)
const errorMsg     = ref('')

const form = ref({ email: '', password: '', remember: false })

const rules = {
  email: {
    required: helpers.withMessage('Email is required', required),
    email:    helpers.withMessage('Invalid email format', emailRule),
  },
  password: {
    required:  helpers.withMessage('Password is required', required),
    minLength: helpers.withMessage('Minimum 8 characters', minLength(8)),
  },
}

const v$ = useVuelidate(rules, form)

async function handleLogin() {
  errorMsg.value = ''
  const valid = await v$.value.$validate()
  if (!valid) return
  try {
    await authStore.login(form.value.email, form.value.password)
    toast.success('Welcome back!')
    const redirect = route.query.redirect || '/app/dashboard'
    router.push(redirect)
  } catch (e) {
    errorMsg.value = e.message
  }
}
</script>