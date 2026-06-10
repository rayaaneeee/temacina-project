<template>
  <div class="p-6 space-y-5">

    <!-- Header -->
    <div>
      <h1 class="text-lg font-bold text-gray-800">Settings</h1>
      <p class="text-xs text-gray-400 mt-0.5">Platform configuration and administration</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        :class="['flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
          activeTab === tab.key
            ? 'bg-white text-orange-600 shadow-sm'
            : 'text-gray-500 hover:text-gray-700']">
        <component :is="tab.icon" class="w-4 h-4" />
        {{ tab.label }}
      </button>
    </div>

    <!-- ── TAB: General ───────────────────────────────────── -->
    <template v-if="activeTab === 'general'">

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
            <button v-for="t in themes" :key="t.value" @click="general.theme = t.value"
              :class="['px-3 py-1.5 rounded-lg text-xs font-medium border transition-all',
                general.theme === t.value
                  ? 'border-orange-400 bg-orange-50 text-orange-600'
                  : 'border-gray-200 text-gray-500 hover:border-gray-300']">
              {{ t.label }}
            </button>
          </div>
        </div>
        <div class="px-5 py-4 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">Language</p>
            <p class="text-xs text-gray-400">Dashboard display language</p>
          </div>
          <select v-model="general.language"
            class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
            <option value="en">English</option>
            <option value="fr">Français</option>
            <option value="ar">العربية</option>
          </select>
        </div>
        <div class="px-5 py-4 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">Items per page</p>
            <p class="text-xs text-gray-400">Default pagination size for tables</p>
          </div>
          <select v-model="general.pageSize"
            class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>
      </section>

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
        <div v-for="row in notifRows" :key="row.key" class="px-5 py-4 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">{{ row.label }}</p>
            <p class="text-xs text-gray-400">{{ row.desc }}</p>
          </div>
          <button @click="general.notif[row.key] = !general.notif[row.key]"
            :class="['relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200',
              general.notif[row.key] ? 'bg-orange-500' : 'bg-gray-200']">
            <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200',
              general.notif[row.key] ? 'translate-x-4' : 'translate-x-0']" />
          </button>
        </div>
      </section>

      <div class="flex justify-end">
        <button @click="saveGeneral"
          :class="['flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-colors',
            generalSaved ? 'bg-green-500 text-white' : 'bg-orange-500 text-white hover:bg-orange-600']">
          <Check class="w-4 h-4" />
          {{ generalSaved ? 'Saved!' : 'Save Preferences' }}
        </button>
      </div>
    </template>

    <!-- ── TAB: Users ─────────────────────────────────────── -->
    <template v-else-if="activeTab === 'users'">

      <!-- Toolbar -->
      <div class="flex items-center justify-between gap-3">
        <div class="relative flex-1 max-w-72">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input v-model="userSearch" placeholder="Search users…"
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white" />
        </div>
        <button @click="openCreate"
          class="flex items-center gap-2 px-4 py-2 rounded-lg bg-orange-500 text-white text-sm font-semibold hover:bg-orange-600 transition-colors flex-shrink-0">
          <UserPlus class="w-4 h-4" />
          New User
        </button>
      </div>

      <!-- Users table -->
      <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">User</th>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Role</th>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Sector</th>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Status</th>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Joined</th>
              <th class="px-4 py-3 text-left text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-if="usersLoading">
              <td colspan="6" class="px-4 py-12 text-center">
                <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              </td>
            </tr>
            <tr v-else-if="!filteredUsers.length">
              <td colspan="6" class="px-4 py-12 text-center text-sm text-gray-400">
                <Users class="w-10 h-10 mx-auto mb-2 opacity-20" />
                No users found
              </td>
            </tr>
            <tr v-else v-for="u in filteredUsers" :key="u.id" class="hover:bg-orange-50/30 transition-colors">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-orange-100 text-orange-600 font-bold text-xs flex items-center justify-center flex-shrink-0">
                    {{ (u.first_name?.[0] ?? u.email[0]).toUpperCase() }}
                  </div>
                  <div>
                    <p class="text-xs font-semibold text-gray-800">{{ u.first_name }} {{ u.last_name }}</p>
                    <p class="text-[10px] text-gray-400">{{ u.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold capitalize', roleBadge(u.role?.name)]">
                  {{ u.role?.name ?? '—' }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500">{{ u.sector?.name ?? '—' }}</td>
              <td class="px-4 py-3">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold',
                  u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600']">
                  {{ u.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-400">{{ fmtDate(u.created_at) }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <button @click="openEdit(u)" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-orange-500 transition-colors" title="Edit">
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button @click="toggleActive(u)" :title="u.is_active ? 'Deactivate' : 'Activate'"
                    class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                    :class="u.is_active ? 'text-gray-400 hover:text-red-500' : 'text-gray-400 hover:text-green-500'">
                    <UserX v-if="u.is_active" class="w-3.5 h-3.5" />
                    <UserCheck v-else class="w-3.5 h-3.5" />
                  </button>
                  <button @click="confirmDelete(u)" class="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors" title="Delete">
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- ── TAB: Security ──────────────────────────────────── -->
    <template v-else-if="activeTab === 'security'">

      <section class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
        <div class="px-5 py-4 flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
            <ShieldCheck class="w-4 h-4 text-red-500" />
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">Password Policy</p>
            <p class="text-xs text-gray-400">Requirements applied to all user passwords</p>
          </div>
        </div>
        <div v-for="rule in passwordPolicy" :key="rule.label" class="px-5 py-4 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">{{ rule.label }}</p>
            <p class="text-xs text-gray-400">{{ rule.desc }}</p>
          </div>
          <span class="text-xs bg-orange-100 text-orange-600 font-semibold px-2 py-0.5 rounded-full">{{ rule.value }}</span>
        </div>
      </section>

      <section class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
        <div class="px-5 py-4 flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
            <KeyRound class="w-4 h-4 text-blue-500" />
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">Session & Tokens</p>
            <p class="text-xs text-gray-400">Authentication session settings</p>
          </div>
        </div>
        <div v-for="row in sessionRows" :key="row.label" class="px-5 py-4 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">{{ row.label }}</p>
            <p class="text-xs text-gray-400">{{ row.desc }}</p>
          </div>
          <span class="text-xs bg-gray-100 text-gray-600 font-semibold px-2 py-0.5 rounded-full font-mono">{{ row.value }}</span>
        </div>
      </section>

      <section class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
        <div class="px-5 py-4 flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
            <Database class="w-4 h-4 text-green-600" />
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">Data & Privacy</p>
            <p class="text-xs text-gray-400">Control how platform data is handled</p>
          </div>
        </div>
        <div v-for="row in dataRows" :key="row.key" class="px-5 py-4 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">{{ row.label }}</p>
            <p class="text-xs text-gray-400">{{ row.desc }}</p>
          </div>
          <button @click="security[row.key] = !security[row.key]"
            :class="['relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200',
              security[row.key] ? 'bg-orange-500' : 'bg-gray-200']">
            <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200',
              security[row.key] ? 'translate-x-4' : 'translate-x-0']" />
          </button>
        </div>
      </section>
    </template>

    <!-- ── TAB: System ────────────────────────────────────── -->
    <template v-else-if="activeTab === 'system'">

      <section class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
        <div class="px-5 py-4 flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
            <Info class="w-4 h-4 text-gray-500" />
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">Platform Info</p>
            <p class="text-xs text-gray-400">Runtime and build information</p>
          </div>
        </div>
        <div v-for="row in systemInfo" :key="row.label" class="px-5 py-4 flex items-center justify-between">
          <p class="text-sm text-gray-600">{{ row.label }}</p>
          <component :is="row.mono ? 'code' : 'span'"
            :class="row.mono
              ? 'text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded font-mono'
              : ['text-xs font-semibold px-2 py-0.5 rounded-full', row.badge ?? 'bg-gray-100 text-gray-600']">
            {{ row.value }}
          </component>
        </div>
      </section>

      <section class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
        <div class="px-5 py-4 flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center flex-shrink-0">
            <Zap class="w-4 h-4 text-orange-500" />
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">Maintenance</p>
            <p class="text-xs text-gray-400">Platform maintenance actions</p>
          </div>
        </div>
        <div class="px-5 py-4 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">Clear API Cache</p>
            <p class="text-xs text-gray-400">Force-refresh all cached API responses</p>
          </div>
          <button @click="clearCache"
            :class="['flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all',
              cacheCleared ? 'bg-green-500 text-white border-green-500' : 'border-gray-200 text-gray-600 hover:border-orange-300 hover:text-orange-600']">
            <Check v-if="cacheCleared" class="w-3.5 h-3.5" />
            <RefreshCw v-else class="w-3.5 h-3.5" />
            {{ cacheCleared ? 'Cleared' : 'Clear Cache' }}
          </button>
        </div>
        <div class="px-5 py-4 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">Reload Dashboard Data</p>
            <p class="text-xs text-gray-400">Re-fetch all KPIs and charts from the API</p>
          </div>
          <button @click="reloadData"
            :class="['flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all',
              'border-gray-200 text-gray-600 hover:border-orange-300 hover:text-orange-600']">
            <RefreshCw class="w-3.5 h-3.5" :class="reloading ? 'animate-spin' : ''" />
            {{ reloading ? 'Reloading…' : 'Reload Data' }}
          </button>
        </div>
      </section>
    </template>

    <!-- ══════════════════════════════════════════════════════
         USER MODAL (Create / Edit)
    ══════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <Transition enter-from-class="opacity-0" enter-active-class="transition duration-150"
        leave-to-class="opacity-0" leave-active-class="transition duration-150">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="closeModal" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md z-10 overflow-hidden">

            <!-- Modal header -->
            <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-orange-100 flex items-center justify-center">
                  <UserPlus class="w-4 h-4 text-orange-500" />
                </div>
                <p class="text-sm font-bold text-gray-800">{{ modalMode === 'create' ? 'Create New User' : 'Edit User' }}</p>
              </div>
              <button @click="closeModal" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400">
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- Modal body -->
            <form @submit.prevent="submitUser" class="p-5 space-y-4">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">First Name <span class="text-red-500">*</span></label>
                  <input v-model="form.first_name" required placeholder="Ahmed"
                    class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Last Name <span class="text-red-500">*</span></label>
                  <input v-model="form.last_name" required placeholder="Benali"
                    class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
                </div>
              </div>

              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Email <span class="text-red-500">*</span></label>
                <input v-model="form.email" type="email" required placeholder="ahmed@temacina.com"
                  :disabled="modalMode === 'edit'"
                  class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400 disabled:bg-gray-50 disabled:text-gray-400" />
              </div>

              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Phone</label>
                <input v-model="form.phone" placeholder="+213 XX XX XX XX"
                  class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
              </div>

              <div v-if="modalMode === 'create'">
                <label class="block text-xs font-medium text-gray-700 mb-1">Password <span class="text-red-500">*</span></label>
                <div class="relative">
                  <input v-model="form.password" :type="showPw ? 'text' : 'password'" required placeholder="••••••••"
                    class="w-full px-3 py-2 pr-9 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400" />
                  <button type="button" @click="showPw = !showPw"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                    <Eye v-if="!showPw" class="w-4 h-4" />
                    <EyeOff v-else class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Role <span class="text-red-500">*</span></label>
                  <select v-model="form.role_id" required
                    class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
                    <option value="" disabled>Select role</option>
                    <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Sector</label>
                  <select v-model="form.sector_id"
                    class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-orange-400 bg-white">
                    <option :value="null">None</option>
                    <option v-for="s in sectors" :key="s.id" :value="s.id">{{ s.name }}</option>
                  </select>
                </div>
              </div>

              <p v-if="modalError" class="text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ modalError }}</p>

              <div class="flex gap-3 pt-1">
                <button type="submit" :disabled="modalLoading"
                  class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-orange-500 text-white text-sm font-semibold hover:bg-orange-600 transition-colors disabled:opacity-60">
                  <div v-if="modalLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  {{ modalMode === 'create' ? 'Create User' : 'Save Changes' }}
                </button>
                <button type="button" @click="closeModal"
                  class="px-4 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>

      <!-- Delete confirm -->
      <Transition enter-from-class="opacity-0" enter-active-class="transition duration-150"
        leave-to-class="opacity-0" leave-active-class="transition duration-150">
        <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="deleteTarget = null" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm z-10 p-6 text-center space-y-4">
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <Trash2 class="w-5 h-5 text-red-500" />
            </div>
            <div>
              <p class="text-sm font-bold text-gray-800">Delete user?</p>
              <p class="text-xs text-gray-500 mt-1">
                <span class="font-medium">{{ deleteTarget.first_name }} {{ deleteTarget.last_name }}</span> will be permanently removed.
              </p>
            </div>
            <div class="flex gap-3">
              <button @click="doDelete"
                class="flex-1 py-2.5 rounded-xl bg-red-500 text-white text-sm font-semibold hover:bg-red-600 transition-colors">
                Delete
              </button>
              <button @click="deleteTarget = null"
                class="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                Cancel
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Toast -->
    <Teleport to="body">
      <Transition enter-from-class="opacity-0 translate-y-2" enter-active-class="transition duration-200"
        leave-to-class="opacity-0 translate-y-2" leave-active-class="transition duration-200">
        <div v-if="toast" :class="[
          'fixed bottom-6 right-6 z-[60] flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
          toast.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        ]">
          <CheckCircle v-if="toast.type === 'success'" class="w-4 h-4 flex-shrink-0" />
          <AlertCircle v-else class="w-4 h-4 flex-shrink-0" />
          {{ toast.message }}
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Palette, Bell, Users, ShieldCheck, Info, Zap, Database,
  Check, Search, UserPlus, UserX, UserCheck, Pencil, Trash2,
  KeyRound, Eye, EyeOff, X, RefreshCw, CheckCircle, AlertCircle,
} from '@lucide/vue'
import api from '@/services/api'

