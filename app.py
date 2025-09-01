"""
Receipt Scanner - Main Application
A web-based tool for scanning receipts, extracting text, and categorizing expenses.

This is the main Streamlit application that provides the user interface for:
- Uploading receipt images
- Displaying extracted text and items
- Manual category assignment
- Data storage options

Author: Receipt Scanner Project
License: GPL-3.0
"""

import streamlit as st
import logging
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.ocr_processor import OCRProcessor
    from src.data_storage import DataStorage
    from src.categories import CategoryManager
    from src.config import Config
    OCR_AVAILABLE = True
except ImportError as e:
    # Try importing just the basic modules
    try:
        from src.data_storage import DataStorage
        from src.categories import CategoryManager
        from src.config import Config
        OCRProcessor = None
        OCR_AVAILABLE = False
        st.error(f"OCR functionality not available: {e}")
        st.error("Please install OCR dependencies: pip install pytesseract opencv-python Pillow")
    except ImportError as e2:
        st.error(f"Core modules not available: {e2}")
        st.error("Please ensure all required modules are available in the src/ directory")
        st.stop()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/receipt_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_page_config():
    """Configure Streamlit page settings for mobile responsiveness"""
    st.set_page_config(
        page_title="Receipt Scanner",
        page_icon="🧾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for mobile responsiveness
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .stFileUploader > div > div > div > div {
        text-align: center;
    }
    
    .uploadedFile {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_components():
    """Initialize all application components"""
    try:
        config = Config()
        data_storage = DataStorage(config)
        category_manager = CategoryManager(config)
        
        if OCR_AVAILABLE:
            ocr_processor = OCRProcessor(config)
        else:
            ocr_processor = None
            st.warning("⚠️ OCR functionality is not available. Please install OCR dependencies to process receipt images.")
        
        return config, ocr_processor, data_storage, category_manager
    except Exception as e:
        st.error(f"Failed to initialize components: {e}")
        logger.error(f"Component initialization failed: {e}")
        return None, None, None, None

def display_header():
    """Display application header and navigation"""
    st.title("🧾 Receipt Scanner")
    st.markdown("**Transform your receipts into organized expense data**")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Scan", "📊 View Data", "🏷️ Categories", "⚙️ Settings"])
    
    return tab1, tab2, tab3, tab4

def handle_file_upload(ocr_processor, category_manager, data_storage):
    """Handle receipt image upload and processing"""
    st.subheader("Upload Receipt Image")
    
    if not ocr_processor:
        st.error("OCR functionality is not available. Please install required dependencies:")
        st.code("pip install pytesseract opencv-python Pillow")
        st.info("You can still use other features like category management and data viewing.")
        return
    
    # Multiple upload options
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose receipt image",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="Drag and drop or click to select your receipt image"
        )
    
    with col2:
        st.markdown("**Tips for better results:**")
        st.markdown("- Ensure good lighting")
        st.markdown("- Keep receipt flat")
        st.markdown("- Avoid shadows and glare")
        st.markdown("- Higher resolution is better")
    
    if uploaded_file is not None:
        try:
            # Display uploaded image
            st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)
            
            # Process the image
            with st.spinner("Processing receipt..."):
                result = ocr_processor.process_image(uploaded_file)
            
            if result:
                display_extraction_results(result, category_manager, data_storage)
            else:
                st.error("Failed to process the receipt. Please try a different image.")
                
        except Exception as e:
            st.error(f"Error processing upload: {e}")
            logger.error(f"Upload processing error: {e}")

def display_extraction_results(result, category_manager, data_storage):
    """Display OCR extraction results and allow categorization"""
    st.subheader("Extraction Results")
    
    # Display raw text
    with st.expander("Raw Extracted Text", expanded=False):
        st.text_area("Full Text", value=result.get('raw_text', ''), height=150, disabled=True)
    
    # Display parsed items
    items = result.get('items', [])
    if items:
        st.subheader("Detected Items")
        
        # Create a form for categorization
        with st.form("categorize_items"):
            categorized_items = []
            
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns([3, 1, 2])
                
                with col1:
                    item_name = st.text_input(f"Item {i+1}", value=item.get('name', ''), key=f"item_{i}")
                
                with col2:
                    price = st.number_input(f"Price", value=item.get('price', 0.0), key=f"price_{i}")
                
                with col3:
                    categories = category_manager.get_categories()
                    category = st.selectbox(
                        f"Category", 
                        options=categories,
                        key=f"category_{i}"
                    )
                
                categorized_items.append({
                    'name': item_name,
                    'price': price,
                    'category': category
                })
            
            # Save button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button("💾 Save Receipt", use_container_width=True):
                    save_receipt_data(categorized_items, result, data_storage)
    else:
        st.warning("No items were detected in this receipt. You may need to adjust the image quality or try manual entry.")

