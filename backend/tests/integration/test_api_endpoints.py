"""Integration tests for API endpoints"""

import io
from unittest.mock import AsyncMock, patch

import fitz  # PyMuPDF
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
    mock_id_card_data = {
        "name": "王小明",
        "id_number": "A123456789",
        "birth_date": "80/05/20",
        "gender": "男",
        "issue_date": "95/12/01",
        "issue_location": "台北市",
        "confidence_score": 0.95,
    }

    # Create test image file
    img_bytes = create_test_image()

    # Patch GeminiClient where it's imported in ocr_service module
    with patch("src.services.ocr_service.GeminiClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.extract_id_card_info = AsyncMock(return_value=mock_id_card_data)
        mock_client.return_value = mock_instance
        
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

    # Return invalid data that will fail Pydantic validation
    invalid_data = {
        "name": "王",  # Too short
        "id_number": "123",  # Invalid format
        "birth_date": "2000/05/20",  # Wrong format
        "gender": "M",  # Wrong value
        "issue_date": "95/12/01",
        "issue_location": "台北市",
    }

    with patch("src.services.ocr_service.GeminiClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.extract_id_card_info = AsyncMock(return_value=invalid_data)
        mock_client.return_value = mock_instance
        
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


# ==================== PDF Upload Tests (User Story 2) ====================


def create_test_pdf() -> bytes:
    """Create a test PDF with simulated ID card content"""
    pdf_bytes = io.BytesIO()
    doc = fitz.open()
    page = doc.new_page(width=856, height=540)  # ID card dimensions
    
    # Add some text content
    page.insert_text((100, 100), "姓名: 李小華", fontsize=16)
    page.insert_text((100, 150), "身分證字號: B234567890", fontsize=14)
    page.insert_text((100, 200), "出生日期: 75/03/15", fontsize=14)
    
    doc.save(pdf_bytes)
    doc.close()
    pdf_bytes.seek(0)
    return pdf_bytes.getvalue()


def test_extract_endpoint_pdf_success():
    """Test successful ID card extraction from PDF"""
    mock_id_card_data = {
        "name": "李小華",
        "id_number": "B234567890",
        "birth_date": "75/03/15",
        "gender": "女",
        "issue_date": "85/11/10",
        "issue_location": "台中市",
        "confidence_score": 0.89,
    }

    pdf_bytes = create_test_pdf()

    with patch("src.services.ocr_service.GeminiClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.extract_id_card_info = AsyncMock(return_value=mock_id_card_data)
        mock_client.return_value = mock_instance
        
        response = client.post(
            "/api/extract",
            files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
        )

    assert response.status_code == 200

    data = response.json()
    assert "request_id" in data
    assert data["status"] == "success"
    assert data["data"]["name"] == "李小華"
    assert data["data"]["id_number"] == "B234567890"


def test_extract_endpoint_empty_pdf():
    """Test handling of PDF with no pages or corrupted structure"""
    # Use minimal invalid PDF structure (PyMuPDF won't save empty PDFs)
    empty_pdf = b"%PDF-1.4\n%%EOF"

    response = client.post(
        "/api/extract",
        files={"file": ("empty.pdf", empty_pdf, "application/pdf")},
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error_code"] == "NO_IMAGE_IN_PDF"
    assert "PDF" in data["message"]


def test_extract_endpoint_invalid_pdf():
    """Test handling of corrupted PDF file"""
    invalid_pdf = b"This is not a valid PDF"

    response = client.post(
        "/api/extract",
        files={"file": ("invalid.pdf", invalid_pdf, "application/pdf")},
    )

    assert response.status_code == 400

    data = response.json()
    # Could be NO_IMAGE_IN_PDF or INVALID_FORMAT depending on error
    assert data["error_code"] in ["NO_IMAGE_IN_PDF", "INVALID_FORMAT"]


def test_extract_endpoint_pdf_too_large():
    """Test PDF file size validation"""
    # Create a large PDF (> 10MB)
    large_pdf = b"x" * (11 * 1024 * 1024)

    response = client.post(
        "/api/extract",
        files={"file": ("large.pdf", large_pdf, "application/pdf")},
    )

    assert response.status_code == 413

    data = response.json()
    assert data["error_code"] == "FILE_TOO_LARGE"


# ==================== Batch Upload Tests (User Story 3) ====================


def test_extract_batch_endpoint_success():
    """Test successful batch extraction of multiple files"""
    mock_results = [
        {
            "name": "王小明",
            "id_number": "A123456789",
            "birth_date": "80/05/20",
            "gender": "男",
            "issue_date": "95/12/01",
            "issue_location": "台北市",
            "confidence_score": 0.95,
        },
        {
            "name": "李小華",
            "id_number": "B234567890",
            "birth_date": "75/03/15",
            "gender": "女",
            "issue_date": "85/11/10",
            "issue_location": "台中市",
            "confidence_score": 0.89,
        },
    ]

    # Create test files
    img1 = create_test_image()
    img2 = create_test_image()

    with patch("src.services.ocr_service.GeminiClient") as mock_client:
        mock_instance = AsyncMock()
        # Return different results for each call
        mock_instance.extract_id_card_info = AsyncMock(side_effect=mock_results)
        mock_client.return_value = mock_instance

        response = client.post(
            "/api/extract/batch",
            files=[
                ("files", ("id1.jpg", img1, "image/jpeg")),
                ("files", ("id2.jpg", img2, "image/jpeg")),
            ],
        )

    assert response.status_code == 200

    data = response.json()
    assert "request_id" in data
    assert "results" in data
    assert len(data["results"]) == 2
    assert data["total_files"] == 2
    assert data["successful_files"] == 2
    assert data["failed_files"] == 0

    # Check first result
    assert data["results"][0]["status"] == "success"
    assert data["results"][0]["data"]["name"] == "王小明"

    # Check second result
    assert data["results"][1]["status"] == "success"
    assert data["results"][1]["data"]["name"] == "李小華"


def test_extract_batch_endpoint_partial_failure():
    """Test batch extraction with some files failing"""
    mock_result = {
        "name": "王小明",
        "id_number": "A123456789",
        "birth_date": "80/05/20",
        "gender": "男",
        "issue_date": "95/12/01",
        "issue_location": "台北市",
    }

    img1 = create_test_image()
    img2 = create_test_image()

    with patch("src.services.ocr_service.GeminiClient") as mock_client:
        mock_instance = AsyncMock()
        # First succeeds, second fails
        mock_instance.extract_id_card_info = AsyncMock(
            side_effect=[mock_result, Exception("OCR failed")]
        )
        mock_client.return_value = mock_instance

        response = client.post(
            "/api/extract/batch",
            files=[
                ("files", ("id1.jpg", img1, "image/jpeg")),
                ("files", ("id2.jpg", img2, "image/jpeg")),
            ],
        )

    assert response.status_code == 200

    data = response.json()
    assert data["total_files"] == 2
    assert data["successful_files"] == 1
    assert data["failed_files"] == 1

    # Check successful result
    assert data["results"][0]["status"] == "success"

    # Check failed result
    assert data["results"][1]["status"] == "error"
    assert "error" in data["results"][1]


def test_extract_batch_endpoint_no_files():
    """Test batch endpoint with no files"""
    response = client.post("/api/extract/batch")

    assert response.status_code == 422  # Validation error


def test_extract_batch_endpoint_too_many_files():
    """Test batch endpoint with too many files"""
    # Create more than max allowed (assume max is 10)
    files = [
        ("files", (f"id{i}.jpg", create_test_image(), "image/jpeg"))
        for i in range(15)
    ]

    response = client.post("/api/extract/batch", files=files)

    assert response.status_code == 400
    data = response.json()
    assert "error_code" in data


def test_extract_batch_endpoint_mixed_formats():
    """Test batch upload with mixed valid formats (JPG, PNG, PDF)"""
    mock_result = {
        "name": "測試用戶",
        "id_number": "C123456789",
        "birth_date": "85/01/01",
        "gender": "男",
        "issue_date": "100/01/01",
        "issue_location": "高雄市",
    }

    img = create_test_image()
    pdf = create_test_pdf()

    with patch("src.services.ocr_service.GeminiClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.extract_id_card_info = AsyncMock(return_value=mock_result)
        mock_client.return_value = mock_instance

        response = client.post(
            "/api/extract/batch",
            files=[
                ("files", ("id1.jpg", img, "image/jpeg")),
                ("files", ("id2.pdf", pdf, "application/pdf")),
            ],
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total_files"] == 2
    assert data["successful_files"] == 2
