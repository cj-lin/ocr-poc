# Technical Research: 身分證資訊擷取系統

**Feature**: 001-id-card-extraction  
**Date**: 2025-11-01  
**Status**: Complete

## 研究目標

解決技術選型和實作方式的不確定性，為 Phase 1 設計階段提供明確的技術決策依據。

## 1. Gemini API 整合策略

### 決策：使用 Gemini 1.5 Flash with Vision

**理由**：
- Gemini 1.5 Flash 是截至 2025-11 最新的穩定版本，支援多模態輸入（文字 + 圖片）
- 針對 OCR 任務優化，回應速度快（平均 2-5 秒）
- 相較於 Gemini 1.5 Pro，Flash 版本成本更低且速度更快，適合 MVP
- 支援結構化輸出（JSON mode），可直接要求輸出身分證欄位的 JSON 格式

**替代方案評估**：
- **Gemini 1.5 Pro**：準確率稍高但回應時間較長（5-10 秒），成本較高，MVP 階段不需要
- **GPT-4 Vision**：需要 OpenAI API，使用者需求明確指定 Gemini
- **專用 OCR API（如 Google Cloud Vision OCR）**：需要額外訓練或規則解析身分證欄位，Gemini 可透過 prompt 直接理解欄位語意

**實作要點**：
```python
# 使用 google-generativeai SDK
import google.generativeai as genai

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Prompt 設計：明確要求輸出 JSON 格式
prompt = """
請辨識這張台灣身分證正面的資訊，並以 JSON 格式輸出以下欄位：
- 姓名 (name)
- 身分證字號 (id_number)
- 出生日期 (birth_date, 格式：民國 YYY/MM/DD)
- 性別 (gender, 值：男 或 女)
- 發證日期 (issue_date, 格式：民國 YYY/MM/DD)
- 發證地點 (issue_location)

如果某個欄位無法辨識，請設為 null。
"""

response = model.generate_content([prompt, image])
```

### Rate Limiting 處理

**決策**：實作指數退避重試機制 + 使用者友善錯誤訊息

**理由**：
- Gemini API 免費層有 RPM（每分鐘請求數）限制
- MVP 階段使用免費層，需優雅處理配額耗盡情境
- 避免直接向使用者顯示技術錯誤碼

**實作策略**：
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_gemini_api(image, prompt):
    try:
        response = await model.generate_content_async([prompt, image])
        return response
    except ResourceExhausted:
        # 記錄到日誌
        logger.warning("Gemini API quota exceeded, retrying...")
        raise
```

---

## 2. 檔案上傳與處理

### 決策：使用 FastAPI UploadFile + 記憶體處理

**理由**：
- FastAPI 原生支援 `UploadFile`，自動處理 multipart/form-data
- 規格要求不永久儲存檔案，使用記憶體處理符合隱私要求
- 10MB 限制下，記憶體處理不會造成效能問題

**實作要點**：
```python
from fastapi import UploadFile, File, HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/api/extract")
async def extract_id_card(file: UploadFile = File(...)):
    # 驗證檔案大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="檔案大小超過 10MB 限制")
    
    # 驗證 MIME 類型
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="不支援的檔案格式")
    
    # 處理完畢後，contents 自動釋放記憶體
```

### PDF 轉圖片處理

**決策：使用 PyMuPDF (fitz) 提取第一頁為圖片

**理由**：
- PyMuPDF 是純 Python 實作，無需系統依賴（如 Poppler）
- 效能優異，支援高解析度轉換
- 可直接輸出 PIL Image 物件，無需寫入檔案

**替代方案評估**：
- **pdf2image**：需要 Poppler 系統依賴，Docker 映像檔變大
- **PyPDF2**：不支援圖片提取，僅能處理文字

**實作要點**：
```python
import fitz  # PyMuPDF
from PIL import Image

def pdf_to_image(pdf_bytes: bytes) -> Image.Image:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if len(doc) == 0:
        raise ValueError("PDF 無有效頁面")
    
    page = doc[0]  # 僅處理第一頁
    pix = page.get_pixmap(dpi=300)  # 高解析度確保 OCR 品質
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img
```

---

## 3. 前端檔案上傳體驗

### 決策：使用原生 HTML5 拖放 API + 進度指示

**理由**：
- Nuxt 4 搭配 Vue 3 Composition API，無需額外檔案上傳套件
- 原生 API 輕量且可控性高，符合「避免過度設計」原則
- 可精確控制檔案驗證邏輯（大小、格式）

**實作要點**：
```typescript
// composables/useFileUpload.ts
export const useFileUpload = () => {
  const isDragging = ref(false)
  const uploadProgress = ref(0)
  
  const validateFile = (file: File) => {
    const maxSize = 10 * 1024 * 1024 // 10MB
    const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
    
    if (file.size > maxSize) {
      throw new Error('檔案大小超過 10MB 限制')
    }
    if (!allowedTypes.includes(file.type)) {
      throw new Error('不支援的檔案格式，請上傳 JPG、PNG 或 PDF')
    }
  }
  
  const uploadFile = async (file: File) => {
    validateFile(file)
    
    const formData = new FormData()
    formData.append('file', file)
    
    // 使用 Nuxt 3 的 $fetch（自動處理 CSRF）
    const response = await $fetch('/api/extract', {
      method: 'POST',
      body: formData,
      onUploadProgress: (e) => {
        uploadProgress.value = (e.loaded / e.total) * 100
      }
    })
    
    return response
  }
  
  return { isDragging, uploadProgress, uploadFile }
}
```

### 拖放區域設計

**決策**：使用 TailwindCSS 實作視覺回饋

**理由**：
- TailwindCSS 是 Nuxt 生態系標準選擇，無需額外 UI 框架
- 原子化 CSS 符合「簡化」原則，避免引入重量級組件庫
- 易於實作拖放視覺狀態（hover、dragging）

**視覺規格**：
- 預設狀態：虛線邊框 + 上傳圖示
- 拖曳中：實線藍色邊框 + 背景色變化
- 上傳中：進度條 + 百分比顯示
- 完成：顯示縮圖 + 擷取結果

---

## 4. 錯誤處理與日誌

### 決策：結構化日誌 + 請求追蹤 ID

**理由**：
- 憲章要求「錯誤訊息必須包含足夠上下文」
- 請求 ID 可關聯前端錯誤與後端日誌，便於除錯
- 結構化 JSON 日誌便於未來接入監控系統

**實作策略**：
```python
# backend/src/utils/logging_config.py
import logging
import json
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar('request_id', default='')

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'request_id': request_id_var.get(),
            'message': record.getMessage(),
            'module': record.module,
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)

