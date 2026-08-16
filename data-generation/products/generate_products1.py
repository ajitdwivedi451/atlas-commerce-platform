import pandas as pd
import random
from faker import Faker
import os

fake = Faker()

NUM_PRODUCTS = 10_000

# ============================================================
# 1. MEGA PRODUCT CATALOG (Ultra-Realistic)
# ============================================================
catalog = {
    "Electronics": {
        "Mobile Phones": ["Apple", "Samsung", "Google", "OnePlus", "Xiaomi", "Motorola"],
        "Laptops": ["Apple", "Dell", "HP", "Lenovo", "Asus", "Acer", "MSI"],
        "Headphones & Audio": ["Sony", "JBL", "Bose", "Sennheiser", "Boat", "Skullcandy", "Marshall"],
        "Televisions": ["Samsung", "LG", "Sony", "TCL", "Hisense", "Panasonic"],
        "Cameras & Photography": ["Canon", "Nikon", "Sony", "Fujifilm", "GoPro", "DJI"],
        "Wearables & Smartwatches": ["Apple", "Garmin", "Samsung", "Fitbit", "Fossil", "Amazfit"],
        "Tablets": ["Apple", "Samsung", "Lenovo", "Microsoft"],
        "Gaming Consoles": ["Sony (PlayStation)", "Microsoft (Xbox)", "Nintendo", "Valve"]
    },

    "Fashion": {
        "Men Clothing": ["Levis", "Nike", "Adidas", "Puma", "Tommy Hilfiger", "Calvin Klein", "Raymond", "Allen Solly"],
        "Women Clothing": ["Zara", "H&M", "Nike", "Vero Moda", "Biba", "FabIndia", "Mango"],
        "Kids Clothing": ["Mothercare", "H&M Kids", "Gini & Jony", "United Colors of Benetton"],
        "Footwear": ["Nike", "Adidas", "Puma", "Reebok", "Skechers", "Bata", "Woodland", "Crocs"],
        "Watches": ["Casio", "Fossil", "Titan", "Seiko", "Rolex", "Tissot", "Fastrack"],
        "Bags & Luggage": ["Samsonite", "American Tourister", "Wildcraft", "Safari", "Tommy Hilfiger"],
        "Accessories": ["Ray-Ban", "Oakley", "Gucci", "Prada", "Fastrack"]
    },

    "Home & Kitchen": {
        "Furniture": ["IKEA", "HomeCentre", "Urban Ladder", "Pepperfry", "Wakefit"],
        "Kitchen Appliances": ["Philips", "LG", "Samsung", "Bosch", "Whirlpool", "Bajaj", "Morphy Richards"],
        "Cookware": ["Prestige", "Hawkins", "Wonderchef", "Pigeon", "Meyer"],
        "Home Decor": ["IKEA", "HomeCentre", "D'Decor", "Chumbak"],
        "Bedding & Linens": ["Bombay Dyeing", "Spaces", "Trident", "Portico"],
        "Cleaning Supplies": ["Dyson", "Eureka Forbes", "Scotch-Brite", "Colin"]
    },

    "Beauty & Personal Care": {
        "Skincare": ["L'Oreal", "Nivea", "The Ordinary", "Cetaphil", "Clinique", "Garnier", "Plum"],
        "Haircare": ["L'Oreal", "Dove", "Tresemme", "Pantene", "Head & Shoulders", "Moroccanoil"],
        "Makeup": ["MAC", "Maybelline", "Lakme", "Sugar", "Colorbar", "Huda Beauty", "NYX"],
        "Fragrance": ["Dior", "Chanel", "Versace", "Calvin Klein", "Davidoff", "Titan Skinn"],
        "Mens Grooming": ["Gillette", "Philips", "Bombay Shaving Company", "Beardo", "Old Spice"]
    },

    "Sports & Outdoors": {
        "Running & Training": ["Nike", "Adidas", "Asics", "Puma", "Under Armour"],
        "Fitness Equipment": ["Decathlon", "Cultsport", "Lifelong", "PowerMax"],
        "Outdoor & Camping": ["The North Face", "Columbia", "Decathlon", "Quechua", "Wildcraft"],
        "Sports Equipment": ["Wilson", "Yonex", "Spalding", "SG", "Kookaburra", "Nivia"],
        "Cycling": ["Firefox", "Hero Cycles", "Hercules", "Trek", "Decathlon Btwin"]
    },

    "Automotive": {
        "Car Accessories": ["3M", "Bosch", "Pioneer", "JBL", "Michelin"],
        "Bike Accessories": ["Studds", "Vega", "Steelbird", "Motul", "Yamaha"],
        "Tires": ["MRF", "CEAT", "Michelin", "Apollo", "Bridgestone"]
    },

    "Grocery & Gourmet": {
        "Snacks & Sweets": ["Haldiram's", "Lays", "Doritos", "Cadbury", "Ferrero Rocher", "Lindt"],
        "Beverages": ["Coca-Cola", "Pepsi", "Red Bull", "Nescafe", "Bru", "Tata Tea", "Taj Mahal"],
        "Staples & Spices": ["Aashirvaad", "India Gate", "Tata Sampann", "Everest", "MDH", "Catch"]
    },

    "Books & Stationery": {
        "Fiction Books": ["Penguin", "HarperCollins", "Random House", "Bloomsbury"],
        "Non-Fiction Books": ["Pearson", "McGraw Hill", "Oxford", "Wiley"],
        "Office Stationery": ["Classmate", "Parker", "Faber-Castell", "Cello", "Reynolds", "Camlin"]
    },
    
    "Toys & Games": {
        "Action Figures": ["Hasbro", "Mattel", "Funko", "Bandai"],
        "Board Games": ["Funskool", "Mattel", "Hasbro Gaming"],
        "Educational Toys": ["LEGO", "Fisher-Price", "Melissa & Doug", "Hot Wheels"]
    }
}



