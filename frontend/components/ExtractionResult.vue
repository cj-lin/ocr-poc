<template>
  <div class="extraction-result">
    <div class="result-header">
      <svg class="success-icon" fill="currentColor" viewBox="0 0 20 20">
        <path
          fill-rule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
          clip-rule="evenodd"
        />
      </svg>
      <h2 class="result-title">辨識完成</h2>
      <span v-if="result.status === 'partial'" class="warning-badge">
        部分欄位信心度較低
      </span>
    </div>

    <div class="result-meta">
      <p class="meta-item">
        <span class="meta-label">處理時間:</span>
        <span class="meta-value">{{ processingTime }}秒</span>
      </p>
      <p v-if="result.data.confidence_score" class="meta-item">
        <span class="meta-label">信心分數:</span>
        <span class="meta-value">{{ confidencePercent }}%</span>
      </p>
    </div>

    <div v-if="result.warnings && result.warnings.length > 0" class="warnings">
      <p v-for="(warning, index) in result.warnings" :key="index" class="warning-text">
        ⚠️ {{ warning }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ExtractionResult } from '~/types'

interface Props {
  result: ExtractionResult
}

const props = defineProps<Props>()

const processingTime = computed(() => {
  return props.result.processing_time.toFixed(2)
})

const confidencePercent = computed(() => {
  if (!props.result.data.confidence_score) return 0
  return Math.round(props.result.data.confidence_score * 100)
})
</script>

<style scoped>
.extraction-result {
  background-color: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.success-icon {
  width: 2rem;
  height: 2rem;
  color: #16a34a;
}

.result-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #166534;
  margin: 0;
}

.warning-badge {
  background-color: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.result-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.meta-item {
  margin: 0;
  font-size: 0.875rem;
}

.meta-label {
  color: #166534;
  font-weight: 500;
}

.meta-value {
  color: #15803d;
  margin-left: 0.25rem;
}

.warnings {
  background-color: #fef3c7;
  border-radius: 0.375rem;
  padding: 0.75rem;
}

.warning-text {
  color: #92400e;
  font-size: 0.875rem;
  margin: 0.25rem 0;
}
</style>
