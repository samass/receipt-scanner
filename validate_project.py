#!/usr/bin/env python3
"""
Receipt Scanner Project Validation

This script validates that the receipt scanner project is properly structured
and all core components are working.

Run with: python validate_project.py
"""

import sys
import os
from pathlib import Path
import importlib.util

def validate_project_structure():
    """Validate project directory structure"""
    print("📁 Validating Project Structure...")
    
    required_files = [
        "app.py",
        "requirements.txt", 
        "README.md",
        ".gitignore",
        "run.py",
        "src/__init__.py",
        "src/config.py",
        "src/categories.py", 
        "src/data_storage.py",
        "src/ocr_processor.py",
        "tests/test_basic.py",
        "sample_data/generate_samples.py",
        "docs/SETUP_GUIDE.md"
    ]
    
    required_dirs = [
        "src",
        "sample_data", 
        "tests",
        "docs",
        "config"
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
        else:
            print(f"  ✅ {dir_path}/")
    
    if missing_files or missing_dirs:
        print(f"  ❌ Missing files: {missing_files}")
        print(f"  ❌ Missing directories: {missing_dirs}")
        return False
    
    print("  🎉 Project structure is complete!")
    return True

def validate_core_modules():
    """Validate core module functionality"""
    print("\n🧩 Validating Core Modules...")
    
    sys.path.append(str(Path("src")))
    
    try:
        # Test config module
        from src.config import Config
        config = Config()
        print(f"  ✅ Config module - Language: {config.ocr.language}")
        
        # Test categories module  
        from src.categories import CategoryManager
        cm = CategoryManager(config)
        categories = cm.get_categories()
        print(f"  ✅ Categories module - {len(categories)} categories")
        
        # Test category suggestions
        suggestion = cm.suggest_category("milk", "walmart")
        print(f"  ✅ Category suggestions - milk -> {suggestion}")
        
        # Test data storage module
        from src.data_storage import DataStorage
        ds = DataStorage(config)
        print("  ✅ Data storage module initialized")
        
        # Test OCR module import (may fail without dependencies)
        try:
            from src.ocr_processor import OCRProcessor
            print("  ✅ OCR processor module available")
            ocr_available = True
        except ImportError as e:
            print(f"  ⚠️  OCR processor not available: {e}")
            ocr_available = False
        
        return True, ocr_available
        
    except Exception as e:
        print(f"  ❌ Module validation failed: {e}")
        return False, False

def validate_sample_data():
    """Validate sample data generation"""
    print("\n📋 Validating Sample Data...")
    
    try:
        # Run sample data generation
        os.chdir(Path.cwd())
        result = os.system("python sample_data/generate_samples.py > /dev/null 2>&1")
        
        if result == 0:
            print("  ✅ Sample data generation works")
            
            # Check that files were created
            sample_files = list(Path("sample_data/images").glob("*.txt"))
            print(f"  ✅ Created {len(sample_files)} sample receipt files")
            
            return True
        else:
            print("  ❌ Sample data generation failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Sample data validation failed: {e}")
        return False

def validate_configuration():
    """Validate configuration system"""
    print("\n⚙️ Validating Configuration...")
    
    try:
        sys.path.append(str(Path("src")))
        from src.config import Config
        
        # Test default configuration
        config = Config()
        print(f"  ✅ Default config loads - Theme: {config.ui.theme}")
        
        # Test configuration update
        original_theme = config.ui.theme
        config.ui.theme = "dark"
        print(f"  ✅ Config update works - Theme: {config.ui.theme}")
        
        # Test configuration save/load
        if config.save_config():
            print("  ✅ Config saves successfully")
        else:
            print("  ⚠️  Config save failed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration validation failed: {e}")
        return False

def check_optional_dependencies():
    """Check status of optional dependencies"""
    print("\n📦 Checking Optional Dependencies...")
    
    dependencies = {
        "streamlit": "Web interface framework",
        "pytesseract": "OCR text extraction", 
        "opencv-python": "Image preprocessing",
        "Pillow": "Image handling",
        "pandas": "Data manipulation",
        "gspread": "Google Sheets integration",
        "python-dotenv": "Environment variables"
    }
    
    available = []
    missing = []
    
    for dep, description in dependencies.items():
        try:
            if dep == "opencv-python":
                import cv2
            else:
                __import__(dep.replace("-", "_"))
            print(f"  ✅ {dep} - {description}")
            available.append(dep)
        except ImportError:
            print(f"  ⚠️  {dep} - {description} (optional)")
            missing.append(dep)
    
    print(f"\n  📊 Available: {len(available)}/{len(dependencies)} dependencies")
    
    if "streamlit" in available:
        print("  🚀 Ready to run web application!")
    else:
        print("  📝 Install streamlit to run web interface: pip install streamlit")
    
    return len(available), len(missing)

def validate_tests():
    """Validate test framework"""
    print("\n🧪 Validating Tests...")
    
    try:
        # Check if pytest is available
        try:
            import pytest
            pytest_available = True
            print("  ✅ pytest available")
        except ImportError:
            pytest_available = False
            print("  ⚠️  pytest not available (optional)")
        
        # Try to run basic test manually
        sys.path.append(str(Path("src")))
        from src.config import Config
        
        # Basic test
        config = Config()
        assert config.ocr.language == 'eng'
        assert config.ui.page_title == "Receipt Scanner"
        print("  ✅ Basic assertions pass")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Test validation failed: {e}")
        return False

def main():
    """Main validation routine"""
    print("🧾 Receipt Scanner Project Validation")
    print("=" * 50)
    
    results = []
    
    # Run all validations
    results.append(("Structure", validate_project_structure()))
    core_result, ocr_available = validate_core_modules()
    results.append(("Core Modules", core_result))
    results.append(("Sample Data", validate_sample_data()))
    results.append(("Configuration", validate_configuration()))
    available_deps, missing_deps = check_optional_dependencies()
    results.append(("Dependencies", available_deps > 0))
    results.append(("Tests", validate_tests()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} validations")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    if passed == len(results):
        print("🎉 Project is fully functional!")
        if ocr_available:
            print("🚀 Ready to run: python run.py")
        else:
            print("📦 Install OCR dependencies for full functionality:")
            print("   pip install pytesseract opencv-python Pillow")
    else:
        print("⚠️  Some validations failed. Check the errors above.")
    
    if missing_deps > 0:
        print(f"📦 Install all dependencies: pip install -r requirements.txt")
    
    print("\n📖 See docs/SETUP_GUIDE.md for detailed setup instructions")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)