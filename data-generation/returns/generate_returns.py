import os
import random
import pandas as pd
from faker import Faker
from datetime import timedelta

fake = Faker()

# ============================================================
# PATHS
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

CUSTOMERS_FILE = os.path.join(
    BASE_DIR, "customers", "customers.csv"
)

ORDERS_FILE = os.path.join(
    BASE_DIR, "orders", "orders.csv"
)

ORDER_ITEMS_FILE = os.path.join(
    BASE_DIR, "order_items", "order_items.csv"
)

PRODUCTS_FILE = os.path.join(
    BASE_DIR, "products", "products.csv"
)

SHIPMENTS_FILE = os.path.join(
    BASE_DIR, "shipments", "shipments.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR, "returns"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "returns.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# LOAD DATASETS
# ============================================================

print("Loading existing datasets...")

customers_df = pd.read_csv(CUSTOMERS_FILE)
orders_df = pd.read_csv(ORDERS_FILE)
order_items_df = pd.read_csv(ORDER_ITEMS_FILE)
products_df = pd.read_csv(PRODUCTS_FILE)
shipments_df = pd.read_csv(SHIPMENTS_FILE)

print(f"Customers loaded: {len(customers_df)}")
print(f"Orders loaded: {len(orders_df)}")
print(f"Order Items loaded: {len(order_items_df)}")
print(f"Products loaded: {len(products_df)}")
print(f"Shipments loaded: {len(shipments_df)}")

# ============================================================
# NORMALIZE DATE COLUMNS
# ============================================================

orders_df["order_date"] = pd.to_datetime(
    orders_df["order_date"], errors="coerce"
)

order_items_df["unit_price"] = pd.to_numeric(
    order_items_df["unit_price"], errors="coerce"
)

shipments_df["shipment_date"] = pd.to_datetime(
    shipments_df["shipment_date"], errors="coerce"
)

shipments_df["actual_delivery_date"] = pd.to_datetime(
    shipments_df["actual_delivery_date"], errors="coerce"
)

# ============================================================
# CREATE LOOKUPS
# ============================================================

customer_ids = set(
    customers_df["customer_id"].astype(str)
)

product_ids = set(
    products_df["product_id"].astype(str)
)

order_ids = set(
    orders_df["order_id"].astype(str)
)

order_item_ids = set(
    order_items_df["order_item_id"].astype(str)
)

shipment_ids = set(
    shipments_df["shipment_id"].astype(str)
)

# ============================================================
# PREPARE ORDER ITEM DATA
# ============================================================

order_items_df["order_id"] = (
    order_items_df["order_id"].astype(str)
)

order_items_df["product_id"] = (
    order_items_df["product_id"].astype(str)
)

order_items_df["order_item_id"] = (
    order_items_df["order_item_id"].astype(str)
)

# ============================================================
# PREPARE ORDER DATA
# ============================================================

orders_df["order_id"] = orders_df["order_id"].astype(str)
orders_df["customer_id"] = orders_df["customer_id"].astype(str)

# ============================================================
# PREPARE SHIPMENT DATA
# ============================================================

shipments_df["shipment_id"] = (
    shipments_df["shipment_id"].astype(str)
)

shipments_df["order_id"] = (
    shipments_df["order_id"].astype(str)
)

# ============================================================
# FIND REALISTIC RETURN-ELIGIBLE ORDERS
# ============================================================

eligible_orders = orders_df[
    orders_df["order_status"].isin(
        ["Delivered", "Returned"]
    )
].copy()

eligible_orders = eligible_orders[
    eligible_orders["order_id"].isin(order_ids)
]

print(f"Eligible orders: {len(eligible_orders)}")

# ============================================================
# MAP ORDER -> SHIPMENTS
# ============================================================

shipment_lookup = {}

for _, shipment in shipments_df.iterrows():

    order_id = str(shipment["order_id"])

    if order_id not in shipment_lookup:
        shipment_lookup[order_id] = []

    shipment_lookup[order_id].append(shipment)

# ============================================================
# RETURN CONFIGURATION
# ============================================================

return_reasons = [
    "Damaged",
    "Defective",
    "Wrong Item",
    "Wrong Size",
    "Not as Described",
    "Changed Mind",
    "Late Delivery",
    "Quality Issue",
    "Missing Parts",
    "Duplicate Order"
]

return_types = [
    "Refund",
    "Replacement",
    "Exchange"
]

return_statuses = [
    "Requested",
    "Approved",
    "Pickup_Scheduled",
    "Picked_Up",
    "Received",
    "Inspected",
    "Refunded",
    "Rejected",
    "Cancelled"
]

item_conditions = [
    "New",
    "Opened",
    "Used",
    "Damaged",
    "Defective"
]

inspection_statuses = [
    "Pending",
    "Passed",
    "Failed",
    "Not_Required"
]

# ============================================================
# GENERATE BASE RETURNS
# ============================================================

returns = []

return_counter = 1

print("Generating realistic return transactions...")

for _, order in eligible_orders.iterrows():

    # Not every order gets returned
    if random.random() > 0.18:
        continue

    order_id = str(order["order_id"])
    customer_id = str(order["customer_id"])

    order_date = order["order_date"]

    if pd.isna(order_date):
        continue

    # Get order items
    items = order_items_df[
        order_items_df["order_id"] == order_id
    ]

    if items.empty:
        continue

    # Usually 1-2 items from an order are returned
    max_items = min(2, len(items))

    selected_items = items.sample(
        n=random.randint(1, max_items)
    )

    # Find shipment for this order
    order_shipments = shipment_lookup.get(
        order_id, []
    )

    shipment = None

    if order_shipments:
        # Prefer delivered shipment
        delivered_shipments = [
            s for s in order_shipments
            if str(s["shipment_status"]) == "Delivered"
        ]

        if delivered_shipments:
            shipment = random.choice(
                delivered_shipments
            )
        else:
            shipment = random.choice(
                order_shipments
            )

    for _, item in selected_items.iterrows():

        order_item_id = str(item["order_item_id"])
        product_id = str(item["product_id"])

        # Quantity ordered
        try:
            quantity_ordered = int(
                float(item.get("quantity", 1))
            )
        except:
            quantity_ordered = 1

        if quantity_ordered <= 0:
            quantity_ordered = 1

        quantity_returned = random.randint(
            1,
            quantity_ordered
        )

        # Shipment details
        shipment_id = None

        shipment_date = None
        delivery_date = None

        if shipment is not None:

            shipment_id = str(
                shipment["shipment_id"]
            )

            shipment_date = shipment[
                "shipment_date"
            ]

            delivery_date = shipment[
                "actual_delivery_date"
            ]

        # If actual delivery is unavailable,
        # use shipment date
        if pd.isna(delivery_date):

            if not pd.isna(shipment_date):

                delivery_date = (
                    shipment_date +
                    timedelta(
                        days=random.randint(2, 7)
                    )
                )

            else:

                delivery_date = (
                    order_date +
                    timedelta(
                        days=random.randint(3, 10)
                    )
                )

        # Return date after delivery
        return_date = (
            delivery_date +
            timedelta(
                days=random.randint(2, 30)
            )
        )

        # Received date
        received_date = (
            return_date +
            timedelta(
                days=random.randint(1, 7)
            )
        )

        # Price
        unit_price = pd.to_numeric(
            item["unit_price"],
            errors="coerce"
        )

        if pd.isna(unit_price):
            unit_price = 0

        refund_amount = round(
            float(unit_price) *
            quantity_returned,
            2
        )

        currency = str(
            order["currency"]
        )

        return_type = random.choice(
            return_types
        )

        return_status = random.choice(
            return_statuses
        )

        # Business logic:
        # Replacement / Exchange normally doesn't
        # immediately mean refund
        if return_type in ["Replacement", "Exchange"]:

            if random.random() < 0.7:
                refund_amount = 0

        pickup_required = (
            random.random() < 0.85
        )

        pickup_date = None

        if pickup_required:

            pickup_date = (
                return_date +
                timedelta(
                    days=random.randint(1, 5)
                )
            )

        inspection_status = random.choice(
            inspection_statuses
        )

        # Refund status consistency
        if return_status == "Refunded":

            refund_amount = max(
                refund_amount,
                0
            )

            inspection_status = "Passed"

        elif return_status in [
            "Rejected",
            "Cancelled"
        ]:

            refund_amount = 0

        return_record = {

            "return_id":
                f"RET{return_counter:08d}",

            "order_id":
                order_id,

            "order_item_id":
                order_item_id,

            "customer_id":
                customer_id,

            "product_id":
                product_id,

            "shipment_id":
                shipment_id,

            "return_date":
                return_date.strftime(
                    "%Y-%m-%d"
                ),

            "return_reason":
                random.choice(
                    return_reasons
                ),

            "return_type":
                return_type,

            "return_status":
                return_status,

            "quantity_returned":
                quantity_returned,

            "item_condition":
                random.choice(
                    item_conditions
                ),

            "pickup_required":
                pickup_required,

            "pickup_date":
                pickup_date.strftime(
                    "%Y-%m-%d"
                ) if pickup_date else None,

            "received_date":
                received_date.strftime(
                    "%Y-%m-%d"
                ),

            "inspection_status":
                inspection_status,

            "refund_amount":
                refund_amount,

            "refund_currency":
                currency,

            "created_date":
                (
                    return_date -
                    timedelta(
                        days=random.randint(0, 2)
                    )
                ).strftime(
                    "%Y-%m-%d"
                ),

            "updated_date":
                (
                    received_date +
                    timedelta(
                        days=random.randint(0, 3)
                    )
                ).strftime(
                    "%Y-%m-%d"
                )
        }

        returns.append(
            return_record
        )

        return_counter += 1


print(
    f"Base return records generated: {len(returns)}"
)

# ============================================================
# CONTROLLED DATA QUALITY ISSUES
# ============================================================

print(
    "Injecting controlled data-quality issues..."
)

base_count = len(returns)

if base_count == 0:
    raise RuntimeError(
        "No return records generated."
    )

# ------------------------------------------------------------
# 1. DUPLICATE RETURN IDs
# ------------------------------------------------------------

duplicate_count = int(
    base_count *
    random.uniform(0.01, 0.02)
)

duplicate_records = random.choices(
    returns,
    k=duplicate_count
)

returns.extend(
    duplicate_records
)

# ------------------------------------------------------------
# 2. NULL VALUES
# ------------------------------------------------------------

for record in returns:

    chance = random.random()

    # ~3% NULL pickup date
    if chance < 0.03:

        record["pickup_date"] = None

    # ~1% NULL received date
    elif chance < 0.04:

        record["received_date"] = None

    # ~1% NULL shipment
    elif chance < 0.05:

        record["shipment_id"] = None

# ------------------------------------------------------------
# 3. INVALID BUSINESS VALUES
# ------------------------------------------------------------

for record in returns:

    chance = random.random()

    if chance < 0.015:

        record["return_status"] = random.choice(
            [
                "INVALID",
                "UNKNOWN",
                "Pending_Validation"
            ]
        )

    elif chance < 0.025:

        record["return_reason"] = random.choice(
            [
                "Unknown_Reason",
                "INVALID_REASON",
                "NotApplicable"
            ]
        )

    elif chance < 0.035:

        record["return_type"] = random.choice(
            [
                "INVALID",
                "Unknown_Type"
            ]
        )

# ------------------------------------------------------------
# 4. INVALID QUANTITIES
# ------------------------------------------------------------

for record in returns:

    if random.random() < 0.02:

        record["quantity_returned"] = random.choice(
            [
                -1,
                0,
                random.randint(10, 50)
            ]
        )

# ------------------------------------------------------------
# 5. INVALID REFUNDS
# ------------------------------------------------------------

for record in returns:

    if random.random() < 0.02:

        record["refund_amount"] = random.choice(
            [
                -50,
                -100,
                round(
                    random.uniform(
                        10000,
                        50000
                    ),
                    2
                )
            ]
        )

# ------------------------------------------------------------
# 6. FUTURE RETURN DATES
# ------------------------------------------------------------

for record in returns:

    if random.random() < 0.01:

        future_date = fake.date_between(
            start_date="+30d",
            end_date="+2y"
        )

        record["return_date"] = (
            future_date.strftime(
                "%Y-%m-%d"
            )
        )

# ------------------------------------------------------------
# 7. DATE ORDER CORRUPTION
# ------------------------------------------------------------

for record in returns:

    if random.random() < 0.01:

        return_date = pd.to_datetime(
            record["return_date"],
            errors="coerce"
        )

        if pd.notna(return_date):

            record["received_date"] = (
                return_date -
                timedelta(days=2)
            ).strftime(
                "%Y-%m-%d"
            )

# ------------------------------------------------------------
# 8. INVALID RELATIONSHIPS
# ------------------------------------------------------------

for record in returns:

    chance = random.random()

    if chance < 0.01:

        record["customer_id"] = (
            f"CUST_INVALID_"
            f"{random.randint(1, 999)}"
        )

    elif chance < 0.02:

        record["order_id"] = (
            f"ORD_INVALID_"
            f"{random.randint(1, 999)}"
        )

    elif chance < 0.03:

        record["product_id"] = (
            f"PROD_INVALID_"
            f"{random.randint(1, 999)}"
        )

    elif chance < 0.04:

        record["order_item_id"] = (
            f"OI_INVALID_"
            f"{random.randint(1, 999)}"
        )

    elif chance < 0.05:

        record["shipment_id"] = (
            f"SHIP_INVALID_"
            f"{random.randint(1, 999)}"
        )

# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(returns)

# ============================================================
# SAVE
# ============================================================

returns_df = pd.DataFrame(returns)

returns_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("==========================================")
print("RETURN GENERATION COMPLETE")
print("==========================================")
print(
    f"Total return records: "
    f"{len(returns_df)}"
)

print(
    f"Saved to: {OUTPUT_FILE}"
)
print("==========================================")