# ============================================================
# 2. MARKET, CURRENCY & EXCHANGE RATES
# ============================================================
markets = {
    "India": "INR",
    "United States": "USD",
    "United Kingdom": "GBP",
    "France": "EUR",
    "Australia": "AUD",
    "Singapore": "SGD",
    "United Arab Emirates": "AED",
    "Japan": "JPY"
}

# Base price USD mein generate hoga, phir is multiplier se multiply hoga
currency_multipliers = {
    "USD": 1.0, "GBP": 0.79, "EUR": 0.92, 
    "AUD": 1.52, "SGD": 1.34, "AED": 3.67, 
    "INR": 83.0, "JPY": 150.0
}

# ============================================================
# 3. BASE PRICE RANGES (In USD) & ATTRIBUTES
# ============================================================
price_ranges = {
    "Electronics": (100, 2500),
    "Fashion": (20, 300),
    "Home & Kitchen": (50, 1500),
    "Beauty & Personal Care": (10, 150),  # Name exact match karna chahiye catalog se
    "Sports & Outdoors": (15, 500),       # Name exact match karna chahiye
    "Automotive": (20, 1000),
    "Grocery & Gourmet": (2, 50),
    "Books & Stationery": (5, 100),
    "Toys & Games": (10, 250)
}

colors = ["Black", "White", "Silver", "Blue", "Red", "Gold", "Grey"]
suffixes = ["Pro", "Max", "Ultra", "Lite", "Plus", "Edition", "Series", "V2", "Essential"]
product_statuses = ["Active", "Inactive", "Discontinued", "Coming Soon"]

products = []

print("🚀 Generating ultra-realistic Product Catalog...")