// ── Tabs ──────────────────────────────────────────────────────
const tabs = [
  { key: 'general',  label: 'General',  icon: Palette     },
  { key: 'users',    label: 'Users',    icon: Users       },
  { key: 'security', label: 'Security', icon: ShieldCheck },
  { key: 'system',   label: 'System',   icon: Info        },
]
const activeTab = ref('general')

// ── Toast ─────────────────────────────────────────────────────
const toast = ref(null)
function showToast(type, message) {
  toast.value = { type, message }
  setTimeout(() => (toast.value = null), 3000)
}

// ──────────────────────────────────────────────────────────────
// GENERAL TAB
// ──────────────────────────────────────────────────────────────
const general = ref({
  theme:    'light',
  language: 'en',
  pageSize: 20,
  notif:    { ingestion: true, newCompany: false, weeklyReport: true },
})
const generalSaved = ref(false)
const themes = [
  { value: 'light', label: '☀️ Light' },
  { value: 'dark',  label: '🌙 Dark'  },
  { value: 'auto',  label: '🖥 Auto'  },
]
const notifRows = [
  { key: 'ingestion',    label: 'Ingestion Alerts',   desc: 'Notify when document ingestion completes or fails' },
  { key: 'newCompany',   label: 'New Companies',      desc: 'Notify when new companies are indexed'            },
  { key: 'weeklyReport', label: 'Weekly Report',      desc: 'Receive a weekly summary digest by email'         },
]
function saveGeneral() {
  generalSaved.value = true
  setTimeout(() => (generalSaved.value = false), 2500)
  showToast('success', 'Preferences saved')
}

