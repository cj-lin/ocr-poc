# 快速開始指南：身分證資訊擷取系統

**Feature**: 001-id-card-extraction  
**Last Updated**: 2025-11-01

## 目標

在 10 分鐘內讓開發者在本地運行完整的身分證 OCR 系統，包含前端上傳介面和後端 API。

---

## 前置需求

### 必要工具

- **Docker Desktop** 4.25+ 及 Docker Compose（推薦）
  - 或 **Node.js** 20.x LTS + **Python** 3.11+（手動設定）
- **Git** 2.40+
- **Gemini API Key**（免費申請：https://makersuite.google.com/app/apikey）

### 可選工具

- **VS Code** + REST Client 擴充套件（測試 API）
- **Postman** 或 **Insomnia**（API 測試）

---

## 方法一：使用 Docker Compose（推薦）

### 步驟 1：Clone 專案並切換分支

```bash
git clone <repository-url>
cd ocr-poc
git checkout 001-id-card-extraction
```

### 步驟 2：設定環境變數

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，填入您的 Gemini API Key
# Windows: notepad .env
# macOS/Linux: nano .env
```

**.env 檔案內容**：
```bash
# Gemini API 設定
GEMINI_API_KEY=your_api_key_here

# 後端設定
BACKEND_URL=http://localhost:8000
LOG_LEVEL=INFO

# 前端設定
FRONTEND_URL=http://localhost:3000
```

### 步驟 3：啟動服務

```bash
docker-compose up --build
```

**預期輸出**：
```
✅ backend_1  | INFO:     Uvicorn running on http://0.0.0.0:8000
✅ frontend_1 | ✔ Nuxt ready in 3.2s
✅ frontend_1 | ➜ Local:   http://localhost:3000/
```

### 步驟 4：驗證安裝

1. **檢查後端健康狀態**：
   ```bash
   curl http://localhost:8000/api/health
   ```
   
   預期回應：
   ```json
   {
     "status": "healthy",
     "gemini_api": "connected",
     "timestamp": "2025-11-01T10:30:00Z"
   }
   ```

2. **開啟前端介面**：
   - 瀏覽器開啟 http://localhost:3000
   - 應看到檔案上傳介面

3. **測試上傳功能**：
   - 下載測試圖片：`tests/fixtures/sample_id_card.jpg`
   - 拖放到上傳區域或點擊選擇檔案
   - 10 秒內應看到擷取結果

---

## 方法二：手動設定（不使用 Docker）

### 步驟 1：設定後端

```bash
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數（Windows PowerShell）
$env:GEMINI_API_KEY="your_api_key_here"
# macOS/Linux:
export GEMINI_API_KEY="your_api_key_here"

# 啟動後端
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 步驟 2：設定前端（新終端機）

```bash
cd frontend

# 安裝依賴
npm install

# 設定環境變數
# Windows PowerShell:
$env:BACKEND_URL="http://localhost:8000"
# macOS/Linux:
export BACKEND_URL="http://localhost:8000"

# 啟動開發伺服器
npm run dev
```

### 步驟 3：驗證

同方法一的步驟 4。

---

## 常見問題排除

### ❌ 錯誤：`Gemini API connection failed`

**原因**：API Key 未設定或無效

**解決方案**：
1. 確認 `.env` 檔案中 `GEMINI_API_KEY` 已填入
2. 確認 API Key 有效：https://makersuite.google.com/app/apikey
3. 重新啟動服務：`docker-compose restart` 或手動重啟

### ❌ 錯誤：`Port 8000 already in use`

**原因**：埠號被其他服務占用

**解決方案**：
```bash
# 方法 1: 修改 docker-compose.yml 或 .env 中的埠號
# 方法 2: 停止占用該埠的服務
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### ❌ 錯誤：`Module not found: PIL`

**原因**：Python 依賴未正確安裝

**解決方案**：
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### ❌ 前端顯示：`Network Error`

**原因**：後端未啟動或 CORS 設定錯誤

**解決方案**：
1. 確認後端正在運行：`curl http://localhost:8000/api/health`
2. 檢查瀏覽器 Console 是否有 CORS 錯誤
3. 確認 `frontend/.env` 中 `BACKEND_URL` 正確

### ❌ 上傳後顯示：`OCR_FAILED`

**原因**：Gemini API 配額耗盡或網路問題

**解決方案**：
1. 檢查 API 配額：https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
2. 確認網路可連線至 Google API：`curl https://generativelanguage.googleapis.com`
3. 查看後端日誌：`docker-compose logs backend` 或手動查看終端機輸出

---

## 測試資料

### 下載測試圖片

專案提供測試用的合成身分證圖片（非真實資料）：

```bash
# 位於專案根目錄
tests/fixtures/
├── valid_id_card.jpg        # 清晰標準圖片
├── blurry_id_card.jpg       # 模糊圖片
├── tilted_id_card.jpg       # 傾斜圖片
└── sample_id_card.pdf       # PDF 格式
```

