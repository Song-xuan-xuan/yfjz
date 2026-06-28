<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { createSuite, deleteSuite, listSuites } from '../api/suites'
import type { SuiteDefinition, SuiteListItem } from '../api/types'
import SuiteEditor from '../components/SuiteEditor.vue'

const suites = ref<SuiteListItem[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const editorError = ref('')

async function loadSuites() {
  loading.value = true
  error.value = ''
  try {
    suites.value = await listSuites()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '测试集加载失败'
  } finally {
    loading.value = false
  }
}

async function saveSuite(suite: SuiteDefinition) {
  saving.value = true
  editorError.value = ''
  try {
    await createSuite({ suite })
    await loadSuites()
  } catch (err) {
    editorError.value = err instanceof Error ? err.message : '测试集校验失败'
  } finally {
    saving.value = false
  }
}

async function removeSuite(suite: SuiteListItem) {
  if (!window.confirm(`确认删除测试集「${suite.name}」？`)) {
    return
  }
  try {
    await deleteSuite(suite.id)
    await loadSuites()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败'
  }
}

onMounted(loadSuites)
</script>

<template>
  <section class="page-stack">
    <header class="page-header">
      <div>
        <p class="eyebrow">Suites</p>
        <h1>测试集</h1>
        <p>使用 JSON suite 描述 prompt、评分规则和样本。</p>
      </div>
    </header>

    <p v-if="error" class="error-message">{{ error }}</p>
    <SuiteEditor :backend-error="editorError" :loading="saving" @create="saveSuite" />

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>测试集列表</h2>
          <p>{{ loading ? '正在加载...' : `共 ${suites.length} 个测试集` }}</p>
        </div>
      </div>

      <div v-if="!suites.length && !loading" class="empty-state">暂无测试集。</div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>描述</th>
              <th>样本数</th>
              <th>指标</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="suite in suites" :key="suite.id">
              <td>{{ suite.name }}</td>
              <td class="text-cell">{{ suite.description }}</td>
              <td>{{ suite.case_count }}</td>
              <td>{{ suite.metric_type }}</td>
              <td>{{ suite.created_at }}</td>
              <td class="action-cell">
                <RouterLink class="ghost-button" :to="`/suites/${suite.id}`">查看</RouterLink>
                <button class="danger-button" type="button" @click="removeSuite(suite)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>
