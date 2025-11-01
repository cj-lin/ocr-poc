"""Test Gemini API client"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from src.services.gemini_client import GeminiClient


@pytest.fixture
def mock_image():
    """Create a mock PIL Image"""
    img = Image.new("RGB", (100, 100), color="white")
    return img


@pytest.fixture
def gemini_client():
    """Create GeminiClient instance with mock API key"""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"}):
        return GeminiClient()


@pytest.mark.asyncio
async def test_extract_id_card_info_success(gemini_client, mock_image):
    """Test successful ID card extraction"""
    # Mock response from Gemini API
    mock_response = MagicMock()
    mock_response.text = """{
        "name": "王小明",
        "id_number": "A123456789",
        "birth_date": "80/05/20",
        "gender": "男",
        "issue_date": "95/12/01",
        "issue_location": "台北市"
    }"""

    with patch.object(
        gemini_client.model, "generate_content_async", return_value=mock_response
    ):
        result = await gemini_client.extract_id_card_info(mock_image)

        assert result["name"] == "王小明"
        assert result["id_number"] == "A123456789"
        assert result["gender"] == "男"


@pytest.mark.asyncio
async def test_extract_id_card_info_with_confidence(gemini_client, mock_image):
    """Test extraction with confidence score"""
    mock_response = MagicMock()
    mock_response.text = """{
        "name": "李小華",
        "id_number": "B234567890",
        "birth_date": "75/03/15",
        "gender": "女",
        "issue_date": "85/11/10",
        "issue_location": "台中市",
        "confidence_score": 0.92
    }"""

    with patch.object(
        gemini_client.model, "generate_content_async", return_value=mock_response
    ):
        result = await gemini_client.extract_id_card_info(mock_image)

        assert "confidence_score" in result
        assert result["confidence_score"] == 0.92


@pytest.mark.asyncio
async def test_extract_id_card_info_invalid_json(gemini_client, mock_image):
    """Test handling of invalid JSON response"""
    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON"

    with patch.object(
        gemini_client.model, "generate_content_async", return_value=mock_response
    ):
        with pytest.raises(ValueError, match="無法解析 Gemini API 回應"):
            await gemini_client.extract_id_card_info(mock_image)


@pytest.mark.asyncio
async def test_extract_id_card_info_api_error(gemini_client, mock_image):
    """Test handling of Gemini API errors"""
    with patch.object(
        gemini_client.model,
        "generate_content_async",
        side_effect=Exception("API Error"),
    ):
        with pytest.raises(Exception, match="API Error"):
            await gemini_client.extract_id_card_info(mock_image)


def test_build_prompt(gemini_client):
    """Test prompt building"""
    prompt = gemini_client._build_prompt()

    # Verify prompt contains required fields
    assert "姓名" in prompt
    assert "身分證字號" in prompt
    assert "出生日期" in prompt
    assert "性別" in prompt
    assert "發證日期" in prompt
    assert "發證地點" in prompt
    assert "JSON" in prompt
