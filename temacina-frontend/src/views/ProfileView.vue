<template>
  <div class="p-6 max-w-3xl mx-auto space-y-6">

    <!-- Profile header banner -->
    <div class="bg-orange-50 border border-orange-100 rounded-2xl p-6 flex items-center gap-5">
      <div class="relative">
        <div class="w-20 h-20 rounded-full bg-orange-500 flex items-center justify-center text-white font-black text-3xl shadow-md">
          {{ initial }}
        </div>
        <button class="absolute bottom-0 right-0 w-7 h-7 bg-white rounded-full border-2 border-orange-200
                       flex items-center justify-center hover:bg-orange-50 transition">
          <Camera class="w-3.5 h-3.5 text-orange-500" />
        </button>
      </div>
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h2 class="text-xl font-bold text-gray-900">{{ authStore.userName }}</h2>
          <span class="badge-sector capitalize">{{ authStore.userRole }}</span>
        </div>
        <p class="text-sm text-gray-500 mt-0.5">{{ authStore.user?.email }}</p>
      </div>
      <button @click="editMode = !editMode" class="btn-ghost text-sm">
        <Pencil class="w-4 h-4" />
        Edit Profile
      </button>
    </div>

    <!-- Edit Profile Form -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-card overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 flex items-center gap-2">
        <User class="w-4 h-4 text-orange-500" />
        <h3 class="font-semibold text-gray-800">Personal Information</h3>
      </div>

      <form @submit.prevent="handleUpdateProfile" class="p-6 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">First Name</label>
            <input v-model="profileForm.first_name" type="text"
              :disabled="!editMode"
              class="form-input disabled:bg-gray-50 disabled:text-gray-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Last Name</label>
            <input v-model="profileForm.last_name" type="text"
              :disabled="!editMode"
              class="form-input disabled:bg-gray-50 disabled:text-gray-500" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Email Address</label>
          <div class="relative">
            <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input :value="authStore.user?.email" type="email"
              disabled
              class="form-input pl-9 bg-gray-50 text-gray-500 cursor-not-allowed" />
          </div>
          <p class="text-xs text-gray-400 mt-1">Email cannot be changed. Contact your admin.</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Phone</label>
          <div class="relative">
            <Phone class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input v-model="profileForm.phone" type="tel"
              :disabled="!editMode"
              placeholder="+213 XX XX XX XX"
              class="form-input pl-9 disabled:bg-gray-50 disabled:text-gray-500" />
          </div>
        </div>

        <div v-if="editMode" class="flex gap-3 pt-2">
          <button type="submit" :disabled="profileLoading" class="btn-primary">
            <Loader2 v-if="profileLoading" class="w-4 h-4 animate-spin" />
            Save Changes
          </button>
          <button type="button" @click="cancelEdit" class="btn-ghost">Cancel</button>
        </div>

        <p v-if="profileSuccess" class="text-sm text-green-600 flex items-center gap-1">
          <CheckCircle2 class="w-4 h-4" /> Profile updated successfully!
        </p>
      </form>
    </div>

    <!-- Security & Password -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-card overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 flex items-center gap-2">
        <ShieldCheck class="w-4 h-4 text-orange-500" />
        <h3 class="font-semibold text-gray-800">Security & Password</h3>
      </div>

      <div class="p-6">
        <p class="text-sm text-gray-500 mb-4">
          We recommend using a unique password for this service.
        </p>

        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Current Password</label>
            <div class="relative">
              <KeyRound class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input v-model="passForm.old_password"
                :type="showPass.old ? 'text' : 'password'"
                placeholder="••••••••••"
                class="form-input pl-9 pr-10" />
              <button type="button" @click="showPass.old = !showPass.old"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                <Eye v-if="!showPass.old" class="w-4 h-4" />
                <EyeOff v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">New Password</label>
              <div class="relative">
                <KeyRound class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input v-model="passForm.new_password"
                  :type="showPass.new ? 'text' : 'password'"
                  placeholder="••••••••••"
                  class="form-input pl-9 pr-10" />
                <button type="button" @click="showPass.new = !showPass.new"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  <Eye v-if="!showPass.new" class="w-4 h-4" />
                  <EyeOff v-else class="w-4 h-4" />
                </button>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Confirm New Password</label>
              <div class="relative">
                <KeyRound class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input v-model="passForm.confirm"
                  :type="showPass.confirm ? 'text' : 'password'"
                  placeholder="••••••••••"
                  class="form-input pl-9 pr-10" />
                <button type="button" @click="showPass.confirm = !showPass.confirm"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  <Eye v-if="!showPass.confirm" class="w-4 h-4" />
                  <EyeOff v-else class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Password requirements -->
          <div class="grid grid-cols-2 gap-1 bg-gray-50 rounded-lg p-3">
            <div v-for="rule in passwordRules" :key="rule.text"
                 :class="rule.valid ? 'text-green-600' : 'text-gray-400'"
                 class="flex items-center gap-1.5 text-xs">
              <CheckCircle2 v-if="rule.valid" class="w-3 h-3" />
              <Circle v-else class="w-3 h-3" />
              {{ rule.text }}
            </div>
          </div>

          <p v-if="passError" class="text-sm text-red-600">{{ passError }}</p>
          <p v-if="passSuccess" class="text-sm text-green-600 flex items-center gap-1">
            <CheckCircle2 class="w-4 h-4" /> Password changed successfully!
          </p>

          <button type="submit" :disabled="passLoading" class="btn-primary">
            <Loader2 v-if="passLoading" class="w-4 h-4 animate-spin" />
            Update Password
          </button>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import {
  User, Mail, Phone, Camera, Pencil, KeyRound,
  Eye, EyeOff, ShieldCheck, CheckCircle2, Circle,
  Loader2
} from '@lucide/vue'

