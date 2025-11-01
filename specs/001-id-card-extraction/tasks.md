# Tasks: 身分證資訊擷取系統

**Input**: Design documents from `/specs/001-id-card-extraction/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.yaml

**Tests**: 本專案採用 TDD（測試驅動開發），依據憲章要求，測試必須先寫且失敗後才能實作。

**Organization**: 任務依 User Story 分組，每個故事可獨立實作和測試。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可平行執行（不同檔案、無相依性）
- **[Story]**: 所屬 User Story（US1、US2、US3）
- 包含確切檔案路徑

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- 本專案採用前後端分離結構

---

## Phase 1: Setup(專案初始化)

**Purpose**: 建立專案基礎結構和開發環境

- [X] T001 建立專案根目錄結構(backend/、frontend/、docker-compose.yml、.env.example)
- [X] T002 [P] 初始化後端 Python 專案(backend/requirements.txt、backend/pyproject.toml)
- [X] T003 [P] 初始化前端 Nuxt 4 專案(frontend/package.json、frontend/nuxt.config.ts、frontend/tsconfig.json)
- [X] T004 [P] 設定 Docker Compose 開發環境(docker-compose.yml,包含 backend 和 frontend 服務)
- [X] T005 [P] 建立環境變數範本(.env.example,包含 GEMINI_API_KEY、BACKEND_URL、LOG_LEVEL)
- [X] T006 [P] 設定後端 linting 工具(backend/.ruff.toml、backend/pyproject.toml 的 Black 設定)
- [X] T007 [P] 設定前端 linting 工具(frontend/.eslintrc.js、frontend/.prettierrc)
- [X] T008 建立專案 README.md(快速開始指南參考 specs/001-id-card-extraction/quickstart.md)

---

## Phase 2: Foundational（基礎架構）

**Purpose**: 建立所有 User Story 共用的核心基礎設施

**⚠️ CRITICAL**: 此階段必須完成後，User Story 實作才能開始

### 後端基礎

- [X] T009 建立 FastAPI 應用程式入口(backend/src/main.py,包含 CORS 設定)
- [X] T010 [P] 實作結構化日誌設定(backend/src/utils/logging_config.py,包含 JSON formatter 和 request_id)
- [X] T011 [P] 建立 Pydantic schemas 基礎檔案(backend/src/models/__init__.py 和 backend/src/models/schemas.py 架構)
- [X] T012 實作請求追蹤中介軟體(backend/src/main.py 中的 add_request_id middleware)
- [X] T013 [P] 建立錯誤代碼對應表(backend/src/utils/constants.py,定義 ERROR_MESSAGES)
- [X] T014 [P] 實作自訂異常處理器(backend/src/main.py 中的 exception handlers)
- [X] T015 實作健康檢查端點(backend/src/api/routes.py 的 /api/health)

### 前端基礎

- [X] T016 設定 TailwindCSS(frontend/tailwind.config.js 和 frontend/nuxt.config.ts 整合)
- [X] T017 [P] 建立 TypeScript 類型定義(frontend/types/index.ts,包含 IdCardInfo、ExtractionResult、ErrorResponse)
- [X] T018 建立 Nuxt 根組件(frontend/app.vue,基本佈局)
- [X] T019 建立主頁面架構(frontend/pages/index.vue,空白頁面架構)

**Checkpoint**: 基礎架構完成 - User Story 實作可開始

---

## Phase 3: User Story 1 - 上傳圖片並擷取基本資訊 (Priority: P1) 🎯 MVP

**Goal**: 使用者上傳 JPG/PNG 身分證圖片，系統透過 Gemini API 辨識並顯示 6 個欄位於可編輯表單中

**Independent Test**: 上傳一張標準身分證圖片，驗證所有欄位正確顯示且可編輯

### 測試(US1) - 必須先寫且失敗

- [X] T020 [P] [US1] 撰寫檔案驗證單元測試(backend/tests/unit/test_validators.py,測試檔案大小、MIME 類型、檔案名稱驗證)
- [X] T021 [P] [US1] 撰寫 Gemini 客戶端單元測試(backend/tests/unit/test_gemini_client.py,mock Gemini API 回應)
- [X] T022 [P] [US1] 撰寫 OCR 服務單元測試(backend/tests/unit/test_ocr_service.py,mock Gemini client)
- [X] T023 [P] [US1] 撰寫圖片上傳 API 整合測試(backend/tests/integration/test_api_endpoints.py,測試 /api/extract 完整流程)
- [X] T024 [P] [US1] 撰寫 FileUpload 組件測試(frontend/tests/components/FileUpload.spec.ts,測試檔案選擇、拖放、驗證)
- [X] T025 [P] [US1] 撰寫 EditableForm 組件測試(frontend/tests/components/EditableForm.spec.ts,測試欄位編輯、驗證)

### 後端實作(US1)

- [X] T026 [P] [US1] 實作檔案驗證工具(backend/src/utils/validators.py,包含 validate_file_size、validate_mime_type)
- [X] T027 [P] [US1] 定義 Pydantic 模型(backend/src/models/schemas.py,包含 IdCardInfo、ExtractionResult、ErrorResponse)
- [X] T028 [US1] 實作 Gemini API 客戶端(backend/src/services/gemini_client.py,包含 prompt 設計和 retry 邏輯)
- [X] T029 [US1] 實作檔案處理服務(backend/src/services/file_service.py,包含圖片讀取和驗證)
- [X] T030 [US1] 實作 OCR 服務(backend/src/services/ocr_service.py,整合 Gemini client 和欄位驗證)
- [X] T031 [US1] 實作圖片上傳 API 路由(backend/src/api/routes.py 的 POST /api/extract,處理圖片上傳)
- [X] T032 [US1] 加入結構化日誌記錄(在 ocr_service.py 和 routes.py 中記錄處理過程)

### 前端實作(US1)

- [X] T033 [P] [US1] 實作檔案上傳 composable(frontend/composables/useFileUpload.ts,包含驗證、拖放、進度)
- [X] T034 [P] [US1] 實作 API 呼叫 composable(frontend/composables/useOcrApi.ts,包含錯誤處理)
- [X] T035 [P] [US1] 建立 FileUpload 組件(frontend/components/FileUpload.vue,拖放區域 + 檔案選擇)
- [X] T036 [P] [US1] 建立 ExtractionResult 組件(frontend/components/ExtractionResult.vue,顯示擷取結果)
- [X] T037 [P] [US1] 建立 EditableForm 組件(frontend/components/EditableForm.vue,6 個可編輯欄位)
- [X] T038 [US1] 整合主頁面(frontend/pages/index.vue,組合所有組件並實作上傳流程)
- [X] T039 [US1] 實作載入指示器和錯誤訊息顯示(在 index.vue 中加入 UI 狀態管理)

### 驗證（US1）

- [ ] T040 [US1] 執行所有 US1 測試並確認通過（pytest backend/tests/ -k US1, npm run test -- FileUpload EditableForm）
- [ ] T041 [US1] 使用測試圖片驗證完整流程（上傳 tests/fixtures/valid_id_card.jpg）
- [ ] T042 [US1] 驗證錯誤情境（檔案過大、格式錯誤、Gemini API 錯誤）

**Checkpoint**: US1 完成 - MVP 可交付！使用者可上傳圖片並取得可編輯的擷取結果

---

## Phase 4: User Story 2 - 支援 PDF 格式上傳 (Priority: P2)

**Goal**: 使用者可上傳包含身分證圖片的 PDF，系統自動從第一頁提取圖片並辨識

**Independent Test**: 上傳單頁 PDF 檔案，驗證系統正確擷取並顯示資訊

### 測試（US2）

- [ ] T043 [P] [US2] 撰寫 PDF 處理單元測試（backend/tests/unit/test_file_service.py，測試 pdf_to_image 函式）
- [ ] T044 [P] [US2] 撰寫 PDF 上傳 API 整合測試（backend/tests/integration/test_api_endpoints.py，測試 PDF 完整流程）

### 後端實作（US2）

- [ ] T045 [US2] 安裝 PyMuPDF 依賴（在 backend/requirements.txt 加入 pymupdf==1.24.10）
- [ ] T046 [US2] 實作 PDF 轉圖片功能（backend/src/services/file_service.py 的 pdf_to_image 函式）
- [ ] T047 [US2] 擴充檔案處理服務（backend/src/services/file_service.py，加入 PDF 檢測和轉換邏輯）
- [ ] T048 [US2] 更新 API 路由處理 PDF（backend/src/api/routes.py，在 /api/extract 加入 PDF 處理分支）
- [ ] T049 [US2] 處理 PDF 特殊錯誤（無圖片、多頁 PDF 提示訊息）

### 前端實作（US2）

- [ ] T050 [US2] 擴充檔案上傳驗證（frontend/composables/useFileUpload.ts，允許 application/pdf MIME type）
- [ ] T051 [US2] 更新上傳介面提示（frontend/components/FileUpload.vue，說明支援 PDF 格式）

### 驗證（US2）

- [ ] T052 [US2] 執行所有 US2 測試並確認通過（pytest backend/tests/ -k US2）
- [ ] T053 [US2] 使用測試 PDF 驗證流程（上傳 tests/fixtures/sample_id_card.pdf）
- [ ] T054 [US2] 驗證多頁 PDF 和無圖片 PDF 錯誤訊息

**Checkpoint**: US1 + US2 完成 - 支援圖片和 PDF 兩種格式

---

## Phase 5: User Story 3 - 批次處理多筆上傳 (Priority: P3)

**Goal**: 使用者一次上傳多個檔案，系統依序處理並顯示所有結果

**Independent Test**: 一次上傳 3 張圖片，驗證系統依序顯示 3 組結果

### 測試（US3）

- [ ] T055 [P] [US3] 撰寫批次處理 API 整合測試（backend/tests/integration/test_api_endpoints.py，測試多檔案上傳）
- [ ] T056 [P] [US3] 撰寫批次結果組件測試（frontend/tests/components/BatchResults.spec.ts）

### 後端實作（US3）

- [ ] T057 [US3] 定義批次回應 Pydantic 模型（backend/src/models/schemas.py，包含 BatchExtractionResult）
- [ ] T058 [US3] 實作批次處理端點（backend/src/api/routes.py 的 POST /api/extract/batch，接受多檔案）
- [ ] T059 [US3] 實作批次 OCR 服務（backend/src/services/ocr_service.py，加入 process_batch 函式）
- [ ] T060 [US3] 加入批次處理進度追蹤（在 batch 端點中回傳處理進度）

### 前端實作（US3）

- [ ] T061 [P] [US3] 實作批次上傳 composable（frontend/composables/useBatchUpload.ts，管理多檔案狀態）
- [ ] T062 [P] [US3] 建立 BatchResults 組件（frontend/components/BatchResults.vue，清單式顯示所有結果）
- [ ] T063 [US3] 擴充檔案上傳支援多選（frontend/components/FileUpload.vue，加入 multiple 屬性）
- [ ] T064 [US3] 更新主頁面支援批次模式（frontend/pages/index.vue，加入批次/單一模式切換）
- [ ] T065 [US3] 實作批次進度指示器（frontend/components/BatchProgress.vue，顯示「處理中: X/Y」）

### 驗證（US3）

- [ ] T066 [US3] 執行所有 US3 測試並確認通過（pytest backend/tests/ -k US3, npm run test -- BatchResults）
- [ ] T067 [US3] 使用多個測試檔案驗證批次流程（上傳 5 張圖片）
- [ ] T068 [US3] 驗證部分失敗情境（批次中有 1 張辨識失敗）

**Checkpoint**: 所有 User Stories 完成 - 完整功能系統

---

## Phase 6: Polish & Cross-Cutting Concerns（最佳化與收尾）

**Purpose**: 改善所有 User Stories 的品質和文件

- [ ] T069 [P] 建立合成測試資料（tests/fixtures/generate_test_id.py，產生測試用身分證圖片）
- [ ] T070 [P] 產生測試圖片和 PDF（執行 generate_test_id.py，建立 valid_id_card.jpg 等）
- [ ] T071 [P] 撰寫 API 文件註解（在 routes.py 加入詳細的 docstring 和 OpenAPI 描述）
- [ ] T072 [P] 實作 Swagger UI（FastAPI 自動生成，驗證 http://localhost:8000/docs 可存取）
- [ ] T073 [P] 加入前端錯誤邊界處理（frontend/app.vue，全域錯誤捕捉）
- [ ] T074 [P] 最佳化 Gemini prompt（backend/src/services/gemini_client.py，調整 prompt 提升準確率）
- [ ] T075 [P] 加入效能監控日誌（在 ocr_service.py 記錄處理時間）
- [ ] T076 執行完整測試套件（pytest backend/tests/ && npm run test）
- [ ] T077 執行 linting 檢查（ruff check backend/src/ && npm run lint）
- [ ] T078 驗證 quickstart.md 指南可執行（依照 specs/001-id-card-extraction/quickstart.md 從頭執行）
- [ ] T079 更新 README.md（加入功能說明、安裝步驟、使用範例）
- [ ] T080 程式碼審查與重構（檢查所有 TODO 註解，移除除錯程式碼）

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS all user stories
    ↓
    ├─→ Phase 3 (US1 - P1) ← MVP
    ├─→ Phase 4 (US2 - P2) ← 可與 US1 平行
    └─→ Phase 5 (US3 - P3) ← 可與 US1, US2 平行
    ↓
Phase 6 (Polish)
```

