<template>
  <div class="p-6 max-w-5xl mx-auto">

    <!-- ── Page Header ── -->
    <div class="mb-8">
      <div class="flex items-center gap-2 mb-1">
        <div class="w-7 h-7 rounded-lg bg-orange-100 flex items-center justify-center">
          <LifeBuoy class="w-4 h-4 text-orange-500" />
        </div>
        <h1 class="text-xl font-bold text-gray-900">Centre d'aide</h1>
      </div>
      <p class="text-sm text-gray-400 ml-9">
        Trouvez des réponses, consultez la documentation ou contactez notre équipe.
      </p>
    </div>

    <!-- ── Search ── -->
    <div class="relative mb-8 max-w-xl">
      <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      <input
        v-model="searchQ"
        type="text"
        placeholder="Rechercher dans la documentation…"
        class="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-300 transition shadow-sm"
      />
    </div>

    <!-- ── Quick links ── -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-8">
      <button
        v-for="q in QUICK_LINKS" :key="q.label"
        class="flex items-center gap-3 px-4 py-3.5 bg-white border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:border-orange-300 hover:bg-orange-50 hover:text-orange-700 transition text-left group"
        @click="activeSection = q.section; activeArticle = q.article ?? null"
      >
        <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition"
             :class="q.iconBg + ' group-hover:bg-orange-100'">
          <component :is="q.icon" class="w-4 h-4 transition" :class="q.iconColor + ' group-hover:text-orange-500'" />
        </div>
        {{ q.label }}
        <ChevronRight class="w-3.5 h-3.5 ml-auto text-gray-300 group-hover:text-orange-400 transition" />
      </button>
    </div>

    <!-- ── Main: sidebar + content ── -->
    <div class="flex gap-6 items-start">

     
      <!-- Content area -->
      <div class="flex-1 min-w-0">

        <!-- Article list -->
        <template v-if="!activeArticle">

          <!-- Search results -->
          <template v-if="searchQ.trim()">
            <div v-if="searchResults.length === 0" class="text-center py-16 text-gray-400">
              <Search class="w-8 h-8 mx-auto mb-3 opacity-30" />
              <p class="text-sm font-medium">Aucun résultat pour « {{ searchQ }} »</p>
            </div>
            <div v-else class="space-y-2">
              <ArticleCard
                v-for="a in searchResults" :key="a.id"
                :article="a"
                :section-label="sectionOf(a.section)"
                @click="activeSection = a.section; activeArticle = a.id"
              />
            </div>
          </template>

          <!-- Normal list -->
          <template v-else>
            <div class="space-y-2">
              <ArticleCard
                v-for="a in visibleArticles" :key="a.id"
                :article="a"
                @click="activeArticle = a.id"
              />
            </div>
          </template>
        </template>

        <!-- Article detail -->
        <template v-else>
          <button
            class="inline-flex items-center gap-1.5 text-xs text-gray-400 hover:text-orange-500 transition mb-4 font-medium"
            @click="activeArticle = null"
          >
            <ChevronLeft class="w-3.5 h-3.5" /> Retour
          </button>

          <div class="bg-white border border-gray-200 rounded-xl p-6">
            <div class="flex items-start justify-between gap-4 mb-5">
              <div>
                <span class="text-xs font-semibold text-orange-500 uppercase tracking-wide">
                  {{ currentSection?.label }}
                </span>
                <h2 class="text-lg font-bold text-gray-900 mt-0.5">{{ currentArticle?.title }}</h2>
              </div>
              <span v-if="currentArticle?.tag" :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border', TAG_STYLE[currentArticle.tag]]">
                {{ currentArticle.tag }}
              </span>
            </div>

            <div class="prose-help" v-html="currentArticle?.body" />

            <div class="mt-6 pt-5 border-t border-gray-100 flex items-center justify-between">
              <p class="text-xs text-gray-400">Cette page vous a-t-elle aidé ?</p>
              <div class="flex gap-2">
                <button
                  :class="['inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition',
                    feedback === 'yes' ? 'bg-green-50 border-green-300 text-green-700' : 'border-gray-200 text-gray-500 hover:border-green-300 hover:text-green-600']"
                  @click="feedback = 'yes'"
                >
                  <ThumbsUp class="w-3.5 h-3.5" /> Oui
                </button>
                <button
                  :class="['inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition',
                    feedback === 'no' ? 'bg-red-50 border-red-300 text-red-700' : 'border-gray-200 text-gray-500 hover:border-red-300 hover:text-red-600']"
                  @click="feedback = 'no'"
                >
                  <ThumbsDown class="w-3.5 h-3.5" /> Non
                </button>
              </div>
            </div>
            <p v-if="feedback" class="text-xs text-gray-400 mt-2 text-right">
              Merci pour votre retour !
            </p>
          </div>
        </template>

      </div>
    </div>

    <!-- ── Contact / support band ── -->
    <div class="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div
        v-for="c in CONTACT_CARDS" :key="c.title"
        class="bg-white border border-gray-200 rounded-xl p-5 flex flex-col gap-3"
      >
        <div :class="['w-9 h-9 rounded-lg flex items-center justify-center', c.iconBg]">
          <component :is="c.icon" :class="['w-4 h-4', c.iconColor]" />
        </div>
        <div>
          <p class="text-sm font-semibold text-gray-900">{{ c.title }}</p>
          <p class="text-xs text-gray-400 mt-0.5 leading-relaxed">{{ c.desc }}</p>
        </div>
        <a
          :href="c.href"
          :class="['mt-auto inline-flex items-center gap-1.5 text-xs font-semibold transition', c.linkColor]"
        >
          {{ c.action }} <ArrowRight class="w-3.5 h-3.5" />
        </a>
      </div>
    </div>

    <!-- ── Bot widget ── -->
    <Transition name="bot-slide">
      <div
        v-if="botOpen"
        class="fixed bottom-24 right-6 z-50 w-80 bg-white border border-gray-200 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
        style="max-height: 440px"
      >
        <div class="flex items-center gap-3 px-4 py-3 bg-orange-500">
          <div class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot class="w-4 h-4 text-white" />
          </div>
          <div class="flex-1">
            <p class="text-xs font-semibold text-white">Assistant Temacina</p>
            <p class="text-[10px] text-orange-100">Répondez à vos questions instantanément</p>
          </div>
          <button class="text-white/70 hover:text-white transition" @click="botOpen = false">
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- Messages -->
        <div ref="chatEl" class="flex-1 overflow-y-auto px-4 py-3 space-y-3 bg-gray-50">
          <div
            v-for="(m, i) in botMessages" :key="i"
            :class="['flex gap-2', m.from === 'user' ? 'justify-end' : 'justify-start']"
          >
            <div v-if="m.from === 'bot'" class="w-6 h-6 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0 mt-0.5">
              <Bot class="w-3 h-3 text-orange-500" />
            </div>
            <div
              :class="[
                'max-w-[200px] px-3 py-2 rounded-xl text-xs leading-relaxed',
                m.from === 'user'
                  ? 'bg-orange-500 text-white rounded-tr-sm'
                  : 'bg-white border border-gray-200 text-gray-700 rounded-tl-sm shadow-sm'
              ]"
            >{{ m.text }}</div>
          </div>
          <div v-if="botTyping" class="flex gap-2">
            <div class="w-6 h-6 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
              <Bot class="w-3 h-3 text-orange-500" />
            </div>
            <div class="bg-white border border-gray-200 rounded-xl rounded-tl-sm px-3 py-2 shadow-sm">
              <span class="flex gap-1 items-center h-4">
                <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:0ms" />
                <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:150ms" />
                <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:300ms" />
              </span>
            </div>
          </div>
        </div>

        <!-- Suggestions -->
        <div v-if="botMessages.length <= 1" class="px-4 py-2 border-t border-gray-100 bg-white flex flex-wrap gap-1.5">
          <button
            v-for="s in BOT_SUGGESTIONS" :key="s"
            class="text-[11px] px-2.5 py-1 bg-orange-50 text-orange-600 border border-orange-200 rounded-lg hover:bg-orange-100 transition font-medium"
            @click="sendBot(s)"
          >{{ s }}</button>
        </div>

        <!-- Input -->
        <div class="flex items-center gap-2 px-4 py-3 border-t border-gray-100 bg-white">
          <input
            v-model="botInput"
            type="text"
            placeholder="Posez votre question…"
            class="flex-1 text-xs px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-300 transition"
            @keydown.enter="sendBot(botInput)"
          />
          <button
            class="w-8 h-8 bg-orange-500 hover:bg-orange-600 rounded-lg flex items-center justify-center transition flex-shrink-0"
            @click="sendBot(botInput)"
          >
            <Send class="w-3.5 h-3.5 text-white" />
          </button>
        </div>
      </div>
    </Transition>

    <!-- Bot FAB -->
    <button
      class="fixed bottom-6 right-6 z-50 w-14 h-14 bg-orange-500 hover:bg-orange-600 rounded-full shadow-lg flex items-center justify-center transition"
      @click="botOpen = !botOpen"
    >
      <Transition name="icon-swap" mode="out-in">
        <X v-if="botOpen" class="w-5 h-5 text-white" />
        <Bot v-else class="w-5 h-5 text-white" />
      </Transition>
      <span v-if="!botOpen" class="absolute -top-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full" />
    </button>

  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import {
  LifeBuoy, Search, ChevronRight, ChevronLeft, ArrowRight,
  BookOpen, Rocket, ShieldCheck, Users, BarChart2, Settings,
  Mail, MessageSquare, Phone, Bot, X, Send, ThumbsUp, ThumbsDown,
} from 'lucide-vue-next'

