"""API routes"""

import os
import time
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from ..models.schemas import (
    BatchExtractionResult,
    BatchFileResult,
    ErrorResponse,
    ExtractionResult,
    HealthCheckResponse,
)
from ..services.file_service import FileService
from ..services.ocr_service import OcrService
from ..utils.constants import ERROR_MESSAGES
from ..utils.logging_config import get_logger, request_id_var

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康檢查端點

    Returns:
        HealthCheckResponse: 服務狀態
    """
    # Check if Gemini API key is configured
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_status = "connected" if gemini_api_key else "disconnected"

    # Determine overall health
    status = "healthy" if gemini_api_key else "degraded"

    return HealthCheckResponse(
        status=status,
        gemini_api=gemini_status,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.post("/extract", response_model=ExtractionResult)
async def extract_id_card(file: UploadFile = File(...)):
    """擷取身分證資訊

    Args:
        file: 上傳的檔案 (JPG, PNG, or PDF)

    Returns:
        ExtractionResult: 擷取結果

    Raises:
        HTTPException: 各種錯誤情況
    """
    request_id = request_id_var.get("")
    start_time = time.time()

    logger.info(
        f"Processing file upload: {file.filename}",
        extra={"uploaded_filename": file.filename, "content_type": file.content_type},
    )

    try:
        # Read file content
        file_content = await file.read()

        # Validate file size first
        if len(file_content) > 10 * 1024 * 1024:
            error_response = ErrorResponse(
                request_id=request_id,
                error_code="FILE_TOO_LARGE",
                message=ERROR_MESSAGES["FILE_TOO_LARGE"],
                details=None,
            )
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content=error_response.model_dump(),
            )

        # Validate and process file
        try:
            image = await FileService.process_upload(
                file_content, file.filename or "unknown", file.content_type or ""
            )
        except ValueError as e:
            error_msg = str(e)
            error_code = "INVALID_FORMAT"

            # Check for PDF-specific errors (not just any message containing "PDF")
            if "無法處理 PDF" in error_msg or "PDF 無有效頁面" in error_msg:
                error_code = "NO_IMAGE_IN_PDF"

            error_response = ErrorResponse(
                request_id=request_id,
                error_code=error_code,
                message=ERROR_MESSAGES.get(error_code, str(e)),
                details=error_msg if os.getenv("DEBUG") else None,
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_response.model_dump(),
            )

        # Process OCR
        ocr_service = OcrService()
        try:
            id_card_info = await ocr_service.process_image(image)
        except ValueError as e:
            logger.error(f"OCR validation error: {e}")
            error_response = ErrorResponse(
                request_id=request_id,
                error_code="VALIDATION_ERROR",
                message=ERROR_MESSAGES["VALIDATION_ERROR"],
                details=str(e) if os.getenv("DEBUG") else None,
            )
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=error_response.model_dump(),
            )

        processing_time = time.time() - start_time

        logger.info(
            f"Successfully extracted ID card info in {processing_time:.2f}s",
            extra={
                "processing_time": processing_time,
                "confidence": id_card_info.confidence_score,
            },
        )

        # Determine status based on confidence or null fields
        extraction_status = "success"
        warnings = []

        if id_card_info.confidence_score and id_card_info.confidence_score < 0.8:
            extraction_status = "partial"
            warnings.append("部分欄位辨識信心度較低,請仔細檢查")

        return ExtractionResult(
            request_id=request_id,
            status=extraction_status,
            data=id_card_info,
            processing_time=processing_time,
            warnings=warnings if warnings else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}", exc_info=True)
        error_response = ErrorResponse(
            request_id=request_id,
            error_code="OCR_FAILED",
            message=ERROR_MESSAGES["OCR_FAILED"],
            details=str(e) if os.getenv("DEBUG") else None,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )


@router.post("/extract/batch", response_model=BatchExtractionResult)
async def extract_id_cards_batch(files: list[UploadFile] = File(...)):
    """
    批次擷取多個身分證資訊 (User Story 3)
    
    支援同時上傳多個檔案，每個檔案獨立處理
    """
    request_id = request_id_var.get()
    start_time = time.time()

    logger.info(f"Processing batch upload: {len(files)} files")

    # 驗證檔案數量
    MAX_BATCH_SIZE = 10
    if len(files) > MAX_BATCH_SIZE:
        error_response = ErrorResponse(
            request_id=request_id,
            error_code="INVALID_FORMAT",
            message=f"批次上傳最多支援 {MAX_BATCH_SIZE} 個檔案",
            details=None,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump(),
        )

    results: list[BatchFileResult] = []
    successful_count = 0
    failed_count = 0

    # 處理每個檔案
    for file in files:
        file_start_time = time.time()
        filename = file.filename or "unknown"

        try:
            logger.info(f"Processing file: {filename}")

            # 讀取檔案內容
            file_content = await file.read()

            # 處理檔案
            image = await FileService.process_upload(
                file_content, filename, file.content_type or ""
            )

            # OCR 處理
            ocr_service = OcrService()
            id_card_info = await ocr_service.process_image(image)

            file_processing_time = time.time() - file_start_time

            # 成功結果
            results.append(
                BatchFileResult(
                    filename=filename,
                    status="success",
                    data=id_card_info,
                    error=None,
                    processing_time=file_processing_time,
                )
            )
            successful_count += 1

            logger.info(
                f"Successfully processed {filename} in {file_processing_time:.2f}s"
            )

        except ValueError as e:
            # 驗證錯誤或檔案處理錯誤
            file_processing_time = time.time() - file_start_time
            error_msg = str(e)

            results.append(
                BatchFileResult(
                    filename=filename,
                    status="error",
                    data=None,
                    error=error_msg,
                    processing_time=file_processing_time,
                )
            )
            failed_count += 1

            logger.warning(f"Failed to process {filename}: {error_msg}")

        except Exception as e:
            # 未預期的錯誤
            file_processing_time = time.time() - file_start_time
            error_msg = "處理檔案時發生錯誤"

            results.append(
                BatchFileResult(
                    filename=filename,
                    status="error",
                    data=None,
                    error=error_msg,
                    processing_time=file_processing_time,
                )
            )
            failed_count += 1

            logger.error(f"Unexpected error processing {filename}: {e}", exc_info=True)

    total_processing_time = time.time() - start_time

    logger.info(
        f"Batch processing complete: {successful_count} success, {failed_count} failed, "
        f"total time: {total_processing_time:.2f}s"
    )

    return BatchExtractionResult(
        request_id=request_id,
        total_files=len(files),
        successful_files=successful_count,
        failed_files=failed_count,
        results=results,
        processing_time=total_processing_time,
    )