### User Story Dependencies

- **US1 (P1)**: 無相依性，完成 Foundational 後即可開始
- **US2 (P2)**: 依賴 US1 的檔案處理服務，但可平行開發（使用分支）
- **US3 (P3)**: 依賴 US1 的基本上傳功能，建議 US1 完成後再開始

### Within Each User Story

1. **測試先行**（TDD）：所有測試任務（T020-T025）平行撰寫 → 執行確認失敗
2. **後端實作**：T026-T027（工具和模型）平行 → T028-T031（服務和 API）依序
3. **前端實作**：T033-T037（composables 和組件）平行 → T038-T039（整合）依序
4. **驗證**：T040-T042 依序執行

### Parallel Opportunities

**Phase 1 Setup**：
- T002, T003 可平行（後端/前端初始化）
- T004, T005, T006, T007 可平行（環境設定）

**Phase 2 Foundational**：
- 後端：T010, T011, T013, T014 可平行
- 前端：T016, T017 可平行
- 後端與前端基礎可完全平行

**Phase 3 US1**：
- 測試：T020-T025 全部可平行撰寫
- 後端實作：T026-T027 可平行
- 前端實作：T033-T037 可平行（5 個任務同時進行）

**Phase 6 Polish**：
- T069-T075 全部可平行執行

