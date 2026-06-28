<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { getHealth } from '../api/client'

const healthState = ref<'checking' | 'online' | 'offline'>('checking')

const navItems = [
  { label: 'Dashboard', to: '/' },
  { label: 'API 配置', to: '/providers' },
  { label: '测试集', to: '/suites' },
  { label: '评估任务', to: '/runs' },
]

onMounted(async () => {
  try {
    await getHealth()
    healthState.value = 'online'
  } catch {
    healthState.value = 'offline'
  }
})
</script>

<template>
  <div class="layout">
    <aside class="sidebar" aria-label="主导航">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">Y</span>
        <div>
          <strong>yfjz</strong>
          <small>LLM 评估工作台</small>
        </div>
      </div>

      <nav class="nav-list">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to">
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="connection" :class="healthState">
        <span aria-hidden="true"></span>
        <p>
          后端连接
          <strong>{{ healthState === 'online' ? '正常' : healthState === 'offline' ? '不可用' : '检测中' }}</strong>
        </p>
      </div>
    </aside>

    <main class="main-panel">
      <RouterView />
    </main>
  </div>
</template>
