/**
 * Composable for OCR API calls
 */
import { ref } from 'vue'
import type { ExtractionResult, ErrorResponse } from '~/types'

export const useOcrApi = () => {
  const config = useRuntimeConfig()
  const isLoading = ref(false)
  const progress = ref(0)
  const result = ref<ExtractionResult | null>(null)
  const error = ref<ErrorResponse | null>(null)

  /**
   * Upload file and extract ID card info
   */
  const extractIdCard = async (file: File): Promise<ExtractionResult | null> => {
    isLoading.value = true
    progress.value = 0
    result.value = null
    error.value = null

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await $fetch<ExtractionResult>('/api/extract', {
        method: 'POST',
        body: formData,
        baseURL: config.public.backendUrl,
        onUploadProgress: (event) => {
          if (event.total) {
            progress.value = Math.round((event.loaded / event.total) * 100)
          }
        },
      })

      result.value = response
      return response
    } catch (err: any) {
      console.error('OCR API error:', err)

      // Extract error details from response
      if (err.data) {
        error.value = err.data as ErrorResponse
      } else {
        error.value = {
          request_id: '',
          error_code: 'OCR_FAILED',
          message: err.message || '發生未知錯誤',
          details: undefined,
        }
      }

      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear current state
   */
  const clearState = () => {
    isLoading.value = false
    progress.value = 0
    result.value = null
    error.value = null
  }

  return {
    isLoading,
    progress,
    result,
    error,
    extractIdCard,
    clearState,
  }
}