---

## Parallel Example: User Story 1

### 步驟 1：平行撰寫所有測試（6 個任務同時）
```bash
Task: "撰寫檔案驗證單元測試（backend/tests/unit/test_validators.py）"
Task: "撰寫 Gemini 客戶端單元測試（backend/tests/unit/test_gemini_client.py）"
Task: "撰寫 OCR 服務單元測試（backend/tests/unit/test_ocr_service.py）"
Task: "撰寫圖片上傳 API 整合測試（backend/tests/integration/test_api_endpoints.py）"
Task: "撰寫 FileUpload 組件測試（frontend/tests/components/FileUpload.spec.ts）"
Task: "撰寫 EditableForm 組件測試（frontend/tests/components/EditableForm.spec.ts）"
```

### 步驟 2：執行測試確認失敗
```bash
pytest backend/tests/  # 預期失敗（未實作）
npm run test           # 預期失敗（未實作）
```

### 步驟 3：平行實作後端基礎（2 個任務）
```bash
Task: "實作檔案驗證工具（backend/src/utils/validators.py）"
Task: "定義 Pydantic 模型（backend/src/models/schemas.py）"
```

### 步驟 4：依序實作後端服務
```bash
Task: "實作 Gemini API 客戶端（backend/src/services/gemini_client.py）"
Task: "實作檔案處理服務（backend/src/services/file_service.py）"
Task: "實作 OCR 服務（backend/src/services/ocr_service.py）"
Task: "實作圖片上傳 API 路由（backend/src/api/routes.py）"
```

