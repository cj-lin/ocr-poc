<template>
  <div class="editable-form">
    <h3 class="form-title">身分證資訊</h3>

    <div class="form-grid">
      <div class="form-field">
        <label for="name" class="field-label">姓名</label>
        <input
          id="name"
          v-model="formData.name"
          type="text"
          name="name"
          class="field-input"
          @input="handleUpdate"
        />
      </div>

      <div class="form-field">
        <label for="id_number" class="field-label">身分證字號</label>
        <input
          id="id_number"
          v-model="formData.id_number"
          type="text"
          name="id_number"
          class="field-input"
          @input="handleUpdate"
        />
        <p v-if="errors.id_number" class="error-message">{{ errors.id_number }}</p>
      </div>

      <div class="form-field">
        <label for="birth_date" class="field-label">出生日期</label>
        <input
          id="birth_date"
          v-model="formData.birth_date"
          type="text"
          name="birth_date"
          class="field-input"
          placeholder="YYY/MM/DD"
          @input="handleUpdate"
        />
        <p v-if="errors.birth_date" class="error-message">{{ errors.birth_date }}</p>
      </div>

      <div class="form-field">
        <label for="gender" class="field-label">性別</label>
        <select
          id="gender"
          v-model="formData.gender"
          name="gender"
          class="field-input"
          @change="handleUpdate"
        >
          <option value="男">男</option>
          <option value="女">女</option>
        </select>
      </div>

      <div class="form-field">
        <label for="issue_date" class="field-label">發證日期</label>
        <input
          id="issue_date"
          v-model="formData.issue_date"
          type="text"
          name="issue_date"
          class="field-input"
          placeholder="YYY/MM/DD"
          @input="handleUpdate"
        />
        <p v-if="errors.issue_date" class="error-message">{{ errors.issue_date }}</p>
      </div>

      <div class="form-field">
        <label for="issue_location" class="field-label">發證地點</label>
        <input
          id="issue_location"
          v-model="formData.issue_location"
          type="text"
          name="issue_location"
          class="field-input"
          @input="handleUpdate"
        />
      </div>
    </div>

    <div v-if="data.confidence_score" class="confidence-display" data-testid="confidence">
      <span class="confidence-label">整體信心分數:</span>
      <span class="confidence-value">{{ confidencePercent }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { IdCardInfo } from '~/types'

interface Props {
  data: IdCardInfo
}

const props = defineProps<Props>()

const emit = defineEmits<{
  update: [data: IdCardInfo]
}>()

const formData = ref<IdCardInfo>({ ...props.data })
const errors = ref<Record<string, string>>({})

const confidencePercent = computed(() => {
  if (!props.data.confidence_score) return 0
  return Math.round(props.data.confidence_score * 100)
})

const validateIdNumber = (value: string): string | null => {
  const pattern = /^[A-Z][12]\d{8}$/
  if (!pattern.test(value)) {
    return '身分證字號格式錯誤(應為 1 個英文字母 + 9 個數字)'
  }
  return null
}

const validateDate = (value: string): string | null => {
  const pattern = /^\d{1,3}\/(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[01])$/
  if (!pattern.test(value)) {
    return '日期格式錯誤(應為 YYY/MM/DD 民國年格式)'
  }
  return null
}

const handleUpdate = () => {
  // Validate fields
  errors.value = {}

  const idError = validateIdNumber(formData.value.id_number)
  if (idError) errors.value.id_number = idError

  const birthError = validateDate(formData.value.birth_date)
  if (birthError) errors.value.birth_date = birthError

  const issueError = validateDate(formData.value.issue_date)
  if (issueError) errors.value.issue_date = issueError

  // Emit update if no errors
  if (Object.keys(errors.value).length === 0) {
    emit('update', { ...formData.value })
  }
}

// Watch for prop changes
watch(
  () => props.data,
  (newData) => {
    formData.value = { ...newData }
  },
  { deep: true }
)
</script>

<style scoped>
.editable-form {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.form-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1.5rem 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 0.375rem;
}

.field-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.field-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.error-message {
  color: #dc2626;
  font-size: 0.75rem;
  margin: 0.25rem 0 0 0;
}

.confidence-display {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confidence-label {
  font-size: 0.875rem;
  color: #64748b;
}

.confidence-value {
  font-size: 1rem;
  font-weight: 600;
  color: #16a34a;
}
</style>