// ── Sub-component: ArticleCard ─────────────────────────────────────────
const ArticleCard = {
  props: { article: Object, sectionLabel: String },
  emits: ['click'],
  template: `
    <div
      class="flex items-center justify-between gap-4 px-4 py-3.5 bg-white border border-gray-200 rounded-xl cursor-pointer hover:border-orange-300 hover:bg-orange-50 transition group"
      @click="$emit('click')"
    >
      <div class="min-w-0">
        <div class="flex items-center gap-2 mb-0.5">
          <span v-if="sectionLabel" class="text-[10px] font-semibold text-orange-400 uppercase tracking-wide">{{ sectionLabel }}</span>
          <span v-if="article.tag" :class="['inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border', TAG_STYLE[article.tag]]">{{ article.tag }}</span>
        </div>
        <p class="text-sm font-medium text-gray-800 truncate">{{ article.title }}</p>
        <p class="text-xs text-gray-400 mt-0.5 truncate">{{ article.summary }}</p>
      </div>
      <ChevronRight class="w-4 h-4 text-gray-300 group-hover:text-orange-400 flex-shrink-0 transition" />
    </div>`,
  setup() { return { ChevronRight, TAG_STYLE } },
}

// ── Constants ──────────────────────────────────────────────────────────

const TAG_STYLE = {
  'Nouveau':    'bg-green-50 text-green-700 border-green-200',
  'Important':  'bg-red-50 text-red-600 border-red-200',
  'API':        'bg-violet-50 text-violet-700 border-violet-200',
  'Admin':      'bg-orange-50 text-orange-700 border-orange-200',
}