### 步驟 5：平行實作前端（5 個任務同時）
```bash
Task: "實作檔案上傳 composable（frontend/composables/useFileUpload.ts）"
Task: "實作 API 呼叫 composable（frontend/composables/useOcrApi.ts）"
Task: "建立 FileUpload 組件（frontend/components/FileUpload.vue）"
Task: "建立 ExtractionResult 組件（frontend/components/ExtractionResult.vue）"
Task: "建立 EditableForm 組件（frontend/components/EditableForm.vue）"
```

### 步驟 6：整合與驗證
```bash
Task: "整合主頁面（frontend/pages/index.vue）"
Task: "執行所有 US1 測試並確認通過"
Task: "使用測試圖片驗證完整流程"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**最快價值交付路徑**：

1. 完成 Phase 1: Setup（T001-T008） → 30 分鐘
2. 完成 Phase 2: Foundational（T009-T019） → 1 小時
3. 完成 Phase 3: User Story 1（T020-T042） → 4-6 小時
4. **STOP and VALIDATE**: 測試 US1 獨立運作
5. 部署/展示 MVP（僅圖片上傳 OCR 功能）

**預估總時間**：6-8 小時可交付可運作的 MVP

### Incremental Delivery

**建議執行順序**：

1. **Day 1**: Setup + Foundational + US1
   - 產出：可上傳圖片並擷取身分證資訊的 MVP
   - 驗證：上傳測試圖片，確認 6 個欄位正確顯示

2. **Day 2**: US2 (PDF 支援)
   - 產出：支援 PDF 格式的增量功能
   - 驗證：上傳 PDF，確認功能與圖片相同

3. **Day 3**: US3 (批次處理)
   - 產出：支援多檔案上傳的增量功能
   - 驗證：一次上傳 5 張圖片，確認所有結果正確

4. **Day 4**: Polish & 測試
   - 產出：完整品質保證的系統
   - 驗證：所有測試通過、quickstart 可執行

### Parallel Team Strategy

**如有 3 位開發者**：

1. **Developer A**: 後端開發
   - Phase 2: 後端基礎（T009-T015）
   - Phase 3: US1 後端（T026-T032）
   - Phase 4: US2 後端（T045-T049）

2. **Developer B**: 前端開發
   - Phase 2: 前端基礎（T016-T019）
   - Phase 3: US1 前端（T033-T039）
   - Phase 4: US2 前端（T050-T051）

3. **Developer C**: 測試與品質
   - Phase 3: US1 測試（T020-T025）
   - Phase 4: US2 測試（T043-T044）
   - Phase 6: Polish（T069-T080）

**優勢**：所有 User Stories 可平行開發，3-4 天內完成全部功能

---

## Notes

- **[P] 任務**：不同檔案、無相依性，可同時執行
- **[Story] 標籤**：清楚標示任務所屬的 User Story，便於追蹤
- **測試先行（TDD）**：所有測試必須先寫且確認失敗才能實作功能（憲章要求）
- **獨立測試**：每個 User Story 的 Checkpoint 都包含獨立驗證標準
- **MVP 優先**：完成 US1 即可交付價值，US2 和 US3 為增量功能
- **檔案路徑明確**：每個任務都包含確切的檔案路徑，可直接執行
- **平行機會**：Setup 階段 5 個任務、Foundational 階段 6 個任務、US1 前端 5 個任務可平行
- **避免**：模糊任務描述、相同檔案衝突、跨 Story 相依性導致無法獨立測試

---

## Summary

- **總任務數**：80 個任務
- **User Story 任務分佈**：
  - US1 (P1 - MVP)：23 個任務（T020-T042）
  - US2 (P2)：12 個任務（T043-T054）
  - US3 (P3)：14 個任務（T055-T068）
- **平行機會**：
  - Setup: 5 個任務可平行
  - Foundational: 6 個任務可平行
  - US1 測試: 6 個任務可平行
  - US1 前端: 5 個任務可平行
  - Polish: 7 個任務可平行
- **建議 MVP 範圍**：Phase 1 + Phase 2 + Phase 3 (US1)，約 6-8 小時可完成
- **格式驗證**：✅ 所有任務遵循 `- [ ] [ID] [P?] [Story?] Description with path` 格式
