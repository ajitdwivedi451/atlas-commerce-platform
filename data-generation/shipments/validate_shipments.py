import os
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

SHIPMENTS_FILE = os.path.join(
    BASE_DIR, "shipments", "shipments.csv"
)

ORDERS_FILE = os.path.join(
    BASE_DIR, "orders", "orders.csv"
)

ADDRESSES_FILE = os.path.join(
    BASE_DIR, "customer_addresses",
    "customer_addresses.csv"
)

WAREHOUSES_FILE = os.path.join(
    BASE_DIR, "warehouses", "warehouses.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading datasets...")

shipments = pd.read_csv(SHIPMENTS_FILE)
orders = pd.read_csv(ORDERS_FILE)
addresses = pd.read_csv(ADDRESSES_FILE)
warehouses = pd.read_csv(WAREHOUSES_FILE)

print(f"Shipments loaded: {len(shipments)}")
print(f"Orders loaded: {len(orders)}")
print(f"Addresses loaded: {len(addresses)}")
print(f"Warehouses loaded: {len(warehouses)}")


# ============================================================
# DATE CONVERSION
# ============================================================

shipments["shipment_date"] = pd.to_datetime(
    shipments["shipment_date"],
    errors="coerce"
)

shipments["estimated_delivery_date"] = pd.to_datetime(
    shipments["estimated_delivery_date"],
    errors="coerce"
)

shipments["actual_delivery_date"] = pd.to_datetime(
    shipments["actual_delivery_date"],
    errors="coerce"
)

shipments["created_date"] = pd.to_datetime(
    shipments["created_date"],
    errors="coerce"
)

shipments["updated_date"] = pd.to_datetime(
    shipments["updated_date"],
    errors="coerce"
)

orders["order_date"] = pd.to_datetime(
    orders["order_date"],
    errors="coerce"
)


# ============================================================
# 1. BASIC STRUCTURE
# ============================================================

print("\n========== SHIPMENT DATA VALIDATION ==========")

print("\nColumns:")
print(shipments.columns.tolist())

print("\nTotal Records:")
print(len(shipments))


# ============================================================
# 2. DUPLICATE SHIPMENT IDs
# ============================================================

duplicate_shipment_ids = (
    shipments["shipment_id"].duplicated().sum()
)

print("\nDuplicate Shipment IDs:")
print(duplicate_shipment_ids)


# ============================================================
# 3. DUPLICATE TRACKING NUMBERS
# ============================================================

duplicate_tracking_numbers = (
    shipments[
        shipments["tracking_number"].notna()
    ]["tracking_number"]
    .duplicated()
    .sum()
)

print("\nDuplicate Tracking Numbers:")
print(duplicate_tracking_numbers)


# ============================================================
# 4. NULL VALUES
# ============================================================

print("\nNull Values:")
print(shipments.isnull().sum())


# ============================================================
# 5. SHIPMENT STATUS
# ============================================================

print("\nShipment Status:")
print(
    shipments["shipment_status"]
    .value_counts(dropna=False)
)


# ============================================================
# 6. SHIPPING METHOD
# ============================================================

print("\nShipping Method:")
print(
    shipments["shipping_method"]
    .value_counts(dropna=False)
)


# ============================================================
# 7. CARRIER
# ============================================================

print("\nCarriers:")
print(
    shipments["carrier"]
    .value_counts(dropna=False)
)


# ============================================================
# 8. INVALID ORDER IDs
# ============================================================

valid_order_ids = set(
    orders["order_id"]
    .astype(str)
)

invalid_order_ids = (
    ~shipments["order_id"]
    .astype(str)
    .isin(valid_order_ids)
)

print("\nInvalid Order IDs:")
print(invalid_order_ids.sum())


# ============================================================
# 9. INVALID WAREHOUSE IDs
# ============================================================

valid_warehouse_ids = set(
    warehouses["warehouse_id"]
    .astype(str)
)

