<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { listProviderConfigs } from '../api/providerConfigs'
import { listRuns } from '../api/runs'
import { listSuites } from '../api/suites'

const loading = ref(true)
const error = ref('')
const providerCount = ref(0)
const suiteCount = ref(0)
const runCount = ref(0)

onMounted(async () => {
  loading.value = true
  error.value = ''
  const [providers, suites, runs] = await Promise.allSettled([
    listProviderConfigs(),
    listSuites(),
    listRuns(),
  ])

  if (providers.status === 'fulfilled') {
    providerCount.value = providers.value.length
  }
  if (suites.status === 'fulfilled') {
    suiteCount.value = suites.value.length
  }
  if (runs.status === 'fulfilled') {
    runCount.value = runs.value.length
  }
  if ([providers, suites, runs].some((item) => item.status === 'rejected')) {
    error.value = '部分数据加载失败，请确认后端服务和 /api 接口是否可用。'
  }
  loading.value = false
})
</script>

<template>
  <section class="page-stack">
    <header class="page-header">
      <div>
        <p class="eyebrow">Dashboard</p>
        <h1>评估工作台</h1>
        <p>集中管理模型 API 配置、测试集和评估运行。</p>
      </div>
      <RouterLink class="primary-button" to="/runs">创建评估任务</RouterLink>
    </header>

    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="loading" class="muted">正在加载工作台数据...</p>

    <section class="metric-grid">
      <article><strong>{{ providerCount }}</strong><span>API 配置</span></article>
      <article><strong>{{ suiteCount }}</strong><span>测试集</span></article>
      <article><strong>{{ runCount }}</strong><span>评估任务</span></article>
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>推荐流程</h2>
          <p>按顺序完成配置、测试集、运行和报告检查。</p>
        </div>
      </div>
      <div class="step-list">
        <RouterLink to="/providers">1. 配置 OpenAI-compatible API</RouterLink>
        <RouterLink to="/suites">2. 创建 JSON 测试集</RouterLink>
        <RouterLink to="/runs">3. 发起评估任务</RouterLink>
      </div>
    </section>
  </section>
</template>
