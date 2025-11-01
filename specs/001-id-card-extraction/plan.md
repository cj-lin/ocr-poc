# Implementation Plan: 身分證資訊擷取系統

**Branch**: `001-id-card-extraction` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-id-card-extraction/spec.md`

## Summary

建立一個網頁應用程式，允許使用者上傳身分證正面圖片或 PDF，透過 Gemini API 進行 OCR 辨識，自動擷取姓名、身分證字號、出生日期、性別、發證日期、發證地點等欄位，並顯示在可編輯表單中。系統採用前後端分離架構，前端使用 Nuxt 4 提供互動介面，後端使用 FastAPI 處理檔案上傳和 LLM 整合，資料不永久儲存。

## Technical Context

**Language/Version**: 
- 前端：Node.js 20.x LTS + TypeScript 5.x
- 後端：Python 3.11+

**Primary Dependencies**: 
- 前端：Nuxt 4 (latest stable), Vue 3, TailwindCSS
- 後端：FastAPI 0.115+, google-generativeai (Gemini SDK), Pillow (圖片處理), PyMuPDF (PDF 處理)

**Storage**: N/A（資料不永久儲存，僅使用記憶體或臨時檔案）

**Testing**: 
- 前端：Vitest + Vue Test Utils
- 後端：pytest + httpx (API 測試)

**Target Platform**: Web 應用程式（瀏覽器 + Linux/Docker 後端）

**Project Type**: Web application（前後端分離）

**Performance Goals**: 
- 圖片上傳到顯示結果 < 30 秒
- API 回應時間（不含 LLM）< 200ms
- 支援 10 位並行使用者

**Constraints**: 
- 單一檔案大小 ≤ 10MB
- Gemini API 配額限制（需處理 rate limiting）
- 不永久儲存個人資料（隱私要求）
- 處理耗時主要受 Gemini API 回應時間影響

**Scale/Scope**: 
- MVP 階段：< 50 並行使用者
- 單一使用者對話期間暫存資料
- 無需資料庫或持久化層

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ 一、高品質優先
- Python 使用 Black + Ruff 進行格式化和 linting
- TypeScript 使用 ESLint + Prettier
- 所有 API 端點使用 Pydantic 模型定義類型
- Vue 組件使用 TypeScript 嚴格模式
- 錯誤處理使用 FastAPI 異常處理機制

### ✅ 二、可測試性設計
- 前端組件可獨立測試（Vitest）
- 後端 API 端點可獨立測試（pytest）
- Gemini API 呼叫使用 dependency injection，可 mock 測試
- 每個 User Story 對應獨立的測試套件

### ✅ 三、MVP 方法論
- P1（圖片上傳 OCR）為 MVP，可獨立交付
- P2（PDF 支援）和 P3（批次處理）為增量功能
- 不預先實作使用者認證、資料庫等非必要功能

### ✅ 四、避免過度設計
- 不使用複雜狀態管理（Pinia 僅在需要時引入）
- 不引入訊息佇列（初期直接處理請求）
- 不使用微服務架構（單一後端服務）
- 不實作快取層（MVP 階段不需要）

### ✅ 五、可觀測性與除錯能力
- 使用 Python logging 模組記錄所有 API 請求
- 前端使用 console 記錄關鍵操作
- 錯誤訊息包含請求 ID 以便追蹤
- 開發模式保留上傳圖片供視覺化驗證

**憲章合規性評估**：✅ 通過，無違反項目

**Phase 1 重新評估**：✅ 設計完成後仍符合所有憲章原則
- 資料模型使用 Pydantic 確保類型安全（高品質）
- API 合約明確定義測試場景（可測試性）
- 架構保持簡單，僅前後端分離（避免過度設計）
- 結構化日誌和請求追蹤已納入設計（可觀測性）

## Project Structure

### Documentation (this feature)

```text
specs/001-id-card-extraction/
├── plan.md              # 本檔案
├── research.md          # Phase 0 技術研究
├── data-model.md        # Phase 1 資料模型
├── quickstart.md        # Phase 1 快速開始指南
├── contracts/           # Phase 1 API 合約
│   └── api.yaml         # OpenAPI 規格
└── checklists/          # 品質檢查清單
    └── requirements.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                 # FastAPI 應用程式入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API 路由定義
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py      # OCR 核心邏輯
│   │   ├── file_service.py     # 檔案處理（上傳、驗證、PDF 轉圖片）
│   │   └── gemini_client.py    # Gemini API 客戶端
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic 模型
│   └── utils/
│       ├── __init__.py
│       ├── logging_config.py   # 日誌設定
│       └── validators.py       # 檔案驗證工具
├── tests/
│   ├── unit/
│   │   ├── test_file_service.py
│   │   ├── test_ocr_service.py
│   │   └── test_validators.py
│   └── integration/
│       └── test_api_endpoints.py
├── requirements.txt
└── pyproject.toml

frontend/
├── app.vue                     # Nuxt 根組件
├── nuxt.config.ts              # Nuxt 設定
├── pages/
│   └── index.vue               # 主頁面（上傳介面）
├── components/
│   ├── FileUpload.vue          # 檔案上傳組件
│   ├── ExtractionResult.vue    # 結果顯示組件
│   └── EditableForm.vue        # 可編輯表單組件
├── composables/
│   ├── useFileUpload.ts        # 檔案上傳邏輯
│   └── useOcrApi.ts            # API 呼叫邏輯
├── types/
│   └── index.ts                # TypeScript 類型定義
├── tests/
│   └── components/
│       ├── FileUpload.spec.ts
│       └── EditableForm.spec.ts
├── package.json
└── tsconfig.json

docker-compose.yml              # 本地開發環境
.env.example                    # 環境變數範例
README.md                       # 專案說明
```

**Structure Decision**: 採用 Web application 結構（Option 2），前後端完全分離。前端負責 UI/UX，後端負責檔案處理和 LLM 整合。此架構符合 MVP 原則，避免過度複雜化，且便於獨立測試各層。

## Complexity Tracking

> 無違反憲章項目，此章節保留為空