invalid_warehouse_ids = (
    ~shipments["warehouse_id"]
    .astype(str)
    .isin(valid_warehouse_ids)
)

print("\nInvalid Warehouse IDs:")
print(invalid_warehouse_ids.sum())


# ============================================================
# 10. INVALID ADDRESS IDs
# ============================================================

valid_address_ids = set(
    addresses["address_id"]
    .astype(str)
)

invalid_address_ids = (
    ~shipments["shipping_address_id"]
    .astype(str)
    .isin(valid_address_ids)
)

print("\nInvalid Shipping Address IDs:")
print(invalid_address_ids.sum())


# ============================================================
# 11. CUSTOMER ↔ ORDER RELATIONSHIP
# ============================================================

order_customer_map = (
    orders
    .set_index("order_id")["customer_id"]
    .astype(str)
    .to_dict()
)

shipment_customer_from_order = (
    shipments["order_id"]
    .astype(str)
    .map(order_customer_map)
)

customer_order_mismatch = (
    shipment_customer_from_order.notna()
    &
    (
        shipment_customer_from_order
        != shipments["customer_id"].astype(str)
    )
)

print("\nCustomer ↔ Order Mismatches:")
print(customer_order_mismatch.sum())


# ============================================================
# 12. CUSTOMER ↔ ADDRESS RELATIONSHIP
# ============================================================

address_customer_map = (
    addresses
    .set_index("address_id")["customer_id"]
    .astype(str)
    .to_dict()
)

shipment_customer_from_address = (
    shipments["shipping_address_id"]
    .astype(str)
    .map(address_customer_map)
)

customer_address_mismatch = (
    shipment_customer_from_address.notna()
    &
    (
        shipment_customer_from_address
        != shipments["customer_id"].astype(str)
    )
)

print("\nCustomer ↔ Shipping Address Mismatches:")
print(customer_address_mismatch.sum())


# ============================================================
# 13. SHIPMENT DATE BEFORE ORDER DATE
# ============================================================

order_date_map = (
    orders
    .set_index("order_id")["order_date"]
    .to_dict()
)

shipment_order_dates = (
    shipments["order_id"]
    .astype(str)
    .map(
        {
            str(k): v
            for k, v in order_date_map.items()
        }
    )
)

shipment_before_order = (
    shipment_order_dates.notna()
    &
    shipments["shipment_date"].notna()
    &
    (
        shipments["shipment_date"]
        < shipment_order_dates
    )
)

print("\nShipment Date < Order Date:")
print(shipment_before_order.sum())


# ============================================================
# 14. ACTUAL DELIVERY BEFORE SHIPMENT
# ============================================================

delivery_before_shipment = (
    shipments["actual_delivery_date"].notna()
    &
    shipments["shipment_date"].notna()
    &
    (
        shipments["actual_delivery_date"]
        < shipments["shipment_date"]
    )
)

print("\nActual Delivery < Shipment Date:")
print(delivery_before_shipment.sum())


# ============================================================
# 15. FUTURE SHIPMENT DATES
# ============================================================

today = pd.Timestamp.today().normalize()

future_shipments = (
    shipments["shipment_date"] > today
)

print("\nFuture Shipment Dates:")
print(future_shipments.sum())


# ============================================================
# 16. FUTURE DELIVERY DATES
# ============================================================

future_deliveries = (
    shipments["actual_delivery_date"] > today
)

print("\nFuture Actual Delivery Dates:")
print(future_deliveries.sum())


# ============================================================
# 17. INVALID STATUSES
# ============================================================

valid_statuses = {
    "Processing",
    "Shipped",
    "In Transit",
    "Out for Delivery",
    "Delivered",
    "Failed",
    "Returned"
}

invalid_status = (
    ~shipments["shipment_status"]
    .isin(valid_statuses)
)

print("\nInvalid Shipment Status:")
print(invalid_status.sum())


