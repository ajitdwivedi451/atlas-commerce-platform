import pandas as pd
import random
from faker import Faker

fake = Faker()

NUM_PRODUCTS = 10_000

categories = {
    "Electronics": [
        "Smartphones",
        "Laptops",
        "Headphones",
        "Televisions",
        "Cameras",
        "Accessories"
    ],
    "Fashion": [
        "Men Clothing",
        "Women Clothing",
        "Footwear",
        "Watches",
        "Bags"
    ],
    "Home & Kitchen": [
        "Furniture",
        "Kitchen Appliances",
        "Cookware",
        "Home Decor"
    ],
    "Beauty": [
        "Skincare",
        "Haircare",
        "Makeup",
        "Fragrance"
    ],
    "Sports": [
        "Fitness",
        "Running",
        "Outdoor",
        "Sports Equipment"
    ]
}

brands = [
    "Atlas",
    "Nova",
    "UrbanX",
    "TechPro",
    "Prime",
    "Velocity",
    "EverStyle",
    "HomeCraft",
    "Apex",
    "Zenith"
]

currencies = ["USD", "EUR", "GBP", "INR", "AED", "AUD"]

product_statuses = ["Active", "Inactive"]

products = []

print("🚀 Generating Base Product Data...")

# ==========================================
# 1. GENERATE CLEAN BASE DATA
# ==========================================

for i in range(1, NUM_PRODUCTS + 1):

    category = random.choice(list(categories.keys()))
    subcategory = random.choice(categories[category])
    brand = random.choice(brands)

    product_name = f"{brand} {fake.word().title()} {subcategory}"

    product = {
        "product_id": f"PROD{i:06d}",
        "product_name": product_name,
        "category": category,
        "subcategory": subcategory,
        "brand": brand,
        "unit_price": round(random.uniform(5, 5000), 2),
        "currency": random.choice(currencies),
        "supplier_id": f"SUP{random.randint(1, 1000):04d}",
        "product_status": random.choice(product_statuses),
        "launch_date": fake.date_between(
            start_date="-5y",
            end_date="today"
        ),
        "rating": round(random.uniform(1, 5), 1),
        "stock_keeping_unit": f"SKU-{i:08d}",
        "created_date": fake.date_between(
            start_date="-5y",
            end_date="today"
        )
    }

    products.append(product)


print("😈 Injecting Data Engineering Edge Cases...")

# ==========================================
# 2. DUPLICATE RECORDS
# ==========================================

num_duplicates = int(
    NUM_PRODUCTS * random.uniform(0.01, 0.02)
)

duplicates = random.choices(
    products,
    k=num_duplicates
)

products.extend(duplicates)

# ==========================================
# 3. DIRTY DATA INJECTION
# ==========================================

for product in products:

    chance = random.random()

    # A. Missing optional fields
    if chance < 0.05:

        field = random.choice([
            "brand",
            "supplier_id",
            "rating"
        ])

        product[field] = None

    # B. Invalid price
    elif 0.05 <= chance < 0.07:

        product["unit_price"] = random.choice([
            -10,
            -99.99,
            0
        ])

    # C. Invalid rating
    elif 0.07 <= chance < 0.09:

        product["rating"] = random.choice([
            0,
            6,
            7,
            10
        ])

    # D. Invalid business status
    elif 0.09 <= chance < 0.11:

        product["product_status"] = random.choice([
            "Pending",
            "Deleted",
            "Unknown"
        ])

    # E. Duplicate SKU
    elif 0.11 <= chance < 0.12:

        product["stock_keeping_unit"] = random.choice(
            products
        )["stock_keeping_unit"]

# ==========================================
# 4. SHUFFLE
# ==========================================

random.shuffle(products)

# ==========================================
# 5. CREATE DATAFRAME
# ==========================================

df = pd.DataFrame(products)

# ==========================================
# 6. SAVE
# ==========================================

df.to_csv(
    "D:/Projects/atlas-commerce-platform/data-generation/products/products_dirty.csv",
    index=False
)

print("✅ Product Data Generation Complete!")
print(f"Total records: {len(df)}")
print(df.head())