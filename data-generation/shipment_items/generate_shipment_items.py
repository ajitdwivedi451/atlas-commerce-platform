import os
import random
import pandas as pd
from faker import Faker

fake = Faker()

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

ORDERS_FILE = os.path.join(
    BASE_DIR, "orders", "orders.csv"
)

ORDER_ITEMS_FILE = os.path.join(
    BASE_DIR, "order_items", "order_items.csv"
)

SHIPMENTS_FILE = os.path.join(
    BASE_DIR, "shipments", "shipments.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR, "shipment_items"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "shipment_items.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD EXISTING DATA
# ============================================================

print("Loading existing datasets...")

orders = pd.read_csv(ORDERS_FILE)
order_items = pd.read_csv(ORDER_ITEMS_FILE)
shipments = pd.read_csv(SHIPMENTS_FILE)

print(f"Orders loaded: {len(orders)}")
print(f"Order Items loaded: {len(order_items)}")
print(f"Shipments loaded: {len(shipments)}")


# ============================================================
# NORMALIZE IDs
# ============================================================

orders["order_id"] = orders["order_id"].astype(str)
order_items["order_id"] = order_items["order_id"].astype(str)
order_items["order_item_id"] = order_items["order_item_id"].astype(str)
shipments["shipment_id"] = shipments["shipment_id"].astype(str)


# ============================================================
# CREATE ORDER LOOKUP
# ============================================================

order_lookup = (
    orders
    .drop_duplicates("order_id")
    .set_index("order_id")
    .to_dict("index")
)


# ============================================================
# CREATE ORDER ITEM GROUPS
# ============================================================

order_item_groups = {
    order_id: group.to_dict("records")
    for order_id, group
    in order_items.groupby("order_id")
}


# ============================================================
# ELIGIBLE SHIPMENTS
# ============================================================

eligible_statuses = {
    "Processing",
    "Shipped",
    "In Transit",
    "Out for Delivery",
    "Delivered",
    "Returned"
}

eligible_shipments = shipments[
    shipments["shipment_status"].isin(eligible_statuses)
].copy()

print(
    f"Eligible shipments: {len(eligible_shipments)}"
)


# ============================================================
# GENERATE SHIPMENT ITEMS
# ============================================================

shipment_items = []

shipment_item_counter = 1

print("\nGenerating shipment-item relationships...")


for _, shipment in eligible_shipments.iterrows():

    shipment_id = shipment["shipment_id"]
    order_id = shipment["order_id"]

    # --------------------------------------------------------
    # Skip invalid order relationships
    # --------------------------------------------------------

    if order_id not in order_item_groups:
        continue

    if order_id not in order_lookup:
        continue

    order = order_lookup[order_id]

    order_items_for_order = order_item_groups[order_id]

    if not order_items_for_order:
        continue

    # --------------------------------------------------------
    # Select items for this shipment
    #
    # This allows partial shipments.
    # --------------------------------------------------------

    selected_items = []

    for item in order_items_for_order:

        # Most shipments contain only a subset
        # of all order items.
        if random.random() < 0.70:
            selected_items.append(item)

    # Make sure every shipment has at least one item
    if not selected_items:
        selected_items = [
            random.choice(order_items_for_order)
        ]

    # --------------------------------------------------------
    # Generate shipment item records
    # --------------------------------------------------------

    for item in selected_items:

        ordered_quantity = int(
            item["quantity"]
        )

        if ordered_quantity <= 0:
            continue

        # ----------------------------------------------------
        # Determine shipped quantity
        # ----------------------------------------------------

        shipment_status = shipment["shipment_status"]

        if shipment_status in {
            "Delivered",
            "Returned"
        }:
            quantity_shipped = ordered_quantity

        elif shipment_status in {
            "Shipped",
            "In Transit",
            "Out for Delivery"
        }:
            quantity_shipped = random.randint(
                1,
                ordered_quantity
            )

        else:
            quantity_shipped = random.randint(
                1,
                ordered_quantity
            )

        # ----------------------------------------------------
        # Cancelled quantity
        # ----------------------------------------------------

        quantity_cancelled = max(
            ordered_quantity - quantity_shipped,
            0
        )

        # ----------------------------------------------------
        # Item status
        # ----------------------------------------------------

        if shipment_status == "Delivered":
            item_status = "Delivered"

        elif shipment_status == "Returned":
            item_status = "Returned"

        elif shipment_status in {
            "Shipped",
            "In Transit",
            "Out for Delivery"
        }:
            item_status = "Shipped"

        else:
            item_status = "Processing"

        # ----------------------------------------------------
        # Price comes from ORIGINAL ORDER ITEM
        # ----------------------------------------------------

        unit_price = item["unit_price"]

        # ----------------------------------------------------
        # Currency comes from ORIGINAL ORDER
        # ----------------------------------------------------

        currency = order["currency"]

        # ----------------------------------------------------
        # Dates
        # ----------------------------------------------------

        shipment_date = pd.to_datetime(
            shipment["shipment_date"],
            errors="coerce"
        )

        created_date = shipment_date

        if pd.isna(created_date):
            created_date = pd.Timestamp.today()

        updated_date = pd.to_datetime(
            shipment["updated_date"],
            errors="coerce"
        )

        if pd.isna(updated_date):
            updated_date = created_date

        # ----------------------------------------------------
        # Create record
        # ----------------------------------------------------

        shipment_item = {

            "shipment_item_id":
                f"SHIPITEM{shipment_item_counter:08d}",

            "shipment_id":
                shipment_id,

            "order_id":
                order_id,

            "order_item_id":
                item["order_item_id"],

            "product_id":
                item["product_id"],

            "quantity_shipped":
                quantity_shipped,

            "quantity_cancelled":
                quantity_cancelled,

            "unit_price":
                unit_price,

            "currency":
                currency,

            "item_status":
                item_status,

            "created_date":
                created_date.strftime("%Y-%m-%d"),

            "updated_date":
                updated_date.strftime("%Y-%m-%d")
        }

        shipment_items.append(shipment_item)

        shipment_item_counter += 1


# ============================================================
# BASE DATA SUMMARY
# ============================================================

print(
    f"\nBase shipment-item records generated: "
    f"{len(shipment_items)}"
)


# ============================================================
# DATA QUALITY ISSUE INJECTION
# ============================================================

print(
    "\nInjecting controlled data-quality issues..."
)


# ------------------------------------------------------------
# 1. Duplicate shipment items
# ------------------------------------------------------------

if shipment_items:

    duplicate_count = int(
        len(shipment_items) *
        random.uniform(0.01, 0.02)
    )

    duplicates = random.choices(
        shipment_items,
        k=duplicate_count
    )

    shipment_items.extend(duplicates)


# ------------------------------------------------------------
# 2. Invalid relationships
# ------------------------------------------------------------

for record in shipment_items:

    chance = random.random()

    # Invalid shipment ID
    if chance < 0.01:

        record["shipment_id"] = (
            f"SHIP_INVALID_{random.randint(1, 500)}"
        )

    # Invalid order item
    elif chance < 0.02:

        record["order_item_id"] = (
            f"OITEM_INVALID_{random.randint(1, 500)}"
        )

    # Invalid product
    elif chance < 0.03:

        record["product_id"] = (
            f"PROD_INVALID_{random.randint(1, 500)}"
        )

    # Negative quantity
    elif chance < 0.04:

        record["quantity_shipped"] = (
            -random.randint(1, 5)
        )

    # Zero quantity
    elif chance < 0.05:

        record["quantity_shipped"] = 0

    # Invalid currency
    elif chance < 0.06:

        record["currency"] = random.choice(
            ["XXX", "INVALID", "UNKNOWN"]
        )

    # Invalid item status
    elif chance < 0.07:

        record["item_status"] = random.choice(
            [
                "UNKNOWN",
                "INVALID",
                "Pending_Validation"
            ]
        )

    # Null quantity
    elif chance < 0.08:

        record["quantity_shipped"] = None


# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(shipment_items)


# ============================================================
# SAVE
# ============================================================

df = pd.DataFrame(shipment_items)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n==========================================")
print("SHIPMENT ITEM GENERATION COMPLETE")
print("==========================================")

print(
    f"Total Shipment Items: {len(df)}"
)

print(
    f"Unique Shipments: "
    f"{df['shipment_id'].nunique()}"
)

print(
    f"Unique Orders: "
    f"{df['order_id'].nunique()}"
)

print(
    f"Unique Products: "
    f"{df['product_id'].nunique()}"
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)

print("==========================================")