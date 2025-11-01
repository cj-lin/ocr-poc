"""Test file service"""

import io

import fitz  # PyMuPDF
import pytest
from PIL import Image

from src.services.file_service import FileService


@pytest.fixture
def valid_image_bytes():
    """Create valid JPG image bytes"""
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()


@pytest.fixture
def valid_pdf_with_content():
    """Create a PDF with drawable content"""
    pdf_bytes = io.BytesIO()
    doc = fitz.open()  # Create new PDF
    page = doc.new_page(width=595, height=842)  # A4 size
    
    # Draw some content (simulating an ID card)
    page.insert_text((100, 100), "姓名: 王小明", fontsize=16)
    page.insert_text((100, 150), "身分證字號: A123456789", fontsize=14)
    
    # Save to bytes
    doc.save(pdf_bytes)
    doc.close()
    return pdf_bytes.getvalue()


@pytest.fixture
def empty_pdf():
    """Create PDF with one page but then remove it (simulates corrupted PDF)"""
    # PyMuPDF won't save a PDF with zero pages, so we test this differently
    # We'll return bytes that look like PDF but will fail when processed
    return b"%PDF-1.4\n%%EOF"  # Minimal invalid PDF structure


@pytest.fixture
def invalid_pdf():
    """Create invalid PDF bytes"""
    return b"This is not a PDF file"


class TestBytesToImage:
    """Test bytes_to_image method"""

    def test_valid_image(self, valid_image_bytes):
        """Test converting valid image bytes"""
        img = FileService.bytes_to_image(valid_image_bytes)
        
        assert isinstance(img, Image.Image)
        assert img.size == (100, 100)
        assert img.mode == "RGB"

    def test_invalid_image_bytes(self):
        """Test handling invalid image data"""
        invalid_bytes = b"Not an image"
        
        with pytest.raises(ValueError, match="無法載入圖片"):
            FileService.bytes_to_image(invalid_bytes)


class TestPdfToImage:
    """Test pdf_to_image method"""

    def test_valid_pdf_conversion(self, valid_pdf_with_content):
        """Test converting valid PDF to image"""
        img = FileService.pdf_to_image(valid_pdf_with_content)
        
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
        # Check reasonable dimensions (A4 at 300 DPI)
        assert img.width > 0
        assert img.height > 0

    def test_empty_pdf(self, empty_pdf):
        """Test handling PDF with no pages"""
        with pytest.raises(ValueError, match="無法處理 PDF 檔案"):
            FileService.pdf_to_image(empty_pdf)

    def test_invalid_pdf(self, invalid_pdf):
        """Test handling invalid PDF bytes"""
        with pytest.raises(ValueError, match="無法處理 PDF 檔案"):
            FileService.pdf_to_image(invalid_pdf)

    def test_pdf_high_resolution(self, valid_pdf_with_content):
        """Test PDF is rendered at high DPI (300) for OCR"""
        img = FileService.pdf_to_image(valid_pdf_with_content)
        
        # A4 page at 300 DPI should be approximately:
        # Width: 595pt → ~2480px at 300 DPI
        # Height: 842pt → ~3508px at 300 DPI
        # Allow some tolerance
        assert img.width > 2000
        assert img.height > 3000


@pytest.mark.asyncio
class TestProcessUpload:
    """Test process_upload method"""

    async def test_process_image_upload(self, valid_image_bytes):
        """Test processing image file upload"""
        img = await FileService.process_upload(
            valid_image_bytes,
            "test.jpg",
            "image/jpeg"
        )
        
        assert isinstance(img, Image.Image)
        assert img.size == (100, 100)

    async def test_process_pdf_upload(self, valid_pdf_with_content):
        """Test processing PDF file upload"""
        img = await FileService.process_upload(
            valid_pdf_with_content,
            "test.pdf",
            "application/pdf"
        )
        
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"

    async def test_process_upload_file_too_large(self, valid_image_bytes):
        """Test file size validation"""
        # Create oversized file (> 10MB)
        large_file = b"x" * (11 * 1024 * 1024)
        
        with pytest.raises(ValueError, match="檔案大小超過限制"):
            await FileService.process_upload(
                large_file,
                "large.jpg",
                "image/jpeg"
            )

    async def test_process_upload_invalid_mime_type(self, valid_image_bytes):
        """Test MIME type validation"""
        with pytest.raises(ValueError, match="不支援的檔案格式"):
            await FileService.process_upload(
                valid_image_bytes,
                "document.txt",
                "text/plain"
            )

    async def test_process_upload_invalid_extension(self, valid_image_bytes):
        """Test file extension validation"""
        with pytest.raises(ValueError, match="不支援的檔案格式"):
            await FileService.process_upload(
                valid_image_bytes,
                "image.bmp",
                "image/jpeg"
            )
