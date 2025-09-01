# Example Sample Receipt Data

# This file contains example data structures for testing and development

sample_receipt_text = """
GROCERY STORE ABC
123 Main Street
Anytown, ST 12345
(555) 123-4567

Date: 2023-12-01
Time: 14:30
Cashier: Jane D.

MILK 2% GALLON      3.99
BREAD WHOLE WHEAT   2.49
EGGS LARGE DOZEN    2.89
BANANAS            1.99
CHICKEN BREAST     8.99
PASTA SAUCE        1.79
CHEESE SLICED      4.99
YOGURT GREEK       5.99

SUBTOTAL          32.12
TAX               2.25
TOTAL            34.37

PAYMENT METHOD: DEBIT CARD
CARD ENDING: ****1234

THANK YOU FOR SHOPPING!
"""

sample_parsed_items = [
    {
        "name": "Milk 2% Gallon",
        "price": 3.99,
        "category": "Groceries"
    },
    {
        "name": "Bread Whole Wheat", 
        "price": 2.49,
        "category": "Groceries"
    },
    {
        "name": "Eggs Large Dozen",
        "price": 2.89,
        "category": "Groceries" 
    },
    {
        "name": "Bananas",
        "price": 1.99,
        "category": "Groceries"
    },
    {
        "name": "Chicken Breast",
        "price": 8.99,
        "category": "Groceries"
    },
    {
        "name": "Pasta Sauce",
        "price": 1.79,
        "category": "Groceries"
    },
    {
        "name": "Cheese Sliced",
        "price": 4.99,
        "category": "Groceries"
    },
    {
        "name": "Yogurt Greek",
        "price": 5.99,
        "category": "Groceries"
    }
]

sample_restaurant_receipt = """
PIZZA PALACE
456 Food Court Ave
Tastyville, ST 12345

Order #: 1234
Table: 15
Server: Mike

LARGE PEPPERONI PIZZA    18.99
CAESAR SALAD             8.99
GARLIC BREAD             4.99
SOFT DRINKS (2)          5.98

SUBTOTAL               38.95
TAX                     2.73
TIP (18%)               7.00
TOTAL                  48.68

THANK YOU!
"""

sample_gas_receipt = """
QUICK FILL STATION
789 Highway Blvd
Roadtown, ST 12345

Date: 2023-12-01
Time: 16:45

UNLEADED 87 OCTANE
Gallons: 12.456
Price/Gal: $3.299
Amount: $41.10

Payment: Credit Card
Card: ****5678

TOTAL: $41.10
"""

# Example category mappings for testing
category_test_cases = [
    {"item": "milk", "store": "walmart", "expected": "Groceries"},
    {"item": "pizza", "store": "pizza palace", "expected": "Dining"},
    {"item": "gasoline", "store": "shell", "expected": "Transportation"},
    {"item": "movie ticket", "store": "cinema", "expected": "Entertainment"},
    {"item": "prescription", "store": "cvs", "expected": "Healthcare"},
    {"item": "shampoo", "store": "salon", "expected": "Personal Care"},
    {"item": "hammer", "store": "home depot", "expected": "Home & Garden"},
    {"item": "textbook", "store": "bookstore", "expected": "Education"},
    {"item": "random item", "store": "unknown", "expected": "Other"}
]