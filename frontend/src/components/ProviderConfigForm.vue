<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { ProviderConfig, ProviderConfigUpdatePayload } from '../api/types'

const props = defineProps<{
  initial?: ProviderConfig | null
  loading?: boolean
}>()

const emit = defineEmits<{
  save: [payload: ProviderConfigUpdatePayload]
  cancel: []
}>()

const form = reactive<ProviderConfigUpdatePayload>({
  name: '',
  base_url: 'https://api.openai.com/v1',
  api_key: '',
  default_model: 'gpt-4o-mini',
  timeout_seconds: 60,
  max_retries: 2,
})

watch(
  () => props.initial,
  (config) => {
    form.name = config?.name || ''
    form.base_url = config?.base_url || 'https://api.openai.com/v1'
    form.api_key = ''
    form.default_model = config?.default_model || 'gpt-4o-mini'
    form.timeout_seconds = config?.timeout_seconds || 60
    form.max_retries = config?.max_retries || 2
  },
  { immediate: true },
)

function submitForm() {
  const payload: ProviderConfigUpdatePayload = {
    name: form.name.trim(),
    base_url: form.base_url.trim(),
    default_model: form.default_model.trim(),
    timeout_seconds: Number(form.timeout_seconds),
    max_retries: Number(form.max_retries),
  }

  if (form.api_key?.trim()) {
    payload.api_key = form.api_key.trim()
  }

  emit('save', payload)
  form.api_key = ''
}
</script>

<template>
  <form class="form-grid" @submit.prevent="submitForm">
    <label>
      <span>配置名称</span>
      <input v-model="form.name" required placeholder="OpenAI Official" />
    </label>
    <label>
      <span>Base URL</span>
      <input v-model="form.base_url" required placeholder="https://api.openai.com/v1" />
    </label>
    <label>
      <span>API Key</span>
      <input
        v-model="form.api_key"
        :required="!initial"
        autocomplete="off"
        type="password"
        :placeholder="initial ? '留空则不替换密钥' : 'sk-...'"
      />
    </label>
    <label>
      <span>默认模型</span>
      <input v-model="form.default_model" required placeholder="gpt-4o-mini" />
    </label>
    <label>
      <span>超时时间（秒）</span>
      <input v-model.number="form.timeout_seconds" min="1" required type="number" />
    </label>
    <label>
      <span>最大重试次数</span>
      <input v-model.number="form.max_retries" min="0" required type="number" />
    </label>

    <div class="form-actions">
      <button class="primary-button" :disabled="loading" type="submit">
        {{ loading ? '保存中...' : initial ? '保存修改' : '新增配置' }}
      </button>
      <button class="ghost-button" :disabled="loading" type="button" @click="emit('cancel')">
        取消
      </button>
    </div>
  </form>
</template>
