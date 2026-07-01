<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const mobileMenuOpen = ref(false)

const navItems = [
  { path: '/admin', label: 'Dashboard', icon: '📊', desc: '数据概览' },
  { path: '/admin/characters', label: 'Characters', icon: '👥', desc: 'CRUD 管理' },
]

function isActive(path) {
  if (path === '/admin') return route.path === '/admin'
  return route.path.startsWith(path)
}

function navigate(path) {
  mobileMenuOpen.value = false
  router.push(path)
}
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-slate-100">
    <!-- 移动端遮罩 -->
    <div v-if="mobileMenuOpen" class="fixed inset-0 bg-black/50 z-40 lg:hidden" @click="mobileMenuOpen = false" />

    <!-- 侧边栏 -->
    <aside
      :class="[
        'fixed lg:static inset-y-0 left-0 z-50 w-64 bg-[#0f0f23] text-white flex flex-col transition-transform duration-300',
        mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <div class="p-6 border-b border-white/10">
        <div class="flex items-center gap-3 cursor-pointer" @click="navigate('/admin')">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-xl">⚜</div>
          <div>
            <h1 class="text-lg font-bold tracking-wider text-amber-400 font-['IM_Fell_English_SC']">Admin Panel</h1>
            <p class="text-xs text-gray-500">Genshin Archive</p>
          </div>
        </div>
      </div>

      <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
        <p class="px-3 py-2 text-xs uppercase tracking-widest text-gray-500">Management</p>
        <button v-for="item in navItems" :key="item.path" @click="navigate(item.path)"
          :class="[
            'w-full flex items-center gap-3 px-3 py-3 rounded-xl text-left transition-all duration-200',
            isActive(item.path) ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                                : 'text-gray-400 hover:bg-white/5 hover:text-white'
          ]">
          <span class="text-xl">{{ item.icon }}</span>
          <div>
            <div class="text-sm font-semibold">{{ item.label }}</div>
            <div class="text-xs opacity-60">{{ item.desc }}</div>
          </div>
          <div v-if="isActive(item.path)" class="ml-auto w-1.5 h-8 rounded-full bg-amber-400" />
        </button>
      </nav>

      <div class="p-4 border-t border-white/10">
        <a href="/" class="block text-center text-xs text-amber-400 hover:text-amber-300 transition mb-2">← Back to Site</a>
        <p class="text-xs text-gray-600 text-center">Crafted by ZMM · 清风玉露</p>
        <p class="text-xs text-gray-700 text-center mt-1">Vue 3 + FastAPI + MySQL</p>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col min-w-0">
      <header class="h-16 bg-white border-b border-gray-200 flex items-center px-4 gap-4 shrink-0 shadow-sm">
        <button @click="mobileMenuOpen = !mobileMenuOpen" class="lg:hidden p-2 rounded-lg hover:bg-gray-100">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <div class="flex items-center gap-2 text-sm text-gray-500">
          <span class="text-amber-500">⚜</span>
          <span>/</span>
          <span class="text-gray-700 font-semibold">{{ route.meta.title || 'Admin' }}</span>
        </div>
        <div class="ml-auto">
          <a href="http://localhost:8000/docs" target="_blank"
            class="text-xs px-3 py-1.5 rounded-lg bg-green-50 text-green-700 border border-green-200 hover:bg-green-100 transition">
            API Docs ↗
          </a>
        </div>
      </header>
      <main class="flex-1 overflow-y-auto p-4 md:p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>
