# Receipt Scanner 🧾

A web-based tool that reads items from photos of shopping receipts, recognizes items and costs, and applies categories to them. This is the first step toward automating budgeting and spending tracking.

## Features

### 📱 **Web Interface**
- **Streamlit-powered** - Simple, beginner-friendly web interface
- **Mobile responsive** - Works seamlessly on phones and tablets
- **Drag & drop upload** - Easy receipt image upload
- **Real-time processing** - Instant OCR results and categorization

### 🔍 **OCR Processing**
- **Tesseract OCR** - Robust text extraction from receipt images
- **Image preprocessing** - Automatic contrast and sharpness enhancement
- **Smart parsing** - Intelligent item and price detection
- **Multiple formats** - Support for PNG, JPG, JPEG, GIF, BMP

### 📊 **Data Management**
- **Local SQLite storage** - Secure local data storage
- **Google Sheets integration** - Cloud backup and sharing (coming soon)
- **CSV export** - Easy data export for analysis
- **Automatic backups** - Regular data protection

### 🏷️ **Smart Categorization**
- **Auto-categorization** - Intelligent expense categorization
- **Custom categories** - Create and manage your own categories
- **Manual override** - Easy category correction
- **ML ready** - Prepared for future machine learning enhancements

## Quick Start

### Prerequisites

- **Python 3.8+** - Download from [python.org](https://python.org)
- **Tesseract OCR** - Required for text extraction

#### Installing Tesseract OCR

**Windows:**
1. Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH
3. Verify with: `tesseract --version`

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/samass/receipt-scanner.git
   cd receipt-scanner
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv receipt_scanner_env
   
   # Activate (Windows)
   receipt_scanner_env\Scripts\activate
   
   # Activate (macOS/Linux)
   source receipt_scanner_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in the terminal

## Usage Guide

### 📤 **Uploading Receipts**

1. **Navigate to the "Upload & Scan" tab**
2. **Upload your receipt image** by:
   - Dragging and dropping the file
   - Clicking "Browse files" to select
   - Using copy & paste (in supported browsers)
3. **Wait for processing** - OCR will extract text automatically
4. **Review and edit** detected items and prices
5. **Assign categories** to each item
6. **Save the receipt** to your database

### 📊 **Viewing Data**

1. **Go to the "View Data" tab**
2. **See summary statistics** - Total receipts, amount spent, averages
3. **Browse recent receipts** - Expandable list with item details
4. **Export data** - Download CSV for external analysis

### 🏷️ **Managing Categories**

1. **Visit the "Categories" tab**
2. **View current categories** - See all available expense categories
3. **Add new categories** - Create custom categories for your needs
4. **Remove categories** - Delete unused categories (items move to "Other")

### ⚙️ **Settings**

1. **Access the "Settings" tab**
2. **Choose storage method** - Local SQLite, Google Sheets (coming soon), or both
3. **Configure OCR** - Set language and processing options
4. **Export data** - Download your complete receipt database

## Project Structure

```
receipt-scanner/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore rules
├── config/              # Configuration files
│   └── app_config.yaml  # Application settings (auto-generated)
├── src/                 # Core application modules
│   ├── __init__.py      # Package initialization
│   ├── config.py        # Configuration management
│   ├── ocr_processor.py # OCR processing logic
│   ├── data_storage.py  # Database operations
│   └── categories.py    # Category management
├── sample_data/         # Sample receipts and examples
├── docs/                # Documentation
├── tests/               # Unit tests
└── logs/                # Application logs (auto-generated)
```

## Configuration

The application uses a YAML configuration file located at `config/app_config.yaml`. This file is automatically created with default settings on first run.

### Environment Variables

You can override configuration settings using environment variables:

```bash
# OCR Settings
export OCR_LANGUAGE=eng
export OCR_CONFIDENCE_THRESHOLD=60.0

# Storage Settings
export DATABASE_PATH=receipt_data.sqlite3
export GOOGLE_SHEETS_ENABLED=false

# UI Settings
export UI_THEME=light
export MAX_FILE_SIZE_MB=10
```

### Configuration Sections

- **OCR**: Language, confidence thresholds, preprocessing options
- **Storage**: Database paths, Google Sheets integration, backup settings
- **UI**: Theme, file size limits, supported formats
- **Categories**: Auto-categorization settings, ML options (future)

## Tips for Better Results

### 📸 **Taking Receipt Photos**

- **Good lighting** - Avoid shadows and dark areas
- **Flat surface** - Keep receipt as flat as possible
- **Avoid glare** - Position to minimize reflections
- **High resolution** - Use your camera's highest quality setting
- **Straight angle** - Take photo directly above receipt
- **Full receipt** - Ensure all text is visible in frame

### 🏷️ **Category Management**

- **Use specific categories** - "Grocery Store" vs "Shopping"
- **Be consistent** - Use the same category names over time
- **Review suggestions** - Check auto-categorization results
- **Create subcategories** - Use detailed categories for better tracking

### 📊 **Data Analysis**

- **Export regularly** - Download CSV for backup and analysis
- **Review monthly** - Check spending patterns and categories
- **Clean data** - Remove or fix incorrectly categorized items
- **Track trends** - Use exported data in spreadsheet applications

## Troubleshooting

### Common Issues

**OCR Not Working:**
- Verify Tesseract is installed: `tesseract --version`
- Check image quality and lighting
- Try different image formats
- Ensure image is not too small or large

**App Won't Start:**
- Check Python version: `python --version` (requires 3.8+)
- Verify all dependencies: `pip install -r requirements.txt`
- Check for port conflicts (default: 8501)

**Poor Text Recognition:**
- Improve image quality (lighting, focus, resolution)
- Ensure receipt is flat and fully visible
- Try preprocessing the image manually
- Check OCR language settings

**Categories Not Saving:**
- Check database permissions
- Verify disk space
- Look for error messages in logs
- Try restarting the application

### Getting Help

1. **Check the logs** - Look in the `logs/` directory for error messages
2. **Review configuration** - Ensure `config/app_config.yaml` is correct
3. **Test components** - Try uploading different receipt images
4. **Check dependencies** - Verify all required packages are installed

## Future Enhancements

### 🤖 **Machine Learning**
- **Automatic categorization** - ML-based expense classification
- **Receipt type detection** - Identify store types automatically
- **Fraud detection** - Identify unusual spending patterns
- **Smart suggestions** - Personalized category recommendations

### 📱 **Mobile Development**
- **Native mobile app** - iOS and Android applications
- **Camera integration** - Direct photo capture within app
- **Offline processing** - Work without internet connection
- **Cloud sync** - Seamless data synchronization

### 🔗 **Integrations**
- **Banking APIs** - Direct transaction import
- **Accounting software** - QuickBooks, YNAB, Mint integration
- **Cloud storage** - Dropbox, Google Drive, OneDrive backup
- **Expense reporting** - Business expense automation

## Contributing

We welcome contributions! Here's how you can help:

1. **Report bugs** - Use the issue tracker for bug reports
2. **Suggest features** - Share ideas for new functionality
3. **Submit code** - Fork, improve, and submit pull requests
4. **Improve documentation** - Help make instructions clearer
5. **Test the application** - Try different receipt types and scenarios

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run existing tests: `pytest tests/`
6. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and request features via GitHub Issues
- **Community**: Join discussions and get help from other users

---

**Made with ❤️ for easier expense tracking**

*Transform your receipts into organized expense data with just a photo!*