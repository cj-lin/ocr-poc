<template>
  <div class="file-upload-container">
    <div
      :class="[
        'upload-area',
        {
          'is-dragging': isDragging,
          'has-error': error,
          'has-file': selectedFile,
        },
      ]"
      data-testid="upload-area"
      @dragenter.prevent="handleDragEnter"
      @dragover.prevent
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        class="file-input"
        accept=".jpg,.jpeg,.png,.pdf"
        @change="onFileChange"
      />

      <div v-if="!selectedFile && !isUploading" class="upload-content">
        <svg
          class="upload-icon"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <p class="upload-text-primary">拖放檔案到此處或點擊上傳</p>
        <p class="upload-text-secondary">支援 JPG、PNG、PDF 格式,最大 10MB</p>
        <button type="button" class="upload-button" @click="triggerFileSelect">
          選擇檔案
        </button>
      </div>

      <div v-if="selectedFile && !isUploading" class="file-info">
        <svg class="file-icon" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
            clip-rule="evenodd"
          />
        </svg>
        <div class="file-details">
          <p class="file-name">{{ fileInfo?.name }}</p>
          <p class="file-size">{{ fileInfo?.size }}</p>
        </div>
        <button type="button" class="remove-button" @click="handleClearFile">
          <svg fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>

      <div v-if="isUploading" class="progress-container" data-testid="progress-bar">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
        </div>
        <p class="progress-text">上傳中... {{ progress }}%</p>
      </div>
    </div>

    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useFileUpload } from '~/composables/useFileUpload'

interface Props {
  isUploading?: boolean
  progress?: number
}

const props = withDefaults(defineProps<Props>(), {
  isUploading: false,
  progress: 0,
})

const emit = defineEmits<{
  fileSelected: [file: File]
  error: [error: string]
  clearFile: []
}>()

const fileInput = ref<HTMLInputElement>()
const {
  isDragging,
  selectedFile,
  error,
  fileInfo,
  handleFileSelect,
  handleDragEnter,
  handleDragLeave,
  handleDrop: onDrop,
  clearFile,
} = useFileUpload()

const triggerFileSelect = () => {
  fileInput.value?.click()
}

const onFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] || null
  handleFileSelect(file)

  if (file && !error.value) {
    emit('fileSelected', file)
  } else if (error.value) {
    emit('error', error.value)
  }
}

const handleDropEvent = (event: DragEvent) => {
  onDrop(event)
  if (selectedFile.value) {
    emit('fileSelected', selectedFile.value)
  } else if (error.value) {
    emit('error', error.value)
  }
}

const handleClearFile = () => {
  clearFile()
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('clearFile')
}
</script>

<style scoped>
.file-upload-container {
  width: 100%;
}

.upload-area {
  border: 2px dashed #cbd5e0;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #f7fafc;
  position: relative;
}

.upload-area.is-dragging {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.upload-area.has-error {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.upload-area.has-file {
  border-color: #10b981;
  background-color: #f0fdf4;
}

.file-input {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  width: 3rem;
  height: 3rem;
  color: #94a3b8;
}

.upload-text-primary {
  font-size: 1rem;
  font-weight: 500;
  color: #1e293b;
  margin: 0;
}

.upload-text-secondary {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.upload-button {
  background-color: #3b82f6;
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 0.375rem;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.upload-button:hover {
  background-color: #2563eb;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: #3b82f6;
}

.file-details {
  flex: 1;
  text-align: left;
}

.file-name {
  font-weight: 500;
  color: #1e293b;
  margin: 0;
}

.file-size {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}

.remove-button {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: none;
  background-color: #fee2e2;
  color: #dc2626;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.remove-button:hover {
  background-color: #fecaca;
}

.remove-button svg {
  width: 1.25rem;
  height: 1.25rem;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-bar {
  width: 100%;
  height: 0.5rem;
  background-color: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #3b82f6;
  transition: width 0.3s;
}

.progress-text {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.error-message {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}
</style>
