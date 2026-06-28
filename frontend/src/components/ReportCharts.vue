<script setup lang="ts">
import type { RunDetail } from '../api/types'

defineProps<{
  run: RunDetail
}>()

function ratio(value: number, total: number): string {
  if (!total) {
    return '0%'
  }
  return `${Math.round((value / total) * 100)}%`
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h2>报告概览</h2>
        <p>用简洁条形图展示通过、失败和错误占比。</p>
      </div>
    </div>

    <div class="chart-row">
      <span>通过</span>
      <div><i class="bar passed" :style="{ width: ratio(run.passed_cases, run.total_cases) }"></i></div>
      <strong>{{ run.passed_cases }}</strong>
    </div>
    <div class="chart-row">
      <span>失败</span>
      <div><i class="bar failed" :style="{ width: ratio(run.failed_cases, run.total_cases) }"></i></div>
      <strong>{{ run.failed_cases }}</strong>
    </div>
    <div class="chart-row">
      <span>错误</span>
      <div><i class="bar error" :style="{ width: ratio(run.error_cases, run.total_cases) }"></i></div>
      <strong>{{ run.error_cases }}</strong>
    </div>
  </section>
</template>
