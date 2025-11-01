# Data Model: 身分證資訊擷取系統

**Feature**: 001-id-card-extraction  
**Date**: 2025-11-01  
**Status**: Draft

## 概述

本系統不使用資料庫，所有資料結構用於 API 請求/回應和記憶體處理。資料生命週期僅限於單次 HTTP 請求期間。

---

## 核心實體

### 1. UploadedFile（上傳檔案）

**用途**：表示使用者上傳的檔案及其元資料

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 | 驗證規則 |
|---------|------|------|------|---------|
| `file_name` | string | ✓ | 原始檔案名稱 | 非空字串 |
| `file_size` | integer | ✓ | 檔案大小（bytes） | 0 < size ≤ 10MB |
| `mime_type` | string | ✓ | MIME 類型 | 必須為 `image/jpeg`, `image/png`, `application/pdf` |
| `content` | bytes | ✓ | 檔案二進位內容 | - |
| `uploaded_at` | datetime | ✓ | 上傳時間戳記（ISO 8601） | 自動生成 |

**狀態轉換**：無（一次性物件）

**Pydantic 模型**：
```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal

class UploadedFileMetadata(BaseModel):
    """僅包含元資料的模型（用於日誌）"""
    file_name: str
    file_size: int = Field(..., gt=0, le=10*1024*1024)
    mime_type: Literal["image/jpeg", "image/png", "application/pdf"]
    uploaded_at: datetime = Field(default_factory=datetime.now)
    
    @field_validator('file_name')
    @classmethod
    def 驗證檔案名稱(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('檔案名稱不可為空')
        return v
```

---

### 2. IdCardInfo（身分證資訊）

**用途**：從圖片中擷取的結構化身分證資料

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 | 驗證規則 |
|---------|------|------|------|---------|
| `name` | string | ✓ | 姓名 | 非空字串，2-10 字元 |
| `id_number` | string | ✓ | 身分證字號 | 格式：1 個英文字母 + 9 個數字（如 A123456789） |
| `birth_date` | string | ✓ | 出生日期 | 格式：`YYY/MM/DD`（民國年） |
| `gender` | string | ✓ | 性別 | 必須為 `男` 或 `女` |
| `issue_date` | string | ✓ | 發證日期 | 格式：`YYY/MM/DD`（民國年） |
| `issue_location` | string | ✓ | 發證地點 | 台灣縣市名稱 |
| `confidence_score` | float | ✗ | 辨識信心分數 | 0.0 ~ 1.0（Gemini 提供時才有） |

**驗證規則細節**：

- **身分證字號**：第一碼英文字母對應區域碼，後 9 碼數字含檢查碼
  ```python
  import re
  ID_PATTERN = re.compile(r'^[A-Z][12]\d{8}$')
  ```

- **民國年格式**：`YYY/MM/DD`，其中 YYY 為民國年（1-999）
  ```python
  DATE_PATTERN = re.compile(r'^\d{1,3}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])$')
  ```

- **縣市列表**：
  ```python
  VALID_LOCATIONS = [
      "台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市",
      "基隆市", "新竹市", "嘉義市",
      "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣",
      "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", "澎湖縣", "金門縣", "連江縣"
  ]
  ```

**Pydantic 模型**：
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class IdCardInfo(BaseModel):
    """身分證資訊實體"""
    name: str = Field(..., min_length=2, max_length=10)
    id_number: str
    birth_date: str
    gender: Literal["男", "女"]
    issue_date: str
    issue_location: str
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    @field_validator('id_number')
    @classmethod
    def 驗證身分證字號(cls, v: str) -> str:
        if not re.match(r'^[A-Z][12]\d{8}$', v):
            raise ValueError('身分證字號格式錯誤（應為 1 個英文字母 + 9 個數字）')
        return v
    
    @field_validator('birth_date', 'issue_date')
    @classmethod
    def 驗證民國日期格式(cls, v: str) -> str:
        if not re.match(r'^\d{1,3}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])$', v):
            raise ValueError('日期格式錯誤（應為 YYY/MM/DD 民國年格式）')
        return v
    
    @field_validator('issue_location')
    @classmethod
    def 驗證發證地點(cls, v: str) -> str:
        valid_locations = [
            "台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市",
            "基隆市", "新竹市", "嘉義市",
            "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣",
            "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", "澎湖縣", "金門縣", "連江縣"
        ]
        if v not in valid_locations:
            raise ValueError(f'無效的發證地點：{v}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "王小明",
                "id_number": "A123456789",
                "birth_date": "80/05/20",
                "gender": "男",
                "issue_date": "95/12/01",
                "issue_location": "台北市",
                "confidence_score": 0.95
            }
        }
