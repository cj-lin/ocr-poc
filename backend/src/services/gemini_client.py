"""Gemini API client for ID card OCR"""

import json
import os
from typing import Any

import google.generativeai as genai
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class GeminiClient:
    """Client for Gemini API"""

    def __init__(self):
        """Initialize Gemini client"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def _build_prompt(self) -> str:
        """Build prompt for Gemini API

        Returns:
            Prompt string
        """
        return """
請辨識這張台灣身分證正面的資訊,並以 JSON 格式輸出以下欄位:
- 姓名 (name)
- 身分證字號 (id_number)
- 出生日期 (birth_date, 格式:民國 YYY/MM/DD)
- 性別 (gender, 值:男 或 女)
- 發證日期 (issue_date, 格式:民國 YYY/MM/DD)
- 發證地點 (issue_location)

如果某個欄位無法辨識,請設為 null。

請只回傳 JSON 格式的資料,不要包含任何其他說明文字。
"""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def extract_id_card_info(self, image: Image.Image) -> dict[str, Any]:
        """Extract ID card information from image using Gemini API

        Args:
            image: PIL Image object

        Returns:
            Dictionary containing extracted information

        Raises:
            ValueError: If response cannot be parsed
            Exception: If Gemini API call fails
        """
        prompt = self._build_prompt()

        logger.info("Calling Gemini API for ID card extraction")

        try:
            response = await self.model.generate_content_async([prompt, image])

            # Parse JSON response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            try:
                data = json.loads(response_text)
                logger.info("Successfully extracted ID card information")
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini API response: {e}")
                raise ValueError(f"無法解析 Gemini API 回應: {response_text}")

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}", exc_info=True)
            raise
