#!/usr/bin/env python3
"""
Run script for Receipt Scanner application

This script provides easy startup options for the Receipt Scanner.
Run with: python run.py

Author: Receipt Scanner Project
License: GPL-3.0
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import pytesseract
        import PIL
        import cv2
        import pandas
        import numpy
        
        print("✅ All Python dependencies are available")
        
        # Check Tesseract OCR
        try:
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Tesseract OCR is installed: {result.stdout.split()[1]}")
            else:
                print("❌ Tesseract OCR is not properly installed")
                return False
        except FileNotFoundError:
            print("❌ Tesseract OCR is not installed or not in PATH")
            print("Please install Tesseract OCR:")
            print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            print("  macOS: brew install tesseract")
            print("  Ubuntu/Debian: sudo apt install tesseract-ocr")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['logs', 'config', 'sample_data/images']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created")

def run_application():
    """Run the Streamlit application"""
    try:
        print("🚀 Starting Receipt Scanner...")
        print("📱 The application will open in your default web browser")
        print("🌐 URL: http://localhost:8501")
        print("\n💡 Tips:")
        print("   - Use Ctrl+C to stop the application")
        print("   - Upload receipt images in the 'Upload & Scan' tab")
        print("   - Check sample_data/ for example images")
        print("\n" + "="*50)
        
        # Run Streamlit app
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.address', 'localhost',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")

def main():
    """Main entry point"""
    print("🧾 Receipt Scanner - Starting Up")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ app.py not found. Please run this script from the receipt-scanner directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing components.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Run application
    run_application()

if __name__ == "__main__":
    main()