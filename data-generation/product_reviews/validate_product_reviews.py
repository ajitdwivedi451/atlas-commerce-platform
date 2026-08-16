import os
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

REVIEWS_FILE = os.path.join(
    BASE_DIR,
    "product_reviews",
    "product_reviews.csv"
)

CUSTOMERS_FILE = os.path.join(
    BASE_DIR,
    "customers",
    "customers.csv"
)

PRODUCTS_FILE = os.path.join(
    BASE_DIR,
    "products",
    "products.csv"
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

# ============================================================
# LOAD DATA
# ============================================================

print("Loading datasets...")

reviews = pd.read_csv(REVIEWS_FILE)
customers = pd.read_csv(CUSTOMERS_FILE)
products = pd.read_csv(PRODUCTS_FILE)
orders = pd.read_csv(ORDERS_FILE)
order_items = pd.read_csv(ORDER_ITEMS_FILE)

print(f"Reviews loaded: {len(reviews)}")
print(f"Customers loaded: {len(customers)}")
print(f"Products loaded: {len(products)}")
print(f"Orders loaded: {len(orders)}")
print(f"Order Items loaded: {len(order_items)}")

# ============================================================
# NORMALIZE IDs
# ============================================================

reviews["customer_id"] = reviews["customer_id"].astype(str)
reviews["product_id"] = reviews["product_id"].astype(str)
reviews["order_id"] = reviews["order_id"].astype(str)
reviews["order_item_id"] = reviews["order_item_id"].astype(str)

customers["customer_id"] = customers["customer_id"].astype(str)
products["product_id"] = products["product_id"].astype(str)
orders["order_id"] = orders["order_id"].astype(str)
orders["customer_id"] = orders["customer_id"].astype(str)

order_items["order_id"] = order_items["order_id"].astype(str)
order_items["order_item_id"] = order_items[
    "order_item_id"
].astype(str)
order_items["product_id"] = order_items[
    "product_id"
].astype(str)

# ============================================================
# DATE CONVERSION
# ============================================================

reviews["review_date"] = pd.to_datetime(
    reviews["review_date"],
    errors="coerce"
)

reviews["created_date"] = pd.to_datetime(
    reviews["created_date"],
    errors="coerce"
)

reviews["updated_date"] = pd.to_datetime(
    reviews["updated_date"],
    errors="coerce"
)

orders["order_date"] = pd.to_datetime(
    orders["order_date"],
    errors="coerce"
)

# ============================================================
# BASIC VALIDATION
# ============================================================

print("\n==========================================")
print("PRODUCT REVIEW DATA VALIDATION")
print("==========================================")

print("\nColumns:")
print(list(reviews.columns))

print("\nTotal Records:")
print(len(reviews))

# ============================================================
# DUPLICATE REVIEW IDs
# ============================================================

duplicate_review_ids = (
    reviews["review_id"].duplicated().sum()
)

print("\nDuplicate Review IDs:")
print(duplicate_review_ids)

# ============================================================
# DUPLICATE CUSTOMER + PRODUCT + ORDER ITEM
# ============================================================

duplicate_business_keys = reviews.duplicated(
    subset=[
        "customer_id",
        "product_id",
        "order_id",
        "order_item_id"
    ]
).sum()

print("\nDuplicate Customer + Product + Order Item:")
print(duplicate_business_keys)

# ============================================================
# NULL VALUES
# ============================================================

print("\nNull Values:")
print(reviews.isnull().sum())

# ============================================================
# RATINGS
# ============================================================

print("\nRating Distribution:")
print(reviews["rating"].value_counts(dropna=False).sort_index())

invalid_ratings = (
    ~reviews["rating"].between(1, 5)
).sum()

print("\nInvalid Ratings:")
print(invalid_ratings)

# ============================================================
# REVIEW STATUS
# ============================================================

print("\nReview Status:")
print(reviews["review_status"].value_counts())

valid_statuses = [
    "Published",
    "Pending",
    "Rejected"
]

invalid_status = (
    ~reviews["review_status"].isin(valid_statuses)
).sum()

print("\nInvalid Review Status:")
print(invalid_status)

# ============================================================
# INVALID CUSTOMER IDs
# ============================================================

valid_customer_ids = set(
    customers["customer_id"]
)

invalid_customer_ids = (
    ~reviews["customer_id"].isin(valid_customer_ids)
).sum()

print("\nInvalid Customer IDs:")
print(invalid_customer_ids)

# ============================================================
# INVALID PRODUCT IDs
# ============================================================

valid_product_ids = set(
    products["product_id"]
)

invalid_product_ids = (
    ~reviews["product_id"].isin(valid_product_ids)
).sum()

print("\nInvalid Product IDs:")
print(invalid_product_ids)

# ============================================================
# INVALID ORDER IDs
# ============================================================

valid_order_ids = set(
    orders["order_id"]
)

invalid_order_ids = (
    ~reviews["order_id"].isin(valid_order_ids)
).sum()

print("\nInvalid Order IDs:")
print(invalid_order_ids)

# ============================================================
# INVALID ORDER ITEM IDs
# ============================================================

valid_order_item_ids = set(
    order_items["order_item_id"]
)

invalid_order_item_ids = (
    ~reviews["order_item_id"].isin(
        valid_order_item_ids
    )
).sum()

print("\nInvalid Order Item IDs:")
print(invalid_order_item_ids)

# ============================================================
# CUSTOMER ↔ ORDER MISMATCH
# ============================================================

review_order = reviews.merge(
    orders[
        [
            "order_id",
            "customer_id"
        ]
    ],
    on="order_id",
    how="left",
    suffixes=(
        "_review",
        "_order"
    )
)

customer_order_mismatch = (
    review_order["customer_id_review"]
    != review_order["customer_id_order"]
).sum()

print("\nCustomer ↔ Order Mismatches:")
print(customer_order_mismatch)

# ============================================================
# PRODUCT ↔ ORDER ITEM MISMATCH
# ============================================================

review_item = reviews.merge(
    order_items[
        [
            "order_item_id",
            "order_id",
            "product_id"
        ]
    ],
    on="order_item_id",
    how="left",
    suffixes=(
        "_review",
        "_item"
    )
)

product_order_item_mismatch = (
    review_item["product_id_review"]
    != review_item["product_id_item"]
).sum()

print("\nProduct ↔ Order Item Mismatches:")
print(product_order_item_mismatch)

# ============================================================
# ORDER ↔ ORDER ITEM MISMATCH
# ============================================================

order_item_order_mismatch = (
    review_item["order_id_review"]
    != review_item["order_id_item"]
).sum()

print("\nOrder ↔ Order Item Mismatches:")
print(order_item_order_mismatch)

# ============================================================
# REVIEW DATE < ORDER DATE
# ============================================================

review_dates = reviews.merge(
    orders[
        [
            "order_id",
            "order_date"
        ]
    ],
    on="order_id",
    how="left"
)

review_before_order = (
    review_dates["review_date"]
    < review_dates["order_date"]
).sum()

print("\nReview Date < Order Date:")
print(review_before_order)

# ============================================================
# FUTURE REVIEW DATES
# ============================================================

today = pd.Timestamp.today().normalize()

future_reviews = (
    reviews["review_date"] > today
).sum()

print("\nFuture Review Dates:")
print(future_reviews)

# ============================================================
# NEGATIVE HELPFUL VOTES
# ============================================================

negative_helpful_votes = (
    reviews["helpful_votes"] < 0
).sum()

print("\nNegative Helpful Votes:")
print(negative_helpful_votes)

# ============================================================
# NEGATIVE REPORTED COUNT
# ============================================================

negative_reported_count = (
    reviews["reported_count"] < 0
).sum()

print("\nNegative Reported Count:")
print(negative_reported_count)

# ============================================================
# VERIFIED PURCHASE CHECK
# ============================================================

verified_reviews = reviews[
    reviews["verified_purchase"] == True
].copy()

verified_purchase_relationships = verified_reviews.merge(
    order_items[
        [
            "order_item_id",
            "order_id",
            "product_id"
        ]
    ],
    on="order_item_id",
    how="left",
    suffixes=(
        "_review",
        "_item"
    )
)

invalid_verified_purchase = (
    (
        verified_purchase_relationships[
            "order_id_review"
        ]
        !=
        verified_purchase_relationships[
            "order_id_item"
        ]
    )
    |
    (
        verified_purchase_relationships[
            "product_id_review"
        ]
        !=
        verified_purchase_relationships[
            "product_id_item"
        ]
    )
).sum()

print("\nInvalid Verified Purchases:")
print(invalid_verified_purchase)

# ============================================================
# REVIEW DATE AFTER CREATED DATE
# ============================================================

invalid_created_date = (
    reviews["review_date"]
    < reviews["created_date"]
).sum()

print("\nReview Date < Created Date:")
print(invalid_created_date)

# ============================================================
# UPDATED DATE BEFORE CREATED DATE
# ============================================================

invalid_updated_date = (
    reviews["updated_date"]
    < reviews["created_date"]
).sum()

print("\nUpdated Date < Created Date:")
print(invalid_updated_date)

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n==========================================")
print("PRODUCT REVIEW VALIDATION SUMMARY")
print("==========================================")

print(
    f"Total Reviews                 : {len(reviews)}"
)
print(
    f"Duplicate Review IDs          : {duplicate_review_ids}"
)
print(
    f"Duplicate Business Keys       : {duplicate_business_keys}"
)
print(
    f"Invalid Ratings               : {invalid_ratings}"
)
print(
    f"Invalid Status                : {invalid_status}"
)
print(
    f"Invalid Customer IDs          : {invalid_customer_ids}"
)
print(
    f"Invalid Product IDs           : {invalid_product_ids}"
)
print(
    f"Invalid Order IDs             : {invalid_order_ids}"
)
print(
    f"Invalid Order Item IDs        : {invalid_order_item_ids}"
)
print(
    f"Customer↔Order Mismatch       : {customer_order_mismatch}"
)
print(
    f"Product↔OrderItem Mismatch    : {product_order_item_mismatch}"
)
print(
    f"Order↔OrderItem Mismatch      : {order_item_order_mismatch}"
)
print(
    f"Review Before Order           : {review_before_order}"
)
print(
    f"Future Review Dates           : {future_reviews}"
)
print(
    f"Negative Helpful Votes        : {negative_helpful_votes}"
)
print(
    f"Invalid Verified Purchases    : {invalid_verified_purchase}"
)

print("==========================================")