def save_receipt_data(items, raw_result, data_storage):
    """Save processed receipt data"""
    try:
        receipt_data = {
            'items': items,
            'raw_text': raw_result.get('raw_text', ''),
            'total_amount': sum(item['price'] for item in items),
            'timestamp': None  # Will be set by data_storage
        }
        
        receipt_id = data_storage.save_receipt(receipt_data)
        
        if receipt_id:
            st.success(f"✅ Receipt saved successfully! (ID: {receipt_id})")
            logger.info(f"Receipt saved with ID: {receipt_id}")
        else:
            st.error("Failed to save receipt data")
            
    except Exception as e:
        st.error(f"Error saving receipt: {e}")
        logger.error(f"Receipt save error: {e}")

def display_data_view(data_storage):
    """Display saved receipt data"""
    st.subheader("📊 Your Receipt Data")
    
    try:
        receipts = data_storage.get_all_receipts()
        
        if receipts:
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Receipts", len(receipts))
            
            with col2:
                total_spent = sum(receipt.get('total_amount', 0) for receipt in receipts)
                st.metric("Total Spent", f"${total_spent:.2f}")
            
            with col3:
                avg_spent = total_spent / len(receipts) if receipts else 0
                st.metric("Average per Receipt", f"${avg_spent:.2f}")
            
            # Display receipts table
            st.subheader("Recent Receipts")
            for receipt in receipts[-10:]:  # Show last 10 receipts
                with st.expander(f"Receipt {receipt.get('id', 'Unknown')} - ${receipt.get('total_amount', 0):.2f}"):
                    items = receipt.get('items', [])
                    for item in items:
                        st.write(f"• {item.get('name', 'Unknown')} - ${item.get('price', 0):.2f} ({item.get('category', 'Uncategorized')})")
        else:
            st.info("No receipts saved yet. Upload and scan your first receipt!")
            
    except Exception as e:
        st.error(f"Error loading receipt data: {e}")
        logger.error(f"Data view error: {e}")

def display_category_management(category_manager):
    """Display category management interface"""
    st.subheader("🏷️ Manage Categories")
    
    try:
        categories = category_manager.get_categories()
        
        # Display current categories
        st.write("**Current Categories:**")
        for category in categories:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {category}")
            with col2:
                if st.button("🗑️", key=f"delete_{category}"):
                    category_manager.remove_category(category)
                    st.rerun()
        
        # Add new category
        st.subheader("Add New Category")
        new_category = st.text_input("Category Name")
        if st.button("Add Category") and new_category:
            category_manager.add_category(new_category)
            st.success(f"Added category: {new_category}")
            st.rerun()
            
    except Exception as e:
        st.error(f"Error managing categories: {e}")
        logger.error(f"Category management error: {e}")

def display_settings(config, data_storage):
    """Display application settings"""
    st.subheader("⚙️ Settings")
    
    # Storage options
    st.write("**Data Storage Options:**")
    
    storage_type = st.radio(
        "Choose storage method:",
        ["Local SQLite", "Google Sheets", "Both"],
        help="Select how you want to store your receipt data"
    )
    
    if storage_type in ["Google Sheets", "Both"]:
        st.write("**Google Sheets Configuration:**")
        
        sheets_key = st.text_input(
            "Google Sheets Key",
            help="Enter your Google Sheets API key or upload credentials file"
        )
        
        if st.button("Test Google Sheets Connection"):
            # This would test the connection
            st.info("Google Sheets integration coming soon!")
    
    # OCR Settings
    st.write("**OCR Settings:**")
    
    ocr_language = st.selectbox(
        "OCR Language",
        ["eng", "spa", "fra", "deu"],
        help="Select the primary language for OCR processing"
    )
    
    # Export options
    st.write("**Export Data:**")
    if st.button("📥 Export to CSV"):
        try:
            csv_data = data_storage.export_to_csv()
            if csv_data:
                st.download_button(
                    "Download CSV",
                    csv_data,
                    "receipts.csv",
                    "text/csv"
                )
        except Exception as e:
            st.error(f"Export failed: {e}")

def main():
    """Main application entry point"""
    # Ensure log directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Setup page configuration
    setup_page_config()
    
    # Initialize components
    config, ocr_processor, data_storage, category_manager = initialize_components()
    
    if not all([config, ocr_processor, data_storage, category_manager]):
        st.error("Failed to initialize application components. Please check your configuration.")
        return
    
    # Display header and get tabs
    tab1, tab2, tab3, tab4 = display_header()
    
    # Handle each tab
    with tab1:
        handle_file_upload(ocr_processor, category_manager, data_storage)
    
    with tab2:
        display_data_view(data_storage)
    
    with tab3:
        display_category_management(category_manager)
    
    with tab4:
        display_settings(config, data_storage)

if __name__ == "__main__":
    main()