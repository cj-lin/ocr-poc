# 身分證資訊擷取系統

使用 Gemini AI 從身分證圖片或 PDF 中自動擷取結構化資訊的網頁應用程式。

## 功能特點

- ✅ 支援 JPG、PNG、PDF 格式上傳
- ✅ 自動辨識 6 個身分證欄位（姓名、身分證字號、出生日期、性別、發證日期、發證地點）
- ✅ 可編輯擷取結果
- ✅ 不永久儲存上傳檔案（符合隱私要求）
- ✅ 前後端分離架構
- ✅ Docker Compose 一鍵啟動

## 快速開始

### 使用 Docker Compose（推薦）

1. **Clone 專案**
   ```bash
   git clone <repository-url>
   cd ocr-poc
   ```

2. **設定環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env 檔案，填入您的 Gemini API Key
   ```

3. **啟動服務**
   ```bash
   docker-compose up --build
   ```

4. **存取應用程式**
   - 前端：http://localhost:3000
   - 後端 API：http://localhost:8000
   - API 文件：http://localhost:8000/docs

### 手動設定

詳細安裝步驟請參考 [快速開始指南](specs/001-id-card-extraction/quickstart.md)。

## 技術棧

### 前端
- Nuxt 4
- Vue 3
- TypeScript 5.x
- TailwindCSS

### 後端
- FastAPI 0.115+
- Python 3.11+
- Gemini 1.5 Flash API
- Pillow (圖片處理)
- PyMuPDF (PDF 處理)

## 專案結構

```
backend/          # FastAPI 後端服務
  src/           # 主程式碼
  tests/         # 測試
frontend/         # Nuxt 4 前端應用程式
  components/    # Vue 組件
  composables/   # Composable functions
  pages/         # 頁面路由
  types/         # TypeScript 類型定義
specs/           # 功能規格文件
  001-id-card-extraction/
docker-compose.yml
.env.example
```

## 開發指南

### 使用 Just 指令（推薦）

本專案提供 [`justfile`](justfile) 來簡化常用的開發與測試指令。

**安裝 just**：
```bash
# Windows (using Scoop)
scoop install just

# 或使用 Chocolatey
choco install just

# 或從 GitHub Releases 下載：https://github.com/casey/just/releases
```

**常用指令**：
```bash
just                    # 顯示所有可用指令
just test-all           # 執行前後端所有測試
just test-backend       # 執行後端測試
just test-frontend      # 執行前端測試
just lint-all           # 檢查程式碼品質
just lint-all-fix       # 自動修正程式碼格式
just up                 # 啟動 Docker 服務
just ci                 # 執行完整 CI 檢查
```

### 傳統方式執行測試

**後端測試**：
```bash
cd backend
pytest                              # 所有測試
pytest tests/unit/                  # 僅單元測試
pytest tests/integration/           # 僅整合測試
pytest --cov=src --cov-report=html  # 帶覆蓋率報告
```

**前端測試**：
```bash
cd frontend
npm run test                # 執行測試
npm run test:coverage       # 帶覆蓋率報告
```

### 程式碼檢查

**後端 linting**：
```bash
cd backend
ruff check src/ tests/      # 檢查
ruff check src/ --fix       # 自動修正
black src/ tests/           # 格式化
```

**前端 linting**：
```bash
cd frontend
npm run lint                # 檢查
npm run lint:fix            # 自動修正
npm run format              # 格式化
```

## API 文件

完整 API 規格請參考：
- [OpenAPI 規格](specs/001-id-card-extraction/contracts/api.yaml)
- [Swagger UI](http://localhost:8000/docs)（服務啟動後可存取）

## 限制

- 單一檔案大小 ≤ 10MB
- 僅支援台灣身分證正面
- PDF 僅處理第一頁
- 辨識準確率取決於圖片品質

## 隱私聲明

本系統不永久儲存任何上傳的檔案或擷取的個人資料。所有資料僅在處理期間暫存於記憶體中，請求結束後立即清除。

## 授權

MIT License

## 相關文件

- [功能規格](specs/001-id-card-extraction/spec.md)
- [技術研究](specs/001-id-card-extraction/research.md)
- [資料模型](specs/001-id-card-extraction/data-model.md)
- [快速開始指南](specs/001-id-card-extraction/quickstart.md)
- [任務清單](specs/001-id-card-extraction/tasks.md)
