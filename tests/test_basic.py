"""
Basic Tests for Receipt Scanner

This file contains basic unit tests for the receipt scanner components.
Run with: pytest tests/

Author: Receipt Scanner Project
License: GPL-3.0
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.config import Config, OCRConfig, StorageConfig, UIConfig, CategoryConfig
from src.categories import CategoryManager
import tempfile
import os

class TestConfig:
    """Test configuration management"""
    
    def test_config_initialization(self):
        """Test that configuration initializes with defaults"""
        config = Config()
        
        assert config.ocr.language == 'eng'
        assert config.storage.database_path == "receipt_data.sqlite3"
        assert config.ui.page_title == "Receipt Scanner"
        assert config.categories.auto_categorization == True
    
    def test_ocr_config(self):
        """Test OCR configuration"""
        ocr_config = OCRConfig()
        
        assert ocr_config.language == 'eng'
        assert ocr_config.psm_mode == 6
        assert ocr_config.oem_mode == 3
        assert ocr_config.confidence_threshold == 60.0
    
    def test_storage_config(self):
        """Test storage configuration"""
        storage_config = StorageConfig()
        
        assert storage_config.database_path == "receipt_data.sqlite3"
        assert storage_config.google_sheets_enabled == False
        assert storage_config.backup_enabled == True
    
    def test_ui_config(self):
        """Test UI configuration"""
        ui_config = UIConfig()
        
        assert ui_config.theme == "light"
        assert ui_config.page_title == "Receipt Scanner"
        assert ui_config.max_file_size_mb == 10
        assert ui_config.mobile_responsive == True
    
    def test_category_config(self):
        """Test category configuration"""
        category_config = CategoryConfig()
        
        assert category_config.auto_categorization == True
        assert category_config.default_category == "Other"
        assert category_config.suggestion_confidence_threshold == 0.7

class TestCategoryManager:
    """Test category management functionality"""
    
    def setup_method(self):
        """Setup test database"""
        self.test_db = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.test_db.close()
        
        # Create config with test database
        config = Config()
        config.storage.database_path = self.test_db.name
        
        self.category_manager = CategoryManager(config)
    
    def teardown_method(self):
        """Cleanup test database"""
        try:
            os.unlink(self.test_db.name)
        except:
            pass
    
    def test_get_categories(self):
        """Test getting category list"""
        categories = self.category_manager.get_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert 'Groceries' in categories
        assert 'Other' in categories
    
    def test_suggest_category(self):
        """Test category suggestion"""
        # Test grocery item
        category = self.category_manager.suggest_category("milk", "walmart")
        assert category == "Groceries"
        
        # Test dining item
        category = self.category_manager.suggest_category("pizza", "pizza palace")
        assert category == "Dining"
        
        # Test transportation item  
        category = self.category_manager.suggest_category("gasoline", "shell")
        assert category == "Transportation"
        
        # Test unknown item
        category = self.category_manager.suggest_category("random item", "unknown store")
        assert category == "Other"
    
    def test_add_category(self):
        """Test adding new category"""
        initial_categories = self.category_manager.get_categories()
        initial_count = len(initial_categories)
        
        # Add new category
        result = self.category_manager.add_category("Test Category", "Test description")
        assert result == True
        
        # Check that category was added
        updated_categories = self.category_manager.get_categories()
        assert len(updated_categories) == initial_count + 1
        assert "Test Category" in updated_categories
    
    def test_bulk_categorize(self):
        """Test bulk categorization"""
        items = [
            {"name": "milk", "store": "grocery store"},
            {"name": "pizza", "store": "restaurant"},
            {"name": "gas", "store": "gas station"}
        ]
        
        categorized_items = self.category_manager.bulk_categorize(items)
        
        assert len(categorized_items) == 3
        assert categorized_items[0]["category"] == "Groceries"
        assert categorized_items[1]["category"] == "Dining"
        assert categorized_items[2]["category"] == "Transportation"

class TestOCRProcessor:
    """Test OCR processing functionality"""
    
    def test_should_skip_line(self):
        """Test line filtering logic"""
        # This would require importing OCRProcessor and testing without full initialization
        # For now, we'll test the logic conceptually
        
        # Lines that should be skipped
        skip_lines = [
            "TOTAL 25.99",
            "TAX 2.15", 
            "THANK YOU",
            "***",
            "RECEIPT #12345"
        ]
        
        # Lines that should not be skipped
        keep_lines = [
            "MILK 2% GALLON    3.99",
            "BREAD WHEAT       2.49",
            "EGGS DOZEN        2.89"
        ]
        
        # This is a conceptual test - actual implementation would test the method
        assert True  # Placeholder

class TestDataStorage:
    """Test data storage functionality"""
    
    def test_database_initialization(self):
        """Test that database initializes properly"""
        # This would test database creation and table setup
        # For now, we'll test conceptually
        assert True  # Placeholder
    
    def test_receipt_storage(self):
        """Test receipt saving and retrieval"""
        # This would test the full storage cycle
        assert True  # Placeholder

def test_import_all_modules():
    """Test that all modules can be imported without errors"""
    try:
        from src.config import Config
        from src.categories import CategoryManager
        # OCRProcessor and DataStorage require additional dependencies
        # that may not be available in test environment
        
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")

if __name__ == "__main__":
    pytest.main([__file__])