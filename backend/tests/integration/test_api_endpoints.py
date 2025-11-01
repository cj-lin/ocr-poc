"""Integration tests for API endpoints"""

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.main import app
from src.models.schemas import IdCardInfo

client = TestClient(app)


def create_test_image() -> bytes:
    """Create a test image in memory"""
    img = Image.new("RGB", (856, 540), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes.getvalue()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "gemini_api" in data
    assert "timestamp" in data


def test_extract_endpoint_success():
    """Test successful ID card extraction"""
    mock_id_card = IdCardInfo(
        name="王小明",
        id_number="A123456789",
        birth_date="80/05/20",
        gender="男",
        issue_date="95/12/01",
        issue_location="台北市",
        confidence_score=0.95,
    )

    # Create test image file
    img_bytes = create_test_image()

    with patch("src.services.ocr_service.OcrService.process_image", return_value=mock_id_card):
        response = client.post(
            "/api/extract",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        )

    assert response.status_code == 200

    data = response.json()
    assert "request_id" in data
    assert "status" in data
    assert "data" in data
    assert "processing_time" in data
    assert data["data"]["name"] == "王小明"
    assert data["data"]["id_number"] == "A123456789"


def test_extract_endpoint_file_too_large():
    """Test file size validation"""
    # Create a file that's too large (> 10MB)
    large_file = b"x" * (11 * 1024 * 1024)

    response = client.post(
        "/api/extract",
        files={"file": ("large.jpg", large_file, "image/jpeg")},
    )

    assert response.status_code == 413

    data = response.json()
    assert data["error_code"] == "FILE_TOO_LARGE"
    assert "10MB" in data["message"]


def test_extract_endpoint_invalid_format():
    """Test invalid file format"""
    txt_content = b"This is not an image"

    response = client.post(
        "/api/extract",
        files={"file": ("document.txt", txt_content, "text/plain")},
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error_code"] == "INVALID_FORMAT"


def test_extract_endpoint_no_file():
    """Test missing file in request"""
    response = client.post("/api/extract")

    assert response.status_code == 422  # Validation error


def test_extract_endpoint_validation_error():
    """Test handling of validation errors from Gemini response"""
    img_bytes = create_test_image()

    with patch(
        "src.services.ocr_service.OcrService.process_image",
        side_effect=ValueError("身分證字號格式錯誤"),
    ):
        response = client.post(
            "/api/extract",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        )

    assert response.status_code == 422

    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"


def test_extract_endpoint_ocr_failed():
    """Test OCR service failure"""
    img_bytes = create_test_image()

    with patch(
        "src.services.ocr_service.OcrService.process_image",
        side_effect=Exception("Gemini API Error"),
    ):
        response = client.post(
            "/api/extract",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        )

    assert response.status_code == 500

    data = response.json()
    assert data["error_code"] == "OCR_FAILED"


def test_request_id_in_response():
    """Test that all responses include X-Request-ID header"""
    response = client.get("/api/health")

    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) == 36  # UUID length
