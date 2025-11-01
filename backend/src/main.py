"""FastAPI application entry point"""

import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .models.schemas import ErrorResponse
from .utils.constants import ERROR_MESSAGES
from .utils.logging_config import get_logger, request_id_var, setup_logging

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting ID Card OCR Backend")
    yield
    # Shutdown
    logger.info("Shutting down ID Card OCR Backend")


# Create FastAPI app
app = FastAPI(
    title="身分證資訊擷取 API",
    description="使用 Gemini AI 從身分證圖片或 PDF 中自動擷取結構化資訊",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to context and response headers"""
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)

    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={"request_id": req_id, "method": request.method, "path": request.url.path},
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id

    logger.info(
        f"Request completed: {response.status_code}",
        extra={"request_id": req_id, "status_code": response.status_code},
    )

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    request_id = request_id_var.get("")
    logger.warning(f"Validation error: {exc}", extra={"request_id": request_id})

    error_response = ErrorResponse(
        request_id=request_id,
        error_code="VALIDATION_ERROR",
        message=ERROR_MESSAGES["VALIDATION_ERROR"],
        details=str(exc) if os.getenv("DEBUG") else None,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    request_id = request_id_var.get("")
    logger.warning(f"Pydantic validation error: {exc}", extra={"request_id": request_id})

    error_response = ErrorResponse(
        request_id=request_id,
        error_code="VALIDATION_ERROR",
        message=ERROR_MESSAGES["VALIDATION_ERROR"],
        details=str(exc) if os.getenv("DEBUG") else None,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    request_id = request_id_var.get("")
    logger.error(
        f"Unhandled exception: {exc}",
        extra={"request_id": request_id},
        exc_info=True,
    )

    error_response = ErrorResponse(
        request_id=request_id,
        error_code="OCR_FAILED",
        message=ERROR_MESSAGES["OCR_FAILED"],
        details=str(exc) if os.getenv("DEBUG") else None,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


# Import routes
from .api.routes import router

app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "身分證資訊擷取 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
