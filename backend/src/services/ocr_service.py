"""OCR service for ID card extraction"""

from PIL import Image

from ..models.schemas import IdCardInfo
from ..utils.logging_config import get_logger
from .gemini_client import GeminiClient

logger = get_logger(__name__)


class OcrService:
    """Service for OCR processing"""

    def __init__(self):
        """Initialize OCR service"""
        self.gemini_client = GeminiClient()

    async def process_image(self, image: Image.Image) -> IdCardInfo:
        """Process image and extract ID card information

        Args:
            image: PIL Image object

        Returns:
            IdCardInfo object with extracted data

        Raises:
            ValueError: If extraction or validation fails
        """
        logger.info("Processing image for ID card extraction")

        # Call Gemini API
        raw_data = await self.gemini_client.extract_id_card_info(image)

        logger.info(f"Received data from Gemini: {raw_data}")

        # Validate and parse data using Pydantic
        try:
            id_card_info = IdCardInfo(**raw_data)
            logger.info("Successfully validated ID card information")
            return id_card_info
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            raise ValueError(f"擷取的資料驗證失敗: {e}")
