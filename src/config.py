"""
Configuration Module for Receipt Scanner

This module handles application configuration including:
- Environment variables and settings
- OCR configuration options
- Storage preferences
- UI customization settings
- Default values and validation

Author: Receipt Scanner Project
License: GPL-3.0
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Optional dependency - load_dotenv
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    def load_dotenv(*args, **kwargs):
        pass

logger = logging.getLogger(__name__)

@dataclass
class OCRConfig:
    """OCR-specific configuration"""
    language: str = 'eng'
    psm_mode: int = 6  # Page segmentation mode
    oem_mode: int = 3  # OCR engine mode
    confidence_threshold: float = 60.0
    preprocessing_enabled: bool = True
    enhance_contrast: bool = True
    enhance_sharpness: bool = True
    min_image_width: int = 800
    min_image_height: int = 600

@dataclass
class StorageConfig:
    """Storage-specific configuration"""
    database_path: str = "receipt_data.sqlite3"
    google_sheets_enabled: bool = False
    google_sheets_key: Optional[str] = None
    google_sheets_url: Optional[str] = None
    backup_enabled: bool = True
    backup_frequency_days: int = 7
    auto_export_enabled: bool = False

@dataclass
class UIConfig:
    """UI-specific configuration"""
    theme: str = "light"  # light, dark, auto
    page_title: str = "Receipt Scanner"
    page_icon: str = "🧾"
    sidebar_expanded: bool = True
    max_file_size_mb: int = 10
    supported_formats: list = field(default_factory=lambda: ['png', 'jpg', 'jpeg', 'gif', 'bmp'])
    mobile_responsive: bool = True

@dataclass
class CategoryConfig:
    """Category management configuration"""
    auto_categorization: bool = True
    ml_categorization: bool = False  # Placeholder for future ML
    suggestion_confidence_threshold: float = 0.7
    custom_categories_enabled: bool = True
    default_category: str = "Other"

class Config:
    """Main configuration manager for the receipt scanner application"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or "config/app_config.yaml"
        self.env_file = ".env"
        
        # Load environment variables
        self._load_environment()
        
        # Initialize configuration sections
        self.ocr = OCRConfig()
        self.storage = StorageConfig()
        self.ui = UIConfig()
        self.categories = CategoryConfig()
        
        # Load configuration from file
        self._load_config()
        
        # Validate configuration
        self._validate_config()
        
        logger.info("Configuration initialized successfully")
    
    def _load_environment(self):
        """Load environment variables from .env file"""
        try:
            env_path = Path(self.env_file)
            if env_path.exists() and DOTENV_AVAILABLE:
                load_dotenv(env_path)
                logger.info(f"Loaded environment variables from {self.env_file}")
            else:
                if not DOTENV_AVAILABLE:
                    logger.info("python-dotenv not available, using system environment variables only")
                else:
                    logger.info("No .env file found, using system environment variables")
                
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            config_path = Path(self.config_file)
            
            if config_path.exists():
                with open(config_path, 'r') as file:
                    config_data = yaml.safe_load(file)
                
                self._update_from_dict(config_data)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info(f"Configuration file {self.config_file} not found, using defaults")
                # Create default configuration file
                self._create_default_config()
                
        except Exception as e:
            logger.error(f"Error loading configuration file: {e}")
            logger.info("Using default configuration")
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary"""
        try:
            # Update OCR configuration
            if 'ocr' in config_data:
                ocr_data = config_data['ocr']
                for key, value in ocr_data.items():
                    if hasattr(self.ocr, key):
                        setattr(self.ocr, key, value)
            
            # Update storage configuration
            if 'storage' in config_data:
                storage_data = config_data['storage']
                for key, value in storage_data.items():
                    if hasattr(self.storage, key):
                        setattr(self.storage, key, value)
            
            # Update UI configuration
            if 'ui' in config_data:
                ui_data = config_data['ui']
                for key, value in ui_data.items():
                    if hasattr(self.ui, key):
                        setattr(self.ui, key, value)
            
            # Update category configuration
            if 'categories' in config_data:
                category_data = config_data['categories']
                for key, value in category_data.items():
                    if hasattr(self.categories, key):
                        setattr(self.categories, key, value)
            
            # Override with environment variables
            self._load_from_env()
            
        except Exception as e:
            logger.error(f"Error updating configuration from dictionary: {e}")
    
    def _load_from_env(self):
        """Load configuration overrides from environment variables"""
        try:
            # OCR settings
            if os.getenv('OCR_LANGUAGE'):
                self.ocr.language = os.getenv('OCR_LANGUAGE')
            if os.getenv('OCR_CONFIDENCE_THRESHOLD'):
                self.ocr.confidence_threshold = float(os.getenv('OCR_CONFIDENCE_THRESHOLD'))
            
            # Storage settings
            if os.getenv('DATABASE_PATH'):
                self.storage.database_path = os.getenv('DATABASE_PATH')
            if os.getenv('GOOGLE_SHEETS_ENABLED'):
                self.storage.google_sheets_enabled = os.getenv('GOOGLE_SHEETS_ENABLED').lower() == 'true'
            if os.getenv('GOOGLE_SHEETS_KEY'):
                self.storage.google_sheets_key = os.getenv('GOOGLE_SHEETS_KEY')
            if os.getenv('GOOGLE_SHEETS_URL'):
                self.storage.google_sheets_url = os.getenv('GOOGLE_SHEETS_URL')
            
            # UI settings
            if os.getenv('UI_THEME'):
                self.ui.theme = os.getenv('UI_THEME')
            if os.getenv('MAX_FILE_SIZE_MB'):
                self.ui.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB'))
            
            # Category settings
            if os.getenv('AUTO_CATEGORIZATION'):
                self.categories.auto_categorization = os.getenv('AUTO_CATEGORIZATION').lower() == 'true'
            
        except Exception as e:
            logger.error(f"Error loading environment variable overrides: {e}")
    
    def _validate_config(self):
        """Validate configuration values"""
        try:
            # Validate OCR config
            if self.ocr.confidence_threshold < 0 or self.ocr.confidence_threshold > 100:
                logger.warning("Invalid OCR confidence threshold, using default")
                self.ocr.confidence_threshold = 60.0
            
            if self.ocr.psm_mode < 0 or self.ocr.psm_mode > 13:
                logger.warning("Invalid OCR PSM mode, using default")
                self.ocr.psm_mode = 6
            
            # Validate storage config
            if self.storage.backup_frequency_days < 1:
                logger.warning("Invalid backup frequency, using default")
                self.storage.backup_frequency_days = 7
            
            # Validate UI config
            if self.ui.max_file_size_mb < 1 or self.ui.max_file_size_mb > 100:
                logger.warning("Invalid max file size, using default")
                self.ui.max_file_size_mb = 10
            
            valid_themes = ['light', 'dark', 'auto']
            if self.ui.theme not in valid_themes:
                logger.warning(f"Invalid theme '{self.ui.theme}', using 'light'")
                self.ui.theme = 'light'
            
            # Validate category config
            if self.categories.suggestion_confidence_threshold < 0 or self.categories.suggestion_confidence_threshold > 1:
                logger.warning("Invalid suggestion confidence threshold, using default")
                self.categories.suggestion_confidence_threshold = 0.7
            
            logger.info("Configuration validation completed")
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
    
    def _create_default_config(self):
        """Create a default configuration file"""
        try:
            config_dir = Path(self.config_file).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            default_config = {
                'ocr': {
                    'language': self.ocr.language,
                    'psm_mode': self.ocr.psm_mode,
                    'oem_mode': self.ocr.oem_mode,
                    'confidence_threshold': self.ocr.confidence_threshold,
                    'preprocessing_enabled': self.ocr.preprocessing_enabled,
                    'enhance_contrast': self.ocr.enhance_contrast,
                    'enhance_sharpness': self.ocr.enhance_sharpness,
                    'min_image_width': self.ocr.min_image_width,
                    'min_image_height': self.ocr.min_image_height
                },
                'storage': {
                    'database_path': self.storage.database_path,
                    'google_sheets_enabled': self.storage.google_sheets_enabled,
                    'backup_enabled': self.storage.backup_enabled,
                    'backup_frequency_days': self.storage.backup_frequency_days,
                    'auto_export_enabled': self.storage.auto_export_enabled
                },
                'ui': {
                    'theme': self.ui.theme,
                    'page_title': self.ui.page_title,
                    'page_icon': self.ui.page_icon,
                    'sidebar_expanded': self.ui.sidebar_expanded,
                    'max_file_size_mb': self.ui.max_file_size_mb,
                    'supported_formats': self.ui.supported_formats,
                    'mobile_responsive': self.ui.mobile_responsive
                },
                'categories': {
                    'auto_categorization': self.categories.auto_categorization,
                    'ml_categorization': self.categories.ml_categorization,
                    'suggestion_confidence_threshold': self.categories.suggestion_confidence_threshold,
                    'custom_categories_enabled': self.categories.custom_categories_enabled,
                    'default_category': self.categories.default_category
                }
            }
            
            with open(self.config_file, 'w') as file:
                yaml.dump(default_config, file, default_flow_style=False, indent=2)
            
            logger.info(f"Created default configuration file: {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error creating default configuration file: {e}")
    
    def save_config(self) -> bool:
        """
        Save current configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            config_data = {
                'ocr': {
                    'language': self.ocr.language,
                    'psm_mode': self.ocr.psm_mode,
                    'oem_mode': self.ocr.oem_mode,
                    'confidence_threshold': self.ocr.confidence_threshold,
                    'preprocessing_enabled': self.ocr.preprocessing_enabled,
                    'enhance_contrast': self.ocr.enhance_contrast,
                    'enhance_sharpness': self.ocr.enhance_sharpness,
                    'min_image_width': self.ocr.min_image_width,
                    'min_image_height': self.ocr.min_image_height
                },
                'storage': {
                    'database_path': self.storage.database_path,
                    'google_sheets_enabled': self.storage.google_sheets_enabled,
                    'backup_enabled': self.storage.backup_enabled,
                    'backup_frequency_days': self.storage.backup_frequency_days,
                    'auto_export_enabled': self.storage.auto_export_enabled
                },
                'ui': {
                    'theme': self.ui.theme,
                    'page_title': self.ui.page_title,
                    'page_icon': self.ui.page_icon,
                    'sidebar_expanded': self.ui.sidebar_expanded,
                    'max_file_size_mb': self.ui.max_file_size_mb,
                    'supported_formats': self.ui.supported_formats,
                    'mobile_responsive': self.ui.mobile_responsive
                },
                'categories': {
                    'auto_categorization': self.categories.auto_categorization,
                    'ml_categorization': self.categories.ml_categorization,
                    'suggestion_confidence_threshold': self.categories.suggestion_confidence_threshold,
                    'custom_categories_enabled': self.categories.custom_categories_enabled,
                    'default_category': self.categories.default_category
                }
            }
            
            config_dir = Path(self.config_file).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as file:
                yaml.dump(config_data, file, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_tesseract_config(self) -> str:
        """
        Get Tesseract configuration string
        
        Returns:
            Tesseract configuration string
        """
        return f"--oem {self.ocr.oem_mode} --psm {self.ocr.psm_mode}"
    
    def get_database_path(self) -> Path:
        """
        Get database path as Path object
        
        Returns:
            Path object for database
        """
        return Path(self.storage.database_path)
    
    def is_google_sheets_enabled(self) -> bool:
        """
        Check if Google Sheets integration is enabled and configured
        
        Returns:
            True if Google Sheets is enabled and configured
        """
        return (
            self.storage.google_sheets_enabled and 
            (self.storage.google_sheets_key is not None or 
             self.storage.google_sheets_url is not None)
        )
    
    def get_ui_config_dict(self) -> Dict[str, Any]:
        """
        Get UI configuration as dictionary for Streamlit
        
        Returns:
            Dictionary containing UI configuration
        """
        return {
            'page_title': self.ui.page_title,
            'page_icon': self.ui.page_icon,
            'layout': 'wide',
            'initial_sidebar_state': 'expanded' if self.ui.sidebar_expanded else 'collapsed'
        }
    
    def update_setting(self, section: str, key: str, value: Any) -> bool:
        """
        Update a specific configuration setting
        
        Args:
            section: Configuration section (ocr, storage, ui, categories)
            key: Setting key
            value: New value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            section_obj = getattr(self, section, None)
            if section_obj is None:
                logger.error(f"Invalid configuration section: {section}")
                return False
            
            if not hasattr(section_obj, key):
                logger.error(f"Invalid configuration key: {key} in section {section}")
                return False
            
            setattr(section_obj, key, value)
            logger.info(f"Updated {section}.{key} = {value}")
            
            # Save configuration
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error updating setting {section}.{key}: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ocr = OCRConfig()
            self.storage = StorageConfig()
            self.ui = UIConfig()
            self.categories = CategoryConfig()
            
            logger.info("Configuration reset to defaults")
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error resetting configuration to defaults: {e}")
            return False
    
    def export_config(self) -> Dict[str, Any]:
        """
        Export configuration for backup/sharing
        
        Returns:
            Dictionary containing all configuration data
        """
        try:
            return {
                'ocr': self.ocr.__dict__,
                'storage': {k: v for k, v in self.storage.__dict__.items() 
                           if not k.endswith('_key')},  # Exclude sensitive data
                'ui': self.ui.__dict__,
                'categories': self.categories.__dict__
            }
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return {}
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"Config(ocr={self.ocr}, storage={self.storage}, ui={self.ui}, categories={self.categories})"