# ============================================================
# 18. FAILED SHIPMENT WITHOUT FAILURE REASON
# ============================================================

failed_without_reason = (
    (shipments["shipment_status"] == "Failed")
    &
    (
        shipments["failure_reason"]
        .isna()
    )
)

print("\nFailed Shipment Without Failure Reason:")
print(failed_without_reason.sum())


# ============================================================
# 19. DELIVERED SHIPMENT WITHOUT ACTUAL DATE
# ============================================================

delivered_without_date = (
    (shipments["shipment_status"] == "Delivered")
    &
    (
        shipments["actual_delivery_date"]
        .isna()
    )
)

print("\nDelivered Shipment Without Actual Delivery Date:")
print(delivered_without_date.sum())


# ============================================================
# 20. NON-DELIVERED SHIPMENT WITH ACTUAL DATE
# ============================================================

non_delivered_with_date = (
    ~shipments["shipment_status"].isin(
        ["Delivered", "Returned"]
    )
    &
    shipments["actual_delivery_date"].notna()
)

print("\nNon-Delivered Shipment With Actual Delivery Date:")
print(non_delivered_with_date.sum())


# ============================================================
# 21. NEGATIVE SHIPPING COST
# ============================================================

negative_shipping_cost = (
    shipments["shipping_cost"] < 0
)

print("\nNegative Shipping Cost:")
print(negative_shipping_cost.sum())


# ============================================================
# 22. INVALID DELIVERY ATTEMPTS
# ============================================================

invalid_delivery_attempts = (
    shipments["delivery_attempts"] < 0
)

print("\nNegative Delivery Attempts:")
print(invalid_delivery_attempts.sum())


# ============================================================
# 23. CURRENCY CONSISTENCY
# ============================================================

order_currency_map = (
    orders
    .set_index("order_id")["currency"]
    .astype(str)
    .to_dict()
)

shipment_order_currency = (
    shipments["order_id"]
    .astype(str)
    .map(order_currency_map)
)

currency_mismatch = (
    shipment_order_currency.notna()
    &
    (
        shipment_order_currency
        != shipments["currency"].astype(str)
    )
)

print("\nShipment ↔ Order Currency Mismatches:")
print(currency_mismatch.sum())


# ============================================================
# 24. BUSINESS SUMMARY
# ============================================================

print("\n==============================================")
print("SHIPMENT VALIDATION SUMMARY")
print("==============================================")

print(
    f"Total Shipments                : {len(shipments)}"
)

print(
    f"Duplicate Shipment IDs         : "
    f"{duplicate_shipment_ids}"
)

print(
    f"Duplicate Tracking Numbers     : "
    f"{duplicate_tracking_numbers}"
)

print(
    f"Invalid Order IDs              : "
    f"{invalid_order_ids.sum()}"
)

print(
    f"Invalid Warehouse IDs          : "
    f"{invalid_warehouse_ids.sum()}"
)

print(
    f"Invalid Address IDs            : "
    f"{invalid_address_ids.sum()}"
)

print(
    f"Customer ↔ Order Mismatch      : "
    f"{customer_order_mismatch.sum()}"
)

print(
    f"Customer ↔ Address Mismatch    : "
    f"{customer_address_mismatch.sum()}"
)

print(
    f"Shipment < Order Date          : "
    f"{shipment_before_order.sum()}"
)

print(
    f"Delivery < Shipment Date       : "
    f"{delivery_before_shipment.sum()}"
)

print(
    f"Future Shipment Dates          : "
    f"{future_shipments.sum()}"
)

print(
    f"Invalid Status                 : "
    f"{invalid_status.sum()}"
)

print(
    f"Failed Without Reason          : "
    f"{failed_without_reason.sum()}"
)

print(
    f"Delivered Without Date         : "
    f"{delivered_without_date.sum()}"
)

print(
    f"Currency Mismatch              : "
    f"{currency_mismatch.sum()}"
)

print("==============================================")