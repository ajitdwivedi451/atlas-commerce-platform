import pandas as pd
import random
import os
from faker import Faker

fake = Faker()

# ============================================================
# 1. FILE PATHS
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

CUSTOMER_FILE = os.path.join(
    BASE_DIR, "customers", "customers.csv"
)

PRODUCT_FILE = os.path.join(
    BASE_DIR, "products", "products.csv"
)

ADDRESS_FILE = os.path.join(
    BASE_DIR, "customer_addresses",
    "customer_addresses.csv"
)

PAYMENT_METHOD_FILE = os.path.join(
    BASE_DIR, "customer_payment_methods",
    "customer_payment_methods.csv"
)

ORDERS_DIR = os.path.join(BASE_DIR, "orders")
ORDER_ITEMS_DIR = os.path.join(BASE_DIR, "order_items")

os.makedirs(ORDERS_DIR, exist_ok=True)
os.makedirs(ORDER_ITEMS_DIR, exist_ok=True)


# ============================================================
# 2. LOAD EXISTING DATA
# ============================================================

customers = pd.read_csv(CUSTOMER_FILE)
products = pd.read_csv(PRODUCT_FILE)
addresses = pd.read_csv(ADDRESS_FILE)
payment_methods = pd.read_csv(PAYMENT_METHOD_FILE)

print("Datasets loaded successfully.")

# Remove duplicate customer IDs for relationship generation.
# Dirty duplicates remain in the original source.
customers = customers.drop_duplicates(
    subset=["customer_id"]
)

products = products.drop_duplicates(
    subset=["product_id"]
)

addresses = addresses.drop_duplicates(
    subset=["address_id"]
)

payment_methods = payment_methods.drop_duplicates(
    subset=["payment_method_id"]
)


# ============================================================
# 3. PRODUCT LOOKUP
# ============================================================

product_lookup = products.set_index("product_id").to_dict("index")


# ============================================================
# 4. CUSTOMER → ADDRESS LOOKUP
# ============================================================

customer_addresses = {}

for customer_id, group in addresses.groupby("customer_id"):

    valid_addresses = group[
        group["address_id"].notna()
    ]

    if len(valid_addresses) > 0:
        customer_addresses[customer_id] = (
            valid_addresses.to_dict("records")
        )


# ============================================================
# 5. CUSTOMER → PAYMENT METHOD LOOKUP
# ============================================================

customer_payment_methods = {}

for customer_id, group in payment_methods.groupby("customer_id"):

    valid_methods = group[
        group["payment_method_id"].notna()
    ]

    if len(valid_methods) > 0:
        customer_payment_methods[customer_id] = (
            valid_methods.to_dict("records")
        )


# ============================================================
# 6. GENERATION SETTINGS
# ============================================================

NUM_ORDERS = 25_000

order_statuses = [
    "Pending",
    "Confirmed",
    "Processing",
    "Shipped",
    "Delivered",
    "Cancelled",
    "Returned"
]

sales_channels = [
    "Website",
    "Mobile App",
    "Marketplace"
]

orders = []
order_items = []

order_item_counter = 1


# ============================================================
# 7. GENERATE ORDERS
# ============================================================

print("Generating Orders + Order Items...")

