import os
import pandas as pd

# ============================================================
# PATHS
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

RETURNS_FILE = os.path.join(
    BASE_DIR,
    "returns",
    "returns.csv"
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

SHIPMENTS_FILE = os.path.join(
    BASE_DIR,
    "shipments",
    "shipments.csv"
)

# ============================================================
# LOAD
# ============================================================

print("Loading datasets...")

returns_df = pd.read_csv(
    RETURNS_FILE
)

customers_df = pd.read_csv(
    CUSTOMERS_FILE
)

orders_df = pd.read_csv(
    ORDERS_FILE
)

order_items_df = pd.read_csv(
    ORDER_ITEMS_FILE
)

products_df = pd.read_csv(
    PRODUCTS_FILE
)

shipments_df = pd.read_csv(
    SHIPMENTS_FILE
)

print(
    f"Returns loaded: {len(returns_df)}"
)

print(
    f"Customers loaded: {len(customers_df)}"
)

print(
    f"Orders loaded: {len(orders_df)}"
)

print(
    f"Order Items loaded: {len(order_items_df)}"
)

print(
    f"Products loaded: {len(products_df)}"
)

print(
    f"Shipments loaded: {len(shipments_df)}"
)

# ============================================================
# NORMALIZE IDs
# ============================================================

for df, columns in [
    (
        returns_df,
        [
            "return_id",
            "customer_id",
            "order_id",
            "order_item_id",
            "product_id",
            "shipment_id"
        ]
    ),
    (
        customers_df,
        ["customer_id"]
    ),
    (
        orders_df,
        ["order_id", "customer_id"]
    ),
    (
        order_items_df,
        [
            "order_item_id",
            "order_id",
            "product_id"
        ]
    ),
    (
        products_df,
        ["product_id"]
    ),
    (
        shipments_df,
        [
            "shipment_id",
            "order_id"
        ]
    )
]:

    for column in columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
            )

# ============================================================
# DATE CONVERSION
# ============================================================

date_columns = [
    "return_date",
    "pickup_date",
    "received_date",
    "created_date",
    "updated_date"
]

for column in date_columns:

    returns_df[column] = pd.to_datetime(
        returns_df[column],
        errors="coerce"
    )

orders_df["order_date"] = pd.to_datetime(
    orders_df["order_date"],
    errors="coerce"
)

shipments_df["shipment_date"] = pd.to_datetime(
    shipments_df["shipment_date"],
    errors="coerce"
)

shipments_df[
    "actual_delivery_date"
] = pd.to_datetime(
    shipments_df[
        "actual_delivery_date"
    ],
    errors="coerce"
)

# ============================================================
# LOOKUPS
# ============================================================

customer_ids = set(
    customers_df["customer_id"]
)

order_ids = set(
    orders_df["order_id"]
)

order_item_ids = set(
    order_items_df["order_item_id"]
)

product_ids = set(
    products_df["product_id"]
)

shipment_ids = set(
    shipments_df["shipment_id"]
)

# ============================================================
# VALIDATION HEADER
# ============================================================

print()
print("==========================================")
print("RETURN DATA VALIDATION")
print("==========================================")

print()
print("Columns:")
print(
    list(returns_df.columns)
)

print()
print("Total Records:")
print(len(returns_df))

# ============================================================
# DUPLICATE RETURN IDS
# ============================================================

duplicate_return_ids = (
    returns_df["return_id"]
    .duplicated()
    .sum()
)

print()
print("Duplicate Return IDs:")
print(duplicate_return_ids)

# ============================================================
# DUPLICATE BUSINESS KEYS
# ============================================================

duplicate_business_keys = (
    returns_df[
        [
            "customer_id",
            "order_id",
            "order_item_id"
        ]
    ]
    .duplicated()
    .sum()
)

print(
    "Duplicate Customer + Order + Order Item:"
)

print(
    duplicate_business_keys
)

# ============================================================
# NULL VALUES
# ============================================================

print()
print("Null Values:")
print(
    returns_df.isnull().sum()
)

# ============================================================
# RETURN STATUS
# ============================================================

print()
print("Return Status:")
print(
    returns_df[
        "return_status"
    ].value_counts()
)

valid_statuses = {
    "Requested",
    "Approved",
    "Pickup_Scheduled",
    "Picked_Up",
    "Received",
    "Inspected",
    "Refunded",
    "Rejected",
    "Cancelled"
}

invalid_status = (
    ~returns_df[
        "return_status"
    ].isin(valid_statuses)
).sum()

print()
print("Invalid Return Status:")
print(invalid_status)

# ============================================================
# RETURN TYPE
# ============================================================

print()
print("Return Type:")
print(
    returns_df[
        "return_type"
    ].value_counts()
)

valid_types = {
    "Refund",
    "Replacement",
    "Exchange"
}

invalid_types = (
    ~returns_df[
        "return_type"
    ].isin(valid_types)
).sum()

print()
print("Invalid Return Type:")
print(invalid_types)

# ============================================================
# INVALID CUSTOMER IDs
# ============================================================