const SECTIONS = [
  { id: 'getting-started', label: 'Démarrage',       icon: Rocket,       desc: 'Premiers pas sur la plateforme.' },
  { id: 'users',           label: 'Utilisateurs',    icon: Users,        desc: 'Gérer les comptes et permissions.' },
  { id: 'data',            label: 'Données & Import', icon: BarChart2,   desc: 'Importer et gérer vos données.' },
  { id: 'security',        label: 'Sécurité',         icon: ShieldCheck, desc: 'Rôles, accès et bonnes pratiques.' },
  { id: 'api',             label: 'API & Intégrations',icon: BookOpen,   desc: 'Endpoints REST et webhooks.' },
  { id: 'settings',        label: 'Paramètres',       icon: Settings,    desc: 'Configuration de votre organisation.' },
]

const ARTICLES = [
  // Getting started
  { id: 'gs-1', section: 'getting-started', title: 'Bienvenue sur Temacina',        summary: 'Présentation de la plateforme et de ses fonctionnalités clés.', tag: null,
    body: `<p>Temacina est un annuaire B2B algérien permettant aux entreprises de <strong>gérer leurs données commerciales</strong>, d'importer des catalogues et de collaborer en équipe.</p>
           <h3>Fonctionnalités principales</h3>
           <ul><li>Gestion des entreprises et contacts</li><li>Import de données en masse (CSV, Excel)</li><li>Contrôle des accès par rôle</li><li>Journaux d'audit complets</li><li>Rapports et exports</li></ul>
           <p>Commencez par inviter votre équipe dans <strong>Gestion des utilisateurs</strong>, puis importez vos premières données via <strong>Import de données</strong>.</p>` },
  { id: 'gs-2', section: 'getting-started', title: 'Inviter votre première équipe',  summary: 'Comment ajouter des collaborateurs et définir leurs rôles.', tag: 'Nouveau',
    body: `<p>Rendez-vous dans <strong>Gestion des utilisateurs</strong> et cliquez sur <em>Inviter un utilisateur</em>. Renseignez l'e-mail, le prénom, le nom et le rôle souhaité.</p>
           <h3>Rôles disponibles</h3>
           <ul><li><strong>Lecteur</strong> — consultation uniquement</li><li><strong>Analyste</strong> — lecture + exports</li><li><strong>Manager</strong> — gère son équipe directe</li><li><strong>Admin</strong> — gestion complète sauf super-admins</li><li><strong>Super Admin</strong> — accès total</li></ul>
           <p>Un e-mail de bienvenue est envoyé automatiquement avec un lien pour définir le mot de passe.</p>` },
  { id: 'gs-3', section: 'getting-started', title: 'Naviguer dans l\'interface',     summary: 'Présentation du menu, des raccourcis et de la barre de recherche.', tag: null,
    body: `<p>Le menu latéral gauche donne accès à toutes les sections. La barre de recherche en haut permet de trouver instantanément une entreprise, un document ou un contact.</p>
           <h3>Raccourcis utiles</h3><ul><li><kbd>Ctrl+K</kbd> — ouvrir la recherche globale</li><li><kbd>Ctrl+N</kbd> — créer un nouvel enregistrement</li></ul>` },

  // Users
  { id: 'u-1', section: 'users', title: 'Comprendre les rôles et hiérarchies', summary: 'Tableau complet des permissions par rôle.', tag: null,
    body: `<p>Les permissions suivent une hiérarchie stricte : <strong>Lecteur &lt; Analyste &lt; Manager &lt; Admin &lt; Super Admin</strong>. Un acteur ne peut gérer que des utilisateurs dont le rôle est inférieur au sien.</p>
           <h3>Matrice des permissions</h3>
           <table><thead><tr><th>Action</th><th>Lecteur</th><th>Analyste</th><th>Manager</th><th>Admin</th></tr></thead>
           <tbody>
           <tr><td>Voir les utilisateurs</td><td>—</td><td>—</td><td>Équipe</td><td>✓</td></tr>
           <tr><td>Inviter un utilisateur</td><td>—</td><td>—</td><td>—</td><td>✓</td></tr>
           <tr><td>Changer un rôle</td><td>—</td><td>—</td><td>—</td><td>✓</td></tr>
           <tr><td>Désactiver un compte</td><td>—</td><td>—</td><td>—</td><td>✓</td></tr>
           </tbody></table>` },
  { id: 'u-2', section: 'users', title: 'Désactiver ou supprimer un compte',  summary: 'Différence entre désactivation (réversible) et suppression définitive.', tag: 'Important',
    body: `<p>La <strong>désactivation</strong> rend le compte inaccessible mais conserve toutes les données (historique, logs). Elle est <em>réversible</em>.</p>
           <p>La <strong>suppression définitive</strong> est irréversible et efface les données personnelles conformément au RGPD. Elle nécessite le rôle Super Admin.</p>
           <p>Nous recommandons toujours de désactiver avant de supprimer définitivement.</p>` },
  { id: 'u-3', section: 'users', title: 'Réinitialiser un mot de passe',       summary: 'Envoyer un lien de réinitialisation à un utilisateur.', tag: null,
    body: `<p>Dans le panneau latéral de l'utilisateur, cliquez sur <em>Modifier le profil</em> puis <em>Envoyer un lien de réinitialisation</em>. L'utilisateur reçoit un e-mail valable 24 h.</p>` },

  // Data
  { id: 'd-1', section: 'data', title: 'Importer des données via CSV',         summary: 'Format attendu, encodage et limites de taille.', tag: null,
    body: `<p>Le fichier CSV doit être encodé en <strong>UTF-8</strong>, séparateur virgule ou point-virgule. Taille maximale : <strong>10 Mo</strong> (≈ 100 000 lignes).</p>
           <h3>Colonnes obligatoires</h3><ul><li><code>company_name</code></li><li><code>sector</code></li><li><code>wilaya</code></li></ul>
           <p>Les colonnes supplémentaires sont importées comme champs personnalisés.</p>` },
  { id: 'd-2', section: 'data', title: 'Gérer les doublons lors de l\'import', summary: 'Stratégies de déduplication disponibles.', tag: null,
    body: `<p>Trois stratégies sont disponibles lors de l'import :<br><strong>Ignorer</strong> — les doublons sont skippés.<br><strong>Mettre à jour</strong> — les champs existants sont écrasés.<br><strong>Fusionner</strong> — seuls les champs vides sont complétés.</p>` },
  { id: 'd-3', section: 'data', title: 'Exporter vos données',                 summary: 'Formats d\'export disponibles : CSV, Excel, JSON.', tag: null,
    body: `<p>Depuis n'importe quelle liste, cliquez sur <em>Exporter CSV</em> en haut à droite. Les filtres actifs sont respectés dans l'export. Pour les exports planifiés, contactez l'équipe technique.</p>` },

  // Security
  { id: 's-1', section: 'security', title: 'Authentification à deux facteurs',  summary: 'Activer le 2FA pour votre organisation.', tag: 'Important',
    body: `<p>Le 2FA peut être rendu obligatoire pour tous les utilisateurs depuis <strong>Paramètres → Sécurité</strong>. Les méthodes supportées sont TOTP (Google Authenticator, Authy) et SMS.</p>` },
  { id: 's-2', section: 'security', title: 'Journaux d\'audit',                 summary: 'Surveiller les actions critiques sur la plateforme.', tag: null,
    body: `<p>Les journaux d'audit enregistrent toutes les actions sensibles : connexions, exports, modifications de rôles, suppressions. Accessibles dans <strong>Audit Logs</strong>, ils sont conservés 12 mois.</p>` },

  // API
  { id: 'api-1', section: 'api', title: 'Authentification API (JWT)',           summary: 'Obtenir et utiliser un token d\'accès.', tag: 'API',
    body: `<p>L'API utilise JWT Bearer tokens. Obtenez un token via <code>POST /api/v1/auth/token/</code> avec vos identifiants. Le token expire après <strong>24 h</strong>.</p>
           <pre><code>curl -X POST https://api.temacina.dz/api/v1/auth/token/ \\
  -H "Content-Type: application/json" \\
  -d '{"email":"you@co.dz","password":"***"}'</code></pre>` },
  { id: 'api-2', section: 'api', title: 'Endpoints utilisateurs',              summary: 'Liste des routes REST pour la gestion des comptes.', tag: 'API',
    body: `<p>Base URL : <code>https://api.temacina.dz/api/v1/users/</code></p>
           <table><thead><tr><th>Méthode</th><th>Route</th><th>Description</th></tr></thead>
           <tbody>
           <tr><td>GET</td><td>/users/</td><td>Liste paginée</td></tr>
           <tr><td>POST</td><td>/users/invite/</td><td>Inviter un utilisateur</td></tr>
           <tr><td>PATCH</td><td>/users/:id/</td><td>Modifier un profil</td></tr>
           <tr><td>PATCH</td><td>/users/:id/role/</td><td>Changer le rôle</td></tr>
           <tr><td>DELETE</td><td>/users/:id/</td><td>Désactiver</td></tr>
           </tbody></table>` },
  { id: 'api-3', section: 'api', title: 'Webhooks',                            summary: 'Recevoir des événements en temps réel.', tag: 'Nouveau',
    body: `<p>Configurez une URL de webhook dans <strong>Paramètres → Intégrations</strong>. Les événements disponibles : <code>user.created</code>, <code>user.role_changed</code>, <code>data.imported</code>, <code>export.completed</code>.</p>
           <p>Chaque requête inclut un header <code>X-Temacina-Signature</code> pour vérifier l'authenticité.</p>` },

  // Settings
  { id: 'set-1', section: 'settings', title: 'Configurer votre organisation',  summary: 'Nom, logo, fuseau horaire et langue par défaut.', tag: null,
    body: `<p>Dans <strong>Paramètres → Organisation</strong>, vous pouvez modifier le nom, charger un logo (PNG/SVG, max 2 Mo), choisir le fuseau horaire et la langue d'interface par défaut pour tous les utilisateurs.</p>` },
  { id: 'set-2', section: 'settings', title: 'Gestion des secteurs',           summary: 'Créer et organiser les secteurs d\'activité.', tag: null,
    body: `<p>Les secteurs permettent de catégoriser vos utilisateurs et vos données. Créez-en depuis <strong>Paramètres → Secteurs</strong>. Vous pouvez en définir jusqu'à <strong>50</strong> par organisation.</p>` },
]

