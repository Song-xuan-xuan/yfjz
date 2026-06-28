<script setup lang="ts">
import type { CaseResultStatus, RunStatus } from '../api/types'

defineProps<{
  status: RunStatus | CaseResultStatus
}>()

const labels: Record<RunStatus | CaseResultStatus, string> = {
  pending: '等待中',
  running: '运行中',
  completed: '已完成',
  failed: '失败',
  passed: '通过',
  error: '错误',
}
</script>

<template>
  <span class="status-badge" :class="status">{{ labels[status] }}</span>
</template>
