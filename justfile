# OCR POC Justfile
# 使用 just 指令簡化開發與測試流程
# 安裝: https://github.com/casey/just

# 預設指令：顯示所有可用指令
default:
    @just --list

# === Docker 相關 ===

# 啟動所有服務（Docker Compose）
up:
    docker-compose up --build

# 停止所有服務
down:
    docker-compose down

# 停止並清除所有資料
down-clean:
    docker-compose down -v

# 查看服務日誌
logs service="":
    @if [ -z "{{service}}" ]; then \
        docker-compose logs -f; \
    else \
        docker-compose logs -f {{service}}; \
    fi

# === 後端測試 ===

# 執行所有後端測試
test-backend:
    cd backend && pytest

# 執行後端測試（帶覆蓋率報告）
test-backend-cov:
    cd backend && pytest --cov=src --cov-report=html --cov-report=term

# 執行特定後端測試檔案
test-backend-file file:
    cd backend && pytest {{file}}

# 執行後端單元測試
test-backend-unit:
    cd backend && pytest tests/unit/

# 執行後端整合測試
test-backend-integration:
    cd backend && pytest tests/integration/

# === 前端測試 ===

# 執行所有前端測試
test-frontend:
    cd frontend && npm run test

# 執行前端測試（帶覆蓋率報告）
test-frontend-cov:
    cd frontend && npm run test:coverage

# 執行前端測試（監看模式）
test-frontend-watch:
    cd frontend && npm run test -- --watch

# === 執行所有測試 ===

# 執行前後端所有測試
test-all: test-backend test-frontend

# 執行所有測試（帶覆蓋率）
test-all-cov: test-backend-cov test-frontend-cov

# === 程式碼品質 ===

# 檢查後端程式碼（ruff + black）
lint-backend:
    cd backend && ruff check src/ tests/
    cd backend && black --check src/ tests/

# 修正後端程式碼格式
lint-backend-fix:
    cd backend && ruff check src/ tests/ --fix
    cd backend && black src/ tests/

# 檢查前端程式碼
lint-frontend:
    cd frontend && npm run lint

# 修正前端程式碼格式
lint-frontend-fix:
    cd frontend && npm run lint:fix
    cd frontend && npm run format

# 檢查所有程式碼
lint-all: lint-backend lint-frontend

# 修正所有程式碼格式
lint-all-fix: lint-backend-fix lint-frontend-fix

# === 開發環境 ===

# 啟動後端開發伺服器（需要先設定 .env）
dev-backend:
    cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 啟動前端開發伺服器
dev-frontend:
    cd frontend && npm run dev

# 安裝後端依賴
install-backend:
    cd backend && pip install -r requirements.txt

# 安裝前端依賴
install-frontend:
    cd frontend && npm install

# 安裝所有依賴
install-all: install-backend install-frontend

# === 清理 ===

# 清理 Python 快取檔案
clean-backend:
    cd backend && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    cd backend && find . -type f -name "*.pyc" -delete
    cd backend && rm -rf .pytest_cache htmlcov .coverage

# 清理前端建置檔案
clean-frontend:
    cd frontend && rm -rf .nuxt .output node_modules/.cache

# 清理所有暫存檔案
clean-all: clean-backend clean-frontend

# === CI/CD 模擬 ===

# 執行 CI 檢查流程（linting + testing）
ci: lint-all test-all

# === 環境檢查 ===

# 檢查開發環境設定
check-env:
    @echo "=== 檢查 Python 版本 ==="
    @python --version
    @echo "\n=== 檢查 Node.js 版本 ==="
    @node --version
    @echo "\n=== 檢查 npm 版本 ==="
    @npm --version
    @echo "\n=== 檢查 Docker 版本 ==="
    @docker --version
    @echo "\n=== 檢查 Docker Compose 版本 ==="
    @docker-compose --version
    @echo "\n=== 檢查 .env 檔案 ==="
    @if [ -f .env ]; then echo "✅ .env 檔案存在"; else echo "❌ .env 檔案不存在，請執行: cp .env.example .env"; fi

# === 快速指令 ===

# 快速測試：後端單元測試（最常用）
t: test-backend-unit

# 快速測試：前端
tf: test-frontend

# 快速 lint 修正
fix: lint-all-fix
