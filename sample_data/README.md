# Sample Receipt Data

This directory contains sample receipt images and example data for testing the Receipt Scanner application.

## Sample Images

The `images/` directory contains example receipt images you can use to test the OCR functionality:

- `grocery_receipt.jpg` - Typical grocery store receipt
- `restaurant_receipt.jpg` - Restaurant bill
- `gas_station_receipt.jpg` - Fuel purchase receipt
- `pharmacy_receipt.jpg` - Pharmacy/drugstore receipt

## Example Categories

The following categories are included by default:

- **Groceries** - Food and household items
- **Entertainment** - Movies, games, leisure activities  
- **Utilities** - Electricity, water, gas, internet
- **Transportation** - Gas, public transit, parking
- **Healthcare** - Medical expenses, pharmacy
- **Dining** - Restaurants and takeout
- **Shopping** - Clothing, electronics, misc items
- **Education** - Books, courses, school supplies
- **Home & Garden** - Home improvement, gardening
- **Personal Care** - Beauty, hygiene products
- **Other** - Miscellaneous expenses

## Testing Tips

1. Start with the sample images to test OCR functionality
2. Try different image qualities and formats
3. Test the categorization suggestions
4. Experiment with adding custom categories
5. Practice exporting data to CSV

## Adding Your Own Samples

To add your own receipt images:

1. Place image files in the `images/` directory
2. Use supported formats: PNG, JPG, JPEG, GIF, BMP
3. Ensure good image quality for best OCR results
4. Consider adding a description file for each image

## Image Quality Guidelines

For best OCR results, sample images should have:

- Good lighting and contrast
- Minimal shadows or glare  
- Sharp, clear text
- Receipt laid flat
- High enough resolution (at least 800x600)
- Complete receipt visible in frame