for order_number in range(1, NUM_ORDERS + 1):

    # --------------------------------------------------------
    # Select existing customer
    # --------------------------------------------------------

    customer = customers.sample(
        n=1
    ).iloc[0]

    customer_id = customer["customer_id"]
    country = customer["country"]

    # --------------------------------------------------------
    # Customer's addresses
    # --------------------------------------------------------

    customer_address_list = customer_addresses.get(
        customer_id,
        []
    )

    if not customer_address_list:
        continue

    # Prefer default address
    default_addresses = [
        address
        for address in customer_address_list
        if address["is_default"] is True
        or str(address["is_default"]).lower() == "true"
    ]

    if default_addresses:
        shipping_address = random.choice(
            default_addresses
        )
    else:
        shipping_address = random.choice(
            customer_address_list
        )

    # Billing can be same or another address
    billing_address = random.choice(
        customer_address_list
    )

    # --------------------------------------------------------
    # Customer's payment methods
    # --------------------------------------------------------

    customer_payment_list = (
        customer_payment_methods.get(
            customer_id,
            []
        )
    )

    if not customer_payment_list:
        continue

    active_methods = [
        method
        for method in customer_payment_list
        if method["status"] == "Active"
    ]

    if not active_methods:
        active_methods = customer_payment_list

    payment_method = random.choice(
        active_methods
    )

    # --------------------------------------------------------
    # Currency
    # --------------------------------------------------------

    currency = payment_method["currency"]

    # --------------------------------------------------------
    # Order date
    # --------------------------------------------------------

    order_date = fake.date_between(
        start_date="-2y",
        end_date="today"
    )

    # --------------------------------------------------------
    # Select 1–5 products
    # --------------------------------------------------------

    number_of_products = random.randint(
        1, 5
    )

    selected_products = random.sample(
        list(product_lookup.keys()),
        min(
            number_of_products,
            len(product_lookup)
        )
    )

    subtotal = 0
    total_discount = 0
    total_tax = 0

    order_id = f"ORD{order_number:08d}"

    # ========================================================
    # ORDER ITEMS
    # ========================================================

    for product_id in selected_products:

        product = product_lookup[product_id]

        quantity = random.randint(
            1, 5
        )

        unit_price = product["unit_price"]

        # Handle invalid product price
        if pd.isna(unit_price) or unit_price <= 0:
            unit_price = round(
                random.uniform(10, 1000),
                2
            )

        line_subtotal = (
            quantity * unit_price
        )

        discount = round(
            line_subtotal *
            random.uniform(0, 0.15),
            2
        )

        taxable_amount = (
            line_subtotal - discount
        )

        tax = round(
            taxable_amount *
            random.uniform(0.05, 0.20),
            2
        )

        line_total = round(
            taxable_amount + tax,
            2
        )

        subtotal += line_subtotal
        total_discount += discount
        total_tax += tax

        order_items.append({

            "order_item_id":
                f"ITEM{order_item_counter:09d}",

            "order_id":
                order_id,

            "product_id":
                product_id,

            "quantity":
                quantity,

            "unit_price":
                round(unit_price, 2),

            "discount_amount":
                discount,

            "tax_amount":
                tax,

            "line_total":
                line_total
        })

        order_item_counter += 1

    # --------------------------------------------------------
    # Shipping charge
    # --------------------------------------------------------

    shipping_amount = round(
        random.uniform(0, 50),
        2
    )

    total_amount = round(
        subtotal
        - total_discount
        + total_tax
        + shipping_amount,
        2
    )

    # --------------------------------------------------------
    # Create order
    # --------------------------------------------------------

    orders.append({

        "order_id":
            order_id,

        "customer_id":
            customer_id,

        "order_date":
            order_date,

        "order_status":
            random.choice(order_statuses),

        "currency":
            currency,

        "shipping_address_id":
            shipping_address["address_id"],

        "billing_address_id":
            billing_address["address_id"],

        "payment_method_id":
            payment_method["payment_method_id"],

        "subtotal_amount":
            round(subtotal, 2),

        "discount_amount":
            round(total_discount, 2),

        "tax_amount":
            round(total_tax, 2),

        "shipping_amount":
            shipping_amount,

        "total_amount":
            total_amount,

        "sales_channel":
            random.choice(sales_channels)
    })


# ============================================================
# 8. CREATE DATAFRAMES
# ============================================================

orders_df = pd.DataFrame(orders)
order_items_df = pd.DataFrame(order_items)


# ============================================================
# 9. DIRTY DATA INJECTION
# ============================================================

print("Injecting controlled data-quality issues...")


# ------------------------------------------------------------
# Duplicate Order IDs
# ------------------------------------------------------------

duplicate_count = int(
    len(orders_df) * 0.01
)

if duplicate_count > 0:

    duplicates = orders_df.sample(
        n=duplicate_count,
        random_state=42
    )

    orders_df = pd.concat(
        [orders_df, duplicates],
        ignore_index=True
    )


# ------------------------------------------------------------
# Invalid Customer IDs
# ------------------------------------------------------------

invalid_count = int(
    len(orders_df) * 0.01
)

invalid_indexes = random.sample(
    list(orders_df.index),
    invalid_count
)

for idx in invalid_indexes:

    orders_df.loc[
        idx,
        "customer_id"
    ] = f"CUST_INVALID_{idx}"


# ------------------------------------------------------------
# Future Order Dates
# ------------------------------------------------------------

future_count = int(
    len(orders_df) * 0.01
)

future_indexes = random.sample(
    list(orders_df.index),
    future_count
)

for idx in future_indexes:

    orders_df.loc[
        idx,
        "order_date"
    ] = fake.date_between(
        start_date="+1y",
        end_date="+2y"
    )


# ============================================================
# 10. SHUFFLE
# ============================================================

orders_df = orders_df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

order_items_df = order_items_df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ============================================================
# 11. SAVE
# ============================================================

orders_file = os.path.join(
    ORDERS_DIR,
    "orders.csv"
)

order_items_file = os.path.join(
    ORDER_ITEMS_DIR,
    "order_items.csv"
)

orders_df.to_csv(
    orders_file,
    index=False
)

order_items_df.to_csv(
    order_items_file,
    index=False
)


# ============================================================
# 12. VALIDATION
# ============================================================

print("\n========== ORDERS VALIDATION ==========")

print("\nOrders:")
print(len(orders_df))

print("\nOrder Items:")
print(len(order_items_df))

print("\nDuplicate Order IDs:")
print(
    orders_df["order_id"].duplicated().sum()
)

print("\nNull Values:")
print(
    orders_df.isnull().sum()
)

print("\nOrder Status:")
print(
    orders_df["order_status"].value_counts()
)

print("\nSales Channel:")
print(
    orders_df["sales_channel"].value_counts()
)

print("\nCurrencies:")
print(
    orders_df["currency"].value_counts()
)

print("\n=======================================")

print("\nFiles saved:")

print(orders_file)
print(order_items_file)