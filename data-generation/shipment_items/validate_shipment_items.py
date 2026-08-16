import os
import pandas as pd

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

SHIPMENT_ITEMS_FILE = os.path.join(
    BASE_DIR, "shipment_items", "shipment_items.csv"
)

SHIPMENTS_FILE = os.path.join(
    BASE_DIR, "shipments", "shipments.csv"
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


# ============================================================
# LOAD DATA
# ============================================================

print("Loading datasets...")

shipment_items = pd.read_csv(SHIPMENT_ITEMS_FILE)
shipments = pd.read_csv(SHIPMENTS_FILE)
orders = pd.read_csv(ORDERS_FILE)
order_items = pd.read_csv(ORDER_ITEMS_FILE)
products = pd.read_csv(PRODUCTS_FILE)

print(f"Shipment Items loaded: {len(shipment_items)}")
print(f"Shipments loaded: {len(shipments)}")
print(f"Orders loaded: {len(orders)}")
print(f"Order Items loaded: {len(order_items)}")
print(f"Products loaded: {len(products)}")


# ============================================================
# NORMALIZE IDs
# ============================================================

for df, columns in [
    (
        shipment_items,
        [
            "shipment_item_id",
            "shipment_id",
            "order_id",
            "order_item_id",
            "product_id"
        ]
    ),
    (
        shipments,
        ["shipment_id", "order_id"]
    ),
    (
        orders,
        ["order_id"]
    ),
    (
        order_items,
        ["order_item_id", "order_id", "product_id"]
    ),
    (
        products,
        ["product_id"]
    )
]:
    for column in columns:
        df[column] = df[column].astype(str)


# ============================================================
# BASIC VALIDATION
# ============================================================

print("\n==========================================")
print("SHIPMENT ITEM DATA VALIDATION")
print("==========================================")

print("\nColumns:")
print(list(shipment_items.columns))

print("\nTotal Records:")
print(len(shipment_items))


# ============================================================
# DUPLICATE IDs
# ============================================================

print("\nDuplicate Shipment Item IDs:")

print(
    shipment_items["shipment_item_id"].duplicated().sum()
)


# Shipment + Order Item combination
duplicate_relationships = shipment_items.duplicated(
    subset=["shipment_id", "order_item_id"]
).sum()

print("\nDuplicate Shipment + Order Item combinations:")
print(duplicate_relationships)


# ============================================================
# NULL VALUES
# ============================================================

print("\nNull Values:")
print(shipment_items.isnull().sum())


# ============================================================
# REFERENCE DATASETS
# ============================================================

shipment_ids = set(
    shipments["shipment_id"]
)

order_ids = set(
    orders["order_id"]
)

order_item_ids = set(
    order_items["order_item_id"]
)

product_ids = set(
    products["product_id"]
)


# ============================================================
# INVALID FOREIGN KEYS
# ============================================================

invalid_shipment_ids = (
    ~shipment_items["shipment_id"].isin(shipment_ids)
).sum()

invalid_order_ids = (
    ~shipment_items["order_id"].isin(order_ids)
).sum()

invalid_order_item_ids = (
    ~shipment_items["order_item_id"].isin(order_item_ids)
).sum()

invalid_product_ids = (
    ~shipment_items["product_id"].isin(product_ids)
).sum()


print("\nInvalid Shipment IDs:")
print(invalid_shipment_ids)

print("\nInvalid Order IDs:")
print(invalid_order_ids)

print("\nInvalid Order Item IDs:")
print(invalid_order_item_ids)

print("\nInvalid Product IDs:")
print(invalid_product_ids)


# ============================================================
# SHIPMENT ↔ ORDER RELATIONSHIP
# ============================================================

shipment_order_lookup = (
    shipments
    .drop_duplicates("shipment_id")
    .set_index("shipment_id")["order_id"]
)

valid_relationships = shipment_items["shipment_id"].isin(
    shipment_order_lookup.index
)

shipment_order_mismatch = (
    shipment_items.loc[valid_relationships, "order_id"].values
    !=
    shipment_items.loc[valid_relationships, "shipment_id"]
        .map(shipment_order_lookup)
        .values
).sum()

print("\nShipment ↔ Order Mismatches:")
print(shipment_order_mismatch)


# ============================================================
# ORDER ITEM ↔ ORDER RELATIONSHIP
# ============================================================

order_item_order_lookup = (
    order_items
    .drop_duplicates("order_item_id")
    .set_index("order_item_id")["order_id"]
)

valid_order_items = shipment_items["order_item_id"].isin(
    order_item_order_lookup.index
)

order_item_order_mismatch = (
    shipment_items.loc[valid_order_items, "order_id"].values
    !=
    shipment_items.loc[valid_order_items, "order_item_id"]
        .map(order_item_order_lookup)
        .values
).sum()

print("\nOrder Item ↔ Order Mismatches:")
print(order_item_order_mismatch)


# ============================================================
# PRODUCT ↔ ORDER ITEM RELATIONSHIP
# ============================================================

order_item_product_lookup = (
    order_items
    .drop_duplicates("order_item_id")
    .set_index("order_item_id")["product_id"]
)

valid_products = shipment_items["order_item_id"].isin(
    order_item_product_lookup.index
)

product_mismatch = (
    shipment_items.loc[valid_products, "product_id"].values
    !=
    shipment_items.loc[valid_products, "order_item_id"]
        .map(order_item_product_lookup)
        .values
).sum()

print("\nProduct ↔ Order Item Mismatches:")
print(product_mismatch)


# ============================================================
# QUANTITY VALIDATION
# ============================================================

order_item_quantity_lookup = (
    order_items
    .drop_duplicates("order_item_id")
    .set_index("order_item_id")["quantity"]
)

shipment_items["quantity_shipped_numeric"] = pd.to_numeric(
    shipment_items["quantity_shipped"],
    errors="coerce"
)

shipment_items["ordered_quantity"] = (
    shipment_items["order_item_id"]
    .map(order_item_quantity_lookup)
)

negative_quantity = (
    shipment_items["quantity_shipped_numeric"] < 0
).sum()

zero_quantity = (
    shipment_items["quantity_shipped_numeric"] == 0
).sum()

shipped_more_than_ordered = (
    shipment_items["quantity_shipped_numeric"]
    >
    shipment_items["ordered_quantity"]
).sum()

print("\nNegative Quantity Shipped:")
print(negative_quantity)

print("\nZero Quantity Shipped:")
print(zero_quantity)

print("\nShipped Quantity > Ordered Quantity:")
print(shipped_more_than_ordered)


# ============================================================
# CURRENCY VALIDATION
# ============================================================

order_currency_lookup = (
    orders
    .drop_duplicates("order_id")
    .set_index("order_id")["currency"]
)

shipment_items["order_currency"] = (
    shipment_items["order_id"]
    .map(order_currency_lookup)
)

currency_mismatch = (
    shipment_items["currency"]
    != shipment_items["order_currency"]
).sum()

print("\nShipment Item ↔ Order Currency Mismatches:")
print(currency_mismatch)


# ============================================================
# UNIT PRICE VALIDATION
# ============================================================

order_item_price_lookup = (
    order_items
    .drop_duplicates("order_item_id")
    .set_index("order_item_id")["unit_price"]
)

shipment_items["order_item_unit_price"] = (
    shipment_items["order_item_id"]
    .map(order_item_price_lookup)
)

shipment_items["unit_price_numeric"] = pd.to_numeric(
    shipment_items["unit_price"],
    errors="coerce"
)

shipment_items["order_item_unit_price"] = pd.to_numeric(
    shipment_items["order_item_unit_price"],
    errors="coerce"
)

price_mismatch = (
    shipment_items["unit_price_numeric"].round(2)
    !=
    shipment_items["order_item_unit_price"].round(2)
).sum()

print("\nUnit Price Mismatches:")
print(price_mismatch)


# ============================================================
# STATUS VALIDATION
# ============================================================

valid_item_statuses = {
    "Processing",
    "Shipped",
    "Delivered",
    "Returned"
}

invalid_status = (
    ~shipment_items["item_status"]
    .isin(valid_item_statuses)
).sum()

print("\nInvalid Item Status:")
print(invalid_status)


# ============================================================
# SHIPMENT STATUS ↔ ITEM STATUS
# ============================================================

shipment_status_lookup = (
    shipments
    .drop_duplicates("shipment_id")
    .set_index("shipment_id")["shipment_status"]
)

shipment_items["shipment_status"] = (
    shipment_items["shipment_id"]
    .map(shipment_status_lookup)
)


delivered_mismatch = (
    (
        shipment_items["shipment_status"] == "Delivered"
    )
    &
    (
        shipment_items["item_status"] != "Delivered"
    )
).sum()

returned_mismatch = (
    (
        shipment_items["shipment_status"] == "Returned"
    )
    &
    (
        shipment_items["item_status"] != "Returned"
    )
).sum()

print("\nDelivered Shipment ↔ Item Status Mismatches:")
print(delivered_mismatch)

print("\nReturned Shipment ↔ Item Status Mismatches:")
print(returned_mismatch)


# ============================================================
# ORPHAN RECORDS
# ============================================================

orphan_shipment_items = (
    ~shipment_items["shipment_id"].isin(shipment_ids)
).sum()

orphan_order_items = (
    ~shipment_items["order_item_id"].isin(order_item_ids)
).sum()

print("\nOrphan Shipment Items:")
print(orphan_shipment_items)

print("\nOrphan Order Items:")
print(orphan_order_items)


# ============================================================
# SUMMARY
# ============================================================

print("\n==========================================")
print("SHIPMENT ITEM VALIDATION SUMMARY")
print("==========================================")

print(
    f"Total Shipment Items          : {len(shipment_items)}"
)

print(
    f"Duplicate Item IDs             : "
    f"{shipment_items['shipment_item_id'].duplicated().sum()}"
)

print(
    f"Duplicate Shipment+Item       : "
    f"{duplicate_relationships}"
)

print(
    f"Invalid Shipment IDs           : "
    f"{invalid_shipment_ids}"
)

print(
    f"Invalid Order Item IDs         : "
    f"{invalid_order_item_ids}"
)

print(
    f"Invalid Product IDs            : "
    f"{invalid_product_ids}"
)

print(
    f"Shipment↔Order Mismatch        : "
    f"{shipment_order_mismatch}"
)

print(
    f"OrderItem↔Order Mismatch       : "
    f"{order_item_order_mismatch}"
)

print(
    f"Product↔OrderItem Mismatch     : "
    f"{product_mismatch}"
)

print(
    f"Negative Quantity              : "
    f"{negative_quantity}"
)

print(
    f"Shipped > Ordered              : "
    f"{shipped_more_than_ordered}"
)

print(
    f"Currency Mismatch              : "
    f"{currency_mismatch}"
)

print(
    f"Unit Price Mismatch             : "
    f"{price_mismatch}"
)

print(
    f"Invalid Item Status            : "
    f"{invalid_status}"
)

print("==========================================")