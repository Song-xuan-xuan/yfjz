<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  createProviderConfig,
  deleteProviderConfig,
  listProviderConfigs,
  testProviderConfig,
  updateProviderConfig,
} from '../api/providerConfigs'
import type { ProviderConfig, ProviderConfigCreatePayload, ProviderConfigUpdatePayload } from '../api/types'
import ProviderConfigForm from '../components/ProviderConfigForm.vue'

const configs = ref<ProviderConfig[]>([])
const editing = ref<ProviderConfig | null>(null)
const loading = ref(false)
const saving = ref(false)
const testingId = ref<number | null>(null)
const error = ref('')
const testMessage = ref('')

async function loadConfigs() {
  loading.value = true
  error.value = ''
  try {
    configs.value = await listProviderConfigs()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'API 配置加载失败'
  } finally {
    loading.value = false
  }
}

function hasApiKey(payload: ProviderConfigUpdatePayload): payload is ProviderConfigCreatePayload {
  return typeof payload.api_key === 'string' && payload.api_key.length > 0
}

async function saveConfig(payload: ProviderConfigUpdatePayload) {
  saving.value = true
  error.value = ''
  try {
    if (editing.value) {
      await updateProviderConfig(editing.value.id, payload)
    } else {
      if (!hasApiKey(payload)) {
        error.value = '新增 API 配置需要填写 API Key'
        return
      }
      await createProviderConfig(payload)
    }
    editing.value = null
    await loadConfigs()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败'
  } finally {
    saving.value = false
  }
}

async function removeConfig(config: ProviderConfig) {
  if (!window.confirm(`确认删除配置「${config.name}」？`)) {
    return
  }
  try {
    await deleteProviderConfig(config.id)
    await loadConfigs()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败'
  }
}

async function testConfig(config: ProviderConfig) {
  testingId.value = config.id
  testMessage.value = ''
  try {
    const result = await testProviderConfig(config.id)
    testMessage.value = result.message || result.status || '连接测试已完成'
  } catch (err) {
    testMessage.value = err instanceof Error ? err.message : '连接测试失败'
  } finally {
    testingId.value = null
  }
}

onMounted(loadConfigs)
</script>

<template>
  <section class="page-stack">
    <header class="page-header">
      <div>
        <p class="eyebrow">Provider Configs</p>
        <h1>API 配置</h1>
        <p>管理 OpenAI-compatible provider，页面只展示 masked key。</p>
      </div>
      <button class="ghost-button" type="button" @click="editing = null">新增配置</button>
    </header>

    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="testMessage" class="info-message">{{ testMessage }}</p>

    <ProviderConfigForm :initial="editing" :loading="saving" @cancel="editing = null" @save="saveConfig" />

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>配置列表</h2>
          <p>{{ loading ? '正在加载...' : `共 ${configs.length} 个配置` }}</p>
        </div>
      </div>

      <div v-if="!configs.length && !loading" class="empty-state">暂无 API 配置。</div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>Base URL</th>
              <th>默认模型</th>
              <th>Masked Key</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="config in configs" :key="config.id">
              <td>{{ config.name }}</td>
              <td class="text-cell">{{ config.base_url }}</td>
              <td>{{ config.default_model }}</td>
              <td>{{ config.api_key_masked }}</td>
              <td>{{ config.updated_at }}</td>
              <td class="action-cell">
                <button class="ghost-button" type="button" @click="editing = config">编辑</button>
                <button
                  class="ghost-button"
                  :disabled="testingId === config.id"
                  type="button"
                  @click="testConfig(config)"
                >
                  {{ testingId === config.id ? '测试中...' : '测试连接' }}
                </button>
                <button class="danger-button" type="button" @click="removeConfig(config)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>