const QUICK_LINKS = [
  { label: 'Démarrer rapidement', section: 'getting-started', article: 'gs-1', icon: Rocket,      iconBg: 'bg-orange-50', iconColor: 'text-orange-500' },
  { label: 'Gérer les accès',     section: 'users',           article: 'u-1',  icon: Users,       iconBg: 'bg-blue-50',   iconColor: 'text-blue-500'   }
]

const CONTACT_CARDS = [
  {
    title: 'Envoyer un e-mail',
    desc: 'Contactez l\'équipe support pour toute question technique ou commerciale.',
    icon: Mail, iconBg: 'bg-orange-50', iconColor: 'text-orange-500',
    href: 'mailto:support@temacina.dz', action: 'support@temacina.dz', linkColor: 'text-orange-500 hover:text-orange-600',
  },
  {
    title: 'Assistance téléphonique',
    desc: 'Pour les clients Enterprise. Numéro disponible dans votre contrat.',
    icon: Phone, iconBg: 'bg-blue-50', iconColor: 'text-blue-500',
    href: 'tel:+21321000000', action: '+213 21 00 00 00', linkColor: 'text-blue-600 hover:text-blue-700',
  },
]

const BOT_SUGGESTIONS = ['Comment inviter un utilisateur ?', 'Réinitialiser un mot de passe']

