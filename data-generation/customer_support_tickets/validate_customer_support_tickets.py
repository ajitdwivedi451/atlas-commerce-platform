import os
import pandas as pd

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

TICKETS_FILE = os.path.join(
    BASE_DIR,
    "customer_support_tickets",
    "customer_support_tickets.csv"
)

CUSTOMERS_FILE = os.path.join(
    BASE_DIR,
    "customers",
    "customers.csv"
)

ORDERS_FILE = os.path.join(
    BASE_DIR,
    "orders",
    "orders.csv"
)

ORDER_ITEMS_FILE = os.path.join(
    BASE_DIR,
    "order_items",
    "order_items.csv"
)

PRODUCTS_FILE = os.path.join(
    BASE_DIR,
    "products",
    "products.csv"
)

PAYMENTS_FILE = os.path.join(
    BASE_DIR,
    "payments",
    "payments.csv"
)

SHIPMENTS_FILE = os.path.join(
    BASE_DIR,
    "shipments",
    "shipments.csv"
)

RETURNS_FILE = os.path.join(
    BASE_DIR,
    "returns",
    "returns.csv"
)


# ============================================================
# LOAD
# ============================================================

print("Loading datasets...")

tickets = pd.read_csv(
    TICKETS_FILE,
    low_memory=False
)

customers = pd.read_csv(
    CUSTOMERS_FILE,
    low_memory=False
)

orders = pd.read_csv(
    ORDERS_FILE,
    low_memory=False
)

order_items = pd.read_csv(
    ORDER_ITEMS_FILE,
    low_memory=False
)

products = pd.read_csv(
    PRODUCTS_FILE,
    low_memory=False
)

payments = pd.read_csv(
    PAYMENTS_FILE,
    low_memory=False
)

shipments = pd.read_csv(
    SHIPMENTS_FILE,
    low_memory=False
)

returns = pd.read_csv(
    RETURNS_FILE,
    low_memory=False
)

print(f"Tickets loaded: {len(tickets)}")
print(f"Customers loaded: {len(customers)}")
print(f"Orders loaded: {len(orders)}")
print(f"Order Items loaded: {len(order_items)}")
print(f"Products loaded: {len(products)}")
print(f"Payments loaded: {len(payments)}")
print(f"Shipments loaded: {len(shipments)}")
print(f"Returns loaded: {len(returns)}")


# ============================================================
# COLUMN VALIDATION
# ============================================================

print("\n==========================================")
print("CUSTOMER SUPPORT TICKET DATA VALIDATION")
print("==========================================")

print("\nColumns:")
print(tickets.columns.tolist())

print("\nTotal Records:")
print(len(tickets))


# ============================================================
# DUPLICATES
# ============================================================

duplicate_ticket_ids = (
    tickets["ticket_id"].duplicated().sum()
)

print("\nDuplicate Ticket IDs:")
print(duplicate_ticket_ids)


# ============================================================
# NULL VALUES
# ============================================================

print("\nNull Values:")
print(tickets.isnull().sum())


# ============================================================
# VALID VALUES
# ============================================================

valid_categories = {
    "Order",
    "Payment",
    "Delivery",
    "Shipment",
    "Return",
    "Refund",
    "Product",
    "Account",
    "Cancellation",
    "Technical",
    "Other"
}

valid_priorities = {
    "Low",
    "Medium",
    "High",
    "Urgent"
}

valid_channels = {
    "Email",
    "Phone",
    "Chat",
    "Web"
}

valid_statuses = {
    "Open",
    "In Progress",
    "Waiting for Customer",
    "Resolved",
    "Closed",
    "Reopened"
}


invalid_categories = (
    ~tickets["ticket_category"].isin(valid_categories)
).sum()

invalid_priorities = (
    ~tickets["priority"].isin(valid_priorities)
).sum()

invalid_channels = (
    ~tickets["channel"].isin(valid_channels)
).sum()

invalid_statuses = (
    ~tickets["ticket_status"].isin(valid_statuses)
).sum()


print("\nTicket Categories:")
print(
    tickets["ticket_category"].value_counts()
)

print("\nInvalid Ticket Categories:")
print(invalid_categories)

print("\nPriority Distribution:")
print(
    tickets["priority"].value_counts()
)

print("\nInvalid Priorities:")
print(invalid_priorities)

print("\nChannel Distribution:")
print(
    tickets["channel"].value_counts()
)

print("\nInvalid Channels:")
print(invalid_channels)

print("\nTicket Status:")
print(
    tickets["ticket_status"].value_counts()
)

print("\nInvalid Ticket Status:")
print(invalid_statuses)


# ============================================================
# ID VALIDATION
# ============================================================

customer_set = set(
    customers["customer_id"].dropna()
)

order_set = set(
    orders["order_id"].dropna()
)

order_item_set = set(
    order_items["order_item_id"].dropna()
)

product_set = set(
    products["product_id"].dropna()
)

payment_set = set(
    payments["payment_id"].dropna()
)

shipment_set = set(
    shipments["shipment_id"].dropna()
)

