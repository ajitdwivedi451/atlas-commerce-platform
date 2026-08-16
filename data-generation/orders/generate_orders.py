import pandas as pd
import random
from faker import Faker

fake = Faker()

NUM_ORDERS = 50_000

CUSTOMER_FILE = "D:/Projects/atlas-commerce-platform/data-generation/customers/customers_dirty.csv"
PRODUCT_FILE = "D:/Projects/atlas-commerce-platform/data-generation/products/products_dirty.csv"
OUTPUT_FILE = "D:/Projects/atlas-commerce-platform/data-generation/orders/orders_dirty.csv"

# ============================================================
# 1. LOAD CUSTOMER AND PRODUCT MASTER IDS
# ============================================================

customers_df = pd.read_csv(CUSTOMER_FILE)
products_df = pd.read_csv(PRODUCT_FILE)

customer_ids = (
    customers_df["customer_id"]
    .dropna()
    .unique()
    .tolist()
)

product_ids = (
    products_df["product_id"]
    .dropna()
    .unique()
    .tolist()
)

print(f"Customers available: {len(customer_ids)}")
print(f"Products available: {len(product_ids)}")

# ============================================================
# 2. ORDER CONFIGURATION
# ============================================================

order_statuses = [
    "Pending",
    "Confirmed",
    "Shipped",
    "Delivered",
    "Cancelled",
    "Returned"
]

payment_statuses = [
    "Pending",
    "Paid",
    "Failed",
    "Refunded"
]

sales_channels = [
    "Website",
    "Mobile App",
    "Physical Store",
    "Marketplace"
]

countries = [
    "India",
    "United States",
    "United Kingdom",
    "France",
    "Australia",
    "Singapore",
    "United Arab Emirates",
    "Japan"
]

currencies = [
    "INR",
    "USD",
    "GBP",
    "EUR",
    "AUD",
    "SGD",
    "AED",
    "JPY"
]

orders = []

print("🚀 Generating Order Data...")

#Products ka actual price aur currency uthane ke liye
product_dict = products_df.set_index('product_id')[['unit_price', 'currency']].to_dict('index')
customer_dict = customers_df.set_index('customer_id')[['country', 'city', 'state']].to_dict('index')

# ============================================================
# 3. GENERATE ORDERS
# ============================================================

for i in range(1, NUM_ORDERS + 1):

    customer_id = random.choice(customer_ids)
    product_id = random.choice(product_ids)

    order_date = fake.date_between(
        start_date="-2y",
        end_date="today"
    )

    quantity = random.randint(1, 5)

    unit_price = product_dict[product_id]['unit_price']
    actual_currency = product_dict[product_id]['currency']

    subtotal = quantity * unit_price

    discount_amount = round(
        subtotal * random.uniform(0, 0.20),
        2
    )

    taxable_amount = subtotal - discount_amount

    tax_amount = round(
        taxable_amount * random.uniform(0.05, 0.20),
        2
    )

    shipping_amount = round(
        random.uniform(0, 50),
        2
    )

    total_amount = round(
        taxable_amount
        + tax_amount
        + shipping_amount,
        2
    )

    orders.append({
        "order_id": f"ORD{i:08d}",
        "customer_id": customer_id,
        "product_id": product_id,
        "order_date": order_date,
        "quantity": quantity,
        "unit_price": unit_price,
        "discount_amount": discount_amount,
        "tax_amount": tax_amount,
        "shipping_amount": shipping_amount,
        "total_amount": total_amount,
        "currency": actual_currency,
        "payment_status": random.choice(payment_statuses),
        "order_status": random.choice(order_statuses),
        "sales_channel": random.choice(sales_channels),
        "shipping_country": random.choice(countries)
    })

print("😈 Injecting controlled data-quality issues...")

# ============================================================
# 4. DUPLICATE ORDERS
# ============================================================

num_duplicates = int(
    NUM_ORDERS * random.uniform(0.01, 0.02)
)

duplicates = random.choices(
    orders,
    k=num_duplicates
)

orders.extend(duplicates)

# ============================================================
# 5. DIRTY DATA
# ============================================================

for order in orders:

    chance = random.random()

    # Missing optional shipping country
    if chance < 0.03:

        order["shipping_country"] = None

    # Invalid quantity
    elif chance < 0.05:

        order["quantity"] = random.choice([
            0,
            -1,
            -5
        ])

    # Invalid price
    elif chance < 0.07:

        order["unit_price"] = random.choice([
            0,
            -50,
            -100
        ])

    # Invalid order status
    elif chance < 0.09:

        order["order_status"] = random.choice([
            "Unknown",
            "Processing_Error",
            "Invalid"
        ])

    # Invalid payment status
    elif chance < 0.11:

        order["payment_status"] = random.choice([
            "Unknown",
            "Not_Processed"
        ])

    # Invalid customer reference
    elif chance < 0.12:

        order["customer_id"] = (
            f"CUST_INVALID_{random.randint(1, 1000)}"
        )

    # Invalid product reference
    elif chance < 0.13:

        order["product_id"] = (
            f"PROD_INVALID_{random.randint(1, 1000)}"
        )
    elif chance < 0.14:
        order["order_date"] = fake.date_between(start_date="+1y", end_date="+2y")


# ============================================================
# 6. SHUFFLE
# ============================================================

random.shuffle(orders)

# ============================================================
# 7. SAVE
# ============================================================

df = pd.DataFrame(orders)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("✅ Order Data Generation Complete!")
print(f"Total records: {len(df)}")
print(df.head())