# ============================================================
# 4. GENERATE PRODUCTS
# ============================================================
for i in range(1, NUM_PRODUCTS + 1):
    category = random.choice(list(catalog.keys()))
    subcategory = random.choice(list(catalog[category].keys()))
    brand = random.choice(catalog[category][subcategory])
    market = random.choice(list(markets.keys()))
    currency = markets[market]

    # 🎯 REALISTIC PRICING LOGIC
    min_price, max_price = price_ranges[category]
    base_usd_price = random.uniform(min_price, max_price)
    
    # Currency conversion & rounding (Japan uses whole numbers, others use 2 decimals)
    converted_price = base_usd_price * currency_multipliers[currency]
    if currency in ["JPY", "INR"]:
        unit_price = round(converted_price, 0)
    else:
        unit_price = round(converted_price, 2)

    # Cost is normally 40-70% of selling price (Profit Margins)
    cost_price = round(unit_price * random.uniform(0.40, 0.70), 2)

    # 🎯 REALISTIC NAMES
    model_name = fake.word().capitalize()
    suffix = random.choice(suffixes) if random.random() > 0.5 else ""
    color = random.choice(colors)
    # E.g., "Apple Vision Pro Laptops - Silver"
    product_name = f"{brand} {model_name} {suffix} {subcategory} - {color}".replace("  ", " ").strip()

    # 🎯 ADDING WEIGHT FOR LOGISTICS
    if category == "Electronics": weight = round(random.uniform(0.1, 5.0), 2)
    elif category == "Home & Kitchen": weight = round(random.uniform(2.0, 45.0), 2)
    elif category == "Beauty": weight = round(random.uniform(0.05, 0.5), 2)
    else: weight = round(random.uniform(0.2, 2.0), 2)

    created_date = fake.date_between(start_date="-5y", end_date="today")
    launch_date = fake.date_between(start_date=created_date, end_date="today")

    products.append({
        "product_id": f"PROD{i:06d}",
        "product_name": product_name,
        "category": category,
        "subcategory": subcategory,
        "brand": brand,
        "market": market,
        "currency": currency,
        "unit_price": unit_price,
        "cost_price": cost_price,
        "weight_kg": weight,  # 👈 Naya column
        "supplier_id": f"SUP{random.randint(1, 500):04d}",
        "product_status": random.choice(product_statuses),
        "launch_date": launch_date,
        "rating": round(random.uniform(3.0, 5.0), 1), # Nobody buys 1.0 rating usually
        "stock_keeping_unit": f"SKU-{brand[:3].upper()}-{i:08d}", # Better SKU format
        "created_date": created_date
    })

print("😈 Injecting controlled data-quality issues...")

# ============================================================
# 5. DUPLICATE RECORDS & DIRTY DATA
# ============================================================
num_duplicates = int(NUM_PRODUCTS * random.uniform(0.01, 0.02))
products.extend(random.choices(products, k=num_duplicates))

for product in products:
    chance = random.random()
    if chance < 0.05:
        field = random.choice(["brand", "supplier_id", "rating",
            "launch_date",# NAYA: Launch date abhi decide nahi hui
            "weight_kg",     # NAYA: Warehouse ne weight update nahi kiya
            "cost_price"])
        product[field] = None
    elif 0.05 <= chance < 0.07:
        product["unit_price"] = random.choice([0, -10, -99.99])
    elif 0.07 <= chance < 0.09:
        product["rating"] = random.choice([0, 6.5, 9.9])
    elif 0.09 <= chance < 0.11:
        product["product_status"] = random.choice(["Unknown", "Pending_Approval", "Deleted"])

random.shuffle(products)
df = pd.DataFrame(products)

# ============================================================
# 6. SAVE PROPERLY
# ============================================================
# Tweak this to your actual path!
output_dir = r"D:\Projects\atlas-commerce-platform\data-generation\products"
os.makedirs(output_dir, exist_ok=True)
file_path = os.path.join(output_dir, "products_dirty1.csv")

df.to_csv(file_path, index=False)

print(f"✅ Product generation completed.")
print(f"Total records: {len(df)}")
print(df[['product_name', 'market', 'currency', 'unit_price', 'weight_kg']].head())