return_set = set(
    returns["return_id"].dropna()
)


invalid_customer_ids = (
    ~tickets["customer_id"].isin(customer_set)
).sum()

invalid_order_ids = (
    tickets["order_id"].notna()
    & ~tickets["order_id"].isin(order_set)
).sum()

invalid_order_item_ids = (
    tickets["order_item_id"].notna()
    & ~tickets["order_item_id"].isin(order_item_set)
).sum()

invalid_product_ids = (
    tickets["product_id"].notna()
    & ~tickets["product_id"].isin(product_set)
).sum()

invalid_payment_ids = (
    tickets["payment_id"].notna()
    & ~tickets["payment_id"].isin(payment_set)
).sum()

invalid_shipment_ids = (
    tickets["shipment_id"].notna()
    & ~tickets["shipment_id"].isin(shipment_set)
).sum()

invalid_return_ids = (
    tickets["return_id"].notna()
    & ~tickets["return_id"].isin(return_set)
).sum()


print("\nInvalid Customer IDs:")
print(invalid_customer_ids)

print("\nInvalid Order IDs:")
print(invalid_order_ids)

print("\nInvalid Order Item IDs:")
print(invalid_order_item_ids)

print("\nInvalid Product IDs:")
print(invalid_product_ids)

print("\nInvalid Payment IDs:")
print(invalid_payment_ids)

print("\nInvalid Shipment IDs:")
print(invalid_shipment_ids)

print("\nInvalid Return IDs:")
print(invalid_return_ids)


# ============================================================
# BUSINESS RELATIONSHIP VALIDATION
# ============================================================

order_customer_map = dict(
    zip(
        orders["order_id"],
        orders["customer_id"]
    )
)

order_item_order_map = dict(
    zip(
        order_items["order_item_id"],
        order_items["order_id"]
    )
)

order_item_product_map = dict(
    zip(
        order_items["order_item_id"],
        order_items["product_id"]
    )
)

shipment_order_map = dict(
    zip(
        shipments["shipment_id"],
        shipments["order_id"]
    )
)

return_order_map = dict(
    zip(
        returns["return_id"],
        returns["order_id"]
    )
)


# ------------------------------------------------------------
# Customer ↔ Order
# ------------------------------------------------------------

customer_order_mismatches = 0

for _, row in tickets.iterrows():

    order_id = row["order_id"]

    if pd.isna(order_id):
        continue

    expected_customer = order_customer_map.get(
        order_id
    )

    if (
        expected_customer is not None
        and row["customer_id"] != expected_customer
    ):

        customer_order_mismatches += 1


# ------------------------------------------------------------
# Order Item ↔ Order
# ------------------------------------------------------------

order_item_order_mismatches = 0

for _, row in tickets.iterrows():

    order_item_id = row["order_item_id"]

    if pd.isna(order_item_id):
        continue

    expected_order = order_item_order_map.get(
        order_item_id
    )

    if (
        expected_order is not None
        and row["order_id"] != expected_order
    ):

        order_item_order_mismatches += 1


# ------------------------------------------------------------
# Order Item ↔ Product
# ------------------------------------------------------------

product_order_item_mismatches = 0

for _, row in tickets.iterrows():

    order_item_id = row["order_item_id"]

    if pd.isna(order_item_id):
        continue

    expected_product = order_item_product_map.get(
        order_item_id
    )

    if (
        expected_product is not None
        and row["product_id"] != expected_product
    ):

        product_order_item_mismatches += 1


# ------------------------------------------------------------
# Shipment ↔ Order
# ------------------------------------------------------------

shipment_order_mismatches = 0

for _, row in tickets.iterrows():

    shipment_id = row["shipment_id"]

    if pd.isna(shipment_id):
        continue

    expected_order = shipment_order_map.get(
        shipment_id
    )

    if (
        expected_order is not None
        and row["order_id"] != expected_order
    ):

        shipment_order_mismatches += 1


# ------------------------------------------------------------
# Return ↔ Order
# ------------------------------------------------------------

return_order_mismatches = 0

for _, row in tickets.iterrows():

    return_id = row["return_id"]

    if pd.isna(return_id):
        continue

    expected_order = return_order_map.get(
        return_id
    )

    if (
        expected_order is not None
        and row["order_id"] != expected_order
    ):

        return_order_mismatches += 1


print("\nCustomer ↔ Order Mismatches:")
print(customer_order_mismatches)

print("\nOrder Item ↔ Order Mismatches:")
print(order_item_order_mismatches)

print("\nProduct ↔ Order Item Mismatches:")
print(product_order_item_mismatches)

print("\nShipment ↔ Order Mismatches:")
print(shipment_order_mismatches)

print("\nReturn ↔ Order Mismatches:")
print(return_order_mismatches)


# ============================================================
# DATE VALIDATION
# ============================================================

tickets["ticket_date"] = pd.to_datetime(
    tickets["ticket_date"],
    errors="coerce"
)

