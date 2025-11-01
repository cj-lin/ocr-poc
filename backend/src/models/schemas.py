"""Pydantic schemas for request/response models"""

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from ..utils.constants import VALID_LOCATIONS


class IdCardInfo(BaseModel):
    """身分證資訊實體"""

    name: str = Field(..., min_length=2, max_length=10, description="姓名")
    id_number: str = Field(..., description="身分證字號(1 個英文字母 + 9 個數字)")
    birth_date: str = Field(..., description="出生日期(民國年格式 YYY/MM/DD)")
    gender: Literal["男", "女"] = Field(..., description="性別")
    issue_date: str = Field(..., description="發證日期(民國年格式 YYY/MM/DD)")
    issue_location: str = Field(..., description="發證地點(台灣縣市)")
    confidence_score: float | None = Field(
        None, ge=0.0, le=1.0, description="辨識信心分數(由 Gemini API 提供)"
    )

    @field_validator("id_number")
    @classmethod
    def validate_id_number(cls, v: str) -> str:
        """驗證身分證字號格式"""
        if not re.match(r"^[A-Z][12]\d{8}$", v):
            raise ValueError("身分證字號格式錯誤(應為 1 個英文字母 + 9 個數字)")
        return v

    @field_validator("birth_date", "issue_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """驗證民國日期格式"""
        if not re.match(r"^\d{1,3}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])$", v):
            raise ValueError("日期格式錯誤(應為 YYY/MM/DD 民國年格式)")
        return v

    @field_validator("issue_location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        """驗證發證地點"""
        if v not in VALID_LOCATIONS:
            raise ValueError(f"無效的發證地點:{v}")
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
                "confidence_score": 0.95,
            }
        }


class ExtractionResult(BaseModel):
    """API 回應:擷取結果"""

    request_id: str = Field(..., description="請求追蹤 ID")
    status: Literal["success", "partial"] = Field(..., description="處理狀態")
    data: IdCardInfo = Field(..., description="擷取的身分證資訊")
    processing_time: float = Field(..., ge=0, description="處理耗時(秒)")
    warnings: list[str] | None = Field(None, description="警告訊息")

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
                    "issue_location": "台北市",
                    "confidence_score": 0.95,
                },
                "processing_time": 3.25,
                "warnings": None,
            }
        }


class ErrorResponse(BaseModel):
    """API 錯誤回應"""

    request_id: str = Field(..., description="請求追蹤 ID")
    error_code: Literal[
        "FILE_TOO_LARGE",
        "INVALID_FORMAT",
        "NO_IMAGE_IN_PDF",
        "OCR_FAILED",
        "RATE_LIMITED",
        "VALIDATION_ERROR",
    ] = Field(..., description="錯誤代碼")
    message: str = Field(..., description="使用者友善的錯誤訊息")
    details: str | None = Field(None, description="技術細節(僅開發模式)")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "750e8400-e29b-41d4-a716-446655440002",
                "error_code": "INVALID_FORMAT",
                "message": "不支援的檔案格式,請上傳 JPG、PNG 或 PDF",
                "details": None,
            }
        }


class HealthCheckResponse(BaseModel):
    """健康檢查回應"""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(..., description="服務狀態")
    gemini_api: Literal["connected", "disconnected"] = Field(..., description="Gemini API 連線狀態")
    timestamp: str = Field(..., description="檢查時間戳記")


class BatchFileResult(BaseModel):
    """單一檔案的批次處理結果"""

    filename: str = Field(..., description="檔案名稱")
    status: Literal["success", "error"] = Field(..., description="處理狀態")
    data: IdCardInfo | None = Field(None, description="擷取的資料（成功時）")
    error: str | None = Field(None, description="錯誤訊息（失敗時）")
    processing_time: float = Field(..., ge=0, description="處理時間（秒）")


class BatchExtractionResult(BaseModel):
    """批次擷取回應"""

    request_id: str = Field(..., description="請求追蹤 ID")
    total_files: int = Field(..., ge=1, description="總檔案數")
    successful_files: int = Field(..., ge=0, description="成功處理的檔案數")
    failed_files: int = Field(..., ge=0, description="失敗的檔案數")
    results: list[BatchFileResult] = Field(..., description="各檔案的處理結果")
    processing_time: float = Field(..., ge=0, description="總處理時間（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_files": 3,
                "successful_files": 2,
                "failed_files": 1,
                "results": [
                    {
                        "filename": "id1.jpg",
                        "status": "success",
                        "data": {
                            "name": "王小明",
                            "id_number": "A123456789",
                            "birth_date": "80/05/20",
                            "gender": "男",
                            "issue_date": "95/12/01",
                            "issue_location": "台北市",
                        },
                        "processing_time": 3.2,
                    },
                    {
                        "filename": "id2.jpg",
                        "status": "error",
                        "data": None,
                        "error": "無法辨識圖片內容",
                        "processing_time": 1.5,
                    },
                ],
                "processing_time": 4.7,
            }
        }