# 中介軟體注入 request_id
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### 使用者友善錯誤訊息

**決策**：定義錯誤代碼對應表

**實作**：
```python
ERROR_MESSAGES = {
    "FILE_TOO_LARGE": "檔案大小超過限制（最大 10MB）",
    "INVALID_FORMAT": "不支援的檔案格式，請上傳 JPG、PNG 或 PDF",
    "NO_IMAGE_IN_PDF": "PDF 中未找到圖片，請上傳包含身分證圖片的檔案",
    "OCR_FAILED": "辨識服務暫時無法使用，請稍後再試",
    "RATE_LIMITED": "處理佇列中，預估等待時間：2 分鐘",
}
```

---

## 5. 測試策略

### 單元測試

**後端**：
- `test_file_service.py`：檔案驗證邏輯（大小、格式、PDF 轉換）
- `test_ocr_service.py`：Mock Gemini API，測試 prompt 生成和回應解析
- `test_validators.py`：欄位驗證（身分證字號格式、日期格式）

**前端**：
- `FileUpload.spec.ts`：檔案選擇、拖放、驗證邏輯
- `EditableForm.spec.ts`：表單欄位編輯、驗證

### 整合測試

**後端**：
```python
# tests/integration/test_api_endpoints.py
def test_上傳有效圖片_應返回擷取結果():
    with open("tests/fixtures/valid_id_card.jpg", "rb") as f:
        response = client.post("/api/extract", files={"file": f})
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "id_number" in data
```

**前端**：
- E2E 測試使用 Playwright（選擇性，MVP 階段可省略）

### 測試資料

**決策**：建立合成測試身分證圖片

**理由**：
- 使用真實身分證違反隱私法規
- 合成圖片需包含：清晰圖片、模糊圖片、傾斜圖片、錯誤格式

**工具**：使用 Pillow + Faker 生成測試資料
```python
# tests/fixtures/generate_test_id.py
from PIL import Image, ImageDraw, ImageFont
from faker import Faker

fake = Faker('zh_TW')

def generate_test_id_card() -> Image.Image:
    img = Image.new('RGB', (856, 540), color='white')
    draw = ImageDraw.Draw(img)
    
    # 繪製身分證樣式...
    draw.text((100, 100), f"姓名：{fake.name()}", fill='black')
    draw.text((100, 150), f"身分證字號：A123456789", fill='black')
    # ... 其他欄位
    
    return img
```

---

## 6. 開發環境設定

### 決策：使用 Docker Compose 統一環境

**理由**：
- 確保前後端開發環境一致
- 簡化新成員 onboarding
- 符合「快速開始指南可執行」憲章要求

**docker-compose.yml 結構**：
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./backend:/app
    command: uvicorn src.main:app --host 0.0.0.0 --reload
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
```

### 環境變數管理

**決策**：使用 `.env` 檔案 + `.env.example` 範本

```bash
# .env.example
GEMINI_API_KEY=your_api_key_here
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=INFO
```

---

## 7. 版本與相依性

### Python 依賴（backend/requirements.txt）

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
python-multipart==0.0.9
google-generativeai==0.8.0
pillow==10.4.0
pymupdf==1.24.10
pydantic==2.9.0
tenacity==9.0.0
pytest==8.3.0
httpx==0.27.0
```

### Node.js 依賴（frontend/package.json）

```json
{
  "dependencies": {
    "nuxt": "^3.13.0",
    "vue": "^3.4.0",
    "@nuxtjs/tailwindcss": "^6.12.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "vitest": "^2.0.0",
    "@vue/test-utils": "^2.4.0",
    "eslint": "^9.0.0",
    "prettier": "^3.3.0"
  }
}
```

---

## 研究結論

所有技術決策已明確，無剩餘 NEEDS CLARIFICATION 項目。主要技術棧：

- **前端**：Nuxt 4 + Vue 3 + TypeScript + TailwindCSS
- **後端**：FastAPI + Python 3.11 + Gemini 1.5 Flash
- **檔案處理**：Pillow（圖片）+ PyMuPDF（PDF）
- **測試**：pytest（後端）+ Vitest（前端）
- **開發環境**：Docker Compose

所有選擇符合憲章原則：
- ✅ 使用穩定版本（高品質）
- ✅ 架構簡單，避免過度設計
- ✅ 可獨立測試各層（可測試性）
- ✅ MVP 優先，延後非必要功能

**下一步**：進入 Phase 1，建立 data-model.md 和 API contracts。
