<script setup lang="ts">
import { ref } from 'vue'
import type { SuiteDefinition } from '../api/types'

defineProps<{
  loading?: boolean
  backendError?: string
}>()

const emit = defineEmits<{
  create: [suite: SuiteDefinition]
}>()

const sampleSuite = {
  name: 'math-basic',
  description: '基础数学问答评估',
  prompt_template: '请回答下面的问题，只输出最终答案：{{ question }}',
  evaluation: {
    type: 'exact_match',
    expected_field: 'answer',
    ignore_case: true,
    strip: true,
  },
  cases: [
    {
      id: 'case_001',
      question: '1 + 1 = ?',
      answer: '2',
    },
    {
      id: 'case_002',
      question: '3 * 4 = ?',
      answer: '12',
    },
  ],
}

const editorValue = ref(JSON.stringify(sampleSuite, null, 2))
const parseError = ref('')

function useSample() {
  editorValue.value = JSON.stringify(sampleSuite, null, 2)
  parseError.value = ''
}

function submitSuite() {
  parseError.value = ''
  try {
    const suite = JSON.parse(editorValue.value) as SuiteDefinition
    emit('create', suite)
  } catch (error) {
    parseError.value = error instanceof Error ? error.message : 'JSON 解析失败'
  }
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h2>新建测试集</h2>
        <p>仅支持 JSON suite，提交前会先进行 JSON.parse 校验。</p>
      </div>
      <button class="ghost-button" type="button" @click="useSample">填入示例 JSON</button>
    </div>

    <label class="editor-label">
      <span>Suite JSON</span>
      <textarea v-model="editorValue" spellcheck="false"></textarea>
    </label>

    <p v-if="parseError" class="error-message">{{ parseError }}</p>
    <p v-if="backendError" class="error-message">{{ backendError }}</p>

    <button class="primary-button" :disabled="loading" type="button" @click="submitSuite">
      {{ loading ? '提交中...' : '创建测试集' }}
    </button>
  </section>
</template>