```

---

### 3. ExtractionResult（擷取結果）

**用途**：API 回應物件，包含擷取的身分證資訊和處理元資料

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `request_id` | string | ✓ | 請求追蹤 ID（UUID） |
| `status` | string | ✓ | 處理狀態（`success` 或 `partial`） |
| `data` | IdCardInfo | ✓ | 擷取的身分證資訊 |
| `processing_time` | float | ✓ | 處理耗時（秒） |
| `warnings` | list[string] | ✗ | 警告訊息（如部分欄位信心分數低） |

**狀態說明**：
- `success`：所有欄位成功擷取
- `partial`：部分欄位無法辨識（欄位值為 `null` 或空字串）

**Pydantic 模型**：
```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class ExtractionResult(BaseModel):
    """API 回應：擷取結果"""
    request_id: str
    status: Literal["success", "partial"]
    data: IdCardInfo
    processing_time: float = Field(..., ge=0)
    warnings: Optional[list[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "success",
                "data": {
                    "name": "王小明",
                    "id_number": "A123456789",
                    "birth_date": "80/05/20",
                    "gender": "男",
                    "issue_date": "95/12/01",
                    "issue_location": "台北市"
                },
                "processing_time": 3.25,
                "warnings": None
            }
        }
```

---

### 4. ErrorResponse（錯誤回應）

**用途**：統一的 API 錯誤回應格式

**欄位**：

| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `request_id` | string | ✓ | 請求追蹤 ID |
| `error_code` | string | ✓ | 錯誤代碼（如 `FILE_TOO_LARGE`） |
| `message` | string | ✓ | 使用者友善的錯誤訊息 |
| `details` | string | ✗ | 技術細節（僅開發模式） |

**錯誤代碼列表**：

| 代碼 | HTTP 狀態碼 | 說明 |
|------|------------|------|
| `FILE_TOO_LARGE` | 413 | 檔案超過 10MB |
| `INVALID_FORMAT` | 400 | 不支援的檔案格式 |
| `NO_IMAGE_IN_PDF` | 400 | PDF 無圖片內容 |
| `OCR_FAILED` | 500 | Gemini API 錯誤 |
| `RATE_LIMITED` | 429 | API 配額耗盡 |
| `VALIDATION_ERROR` | 422 | 擷取資料驗證失敗 |

**Pydantic 模型**：
```python
from pydantic import BaseModel
from typing import Optional, Literal

class ErrorResponse(BaseModel):
    """API 錯誤回應"""
    request_id: str
    error_code: Literal[
        "FILE_TOO_LARGE",
        "INVALID_FORMAT", 
        "NO_IMAGE_IN_PDF",
        "OCR_FAILED",
        "RATE_LIMITED",
        "VALIDATION_ERROR"
    ]
    message: str
    details: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "error_code": "FILE_TOO_LARGE",
                "message": "檔案大小超過限制（最大 10MB）",
                "details": None
            }
        }
```

---

## TypeScript 類型定義（前端）

```typescript
// frontend/types/index.ts

/**
 * 身分證資訊
 */
export interface IdCardInfo {
  name: string
  id_number: string
  birth_date: string  // 民國年格式：YYY/MM/DD
  gender: '男' | '女'
  issue_date: string  // 民國年格式：YYY/MM/DD
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
  progress: number  // 0-100
  error: ErrorResponse | null
  result: ExtractionResult | null
}
```

---

## 實體關係與流程

```
┌─────────────┐
│ 使用者上傳   │
│   檔案      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ UploadedFile    │ ─────► 驗證大小、格式
│ (檔案元資料)     │
└────────┬────────┘
         │
         ▼
    [PDF?] ───Yes──► PDF 轉圖片
         │
         No
         │
         ▼
┌─────────────────┐
│ Gemini API 呼叫 │ ─────► 辨識圖片
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ IdCardInfo      │ ─────► 驗證欄位格式
│ (原始 JSON)     │
└────────┬────────┘
         │
         ▼
    [驗證通過?]
         │
    Yes  │  No
         │  └─────► ErrorResponse (VALIDATION_ERROR)
         │
         ▼
┌─────────────────┐
│ExtractionResult │ ─────► 回傳前端
│ (完整回應)      │
└─────────────────┘
```

---

## 資料生命週期

1. **請求開始**：使用者上傳檔案 → 建立 `UploadedFile` 物件（記憶體）
2. **處理中**：檔案內容傳遞給 Gemini API → 取得 JSON 回應
3. **解析驗證**：JSON 解析為 `IdCardInfo` → Pydantic 驗證
4. **回應**：封裝為 `ExtractionResult` → 返回前端
5. **清理**：請求結束後，所有物件自動被 Python GC 回收

**重要**：無任何資料寫入磁碟或資料庫，符合隱私要求。

---

## 測試資料範例

### 有效身分證資訊
```json
{
  "name": "陳大明",
  "id_number": "F123456789",
  "birth_date": "75/03/15",
  "gender": "男",
  "issue_date": "90/06/20",
  "issue_location": "高雄市",
  "confidence_score": 0.92
}
```

### 部分辨識失敗（partial）
```json
{
  "name": "李小華",
  "id_number": "B234567890",
  "birth_date": null,  // 無法辨識
  "gender": "女",
  "issue_date": "85/11/10",
  "issue_location": "台中市",
  "confidence_score": 0.67
}
```

### 驗證失敗範例
```json
{
  "name": "王",  // ❌ 少於 2 字元
  "id_number": "123456789",  // ❌ 缺少英文字母
  "birth_date": "1991/05/20",  // ❌ 西元年非民國年
  "gender": "M",  // ❌ 應為「男」
  "issue_date": "95/13/01",  // ❌ 月份無效
  "issue_location": "北京市"  // ❌ 非台灣縣市
}
```

---

## 下一步

資料模型已定義完成，接下來建立 API contracts（OpenAPI 規格）。
