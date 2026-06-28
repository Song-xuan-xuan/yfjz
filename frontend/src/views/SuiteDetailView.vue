<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getSuite } from '../api/suites'
import type { SuiteCase, SuiteDetail } from '../api/types'

const route = useRoute()
const suite = ref<SuiteDetail | null>(null)
const loading = ref(true)
const error = ref('')

function caseValue(item: SuiteCase, key: string): string {
  const value = item[key]
  return typeof value === 'string' ? value : JSON.stringify(value)
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    suite.value = await getSuite(Number(route.params.id))
  } catch (err) {
    error.value = err instanceof Error ? err.message : '测试集详情加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="page-stack">
    <header class="page-header">
      <div>
        <p class="eyebrow">Suite Detail</p>
        <h1>{{ suite?.name || '测试集详情' }}</h1>
        <p>{{ suite?.description || '查看 prompt 模板、评分配置和样本表格。' }}</p>
      </div>
      <RouterLink class="ghost-button" to="/suites">返回列表</RouterLink>
    </header>

    <p v-if="loading" class="muted">正在加载测试集详情...</p>
    <p v-if="error" class="error-message">{{ error }}</p>

    <template v-if="suite">
      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>Prompt Template</h2>
            <p class="text-block">{{ suite.prompt_template }}</p>
          </div>
        </div>
        <pre class="code-block">{{ JSON.stringify(suite.evaluation, null, 2) }}</pre>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>Cases</h2>
            <p>共 {{ suite.cases.length }} 条样本。</p>
          </div>
        </div>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th v-for="key in Object.keys(suite.cases[0] || {})" :key="key">{{ key }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in suite.cases" :key="item.id">
                <td v-for="key in Object.keys(item)" :key="key" class="text-cell">
                  {{ caseValue(item, key) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </section>
</template>
