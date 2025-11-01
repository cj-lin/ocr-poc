"""Test OCR service"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from src.models.schemas import IdCardInfo
from src.services.ocr_service import OcrService


@pytest.fixture
def mock_image():
    """Create a mock PIL Image"""
    return Image.new("RGB", (100, 100), color="white")


@pytest.fixture
def ocr_service():
    """Create OcrService instance"""
    return OcrService()


@pytest.mark.asyncio
async def test_process_image_success(ocr_service, mock_image):
    """Test successful image processing"""
    mock_data = {
        "name": "王小明",
        "id_number": "A123456789",
        "birth_date": "80/05/20",
        "gender": "男",
        "issue_date": "95/12/01",
        "issue_location": "台北市",
        "confidence_score": 0.95,
    }

    with patch.object(
        ocr_service.gemini_client,
        "extract_id_card_info",
        return_value=mock_data,
    ):
        result = await ocr_service.process_image(mock_image)

        assert isinstance(result, IdCardInfo)
        assert result.name == "王小明"
        assert result.id_number == "A123456789"
        assert result.confidence_score == 0.95


@pytest.mark.asyncio
async def test_process_image_validation_error(ocr_service, mock_image):
    """Test handling of invalid data from Gemini"""
    mock_data = {
        "name": "王",  # Too short
        "id_number": "123",  # Invalid format
        "birth_date": "2000/05/20",  # Wrong format
        "gender": "M",  # Wrong value
        "issue_date": "95/12/01",
        "issue_location": "台北市",
    }

    with patch.object(
        ocr_service.gemini_client,
        "extract_id_card_info",
        return_value=mock_data,
    ):
        with pytest.raises(ValueError):
            await ocr_service.process_image(mock_image)


@pytest.mark.asyncio
async def test_process_image_missing_fields(ocr_service, mock_image):
    """Test handling of missing required fields"""
    mock_data = {
        "name": "王小明",
        "id_number": "A123456789",
        # Missing other required fields
    }

    with patch.object(
        ocr_service.gemini_client,
        "extract_id_card_info",
        return_value=mock_data,
    ):
        with pytest.raises(ValueError):
            await ocr_service.process_image(mock_image)


@pytest.mark.asyncio
async def test_process_image_partial_success(ocr_service, mock_image):
    """Test partial extraction with null fields"""
    mock_data = {
        "name": "李小華",
        "id_number": "B234567890",
        "birth_date": "75/03/15",
        "gender": "女",
        "issue_date": "85/11/10",
        "issue_location": "台中市",
        "confidence_score": 0.67,
    }

    with patch.object(
        ocr_service.gemini_client,
        "extract_id_card_info",
        return_value=mock_data,
    ):
        result = await ocr_service.process_image(mock_image)

        assert isinstance(result, IdCardInfo)
        assert result.name == "李小華"
        assert result.confidence_score == 0.67