invalid_customers = (
    ~returns_df[
        "customer_id"
    ].isin(customer_ids)
).sum()

print()
print("Invalid Customer IDs:")
print(invalid_customers)

# ============================================================
# INVALID ORDER IDs
# ============================================================

invalid_orders = (
    ~returns_df[
        "order_id"
    ].isin(order_ids)
).sum()

print()
print("Invalid Order IDs:")
print(invalid_orders)

# ============================================================
# INVALID ORDER ITEM IDs
# ============================================================

invalid_order_items = (
    ~returns_df[
        "order_item_id"
    ].isin(order_item_ids)
).sum()

print()
print("Invalid Order Item IDs:")
print(invalid_order_items)

# ============================================================
# INVALID PRODUCT IDs
# ============================================================

invalid_products = (
    ~returns_df[
        "product_id"
    ].isin(product_ids)
).sum()

print()
print("Invalid Product IDs:")
print(invalid_products)

# ============================================================
# INVALID SHIPMENT IDs
# ============================================================

valid_shipment_values = (
    returns_df["shipment_id"]
    .isna()
    |
    returns_df["shipment_id"]
    .isin(shipment_ids)
)

invalid_shipments = (
    ~valid_shipment_values
).sum()

print()
print("Invalid Shipment IDs:")
print(invalid_shipments)

# ============================================================
# CUSTOMER ↔ ORDER MISMATCH
# ============================================================

order_customer_map = (
    orders_df
    .drop_duplicates("order_id")
    .set_index("order_id")[
        "customer_id"
    ]
    .to_dict()
)

customer_order_mismatch = 0

for _, row in returns_df.iterrows():

    order_id = row["order_id"]

    if order_id in order_customer_map:

        expected_customer = (
            order_customer_map[
                order_id
            ]
        )

        if (
            row["customer_id"]
            != expected_customer
        ):

            customer_order_mismatch += 1

print()
print(
    "Customer ↔ Order Mismatches:"
)

print(
    customer_order_mismatch
)

# ============================================================
# ORDER ITEM ↔ ORDER
# ============================================================

order_item_order_map = (
    order_items_df
    .drop_duplicates(
        "order_item_id"
    )
    .set_index(
        "order_item_id"
    )[
        "order_id"
    ]
    .to_dict()
)

order_item_order_mismatch = 0

for _, row in returns_df.iterrows():

    item_id = row["order_item_id"]

    if item_id in order_item_order_map:

        expected_order = (
            order_item_order_map[
                item_id
            ]
        )

        if (
            row["order_id"]
            != expected_order
        ):

            order_item_order_mismatch += 1

print()
print(
    "Order Item ↔ Order Mismatches:"
)

print(
    order_item_order_mismatch
)

# ============================================================
# PRODUCT ↔ ORDER ITEM
# ============================================================

order_item_product_map = (
    order_items_df
    .drop_duplicates(
        "order_item_id"
    )
    .set_index(
        "order_item_id"
    )[
        "product_id"
    ]
    .to_dict()
)

product_order_item_mismatch = 0

for _, row in returns_df.iterrows():

    item_id = row["order_item_id"]

    if item_id in order_item_product_map:

        expected_product = (
            order_item_product_map[
                item_id
            ]
        )

        if (
            row["product_id"]
            != expected_product
        ):

            product_order_item_mismatch += 1

print()
print(
    "Product ↔ Order Item Mismatches:"
)

print(
    product_order_item_mismatch
)

# ============================================================
# RETURN DATE < ORDER DATE
# ============================================================

order_date_map = (
    orders_df
    .drop_duplicates("order_id")
    .set_index("order_id")[
        "order_date"
    ]
    .to_dict()
)

return_before_order = 0

for _, row in returns_df.iterrows():

    order_id = row["order_id"]

    if order_id in order_date_map:

        order_date = (
            order_date_map[
                order_id
            ]
        )

        return_date = row[
            "return_date"
        ]

        if (
            pd.notna(return_date)
            and pd.notna(order_date)
            and return_date < order_date
        ):

            return_before_order += 1

print()
print(
    "Return Date < Order Date:"
)

print(
    return_before_order
)

# ============================================================
# FUTURE RETURN DATE
# ============================================================

today = pd.Timestamp.today().normalize()

future_returns = (
    returns_df[
        "return_date"
    ] > today
).sum()

print()
print("Future Return Dates:")
print(future_returns)

# ============================================================
# RECEIVED DATE < RETURN DATE
# ============================================================

invalid_received_dates = (
    (
        returns_df[
            "received_date"
        ].notna()
    )
    &
    (
        returns_df[
            "return_date"
        ].notna()
    )
    &
    (
        returns_df[
            "received_date"
        ]
        <
        returns_df[
            "return_date"
        ]
    )
).sum()

print()
print(
    "Received Date < Return Date:"
)

print(
    invalid_received_dates
)

# ============================================================
# NEGATIVE / ZERO QUANTITY
# ============================================================

