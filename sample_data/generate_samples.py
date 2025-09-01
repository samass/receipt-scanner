"""
Sample Receipt Generator

This script creates text-based sample receipts for testing the OCR functionality
when real receipt images aren't available.

Usage: python generate_samples.py
"""

import os
from pathlib import Path

def create_sample_receipt_texts():
    """Create sample receipt text files for testing"""
    
    sample_receipts = {
        "grocery_receipt.txt": """
FRESH MART GROCERY
123 Main Street
Springfield, IL 62701
(217) 555-0123

Date: 12/01/2023    Time: 2:30 PM
Cashier: Sarah M.    Register: 3

MILK 2% GALLON         3.99
BREAD WHOLE WHEAT      2.49
EGGS LARGE DOZEN       2.89
BANANAS LB            1.99
CHICKEN BREAST LB      8.99
PASTA SAUCE           1.79
CHEESE SLICED         4.99
YOGURT GREEK          5.99
APPLES HONEYCRISP     3.49
CEREAL CHEERIOS       4.99

SUBTOTAL             41.60
TAX (8.25%)           3.43
TOTAL               45.03

DEBIT CARD ****1234
APPROVED

THANK YOU FOR SHOPPING!
Visit us online: freshmartgrocery.com
        """,
        
        "restaurant_receipt.txt": """
LUIGI'S ITALIAN RESTAURANT
456 Oak Avenue
Chicago, IL 60614
(312) 555-0199

Table: 12    Server: Marco
Date: 12/01/2023    Time: 7:45 PM

CHICKEN PARMESAN      18.99
CAESAR SALAD           8.99
GARLIC BREAD           4.99
SPAGHETTI MARINARA    14.99
TIRAMISU               6.99
SOFT DRINKS (2)        5.98

SUBTOTAL             59.93
TAX                   4.79
TIP (18%)            10.79
TOTAL                75.51

CREDIT CARD ****5678
APPROVED

Grazie! Come back soon!
        """,
        
        "gas_station_receipt.txt": """
SPEEDWAY #1234
789 Highway 55
Bloomington, IL 61701
(309) 555-0156

Date: 12/01/2023
Time: 4:15 PM

UNLEADED 87 OCTANE
Gallons: 12.456
Price/Gal: $3.299
Fuel Total: $41.10

ENERGY DRINK           2.99
CHIPS                  1.99
CANDY BAR              1.49

MERCHANDISE TOTAL:     6.47
FUEL TOTAL:           41.10
TOTAL:                47.57

DEBIT CARD ****9012
APPROVED

THANK YOU!
        """,
        
        "pharmacy_receipt.txt": """
HEALTH PLUS PHARMACY
321 Medical Center Dr
Peoria, IL 61602
(309) 555-0287

Date: 12/01/2023    Time: 11:30 AM
Pharmacist: Dr. Johnson

PRESCRIPTION #RX123456
IBUPROFEN 200MG       12.99
VITAMINS DAILY        19.99
BANDAGES              5.99
THERMOMETER          14.99
COUGH DROPS           3.99

SUBTOTAL             57.95
TAX                   4.64
TOTAL                62.59

INSURANCE COPAY:      10.00
PATIENT PAYS:         52.59

CREDIT CARD ****3456
APPROVED

Get well soon!
        """,
        
        "coffee_shop_receipt.txt": """
BREW & BEANS COFFEE
159 University Ave
Champaign, IL 61820
(217) 555-0344

Date: 12/01/2023    Time: 8:15 AM
Barista: Alex

LARGE LATTE            4.99
BLUEBERRY MUFFIN       3.49
LARGE AMERICANO        3.99
CROISSANT             2.99

SUBTOTAL             15.46
TAX                   1.24
TIP                   3.00
TOTAL                19.70

MOBILE PAY ****7890
APPROVED

Thanks for choosing Brew & Beans!
Free WiFi: BrewGuest / Password: coffee123
        """,
        
        "hardware_store_receipt.txt": """
BUILDER'S SUPPLY
987 Industrial Blvd
Rockford, IL 61108
(815) 555-0433

Date: 12/01/2023    Time: 10:45 AM
Associate: Mike T.

HAMMER 16OZ           19.99
SCREWS 1" (50 pack)    8.99
PAINT BRUSH SET       12.99
EXTENSION CORD 25FT   24.99
WORK GLOVES           9.99
DUCT TAPE             5.99

SUBTOTAL             82.94
TAX (7.5%)            6.22
TOTAL                89.16

CASH PAYMENT         90.00
CHANGE               0.84

Thank you for your business!
Pro contractor discount available
        """
    }
    
    # Create sample_data/images directory
    sample_dir = Path("sample_data/images")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # Write sample receipt text files
    for filename, content in sample_receipts.items():
        file_path = sample_dir / filename
        with open(file_path, 'w') as f:
            f.write(content.strip())
        print(f"Created: {file_path}")
    
    print(f"\nCreated {len(sample_receipts)} sample receipt text files in {sample_dir}")

def create_sample_instructions():
    """Create instructions for adding real receipt images"""
    
    instructions = """
# Adding Real Receipt Images

To test the OCR functionality with actual receipt images:

## Supported Formats
- PNG (recommended for scanned receipts)
- JPG/JPEG (good for photos)
- GIF, BMP (also supported)

## Image Quality Tips
1. **Lighting**: Use bright, even lighting
2. **Angle**: Take photo straight-on, not at an angle
3. **Focus**: Ensure text is sharp and clear
4. **Size**: Minimum 800x600 pixels recommended
5. **Contrast**: Good contrast between text and background

## Sample Image Names
Place your real receipt images in this directory with descriptive names:
- `grocery_walmart_20231201.jpg`
- `restaurant_dinner_20231201.jpg` 
- `gas_shell_station_20231201.jpg`
- `pharmacy_cvs_20231201.jpg`
- `coffee_starbucks_20231201.jpg`

## Testing Process
1. Add image files to this directory
2. Run the Receipt Scanner application
3. Upload images via the web interface
4. Review OCR accuracy and categorization
5. Adjust categories as needed

## Image Sources
- Take photos of your own receipts
- Use a scanner for best quality
- Ensure receipts are flat (no wrinkles)
- Clean any dirt or stains before scanning

## Privacy Note
Sample receipt images should not contain real personal information like:
- Full credit card numbers
- Personal addresses
- Phone numbers
- Real names

Use test receipts or blur sensitive information before adding to samples.
    """
    
    instructions_path = Path("sample_data/images/README.md")
    with open(instructions_path, 'w') as f:
        f.write(instructions.strip())
    
    print(f"Created image instructions: {instructions_path}")

if __name__ == "__main__":
    print("🧾 Creating sample receipt data...")
    
    create_sample_receipt_texts()
    create_sample_instructions()
    
    print("\n✅ Sample data creation complete!")
    print("\n📋 Next steps:")
    print("1. Add real receipt images to sample_data/images/")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application: python run.py")
    print("4. Test OCR with your sample images")