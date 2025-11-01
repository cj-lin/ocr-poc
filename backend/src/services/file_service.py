"""File handling service"""

import io

import fitz  # PyMuPDF
from PIL import Image

from ..utils.logging_config import get_logger
from ..utils.validators import validate_file_extension, validate_file_size, validate_mime_type

logger = get_logger(__name__)


class FileService:
    """Service for file handling and validation"""

    @staticmethod
    def validate_upload(file_content: bytes, filename: str, content_type: str) -> None:
        """Validate uploaded file

        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type

        Raises:
            ValueError: If validation fails
        """
        # Validate file size
        validate_file_size(len(file_content))

        # Validate MIME type
        validate_mime_type(content_type)

        # Validate file extension
        validate_file_extension(filename)

        logger.info(
            f"File validation passed: {filename} ({len(file_content)} bytes, {content_type})"
        )

    @staticmethod
    def bytes_to_image(file_content: bytes) -> Image.Image:
        """Convert bytes to PIL Image

        Args:
            file_content: Image file content as bytes

        Returns:
            PIL Image object

        Raises:
            ValueError: If image cannot be loaded
        """
        try:
            img = Image.open(io.BytesIO(file_content))
            logger.info(f"Loaded image: {img.size} {img.mode}")
            return img
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            raise ValueError(f"無法載入圖片: {e}")

    @staticmethod
    def pdf_to_image(pdf_content: bytes) -> Image.Image:
        """Convert first page of PDF to image

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            PIL Image object of first page

        Raises:
            ValueError: If PDF has no pages or cannot extract image
        """
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")

            if len(doc) == 0:
                raise ValueError("PDF 無有效頁面")

            # Get first page
            page = doc[0]

            # Render page to pixmap (high DPI for better OCR)
            pix = page.get_pixmap(dpi=300)

            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            doc.close()

            logger.info(f"Converted PDF to image: {img.size}")
            return img

        except Exception as e:
            logger.error(f"Failed to convert PDF to image: {e}")
            raise ValueError(f"無法處理 PDF 檔案: {e}")

    @staticmethod
    async def process_upload(
        file_content: bytes, filename: str, content_type: str
    ) -> Image.Image:
        """Process uploaded file and return image

        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type

        Returns:
            PIL Image object ready for OCR

        Raises:
            ValueError: If file processing fails
        """
        # Validate file
        FileService.validate_upload(file_content, filename, content_type)

        # Convert to image based on type
        if content_type == "application/pdf":
            return FileService.pdf_to_image(file_content)
        else:
            return FileService.bytes_to_image(file_content)
