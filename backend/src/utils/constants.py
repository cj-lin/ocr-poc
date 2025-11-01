"""Error code constants and mappings"""

# Error codes for API responses
ERROR_CODES = {
    "FILE_TOO_LARGE": "FILE_TOO_LARGE",
    "INVALID_FORMAT": "INVALID_FORMAT",
    "NO_IMAGE_IN_PDF": "NO_IMAGE_IN_PDF",
    "OCR_FAILED": "OCR_FAILED",
    "RATE_LIMITED": "RATE_LIMITED",
    "VALIDATION_ERROR": "VALIDATION_ERROR",
}

# User-friendly error messages (Traditional Chinese)
ERROR_MESSAGES = {
    "FILE_TOO_LARGE": "檔案大小超過限制(最大 10MB)",
    "INVALID_FORMAT": "不支援的檔案格式,請上傳 JPG、PNG 或 PDF",
    "NO_IMAGE_IN_PDF": "PDF 中未找到圖片,請上傳包含身分證圖片的檔案",
    "OCR_FAILED": "辨識服務暫時無法使用,請稍後再試",
    "RATE_LIMITED": "處理佇列中,預估等待時間:2 分鐘",
    "VALIDATION_ERROR": "擷取的資料驗證失敗",
}

# File validation constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf"]
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf"]

# Taiwan locations for validation
VALID_LOCATIONS = [
    "台北市",
    "新北市",
    "桃園市",
    "台中市",
    "台南市",
    "高雄市",
    "基隆市",
    "新竹市",
    "嘉義市",
    "新竹縣",
    "苗栗縣",
    "彰化縣",
    "南投縣",
    "雲林縣",
    "嘉義縣",
    "屏東縣",
    "宜蘭縣",
    "花蓮縣",
    "台東縣",
    "澎湖縣",
    "金門縣",
    "連江縣",
]
