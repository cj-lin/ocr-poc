<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8">
      <header class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 text-center">身分證資訊擷取系統</h1>
        <p class="text-gray-600 text-center mt-2">使用 AI 自動辨識身分證資訊</p>
      </header>

      <main>
        <div class="max-w-2xl mx-auto">
          <!-- File Upload -->
          <FileUpload
            :is-uploading="isLoading"
            :progress="progress"
            @file-selected="handleFileSelected"
            @error="handleUploadError"
            @clear-file="handleClearFile"
          />

          <!-- Error Display -->
          <div v-if="apiError" class="error-container">
            <div class="error-header">
              <svg class="error-icon" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clip-rule="evenodd"
                />
              </svg>
              <h2 class="error-title">處理失敗</h2>
            </div>
            <p class="error-message">{{ apiError.message }}</p>
            <p v-if="apiError.details" class="error-details">{{ apiError.details }}</p>
            <button class="retry-button" @click="handleRetry">
              重試
            </button>
          </div>

          <!-- Loading Indicator -->
          <div v-if="isLoading" class="loading-container">
            <div class="loading-spinner"></div>
            <p class="loading-text">正在辨識中,請稍候...</p>
          </div>

          <!-- Extraction Result -->
          <div v-if="extractionResult && !isLoading">
            <ExtractionResult :result="extractionResult" />
            <EditableForm
              :data="extractionResult.data"
              @update="handleDataUpdate"
            />

            <!-- Actions -->
            <div class="actions">
              <button class="action-button action-button-secondary" @click="handleClearAll">
                清除並重新上傳
              </button>
              <button class="action-button action-button-primary" @click="handleExport">
                匯出資料
              </button>
            </div>
          </div>
        </div>
      </main>

      <!-- Footer -->
      <footer class="mt-12 text-center text-gray-500 text-sm">
        <p>本系統不永久儲存任何上傳的檔案或擷取的個人資料</p>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useOcrApi } from '~/composables/useOcrApi'
import type { IdCardInfo, ExtractionResult as ExtractionResultType } from '~/types'

const { isLoading, progress, result, error: apiError, extractIdCard, clearState } = useOcrApi()

const extractionResult = ref<ExtractionResultType | null>(null)
const currentFile = ref<File | null>(null)
const editedData = ref<IdCardInfo | null>(null)

const handleFileSelected = async (file: File) => {
  currentFile.value = file
  editedData.value = null

  // Call API to extract
  const response = await extractIdCard(file)
  if (response) {
    extractionResult.value = response
  }
}

const handleUploadError = (error: string) => {
  console.error('Upload error:', error)
}

const handleClearFile = () => {
  currentFile.value = null
  extractionResult.value = null
  editedData.value = null
  clearState()
}

const handleClearAll = () => {
  handleClearFile()
}

const handleRetry = async () => {
  if (currentFile.value) {
    clearState()
    await handleFileSelected(currentFile.value)
  }
}

const handleDataUpdate = (data: IdCardInfo) => {
  editedData.value = data
}

const handleExport = () => {
  const dataToExport = editedData.value || extractionResult.value?.data
  if (!dataToExport) return

  // Export as JSON
  const jsonStr = JSON.stringify(dataToExport, null, 2)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `id_card_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.container {
  max-width: 1200px;
}

.error-container {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-top: 1rem;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.error-icon {
  width: 2rem;
  height: 2rem;
  color: #dc2626;
}

.error-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #991b1b;
  margin: 0;
}

.error-message {
  color: #991b1b;
  margin: 0 0 0.5rem 0;
}

.error-details {
  color: #7f1d1d;
  font-size: 0.875rem;
  font-family: monospace;
  margin: 0;
}

.retry-button {
  margin-top: 1rem;
  background-color: #dc2626;
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 0.375rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-button:hover {
  background-color: #b91c1c;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
  background-color: white;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.loading-spinner {
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  width: 3rem;
  height: 3rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 1rem;
  color: #64748b;
  font-size: 0.875rem;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  justify-content: flex-end;
}

.action-button {
  padding: 0.625rem 1.5rem;
  border-radius: 0.375rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-button-primary {
  background-color: #3b82f6;
  color: white;
}

.action-button-primary:hover {
  background-color: #2563eb;
}

.action-button-secondary {
  background-color: #f3f4f6;
  color: #374151;
}

.action-button-secondary:hover {
  background-color: #e5e7eb;
}
</style>