const authStore = useAuthStore()
const toast     = useToast()

const initial = computed(() =>
  authStore.userName ? authStore.userName.charAt(0).toUpperCase() : 'U'
)

// ── Profile edit ─────────────────────────────────────────────
const editMode      = ref(false)
const profileLoading = ref(false)
const profileSuccess = ref(false)

const profileForm = ref({
  first_name: '',
  last_name:  '',
  phone:      '',
})

onMounted(() => {
  if (authStore.user) {
    profileForm.value.first_name = authStore.user.first_name ?? ''
    profileForm.value.last_name  = authStore.user.last_name  ?? ''
    profileForm.value.phone      = authStore.user.phone      ?? ''
  }
})

function cancelEdit() {
  editMode.value = false
  profileForm.value.first_name = authStore.user?.first_name ?? ''
  profileForm.value.last_name  = authStore.user?.last_name  ?? ''
  profileForm.value.phone      = authStore.user?.phone      ?? ''
}

async function handleUpdateProfile() {
  profileLoading.value = true
  profileSuccess.value = false
  try {
    await authStore.updateProfile(profileForm.value)
    profileSuccess.value = true
    editMode.value = false
    toast.success('Profile updated!')
    setTimeout(() => { profileSuccess.value = false }, 3000)
  } catch (e) {
    toast.error(e.message)
  } finally {
    profileLoading.value = false
  }
}

// ── Change password ───────────────────────────────────────────
const passLoading = ref(false)
const passError   = ref('')
const passSuccess = ref(false)
const showPass    = ref({ old: false, new: false, confirm: false })

const passForm = ref({
  old_password: '',
  new_password: '',
  confirm:      '',
})

const passwordRules = computed(() => [
  { text: 'Min. 10 characters',  valid: passForm.value.new_password.length >= 10 },
  { text: 'Uppercase letter',    valid: /[A-Z]/.test(passForm.value.new_password) },
  { text: 'At least one number', valid: /\d/.test(passForm.value.new_password) },
  { text: 'No repetitive patterns', valid: passForm.value.new_password.length > 0 &&
    !/(.)\1{2,}/.test(passForm.value.new_password) },
])

async function handleChangePassword() {
  passError.value   = ''
  passSuccess.value = false
  if (!passForm.value.old_password) {
    passError.value = 'Current password is required.'; return
  }
  if (!passwordRules.value.every(r => r.valid)) {
    passError.value = 'Password does not meet requirements.'; return
  }
  if (passForm.value.new_password !== passForm.value.confirm) {
    passError.value = 'Passwords do not match.'; return
  }
  passLoading.value = true
  try {
    await authStore.changePassword(passForm.value.old_password, passForm.value.new_password)
    passSuccess.value = true
    passForm.value = { old_password: '', new_password: '', confirm: '' }
    toast.success('Password changed!')
    setTimeout(() => { passSuccess.value = false }, 3000)
  } catch (e) {
    passError.value = e.message
  } finally {
    passLoading.value = false
  }
}
</script>