negative_quantity = (
    pd.to_numeric(
        returns_df[
            "quantity_returned"
        ],
        errors="coerce"
    ) < 0
).sum()

zero_quantity = (
    pd.to_numeric(
        returns_df[
            "quantity_returned"
        ],
        errors="coerce"
    ) == 0
).sum()

print()
print("Negative Quantity Returned:")
print(negative_quantity)

print()
print("Zero Quantity Returned:")
print(zero_quantity)

# ============================================================
# QUANTITY > ORDERED QUANTITY
# ============================================================

ordered_quantity_map = (
    pd.to_numeric(
        order_items_df.get(
            "quantity",
            pd.Series(
                1,
                index=order_items_df.index
            )
        ),
        errors="coerce"
    )
)

temp_order_items = (
    order_items_df.copy()
)

if "quantity" in temp_order_items.columns:

    temp_order_items[
        "quantity"
    ] = pd.to_numeric(
        temp_order_items[
            "quantity"
        ],
        errors="coerce"
    )

else:

    temp_order_items[
        "quantity"
    ] = 1

quantity_map = (
    temp_order_items
    .drop_duplicates(
        "order_item_id"
    )
    .set_index(
        "order_item_id"
    )[
        "quantity"
    ]
    .to_dict()
)

quantity_exceeds_ordered = 0

for _, row in returns_df.iterrows():

    item_id = row[
        "order_item_id"
    ]

    if item_id in quantity_map:

        returned_qty = pd.to_numeric(
            row[
                "quantity_returned"
            ],
            errors="coerce"
        )

        ordered_qty = quantity_map[
            item_id
        ]

        if (
            pd.notna(returned_qty)
            and pd.notna(ordered_qty)
            and returned_qty > ordered_qty
        ):

            quantity_exceeds_ordered += 1

print()
print(
    "Returned Quantity > Ordered Quantity:"
)

print(
    quantity_exceeds_ordered
)

# ============================================================
# NEGATIVE REFUND
# ============================================================

refund_amounts = pd.to_numeric(
    returns_df[
        "refund_amount"
    ],
    errors="coerce"
)

negative_refunds = (
    refund_amounts < 0
).sum()

print()
print("Negative Refund Amount:")
print(negative_refunds)

# ============================================================
# REFUND CURRENCY
# ============================================================

print()
print("Refund Currencies:")
print(
    returns_df[
        "refund_currency"
    ].value_counts()
)

# ============================================================
# REFUNDED WITHOUT REFUND AMOUNT
# ============================================================

refunded_without_amount = (
    (
        returns_df[
            "return_status"
        ] == "Refunded"
    )
    &
    (
        returns_df[
            "refund_amount"
        ].fillna(0) <= 0
    )
).sum()

print()
print(
    "Refunded Returns Without Refund Amount:"
)

print(
    refunded_without_amount
)

# ============================================================
# REPLACEMENT / EXCHANGE WITH REFUND
# ============================================================

replacement_with_refund = (
    (
        returns_df[
            "return_type"
        ].isin(
            [
                "Replacement",
                "Exchange"
            ]
        )
    )
    &
    (
        returns_df[
            "refund_amount"
        ].fillna(0) > 0
    )
).sum()

print()
print(
    "Replacement/Exchange With Refund:"
)

print(
    replacement_with_refund
)

# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("==========================================")
print("RETURN VALIDATION SUMMARY")
print("==========================================")

print(
    f"Total Returns                  : "
    f"{len(returns_df)}"
)

print(
    f"Duplicate Return IDs           : "
    f"{duplicate_return_ids}"
)

print(
    f"Duplicate Business Keys        : "
    f"{duplicate_business_keys}"
)

print(
    f"Invalid Customer IDs           : "
    f"{invalid_customers}"
)

print(
    f"Invalid Order IDs              : "
    f"{invalid_orders}"
)

print(
    f"Invalid Order Item IDs         : "
    f"{invalid_order_items}"
)

print(
    f"Invalid Product IDs            : "
    f"{invalid_products}"
)

print(
    f"Invalid Shipment IDs           : "
    f"{invalid_shipments}"
)

print(
    f"Customer↔Order Mismatch        : "
    f"{customer_order_mismatch}"
)

print(
    f"OrderItem↔Order Mismatch       : "
    f"{order_item_order_mismatch}"
)

print(
    f"Product↔OrderItem Mismatch     : "
    f"{product_order_item_mismatch}"
)

print(
    f"Return Before Order            : "
    f"{return_before_order}"
)

print(
    f"Future Return Dates            : "
    f"{future_returns}"
)

print(
    f"Received Before Return         : "
    f"{invalid_received_dates}"
)

print(
    f"Negative Quantity              : "
    f"{negative_quantity}"
)

print(
    f"Quantity > Ordered             : "
    f"{quantity_exceeds_ordered}"
)

print(
    f"Negative Refund                : "
    f"{negative_refunds}"
)

print(
    f"Invalid Status                 : "
    f"{invalid_status}"
)

print(
    f"Invalid Return Type            : "
    f"{invalid_types}"
)

print("==========================================")