const BOT_RESPONSES = {
  default: 'Je n\'ai pas trouvé de réponse précise. Consultez la documentation ou contactez support@temacina.dz.',
  'inviter': 'Pour inviter un utilisateur, allez dans Gestion des utilisateurs → Inviter un utilisateur. Renseignez l\'e-mail et le rôle souhaité.',
  'mot de passe': 'Pour réinitialiser un mot de passe, ouvrez le profil de l\'utilisateur dans la gestion des utilisateurs et cliquez sur Modifier le profil → Envoyer un lien de réinitialisation.',
  'rôle': 'Les rôles disponibles sont : Lecteur, Analyste, Manager, Admin, Super Admin. Chaque rôle a des permissions croissantes. Consultez la section Utilisateurs pour la matrice complète.',
  'import': 'Pour importer des données, rendez-vous dans Import de données. Le format CSV UTF-8 est supporté jusqu\'à 10 Mo.',
  'export': 'Depuis n\'importe quelle liste, cliquez sur Exporter CSV en haut à droite. Les filtres actifs sont appliqués à l\'export.',
  'audit': 'Les journaux d\'audit se trouvent dans la section Audit Logs. Toutes les actions sensibles y sont enregistrées pendant 12 mois.',
}

// ── State ──────────────────────────────────────────────────────────────

