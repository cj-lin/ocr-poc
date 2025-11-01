/**
 * Composable for file upload functionality
 */
import { ref, computed } from 'vue'
import type { ErrorResponse } from '~/types'

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf']
const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf']

export const useFileUpload = () => {
  const isDragging = ref(false)
  const selectedFile = ref<File | null>(null)
  const error = ref<string | null>(null)

  /**
   * Validate file size
   */
  const validateFileSize = (file: File): boolean => {
    if (file.size > MAX_FILE_SIZE) {
      error.value = '檔案大小超過限制(最大 10MB)'
      return false
    }
    return true
  }

  /**
   * Validate file type
   */
  const validateFileType = (file: File): boolean => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      error.value = '不支援的檔案格式,請上傳 JPG、PNG 或 PDF'
      return false
    }
    return true
  }

  /**
   * Validate file extension
   */
  const validateFileExtension = (file: File): boolean => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      error.value = '不支援的檔案格式,請上傳 JPG、PNG 或 PDF'
      return false
    }
    return true
  }

  /**
   * Validate file
   */
  const validateFile = (file: File): boolean => {
    error.value = null

    if (!validateFileSize(file)) return false
    if (!validateFileType(file)) return false
    if (!validateFileExtension(file)) return false

    return true
  }

  /**
   * Handle file selection
   */
  const handleFileSelect = (file: File | null) => {
    if (!file) {
      selectedFile.value = null
      error.value = null
      return
    }

    if (validateFile(file)) {
      selectedFile.value = file
      error.value = null
    } else {
      selectedFile.value = null
    }
  }

  /**
   * Handle drag enter
   */
  const handleDragEnter = () => {
    isDragging.value = true
  }

  /**
   * Handle drag leave
   */
  const handleDragLeave = () => {
    isDragging.value = false
  }

  /**
   * Handle drop
   */
  const handleDrop = (e: DragEvent) => {
    isDragging.value = false

    const files = e.dataTransfer?.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  /**
   * Clear selection
   */
  const clearFile = () => {
    selectedFile.value = null
    error.value = null
  }

  /**
   * File info for display
   */
  const fileInfo = computed(() => {
    if (!selectedFile.value) return null

    return {
      name: selectedFile.value.name,
      size: (selectedFile.value.size / 1024).toFixed(2) + ' KB',
      type: selectedFile.value.type,
    }
  })

  return {
    isDragging,
    selectedFile,
    error,
    fileInfo,
    handleFileSelect,
    handleDragEnter,
    handleDragLeave,
    handleDrop,
    clearFile,
    validateFile,
  }
}
