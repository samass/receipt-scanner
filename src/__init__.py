"""
Receipt Scanner Package

This package contains the core modules for the receipt scanner application:
- ocr_processor: Handles OCR processing and text extraction
- data_storage: Manages data persistence (SQLite, Google Sheets)
- categories: Handles expense categorization
- config: Application configuration management

Author: Receipt Scanner Project
License: GPL-3.0
"""

__version__ = "1.0.0"
__author__ = "Receipt Scanner Project"
__license__ = "GPL-3.0"

from .config import Config
from .categories import CategoryManager
from .data_storage import DataStorage

# OCR processor requires additional dependencies
try:
    from .ocr_processor import OCRProcessor
    OCR_AVAILABLE = True
except ImportError:
    OCRProcessor = None
    OCR_AVAILABLE = False

__all__ = [
    'Config',
    'CategoryManager',
    'DataStorage'
]

if OCR_AVAILABLE:
    __all__.append('OCRProcessor')