const searchQ       = ref('')
const activeSection = ref('getting-started')
const activeArticle = ref(null)
const feedback      = ref(null)

const botOpen     = ref(false)
const botInput    = ref('')
const botTyping   = ref(false)
const botMessages = ref([
  { from: 'bot', text: 'Bonjour ! Je suis l\'assistant Temacina. Comment puis-je vous aider ?' }
])
const chatEl = ref(null)

// ── Computed ───────────────────────────────────────────────────────────

const currentSection = computed(() => SECTIONS.find(s => s.id === activeSection.value))

const visibleArticles = computed(() =>
  ARTICLES.filter(a => a.section === activeSection.value)
)

const currentArticle = computed(() =>
  ARTICLES.find(a => a.id === activeArticle.value)
)

const searchResults = computed(() => {
  const q = searchQ.value.trim().toLowerCase()
  if (!q) return []
  return ARTICLES.filter(a =>
    a.title.toLowerCase().includes(q) || a.summary.toLowerCase().includes(q)
  )
})

function sectionOf(sectionId) {
  return SECTIONS.find(s => s.id === sectionId)?.label ?? ''
}

// Reset feedback when article changes
watch(activeArticle, () => { feedback.value = null })

// ── Bot logic ──────────────────────────────────────────────────────────

async function sendBot(text) {
  const msg = (typeof text === 'string' ? text : botInput.value).trim()
  if (!msg) return
  botInput.value = ''
  botMessages.value.push({ from: 'user', text: msg })
  botTyping.value = true
  await nextTick()
  scrollChat()

  await new Promise(r => setTimeout(r, 900 + Math.random() * 400))

  const key = Object.keys(BOT_RESPONSES).find(k => k !== 'default' && msg.toLowerCase().includes(k))
  botMessages.value.push({ from: 'bot', text: BOT_RESPONSES[key ?? 'default'] })
  botTyping.value = false
  await nextTick()
  scrollChat()
}

