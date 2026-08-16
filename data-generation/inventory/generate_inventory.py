import pandas as pd
import random
import os
from faker import Faker

fake = Faker()

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

PRODUCT_FILE = os.path.join(
    BASE_DIR,
    "products",
    "products.csv"
)

WAREHOUSE_FILE = os.path.join(
    BASE_DIR,
    "warehouses",
    "warehouses.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "inventory"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "inventory.csv"
)

# Number of inventory records
NUM_INVENTORY = 100_000


# ============================================================
# LOAD EXISTING DATASETS
# ============================================================

print("Loading existing Products and Warehouses...")

products_df = pd.read_csv(PRODUCT_FILE)

warehouses_df = pd.read_csv(WAREHOUSE_FILE)

print(f"Products loaded: {len(products_df)}")
print(f"Warehouses loaded: {len(warehouses_df)}")


# ============================================================
# REMOVE DUPLICATE MASTER IDs FOR RELATIONSHIP GENERATION
# ============================================================

products_df = products_df.drop_duplicates(
    subset=["product_id"]
)

warehouses_df = warehouses_df.drop_duplicates(
    subset=["warehouse_id"]
)


product_ids = products_df["product_id"].dropna().tolist()

warehouse_ids = warehouses_df["warehouse_id"].dropna().tolist()


# ============================================================
# PRODUCT CATEGORY INFORMATION
# ============================================================

product_category = {}

for _, row in products_df.iterrows():

    product_category[
        row["product_id"]
    ] = row["category"]


# ============================================================
# CATEGORY-BASED INVENTORY RANGES
# ============================================================

inventory_ranges = {

    "Electronics": {
        "min": 10,
        "max": 500
    },

    "Computers": {
        "min": 5,
        "max": 300
    },

    "Clothing": {
        "min": 100,
        "max": 5000
    },

    "Home": {
        "min": 50,
        "max": 2000
    },

    "Beauty": {
        "min": 100,
        "max": 4000
    },

    "Sports": {
        "min": 50,
        "max": 2000
    },

    "Grocery": {
        "min": 200,
        "max": 10000
    }
}


# ============================================================
# DEFAULT RANGE
# ============================================================

default_range = {
    "min": 20,
    "max": 2000
}


# ============================================================
# GENERATE PRODUCT-WAREHOUSE COMBINATIONS
# ============================================================

print("\nGenerating Product-Warehouse inventory relationships...")

inventory = []

used_combinations = set()

inventory_counter = 1


while len(inventory) < NUM_INVENTORY:

    product_id = random.choice(product_ids)

    warehouse_id = random.choice(warehouse_ids)

    combination = (
        product_id,
        warehouse_id
    )

    # Prevent duplicate product + warehouse combination
    if combination in used_combinations:
        continue

    used_combinations.add(combination)

    category = product_category.get(
        product_id,
        "Unknown"
    )

    quantity_range = inventory_ranges.get(
        category,
        default_range
    )

    # --------------------------------------------------------
    # Quantity generation
    # --------------------------------------------------------

    available_quantity = random.randint(
        quantity_range["min"],
        quantity_range["max"]
    )

    reserved_quantity = random.randint(
        0,
        max(
            1,
            int(available_quantity * 0.15)
        )
    )

    damaged_quantity = random.randint(
        0,
        max(
            1,
            int(available_quantity * 0.03)
        )
    )

    in_transit_quantity = random.randint(
        0,
        max(
            1,
            int(available_quantity * 0.30)
        )
    )

    # --------------------------------------------------------
    # Reorder logic
    # --------------------------------------------------------

    reorder_level = max(
        10,
        int(
            available_quantity *
            random.uniform(0.20, 0.40)
        )
    )

    reorder_quantity = max(
        reorder_level * 2,
        random.randint(
            50,
            1000
        )
    )

    # --------------------------------------------------------
    # Inventory status
    # --------------------------------------------------------

    if available_quantity == 0:

        inventory_status = "Out of Stock"

    elif available_quantity <= reorder_level:

        inventory_status = "Low Stock"

    else:

        inventory_status = "In Stock"

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    last_restocked_date = fake.date_between(
        start_date="-1y",
        end_date="today"
    )

    last_updated_date = fake.date_between(
        start_date="-90d",
        end_date="today"
    )

    inventory.append({

        "inventory_id":
            f"INV{inventory_counter:08d}",

        "product_id":
            product_id,

        "warehouse_id":
            warehouse_id,

        "available_quantity":
            available_quantity,

        "reserved_quantity":
            reserved_quantity,

        "damaged_quantity":
            damaged_quantity,

        "in_transit_quantity":
            in_transit_quantity,

        "reorder_level":
            reorder_level,

        "reorder_quantity":
            reorder_quantity,

        "inventory_status":
            inventory_status,

        "last_restocked_date":
            last_restocked_date,

        "last_updated_date":
            last_updated_date
    })

    inventory_counter += 1


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(inventory)


