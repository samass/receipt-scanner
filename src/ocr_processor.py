"""
OCR Processing Module for Receipt Scanner

This module handles image preprocessing and text extraction from receipt images
using Tesseract OCR. It includes functionality for:
- Image preprocessing (noise reduction, contrast enhancement)
- Text extraction from receipt images
- Basic item and price parsing
- Error handling and logging

Author: Receipt Scanner Project
License: GPL-3.0
"""

import re
import logging
from typing import Dict, List, Optional, Union, IO
import io

# Optional dependencies for OCR functionality
try:
    import cv2
    import numpy as np
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    OCR_DEPENDENCIES_AVAILABLE = False
    OCR_IMPORT_ERROR = str(e)
    # Create dummy classes for type hints
    class Image:
        class Image:
            pass
    cv2 = None
    np = None
    pytesseract = None
    ImageEnhance = None
    ImageFilter = None

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Handles OCR processing for receipt images"""
    
    def __init__(self, config):
        """
        Initialize OCR processor with configuration
        
        Args:
            config: Configuration object containing OCR settings
        """
        self.config = config
        self.tesseract_config = '--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6
        
        if not OCR_DEPENDENCIES_AVAILABLE:
            logger.error(f"OCR dependencies not available: {OCR_IMPORT_ERROR}")
            logger.error("Please install: pip install pytesseract opencv-python Pillow")
            raise ImportError("OCR dependencies not available")
        
        # Verify Tesseract installation
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR initialized successfully")
        except Exception as e:
            logger.error(f"Tesseract initialization failed: {e}")
            raise
    
    def process_image(self, image_input: Union[str, IO, Image.Image]) -> Optional[Dict]:
        """
        Process receipt image and extract text and items
        
        Args:
            image_input: Image file path, file object, or PIL Image
            
        Returns:
            Dictionary containing extracted text and parsed items, or None if failed
        """
        try:
            # Load and preprocess image
            image = self._load_image(image_input)
            if image is None:
                return None
            
            preprocessed_image = self._preprocess_image(image)
            
            # Extract text using OCR
            raw_text = self._extract_text(preprocessed_image)
            if not raw_text:
                logger.warning("No text extracted from image")
                return None
            
            # Parse items and prices from text
            items = self._parse_items_and_prices(raw_text)
            
            result = {
                'raw_text': raw_text,
                'items': items,
                'total_items': len(items),
                'processing_success': True
            }
            
            logger.info(f"Successfully processed image: {len(items)} items found")
            return result
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
    
    def _load_image(self, image_input: Union[str, IO, Image.Image]) -> Optional[Image.Image]:
        """
        Load image from various input types
        
        Args:
            image_input: Image source
            
        Returns:
            PIL Image object or None if loading failed
        """
        try:
            if isinstance(image_input, Image.Image):
                return image_input
            elif isinstance(image_input, str):
                return Image.open(image_input)
            else:
                # Assume it's a file-like object (e.g., from Streamlit)
                return Image.open(image_input)
                
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image: Input PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image if too small (improves OCR accuracy)
            width, height = image.size
            if width < 800 or height < 600:
                scale_factor = max(800/width, 600/height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Convert to grayscale for OCR
            image = image.convert('L')
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Convert to OpenCV format for advanced processing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_GRAY2BGR)
            
            # Apply adaptive thresholding
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(thresh)
            
            logger.debug("Image preprocessing completed")
            return processed_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image  # Return original if preprocessing fails
    
    def _extract_text(self, image: Image.Image) -> str:
        """
        Extract text from preprocessed image using Tesseract OCR
        
        Args:
            image: Preprocessed PIL Image
            
        Returns:
            Extracted text string
        """
        try:
            # Extract text using Tesseract
            text = pytesseract.image_to_string(
                image, 
                config=self.tesseract_config,
                lang='eng'  # Can be made configurable
            )
            
            # Clean up the text
            text = text.strip()
            
            logger.debug(f"Extracted text length: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def _parse_items_and_prices(self, text: str) -> List[Dict]:
        """
        Parse items and prices from extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            List of dictionaries containing item names and prices
        """
        items = []
        
        try:
            # Split text into lines
            lines = text.split('\n')
            
            # Common price patterns (adjust based on receipt formats)
            price_patterns = [
                r'(\d+[.,]\d{2})',  # Basic price pattern
                r'\$(\d+[.,]\d{2})',  # Price with dollar sign
                r'(\d+[.,]\d{2})\s*\$',  # Price followed by dollar sign
                r'(\d+[.,]\d{2})\s*(USD|usd)',  # Price with currency
            ]
            
            # Item and price extraction patterns
            item_price_patterns = [
                r'^(.+?)\s+(\d+[.,]\d{2})$',  # Item name followed by price
                r'^(.+?)\s+\$(\d+[.,]\d{2})$',  # Item name followed by price with $
                r'^(.+?)\s+(\d+[.,]\d{2})\s*\$$',  # Item name, price, $
            ]
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Skip lines that look like headers, totals, or non-item lines
                if self._should_skip_line(line):
                    continue
                
                # Try to match item and price patterns
                item_found = False
                for pattern in item_price_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        item_name = match.group(1).strip()
                        price_str = match.group(2).replace(',', '.')
                        
                        try:
                            price = float(price_str)
                            
                            # Filter out unreasonable prices
                            if 0.01 <= price <= 1000.00:
                                items.append({
                                    'name': self._clean_item_name(item_name),
                                    'price': price,
                                    'raw_line': line
                                })
                                item_found = True
                                break
                        except ValueError:
                            continue
                
                # If no pattern matched, try to find standalone prices
                if not item_found:
                    for pattern in price_patterns:
                        match = re.search(pattern, line)
                        if match:
                            price_str = match.group(1).replace(',', '.')
                            try:
                                price = float(price_str)
                                if 0.01 <= price <= 1000.00:
                                    # Extract potential item name (text before price)
                                    item_name = re.sub(pattern, '', line).strip()
                                    if item_name and len(item_name) > 2:
                                        items.append({
                                            'name': self._clean_item_name(item_name),
                                            'price': price,
                                            'raw_line': line
                                        })
                                        break
                            except ValueError:
                                continue
            
            # Remove duplicates based on name and price
            unique_items = []
            seen = set()
            for item in items:
                key = (item['name'].lower(), item['price'])
                if key not in seen:
                    seen.add(key)
                    unique_items.append(item)
            
            logger.info(f"Parsed {len(unique_items)} unique items from text")
            return unique_items
            
        except Exception as e:
            logger.error(f"Error parsing items and prices: {e}")
            return []
    
    def _should_skip_line(self, line: str) -> bool:
        """
        Determine if a line should be skipped during parsing
        
        Args:
            line: Text line to evaluate
            
        Returns:
            True if line should be skipped
        """
        line_lower = line.lower()
        
        # Skip common receipt header/footer content
        skip_keywords = [
            'total', 'subtotal', 'tax', 'receipt', 'store', 'thank you',
            'visit', 'date', 'time', 'cashier', 'card', 'change',
            'balance', 'tender', 'auth', 'approval', 'ref', 'trans',
            'customer', 'copy', 'merchant', 'terminal', 'batch'
        ]
        
        for keyword in skip_keywords:
            if keyword in line_lower:
                return True
        
        # Skip lines that are too short or too long
        if len(line) < 3 or len(line) > 50:
            return True
        
        # Skip lines with only numbers or special characters
        if re.match(r'^[\d\s\.\,\-\*]+$', line):
            return True
        
        return False
    
    def _clean_item_name(self, name: str) -> str:
        """
        Clean and normalize item names
        
        Args:
            name: Raw item name
            
        Returns:
            Cleaned item name
        """
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^[\d\s\.\-\*]+', '', name)  # Remove leading numbers/symbols
        name = re.sub(r'[\d\s\.\-\*]+$', '', name)  # Remove trailing numbers/symbols
        
        # Capitalize first letter of each word
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name.strip()
    
    def get_processing_stats(self) -> Dict:
        """
        Get OCR processing statistics
        
        Returns:
            Dictionary containing processing statistics
        """
        try:
            tesseract_version = pytesseract.get_tesseract_version()
            return {
                'tesseract_version': str(tesseract_version),
                'supported_languages': pytesseract.get_languages(),
                'config': self.tesseract_config
            }
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {}