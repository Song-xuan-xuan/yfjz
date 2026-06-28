<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getRun, getRunResults } from '../api/runs'
import type { CaseResult, RunDetail } from '../api/types'
import CaseResultsTable from '../components/CaseResultsTable.vue'
import ProgressSummary from '../components/ProgressSummary.vue'
import ReportCharts from '../components/ReportCharts.vue'

const route = useRoute()
const run = ref<RunDetail | null>(null)
const results = ref<CaseResult[]>([])
const loading = ref(true)
const error = ref('')
const resultsError = ref('')
let poller: number | undefined

function shouldPoll(current: RunDetail): boolean {
  return current.status === 'pending' || current.status === 'running'
}

async function loadRun() {
  error.value = ''
  try {
    const runId = Number(route.params.id)
    run.value = await getRun(runId)
    try {
      results.value = await getRunResults(runId)
      resultsError.value = ''
    } catch (err) {
      resultsError.value = err instanceof Error ? err.message : '样本结果加载失败'
    }
    if (run.value && !shouldPoll(run.value) && poller) {
      window.clearInterval(poller)
      poller = undefined
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '运行详情加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadRun()
  if (run.value && shouldPoll(run.value)) {
    poller = window.setInterval(loadRun, 1500)
  }
})

onUnmounted(() => {
  if (poller) {
    window.clearInterval(poller)
  }
})
</script>

<template>
  <section class="page-stack">
    <header class="page-header">
      <div>
        <p class="eyebrow">Run Detail</p>
        <h1>运行详情 #{{ route.params.id }}</h1>
        <p>pending / running 状态下每 1.5 秒自动刷新。</p>
      </div>
      <RouterLink class="ghost-button" to="/runs">返回任务</RouterLink>
    </header>

    <p v-if="loading" class="muted">正在加载运行详情...</p>
    <p v-if="error" class="error-message">{{ error }}</p>

    <template v-if="run">
      <ProgressSummary :run="run" />
      <ReportCharts :run="run" />
      <CaseResultsTable :error-message="resultsError" :results="results" />
    </template>
  </section>
</template>
