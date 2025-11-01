"""File validation utilities"""

from src.utils.constants import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_FILE_SIZE


def validate_file_size(size: int) -> None:
    """Validate file size

    Args:
        size: File size in bytes

    Raises:
        ValueError: If file size exceeds MAX_FILE_SIZE
    """
    if size > MAX_FILE_SIZE:
        raise ValueError(f"檔案大小超過限制(最大 {MAX_FILE_SIZE // (1024 * 1024)}MB)")


def validate_mime_type(mime_type: str) -> None:
    """Validate MIME type

    Args:
        mime_type: MIME type string

    Raises:
        ValueError: If MIME type is not in ALLOWED_MIME_TYPES
    """
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError("不支援的檔案格式,請上傳 JPG、PNG 或 PDF")


def validate_file_extension(filename: str) -> None:
    """Validate file extension

    Args:
        filename: File name with extension

    Raises:
        ValueError: If file extension is not in ALLOWED_EXTENSIONS
    """
    # Get file extension (case insensitive)
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("不支援的檔案格式,請上傳 JPG、PNG 或 PDF")
