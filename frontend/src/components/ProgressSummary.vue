<script setup lang="ts">
import type { RunDetail } from '../api/types'
import StatusBadge from './StatusBadge.vue'

defineProps<{
  run: RunDetail
}>()

function percent(run: RunDetail): number {
  if (!run.total_cases) {
    return 0
  }
  return Math.round((run.completed_cases / run.total_cases) * 100)
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h2>运行进度</h2>
        <p>模型：{{ run.model }}</p>
      </div>
      <StatusBadge :status="run.status" />
    </div>

    <div class="progress-track" aria-label="运行完成度">
      <span :style="{ width: `${percent(run)}%` }"></span>
    </div>

    <div class="metric-grid">
      <div><strong>{{ run.total_cases }}</strong><span>总样本</span></div>
      <div><strong>{{ run.completed_cases }}</strong><span>已完成</span></div>
      <div><strong>{{ run.passed_cases }}</strong><span>通过</span></div>
      <div><strong>{{ run.failed_cases }}</strong><span>失败</span></div>
      <div><strong>{{ run.error_cases }}</strong><span>错误</span></div>
      <div><strong>{{ (run.score * 100).toFixed(1) }}%</strong><span>得分</span></div>
      <div><strong>{{ run.average_latency_ms ?? 0 }}</strong><span>平均延迟 ms</span></div>
      <div><strong>{{ run.cache_hit_count ?? 0 }}</strong><span>缓存命中</span></div>
    </div>
  </section>
</template>
