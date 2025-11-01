# OCR POC Development Guidelines

AI-generated guidance for the Taiwan ID Card OCR extraction system. Last updated: 2025-11-01

## System Architecture

**What**: Full-stack OCR system that extracts structured data from Taiwan national ID cards using Gemini AI.

**Frontend → Backend Flow**:
1. Nuxt 4 frontend (`/frontend`) uploads file via composable `useOcrApi.ts`
2. FastAPI backend (`/backend/src`) receives file at `/api/extract` endpoint
3. `FileService` validates & converts (PDF → image via PyMuPDF at 300 DPI)
4. `OcrService` → `GeminiClient` processes with structured prompt
5. `IdCardInfo` Pydantic model validates response (regex for ID format, Taiwan ROC dates, location list)
6. Returns `ExtractionResult` with request_id, processing_time, confidence_score

**Privacy**: Files never persist to disk—everything in-memory only (`io.BytesIO`). See `file_service.py:bytes_to_image()`.

**Error Handling**: Request IDs tracked via context vars (`request_id_var`). All errors return structured `ErrorResponse` with error codes like `INVALID_FORMAT`, `FILE_TOO_LARGE`. See `constants.py:ERROR_MESSAGES`.

## Key Technologies

**Backend**: Python 3.11+, FastAPI 0.115+, Pydantic 2.9 (validation), Gemini 1.5 Flash API, Pillow + PyMuPDF, Tenacity (retry logic)

**Frontend**: Nuxt 4, Vue 3, TypeScript 5.x, TailwindCSS, Vitest for testing

**Testing**: pytest + pytest-asyncio (backend), Vitest + happy-dom (frontend)

## Essential Commands

```bash
# Start full stack (requires .env with GEMINI_API_KEY)
docker-compose up --build

# Backend dev (from backend/)
pytest                                    # Run all tests
pytest tests/unit/test_ocr_service.py    # Specific test
ruff check src/                          # Lint
black --check src/                       # Format check

# Frontend dev (from frontend/)
npm run dev                              # Dev server
npm run test                             # Vitest tests
npm run lint                             # ESLint
```

## Project-Specific Patterns

### Date Format: Taiwan ROC Calendar
All dates use ROC (民國) format `YYY/MM/DD` (e.g., `80/05/20` = 1991-05-20). Validated by regex in `schemas.py:validate_date_format()`.

### ID Number Validation
Taiwan ID: 1 letter + 9 digits (2nd digit must be 1 or 2 for gender). Regex: `^[A-Z][12]\d{8}$`. See `schemas.py:validate_id_number()`.

### Location Validation
Only 22 valid Taiwan locations accepted (台北市, 新北市, etc.). Full list in `constants.py:VALID_LOCATIONS`.

### Gemini Prompt Engineering
Structured JSON extraction prompt in `gemini_client.py:_build_prompt()` instructs Gemini to:
- Return only JSON (no markdown/explanations)
- Set null for unrecognizable fields
- Use exact field names matching `IdCardInfo` schema

Response cleaned by stripping markdown code blocks before JSON parsing.

### Async Retry Pattern
Gemini API calls use `@retry` decorator with exponential backoff (3 attempts, 2-10s wait). See `gemini_client.py:extract_id_card_info()`.

### Request ID Middleware
Every request gets UUID injected via `request_id_var` context var and returned in `X-Request-ID` header. Used for log correlation.

## Code Conventions

- **Error messages**: Traditional Chinese (繁體中文) for user-facing strings
- **Logging**: Use `get_logger(__name__)` with structured extra fields: `{"request_id": ..., "filename": ...}`
- **Pydantic models**: Define examples in `Config.json_schema_extra` for OpenAPI docs
- **File validation**: Always chain: size → MIME type → extension (see `file_service.py:validate_upload()`)
- **Test fixtures**: Create via `create_test_image()` helper, mock Gemini responses in JSON

## Testing Patterns

**Backend**: Mock external calls (Gemini API via `@patch`), test validation edge cases (invalid dates, wrong gender codes). Integration tests use `TestClient` from FastAPI.

**Frontend**: Test composables with mocked `$fetch`, test components with `@vue/test-utils`. Use `happy-dom` for DOM simulation.

## Critical Files for Reference

- `backend/src/models/schemas.py` - All Pydantic models, validators, examples
- `backend/src/utils/constants.py` - Error codes, validation lists, limits
- `backend/src/services/gemini_client.py` - Prompt engineering, retry logic
- `frontend/composables/useOcrApi.ts` - API integration pattern
- `specs/001-id-card-extraction/spec.md` - Full feature requirements

## Environment Setup

Required env vars:
- `GEMINI_API_KEY` (required for backend)
- `LOG_LEVEL` (optional, default: INFO)
- `BACKEND_URL` (frontend, default: http://localhost:8000)

Copy `.env.example` to `.env` before running.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