print("\nBase inventory records generated:")
print(len(df))


# ============================================================
# DIRTY DATA INJECTION
# ============================================================

print("\nInjecting controlled data-quality issues...")


# ============================================================
# 1. DUPLICATE INVENTORY IDs
# ============================================================

duplicate_count = max(
    1,
    int(len(df) * 0.01)
)

duplicate_rows = df.sample(
    n=duplicate_count,
    random_state=42
)

df = pd.concat(
    [
        df,
        duplicate_rows
    ],
    ignore_index=True
)


# ============================================================
# 2. NULL REORDER LEVEL
# ============================================================

null_reorder_count = max(
    1,
    int(len(df) * 0.01)
)

indexes = random.sample(
    list(df.index),
    null_reorder_count
)

df.loc[
    indexes,
    "reorder_level"
] = None


# ============================================================
# 3. NULL LAST RESTOCKED DATE
# ============================================================

null_date_count = max(
    1,
    int(len(df) * 0.01)
)

indexes = random.sample(
    list(df.index),
    null_date_count
)

df.loc[
    indexes,
    "last_restocked_date"
] = None


# ============================================================
# 4. INVALID NEGATIVE QUANTITIES
# ============================================================

negative_quantity_count = max(
    1,
    int(len(df) * 0.01)
)

indexes = random.sample(
    list(df.index),
    negative_quantity_count
)

for index in indexes:

    df.loc[
        index,
        "available_quantity"
    ] = random.randint(
        -500,
        -1
    )


# ============================================================
# 5. INVALID INVENTORY STATUS
# ============================================================

invalid_status_count = max(
    1,
    int(len(df) * 0.01)
)

indexes = random.sample(
    list(df.index),
    invalid_status_count
)

for index in indexes:

    df.loc[
        index,
        "inventory_status"
    ] = random.choice([
        "UNKNOWN",
        "INVALID",
        "Pending_Validation"
    ])


# ============================================================
# 6. INVALID PRODUCT IDs
# ============================================================

invalid_product_count = max(
    1,
    int(len(df) * 0.01)
)

indexes = random.sample(
    list(df.index),
    invalid_product_count
)

for index in indexes:

    df.loc[
        index,
        "product_id"
    ] = (
        f"PROD_INVALID_"
        f"{random.randint(1, 9999)}"
    )


# ============================================================
# 7. INVALID WAREHOUSE IDs
# ============================================================

invalid_warehouse_count = max(
    1,
    int(len(df) * 0.01)
)

indexes = random.sample(
    list(df.index),
    invalid_warehouse_count
)

for index in indexes:

    df.loc[
        index,
        "warehouse_id"
    ] = (
        f"WH_INVALID_"
        f"{random.randint(1, 999)}"
    )


# ============================================================
# 8. FUTURE LAST UPDATED DATE
# ============================================================

future_date_count = max(
    1,
    int(len(df) * 0.01)
)

indexes = random.sample(
    list(df.index),
    future_date_count
)

for index in indexes:

    df.loc[
        index,
        "last_updated_date"
    ] = fake.date_between(
        start_date="+1y",
        end_date="+2y"
    )


# ============================================================
# 9. BUSINESS LOGIC ERROR
# ============================================================
# reserved quantity > available quantity

business_error_count = max(
    1,
    int(len(df) * 0.01)
)

indexes = random.sample(
    list(df.index),
    business_error_count
)

for index in indexes:

    available = df.loc[
        index,
        "available_quantity"
    ]

    if pd.notna(available) and available > 0:

        df.loc[
            index,
            "reserved_quantity"
        ] = available + random.randint(
            100,
            500
        )


# ============================================================
# SHUFFLE
# ============================================================

df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# VALIDATION
# ============================================================

print("\n========== INVENTORY VALIDATION ==========")

print("\nColumns:")
print(
    df.columns.tolist()
)

print("\nTotal Records:")
print(
    len(df)
)

print("\nDuplicate Inventory IDs:")
print(
    df["inventory_id"].duplicated().sum()
)

print("\nNull Values:")
print(
    df.isnull().sum()
)

print("\nInventory Status:")
print(
    df["inventory_status"].value_counts()
)

print("\nNegative Available Quantity:")
print(
    (
        df["available_quantity"] < 0
    ).sum()
)

print("\nInvalid Product IDs:")
print(
    (
        ~df["product_id"].isin(
            product_ids
        )
    ).sum()
)

print("\nInvalid Warehouse IDs:")
print(
    (
        ~df["warehouse_id"].isin(
            warehouse_ids
        )
    ).sum()
)

print("\nReserved > Available:")
print(
    (
        df["reserved_quantity"]
        > df["available_quantity"]
    ).sum()
)

print("\nFuture Updated Dates:")

today = pd.Timestamp.today()

print(
    (
        pd.to_datetime(
            df["last_updated_date"]
        ) > today
    ).sum()
)

print("\n==========================================")

print("\nSaved to:")
print(
    OUTPUT_FILE
)