### 使用測試圖片

1. **方法 1**：透過前端網頁上傳
   - 開啟 http://localhost:3000
   - 選擇 `tests/fixtures/valid_id_card.jpg`
   - 點擊上傳

2. **方法 2**：使用 cURL 測試 API
   ```bash
   curl -X POST http://localhost:8000/api/extract \
     -F "file=@tests/fixtures/valid_id_card.jpg" \
     -H "Content-Type: multipart/form-data"
   ```

3. **方法 3**：使用 Python 腳本
   ```python
   import requests
   
   url = "http://localhost:8000/api/extract"
   files = {"file": open("tests/fixtures/valid_id_card.jpg", "rb")}
   response = requests.post(url, files=files)
   
   print(response.json())
   ```

---

## 執行測試

### 後端測試

```bash
cd backend

# 執行所有測試
pytest

# 執行單元測試
pytest tests/unit/

# 執行整合測試
pytest tests/integration/

# 顯示詳細輸出
pytest -v

# 顯示覆蓋率
pytest --cov=src
```

**預期輸出**：
```
======================== test session starts =========================
collected 15 items

tests/unit/test_file_service.py ........                       [ 53%]
tests/unit/test_validators.py ....                             [ 80%]
tests/integration/test_api_endpoints.py ...                    [100%]

======================== 15 passed in 3.25s ==========================
```

### 前端測試

```bash
cd frontend

# 執行所有測試
npm run test

# 執行特定測試檔案
npm run test FileUpload.spec.ts

# 執行測試並顯示覆蓋率
npm run test:coverage
```

---

## 開發工作流程

### 1. 啟動開發環境

```bash
# 使用 Docker Compose
docker-compose up

# 或手動啟動前後端（兩個終端機）
# 終端機 1:
cd backend && uvicorn src.main:app --reload

# 終端機 2:
cd frontend && npm run dev
```

### 2. 修改程式碼

- **後端**：編輯 `backend/src/` 下的檔案，Uvicorn 自動重新載入
- **前端**：編輯 `frontend/` 下的檔案，Vite 熱更新（HMR）

### 3. 查看日誌

```bash
# Docker Compose 日誌
docker-compose logs -f backend
docker-compose logs -f frontend

# 手動啟動的日誌直接顯示在終端機
```

### 4. 停止服務

```bash
# Docker Compose
docker-compose down

# 手動啟動：在終端機按 Ctrl+C
```

---

## API 使用範例

### 範例 1：上傳 JPG 圖片

**請求**：
```http
POST http://localhost:8000/api/extract
Content-Type: multipart/form-data

file: @valid_id_card.jpg
```

**回應**（200 OK）：
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "data": {
    "name": "王小明",
    "id_number": "A123456789",
    "birth_date": "80/05/20",
    "gender": "男",
    "issue_date": "95/12/01",
    "issue_location": "台北市",
    "confidence_score": 0.95
  },
  "processing_time": 3.25,
  "warnings": null
}
```

### 範例 2：上傳 PDF 檔案

**請求**：
```http
POST http://localhost:8000/api/extract
Content-Type: multipart/form-data

file: @sample_id_card.pdf
```

**回應**（200 OK）：
```json
{
  "request_id": "650e8400-e29b-41d4-a716-446655440001",
  "status": "success",
  "data": {
    "name": "李小華",
    "id_number": "B234567890",
    "birth_date": "75/03/15",
    "gender": "女",
    "issue_date": "85/11/10",
    "issue_location": "台中市"
  },
  "processing_time": 4.56
}
```

### 範例 3：檔案過大錯誤

**請求**：上傳 15MB 圖片

**回應**（413 Payload Too Large）：
```json
{
  "request_id": "950e8400-e29b-41d4-a716-446655440004",
  "error_code": "FILE_TOO_LARGE",
  "message": "檔案大小超過限制（最大 10MB）",
  "details": null
}
```

---

## 下一步

✅ 系統已運行，接下來可以：

1. **查看 API 文件**：http://localhost:8000/docs（Swagger UI）
2. **開始開發任務**：參考 `specs/001-id-card-extraction/tasks.md`
3. **閱讀技術文件**：
   - `specs/001-id-card-extraction/research.md` - 技術決策
   - `specs/001-id-card-extraction/data-model.md` - 資料模型
   - `specs/001-id-card-extraction/contracts/api.yaml` - API 規格

---

## 聯絡與支援

如遇到問題：

1. 查看常見問題排除章節
2. 檢查 GitHub Issues
3. 查看後端日誌：`docker-compose logs backend`
4. 查看前端 Console（瀏覽器開發者工具）

**重要**：測試時請使用專案提供的合成測試圖片，請勿使用真實身分證。
