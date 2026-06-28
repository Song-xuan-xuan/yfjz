<script setup lang="ts">
import type { CaseResult } from '../api/types'
import StatusBadge from './StatusBadge.vue'

defineProps<{
  results: CaseResult[]
  errorMessage?: string
}>()
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h2>样本结果</h2>
        <p>长文本会自动换行，便于检查模型原始输出。</p>
      </div>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <div v-if="!results.length" class="empty-state">暂无样本结果。</div>
    <div v-else class="table-wrap">
      <table class="data-table case-table">
        <thead>
          <tr>
            <th>Case ID</th>
            <th>状态</th>
            <th>Prompt</th>
            <th>期望</th>
            <th>输出</th>
            <th>得分</th>
            <th>原因</th>
            <th>延迟</th>
            <th>缓存</th>
            <th>错误</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in results" :key="item.id">
            <td>{{ item.case_id }}</td>
            <td><StatusBadge :status="item.status" /></td>
            <td class="text-cell">{{ item.prompt }}</td>
            <td class="text-cell">{{ item.expected }}</td>
            <td class="text-cell">{{ item.output || '-' }}</td>
            <td>{{ item.score }}</td>
            <td class="text-cell">{{ item.reason }}</td>
            <td>{{ item.latency_ms == null ? '-' : `${item.latency_ms} ms` }}</td>
            <td>{{ item.cache_hit ? '是' : '否' }}</td>
            <td class="text-cell">{{ item.error_message || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