function scrollChat() {
  if (chatEl.value) chatEl.value.scrollTop = chatEl.value.scrollHeight
}
</script>

<style scoped>
/* Prose styles for article bodies */
.prose-help :deep(p)      { @apply text-sm text-gray-600 leading-relaxed mb-3; }
.prose-help :deep(h3)     { @apply text-sm font-semibold text-gray-900 mt-5 mb-2; }
.prose-help :deep(ul)     { @apply list-disc list-inside space-y-1 mb-3; }
.prose-help :deep(li)     { @apply text-sm text-gray-600; }
.prose-help :deep(pre)    { @apply bg-gray-900 text-green-300 text-xs rounded-xl p-4 overflow-x-auto mb-3 font-mono; }
.prose-help :deep(code)   { @apply bg-gray-100 text-orange-600 text-xs px-1.5 py-0.5 rounded font-mono; }
.prose-help :deep(pre code) { @apply bg-transparent text-green-300 p-0; }
.prose-help :deep(kbd)    { @apply bg-gray-100 border border-gray-300 text-gray-700 text-xs px-1.5 py-0.5 rounded font-mono; }
.prose-help :deep(strong) { @apply font-semibold text-gray-800; }
.prose-help :deep(table)  { @apply w-full text-xs border-collapse mt-3 mb-4; }
.prose-help :deep(th)     { @apply px-3 py-2 bg-gray-50 text-gray-500 font-semibold text-left border border-gray-200; }
.prose-help :deep(td)     { @apply px-3 py-2 text-gray-600 border border-gray-200; }

/* Bot slide */
.bot-slide-enter-active, .bot-slide-leave-active { transition: transform 250ms ease, opacity 250ms ease; }
.bot-slide-enter-from, .bot-slide-leave-to       { transform: translateY(16px); opacity: 0; }

/* Icon swap */
.icon-swap-enter-active, .icon-swap-leave-active { transition: opacity 150ms ease; }
.icon-swap-enter-from, .icon-swap-leave-to       { opacity: 0; }
</style>