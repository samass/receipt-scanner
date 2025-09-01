# Receipt Scanner Setup and Testing Guide

This guide helps you set up and test the Receipt Scanner application from scratch.

## Quick Start (Minimum Dependencies)

### 1. Basic Setup
```bash
# Clone the repository
git clone https://github.com/samass/receipt-scanner.git
cd receipt-scanner

# Create virtual environment (recommended)
python -m venv receipt_scanner_env

# Activate virtual environment
# Windows:
receipt_scanner_env\Scripts\activate
# macOS/Linux:
source receipt_scanner_env/bin/activate

# Install core dependencies
pip install streamlit pyyaml
```

### 2. Test Core Functionality
```bash
# Run basic module test
python -c "
import sys
from pathlib import Path
sys.path.append(str(Path('src')))
from src.config import Config
from src.categories import CategoryManager
print('✅ Core modules working!')
"

# Run the web application
streamlit run app.py
```

This will start the application with core functionality (category management, data storage) but without OCR capabilities.

## Full Setup (All Features)

### 1. Install Tesseract OCR

**Windows:**
1. Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH
3. Verify: `tesseract --version`

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

### 2. Install All Dependencies
```bash
pip install -r requirements.txt
```

### 3. Test Full Functionality
```bash
# Run comprehensive test
python tests/test_basic.py

# Or use pytest
pytest tests/

# Run the application with all features
python run.py
```

## Testing the Application

### 1. Core Features Test
- ✅ **Configuration**: Settings load and save properly
- ✅ **Categories**: Can add, remove, and manage expense categories
- ✅ **Data Storage**: SQLite database creates and stores data
- ✅ **Web Interface**: Streamlit app loads and is responsive

### 2. OCR Features Test (requires Tesseract)
- 📤 **Upload**: Drag and drop receipt images
- 🔍 **OCR Processing**: Text extraction from images
- 🏷️ **Auto-categorization**: Smart category suggestions
- 💾 **Data Saving**: Processed receipts save to database

### 3. Sample Data Test
```bash
# Generate sample data
python sample_data/generate_samples.py

# Test category suggestions
python -c "
import sys
from pathlib import Path
sys.path.append(str(Path('src')))
from src.config import Config
from src.categories import CategoryManager

config = Config()
cm = CategoryManager(config)

test_items = [
    ('milk', 'walmart'),
    ('pizza', 'restaurant'),
    ('gasoline', 'shell')
]

for item, store in test_items:
    category = cm.suggest_category(item, store)
    print(f'{item} at {store} -> {category}')
"
```

## Application Structure

```
receipt-scanner/
├── app.py                    # 🚀 Main Streamlit application
├── run.py                    # 🎯 Easy startup script
├── requirements.txt          # 📦 Dependencies
├── README.md                # 📖 Documentation
├── src/                     # 🧩 Core modules
│   ├── config.py            # ⚙️ Configuration management
│   ├── ocr_processor.py     # 🔍 OCR and image processing
│   ├── data_storage.py      # 💾 Database operations
│   └── categories.py        # 🏷️ Category management
├── sample_data/             # 📋 Test data and examples
├── tests/                   # 🧪 Unit tests
├── config/                  # ⚙️ Configuration files
└── logs/                    # 📝 Application logs
```

## Feature Testing Checklist

### ✅ Core Features (No External Dependencies)
- [ ] App starts without errors
- [ ] Configuration loads with defaults
- [ ] Categories display and can be managed
- [ ] Data storage initializes SQLite database
- [ ] Settings can be modified and saved
- [ ] Interface is mobile-responsive

### 🔍 OCR Features (Requires Tesseract + Dependencies)
- [ ] Tesseract is detected and working
- [ ] Images can be uploaded via interface
- [ ] OCR extracts text from images
- [ ] Items and prices are parsed correctly
- [ ] Categories are suggested automatically
- [ ] Processed data saves to database

### 📊 Data Management
- [ ] Receipts save with all item details
- [ ] Data can be viewed in the interface
- [ ] CSV export works correctly
- [ ] Database statistics are accurate
- [ ] Categories can be added/removed

### 🎨 User Interface
- [ ] All tabs load without errors
- [ ] Upload interface works on mobile
- [ ] Forms submit correctly
- [ ] Error messages are helpful
- [ ] Success feedback is clear

## Troubleshooting

### Common Issues

**"No module named 'streamlit'"**
```bash
pip install streamlit
```

**"Tesseract not found"**
- Install Tesseract OCR for your platform
- Ensure it's in your system PATH
- Test with: `tesseract --version`

**"OCR dependencies not available"**
```bash
pip install pytesseract opencv-python Pillow
```

**Database errors**
- Check file permissions in application directory
- Ensure SQLite is available (built into Python)
- Delete `receipt_data.sqlite3` to reset database

**Configuration errors**
- Delete `config/app_config.yaml` to regenerate
- Check YAML syntax if manually edited
- Verify environment variables are set correctly

### Performance Tips

**For better OCR results:**
- Use high-resolution images (min 800x600)
- Ensure good lighting and contrast
- Keep receipts flat when photographing
- Use PNG format for scanned receipts

**For faster startup:**
- Use virtual environment
- Install only needed dependencies
- Clear logs periodically

## Advanced Configuration

### Environment Variables
```bash
# OCR Settings
export OCR_LANGUAGE=eng
export OCR_CONFIDENCE_THRESHOLD=60.0

# Storage Settings  
export DATABASE_PATH=custom_receipts.db
export GOOGLE_SHEETS_ENABLED=false

# UI Settings
export UI_THEME=dark
export MAX_FILE_SIZE_MB=20
```

### Custom Categories
Add your own categories via the web interface or programmatically:

```python
from src.config import Config
from src.categories import CategoryManager

config = Config()
cm = CategoryManager(config)

# Add custom category
cm.add_category("Pet Supplies", "Pet food, toys, vet bills")

# Add keywords for better auto-categorization
cm.update_category_keywords("Pet Supplies", [
    "petco", "petsmart", "vet", "dog food", "cat food", 
    "pet", "animal", "veterinary"
])
```

## Support and Development

- **Issues**: Report bugs via GitHub Issues
- **Features**: Request new features via GitHub Issues  
- **Contributing**: Fork, improve, submit pull requests
- **Documentation**: Help improve this guide

---

**Ready to scan some receipts? Run `python run.py` to get started! 🧾**