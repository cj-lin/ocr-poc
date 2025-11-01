"""Test file validators"""

import pytest

from src.utils.constants import ALLOWED_MIME_TYPES, MAX_FILE_SIZE
from src.utils.validators import validate_file_size, validate_mime_type, validate_file_extension


def test_validate_file_size_valid():
    """Test that valid file sizes pass validation"""
    # 5MB file should be valid (under 10MB limit)
    size = 5 * 1024 * 1024
    validate_file_size(size)  # Should not raise


def test_validate_file_size_too_large():
    """Test that oversized files are rejected"""
    # 15MB file should be invalid
    size = 15 * 1024 * 1024
    with pytest.raises(ValueError, match="檔案大小超過限制"):
        validate_file_size(size)


def test_validate_file_size_at_limit():
    """Test that files at exactly 10MB are valid"""
    size = MAX_FILE_SIZE
    validate_file_size(size)  # Should not raise


def test_validate_mime_type_valid():
    """Test that allowed MIME types pass validation"""
    for mime_type in ALLOWED_MIME_TYPES:
        validate_mime_type(mime_type)  # Should not raise


def test_validate_mime_type_invalid():
    """Test that disallowed MIME types are rejected"""
    invalid_types = ["image/gif", "application/zip", "text/plain", "video/mp4"]
    for mime_type in invalid_types:
        with pytest.raises(ValueError, match="不支援的檔案格式"):
            validate_mime_type(mime_type)


def test_validate_file_extension_valid():
    """Test that allowed file extensions pass validation"""
    valid_filenames = [
        "id_card.jpg",
        "document.jpeg",
        "scan.png",
        "file.pdf",
        "ID_CARD.JPG",  # Case insensitive
    ]
    for filename in valid_filenames:
        validate_file_extension(filename)  # Should not raise


def test_validate_file_extension_invalid():
    """Test that disallowed file extensions are rejected"""
    invalid_filenames = [
        "document.gif",
        "file.txt",
        "archive.zip",
        "video.mp4",
        "noextension",
    ]
    for filename in invalid_filenames:
        with pytest.raises(ValueError, match="不支援的檔案格式"):
            validate_file_extension(filename)
