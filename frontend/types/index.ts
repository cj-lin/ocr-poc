/**
 * 身分證資訊
 */
export interface IdCardInfo {
  name: string
  id_number: string
  birth_date: string // 民國年格式:YYY/MM/DD
  gender: '男' | '女'
  issue_date: string // 民國年格式:YYY/MM/DD
  issue_location: string
  confidence_score?: number
}

/**
 * API 擷取結果
 */
export interface ExtractionResult {
  request_id: string
  status: 'success' | 'partial'
  data: IdCardInfo
  processing_time: number
  warnings?: string[]
}

/**
 * API 錯誤回應
 */
export interface ErrorResponse {
  request_id: string
  error_code:
    | 'FILE_TOO_LARGE'
    | 'INVALID_FORMAT'
    | 'NO_IMAGE_IN_PDF'
    | 'OCR_FAILED'
    | 'RATE_LIMITED'
    | 'VALIDATION_ERROR'
  message: string
  details?: string
}

/**
 * 檔案上傳狀態
 */
export interface UploadState {
  isUploading: boolean
  progress: number // 0-100
  error: ErrorResponse | null
  result: ExtractionResult | null
}

/**
 * 健康檢查回應
 */
export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  gemini_api: 'connected' | 'disconnected'
  timestamp: string
}

/**
 * 批次擷取結果 (US3)
 */
export interface BatchExtractionResult {
  request_id: string
  total: number
  processed: number
  results: ExtractionResult[]
  failed: ErrorResponse[]
  processing_time: number
}