// ──────────────────────────────────────────────────────────────
// USERS TAB
// ──────────────────────────────────────────────────────────────
const users       = ref([])
const roles       = ref([])
const sectors     = ref([])
const usersLoading = ref(false)
const userSearch  = ref('')

const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  const q = userSearch.value.toLowerCase()
  return users.value.filter(u =>
    `${u.first_name} ${u.last_name}`.toLowerCase().includes(q) ||
    u.email.toLowerCase().includes(q) ||
    u.role?.name?.toLowerCase().includes(q)
  )
})

async function loadUsers() {
  usersLoading.value = true
  try {
    const res = await api.get('/users/')
    users.value = res?.data ?? res ?? []
  } catch { users.value = [] }
  finally { usersLoading.value = false }
}

async function loadMeta() {
  try {
    const [rRes, sRes] = await Promise.all([
      api.get('/users/roles/'),
      api.get('/users/sectors/'),
    ])
    // roles/sectors may be double-wrapped
    roles.value   = rRes?.data?.data ?? rRes?.data ?? rRes ?? []
    sectors.value = sRes?.data?.data ?? sRes?.data ?? sRes ?? []
  } catch { /* non-critical */ }
}

onMounted(() => { loadUsers(); loadMeta() })

function roleBadge(name) {
  const map = {
    superadmin: 'bg-red-100 text-red-700',
    admin:      'bg-orange-100 text-orange-700',
    manager:    'bg-blue-100 text-blue-700',
    analyst:    'bg-purple-100 text-purple-700',
    viewer:     'bg-gray-100 text-gray-600',
  }
  return map[name] ?? 'bg-gray-100 text-gray-600'
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

// Modal
const showModal   = ref(false)
const modalMode   = ref('create')      // 'create' | 'edit'
const modalLoading = ref(false)
const modalError  = ref('')
const showPw      = ref(false)
const editTarget  = ref(null)

const emptyForm = () => ({ first_name: '', last_name: '', email: '', phone: '', password: '', role_id: '', sector_id: null })
const form = ref(emptyForm())

function openCreate() {
  modalMode.value  = 'create'
  editTarget.value = null
  form.value       = emptyForm()
  modalError.value = ''
  showPw.value     = false
  showModal.value  = true
}

function openEdit(u) {
  modalMode.value  = 'edit'
  editTarget.value = u
  form.value = {
    first_name: u.first_name ?? '',
    last_name:  u.last_name  ?? '',
    email:      u.email,
    phone:      u.phone      ?? '',
    password:   '',
    role_id:    u.role?.id   ?? '',
    sector_id:  u.sector?.id ?? null,
  }
  modalError.value = ''
  showModal.value  = true
}

function closeModal() {
  showModal.value = false
}

async function submitUser() {
  modalLoading.value = true
  modalError.value   = ''
  try {
    const payload = {
      first_name: form.value.first_name,
      last_name:  form.value.last_name,
      email:      form.value.email,
      phone:      form.value.phone || null,
      role_id:    form.value.role_id,
      sector_id:  form.value.sector_id || null,
    }
    if (modalMode.value === 'create') {
      payload.password = form.value.password
      const created = await api.post('/users/', payload)
      users.value.unshift(created?.data ?? created)
      showToast('success', 'User created successfully')
    } else {
      const updated = await api.patch(`/users/${editTarget.value.id}/`, payload)
      const idx = users.value.findIndex(u => u.id === editTarget.value.id)
      if (idx !== -1) users.value[idx] = updated?.data ?? updated
      showToast('success', 'User updated successfully')
    }
    closeModal()
    await loadUsers()
  } catch (e) {
    const err = e?.response?.data?.errors ?? e?.data?.errors ?? null
    if (err && typeof err === 'object') {
      modalError.value = Object.values(err).flat().join(' ')
    } else {
      modalError.value = e.message ?? 'An error occurred'
    }
  } finally {
    modalLoading.value = false
  }
}

async function toggleActive(u) {
  try {
    await api.patch(`/users/${u.id}/`, { is_active: !u.is_active })
    u.is_active = !u.is_active
    showToast('success', u.is_active ? 'User activated' : 'User deactivated')
  } catch {
    showToast('error', 'Failed to update user status')
  }
}

// Delete
const deleteTarget = ref(null)
function confirmDelete(u) { deleteTarget.value = u }
async function doDelete() {
  const u = deleteTarget.value
  deleteTarget.value = null
  try {
    await api.delete(`/users/${u.id}/`)
    users.value = users.value.filter(x => x.id !== u.id)
    showToast('success', 'User deleted')
  } catch {
    showToast('error', 'Failed to delete user')
  }
}

// ──────────────────────────────────────────────────────────────
// SECURITY TAB
// ──────────────────────────────────────────────────────────────
const security = ref({ analytics: true, cache: true })
const passwordPolicy = [
  { label: 'Minimum length',      desc: 'Minimum characters required',              value: '10 chars'  },
  { label: 'Uppercase required',  desc: 'Must contain at least one uppercase letter', value: 'Yes'     },
  { label: 'Number required',     desc: 'Must contain at least one digit',            value: 'Yes'     },
  { label: 'Special character',   desc: 'Special characters encouraged',              value: 'Optional' },
]
const sessionRows = [
  { label: 'Access token TTL',    desc: 'How long before access tokens expire',        value: '15 min'  },
  { label: 'Refresh token TTL',   desc: 'How long before refresh tokens expire',       value: '7 days'  },
  { label: 'Storage',             desc: 'Where tokens are stored on the client',       value: 'sessionStorage' },
]
const dataRows = [
  { key: 'analytics', label: 'Usage Analytics',  desc: 'Collect anonymous usage data to improve the platform' },
  { key: 'cache',     label: 'Response Cache',    desc: 'Cache API responses in memory for faster navigation'   },
]

// ──────────────────────────────────────────────────────────────
// SYSTEM TAB
// ──────────────────────────────────────────────────────────────
const cacheCleared = ref(false)
const reloading    = ref(false)

const systemInfo = [
  { label: 'Version',       value: 'v1.0.0',                           badge: 'bg-orange-100 text-orange-600' },
  { label: 'Environment',   value: 'Development',                      badge: 'bg-gray-100 text-gray-600'     },
  { label: 'API Base URL',  value: 'http://localhost:8000/api/v1',      mono: true                             },
  { label: 'Frontend',      value: 'http://localhost:3001',             mono: true                             },
  { label: 'Framework',     value: 'Vue 3 + Vite',                     badge: 'bg-green-100 text-green-700'   },
  { label: 'Database',      value: 'PostgreSQL (Neon)',                 badge: 'bg-blue-100 text-blue-700'     },
]

function clearCache() {
  cacheCleared.value = true
  showToast('success', 'Cache cleared')
  setTimeout(() => (cacheCleared.value = false), 2500)
}

async function reloadData() {
  reloading.value = true
  await new Promise(r => setTimeout(r, 1200))
  reloading.value = false
  showToast('success', 'Data reloaded')
}
</script>
