<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { listProviderConfigs } from '../api/providerConfigs'
import { createRun, listRuns } from '../api/runs'
import { listSuites } from '../api/suites'
import type { ProviderConfig, RunCreatePayload, RunSummary, SuiteListItem } from '../api/types'
import StatusBadge from '../components/StatusBadge.vue'

const router = useRouter()
const suites = ref<SuiteListItem[]>([])
const providers = ref<ProviderConfig[]>([])
const runs = ref<RunSummary[]>([])
const loading = ref(false)
const submitting = ref(false)
const error = ref('')

const form = reactive<RunCreatePayload>({
  suite_id: 0,
  provider_config_id: 0,
  model: '',
  temperature: 0,
  max_tokens: 512,
  concurrency: 3,
  use_cache: true,
})

const selectedProvider = computed(() =>
  providers.value.find((item) => item.id === Number(form.provider_config_id)),
)

watch(selectedProvider, (provider) => {
  if (provider && !form.model) {
    form.model = provider.default_model
  }
})

async function loadOptions() {
  loading.value = true
  error.value = ''
  try {
    const [suiteItems, providerItems, runItems] = await Promise.all([
      listSuites(),
      listProviderConfigs(),
      listRuns(),
    ])
    suites.value = suiteItems
    providers.value = providerItems
    runs.value = runItems
    form.suite_id = suiteItems[0]?.id || 0
    form.provider_config_id = providerItems[0]?.id || 0
    form.model = providerItems[0]?.default_model || ''
  } catch (err) {
    error.value = err instanceof Error ? err.message : '评估任务选项加载失败'
  } finally {
    loading.value = false
  }
}

async function submitRun() {
  submitting.value = true
  error.value = ''
  try {
    const created = await createRun({ ...form })
    await router.push(`/runs/${created.id}`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '评估任务创建失败'
  } finally {
    submitting.value = false
  }
}

onMounted(loadOptions)
</script>

<template>
  <section class="page-stack">
    <header class="page-header">
      <div>
        <p class="eyebrow">Runs</p>
        <h1>评估任务</h1>
        <p>选择测试集、provider 和模型参数后启动一次评估。</p>
      </div>
    </header>

    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="loading" class="muted">正在加载测试集和 API 配置...</p>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>创建任务</h2>
          <p>concurrency 限制为 1 / 3 / 5 / 10，默认开启缓存。</p>
        </div>
      </div>

      <form class="form-grid" @submit.prevent="submitRun">
        <label>
          <span>测试集</span>
          <select v-model.number="form.suite_id" required>
            <option disabled value="0">请选择测试集</option>
            <option v-for="suite in suites" :key="suite.id" :value="suite.id">
              {{ suite.name }}
            </option>
          </select>
        </label>
        <label>
          <span>API 配置</span>
          <select v-model.number="form.provider_config_id" required>
            <option disabled value="0">请选择 API 配置</option>
            <option v-for="provider in providers" :key="provider.id" :value="provider.id">
              {{ provider.name }}
            </option>
          </select>
        </label>
        <label>
          <span>模型</span>
          <input v-model="form.model" required placeholder="gpt-4o-mini" />
        </label>
        <label>
          <span>Temperature</span>
          <input v-model.number="form.temperature" max="2" min="0" step="0.1" type="number" />
        </label>
        <label>
          <span>Max Tokens</span>
          <input v-model.number="form.max_tokens" min="1" type="number" />
        </label>
        <label>
          <span>Concurrency</span>
          <select v-model.number="form.concurrency">
            <option :value="1">1</option>
            <option :value="3">3</option>
            <option :value="5">5</option>
            <option :value="10">10</option>
          </select>
        </label>
        <label class="checkbox-field">
          <input v-model="form.use_cache" type="checkbox" />
          <span>启用缓存</span>
        </label>

        <div class="form-actions">
          <button class="primary-button" :disabled="submitting" type="submit">
            {{ submitting ? '创建中...' : '创建并进入详情' }}
          </button>
        </div>
      </form>
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>最近任务</h2>
          <p>创建成功后可进入详情页查看轮询进度。</p>
        </div>
      </div>
      <div v-if="!runs.length" class="empty-state">暂无评估任务。</div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>状态</th>
              <th>模型</th>
              <th>进度</th>
              <th>得分</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="run in runs" :key="run.id">
              <td>{{ run.id }}</td>
              <td><StatusBadge :status="run.status" /></td>
              <td>{{ run.model }}</td>
              <td>{{ run.completed_cases }} / {{ run.total_cases }}</td>
              <td>{{ (run.score * 100).toFixed(1) }}%</td>
              <td>{{ run.created_at }}</td>
              <td><RouterLink class="ghost-button" :to="`/runs/${run.id}`">查看</RouterLink></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>