tickets["first_response_date"] = pd.to_datetime(
    tickets["first_response_date"],
    errors="coerce"
)

tickets["resolved_date"] = pd.to_datetime(
    tickets["resolved_date"],
    errors="coerce"
)

tickets["created_date"] = pd.to_datetime(
    tickets["created_date"],
    errors="coerce"
)

tickets["updated_date"] = pd.to_datetime(
    tickets["updated_date"],
    errors="coerce"
)

orders["order_date"] = pd.to_datetime(
    orders["order_date"],
    errors="coerce"
)


order_date_map = dict(
    zip(
        orders["order_id"],
        orders["order_date"]
    )
)


ticket_before_order = 0

for _, row in tickets.iterrows():

    order_id = row["order_id"]

    if pd.isna(order_id):
        continue

    order_date = order_date_map.get(
        order_id
    )

    if (
        order_date is not None
        and pd.notna(order_date)
        and pd.notna(row["ticket_date"])
        and row["ticket_date"] < order_date
    ):

        ticket_before_order += 1


future_ticket_dates = (
    tickets["ticket_date"] > pd.Timestamp.today()
).sum()


response_before_ticket = (
    tickets["first_response_date"].notna()
    &
    (
        tickets["first_response_date"]
        < tickets["ticket_date"]
    )
).sum()


resolved_before_ticket = (
    tickets["resolved_date"].notna()
    &
    (
        tickets["resolved_date"]
        < tickets["ticket_date"]
    )
).sum()


resolved_before_response = (
    tickets["resolved_date"].notna()
    &
    tickets["first_response_date"].notna()
    &
    (
        tickets["resolved_date"]
        <
        tickets["first_response_date"]
    )
).sum()


print("\nTicket Date < Order Date:")
print(ticket_before_order)

print("\nFuture Ticket Dates:")
print(future_ticket_dates)

print("\nFirst Response < Ticket Date:")
print(response_before_ticket)

print("\nResolved < Ticket Date:")
print(resolved_before_ticket)

print("\nResolved < First Response:")
print(resolved_before_response)


# ============================================================
# SATISFACTION VALIDATION
# ============================================================

invalid_satisfaction = (
    tickets["customer_satisfaction_score"].notna()
    &
    (
        (tickets["customer_satisfaction_score"] < 1)
        |
        (tickets["customer_satisfaction_score"] > 5)
    )
).sum()


negative_reopened = (
    tickets["reopened_count"] < 0
).sum()


print("\nInvalid Satisfaction Scores:")
print(invalid_satisfaction)

print("\nNegative Reopened Counts:")
print(negative_reopened)


# ============================================================
# STATUS BUSINESS RULES
# ============================================================

open_with_resolved_date = (
    tickets["ticket_status"].isin([
        "Open",
        "In Progress",
        "Waiting for Customer"
    ])
    &
    tickets["resolved_date"].notna()
).sum()


closed_without_resolution = (
    tickets["ticket_status"].isin([
        "Closed",
        "Resolved"
    ])
    &
    tickets["resolved_date"].isna()
).sum()


print("\nOpen/In-Progress Tickets With Resolved Date:")
print(open_with_resolved_date)

print("\nResolved/Closed Tickets Without Resolved Date:")
print(closed_without_resolution)


# ============================================================
# SUMMARY
# ============================================================

print("\n==========================================")
print("SUPPORT TICKET VALIDATION SUMMARY")
print("==========================================")

print(
    f"Total Tickets                  : {len(tickets)}"
)

print(
    f"Duplicate Ticket IDs            : {duplicate_ticket_ids}"
)

print(
    f"Invalid Customer IDs            : {invalid_customer_ids}"
)

print(
    f"Invalid Order IDs               : {invalid_order_ids}"
)

print(
    f"Invalid Order Item IDs          : {invalid_order_item_ids}"
)

print(
    f"Invalid Product IDs             : {invalid_product_ids}"
)

print(
    f"Invalid Payment IDs             : {invalid_payment_ids}"
)

print(
    f"Invalid Shipment IDs            : {invalid_shipment_ids}"
)

print(
    f"Invalid Return IDs              : {invalid_return_ids}"
)

print(
    f"Customer↔Order Mismatch         : {customer_order_mismatches}"
)

print(
    f"OrderItem↔Order Mismatch        : {order_item_order_mismatches}"
)

print(
    f"Product↔OrderItem Mismatch      : {product_order_item_mismatches}"
)

print(
    f"Shipment↔Order Mismatch         : {shipment_order_mismatches}"
)

print(
    f"Return↔Order Mismatch           : {return_order_mismatches}"
)

print(
    f"Ticket Before Order             : {ticket_before_order}"
)

print(
    f"Future Ticket Dates             : {future_ticket_dates}"
)

print(
    f"Invalid Satisfaction            : {invalid_satisfaction}"
)

print(
    f"Negative Reopened Count         : {negative_reopened}"
)

print(
    f"Invalid Status                  : {invalid_statuses}"
)

print(
    f"Invalid Priority               : {invalid_priorities}"
)

print("==========================================")