import os
import random
import pandas as pd
from faker import Faker

fake = Faker()

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

CUSTOMERS_FILE = os.path.join(
    BASE_DIR, "customers", "customers.csv"
)

PRODUCTS_FILE = os.path.join(
    BASE_DIR, "products", "products.csv"
)

ORDERS_FILE = os.path.join(
    BASE_DIR, "orders", "orders.csv"
)

ORDER_ITEMS_FILE = os.path.join(
    BASE_DIR, "order_items", "order_items.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR, "product_reviews"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "product_reviews.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# LOAD EXISTING DATASETS
# ============================================================

print("Loading existing datasets...")

customers_df = pd.read_csv(CUSTOMERS_FILE)
products_df = pd.read_csv(PRODUCTS_FILE)
orders_df = pd.read_csv(ORDERS_FILE)
order_items_df = pd.read_csv(ORDER_ITEMS_FILE)

print(f"Customers loaded: {len(customers_df)}")
print(f"Products loaded: {len(products_df)}")
print(f"Orders loaded: {len(orders_df)}")
print(f"Order Items loaded: {len(order_items_df)}")

# ============================================================
# NORMALIZE DATES
# ============================================================

orders_df["order_date"] = pd.to_datetime(
    orders_df["order_date"],
    errors="coerce"
)

order_items_df["order_id"] = order_items_df["order_id"].astype(str)
order_items_df["product_id"] = order_items_df["product_id"].astype(str)

orders_df["order_id"] = orders_df["order_id"].astype(str)

customers_df["customer_id"] = customers_df["customer_id"].astype(str)
products_df["product_id"] = products_df["product_id"].astype(str)

# ============================================================
# CREATE VALID PURCHASE RELATIONSHIP
#
# Customer -> Order -> Order Item -> Product
# ============================================================

print("\nBuilding valid purchase relationships...")

purchase_df = order_items_df.merge(
    orders_df[
        [
            "order_id",
            "customer_id",
            "order_date",
            "order_status"
        ]
    ],
    on="order_id",
    how="inner"
)

# Only orders that could realistically have a review
eligible_statuses = [
    "Delivered",
    "Returned"
]

purchase_df = purchase_df[
    purchase_df["order_status"].isin(eligible_statuses)
].copy()

# Remove rows with missing critical relationship fields
purchase_df = purchase_df.dropna(
    subset=[
        "order_id",
        "customer_id",
        "product_id",
        "order_item_id",
        "order_date"
    ]
)

print(
    f"Eligible purchase relationships: {len(purchase_df)}"
)

# ============================================================
# GENERATE REVIEWS
# ============================================================

print("\nGenerating realistic product reviews...")

reviews = []

# Approximately 35% of eligible purchases receive a review
review_probability = 0.35

review_statuses = [
    "Published",
    "Published",
    "Published",
    "Pending",
    "Rejected"
]

review_titles = [
    "Great product",
    "Good quality",
    "Worth the price",
    "Very satisfied",
    "Excellent purchase",
    "Good product",
    "Average experience",
    "Not as expected",
    "Could be better",
    "Highly recommended"
]

review_texts = [
    "The product quality is very good and I am satisfied with the purchase.",
    "Good product and the quality is as expected.",
    "The product arrived in good condition and works well.",
    "Overall a good experience. The product matches the description.",
    "The product is useful and worth the price.",
    "Quality is average but the product is usable.",
    "The product was okay but I expected slightly better quality.",
    "Good purchase. Delivery was also smooth.",
    "I am happy with the product and would recommend it.",
    "The product did not completely meet my expectations."
]

review_id_counter = 1

for _, purchase in purchase_df.iterrows():

    # Not every customer leaves a review
    if random.random() > review_probability:
        continue

    order_date = purchase["order_date"]

    # Review normally happens 1-30 days after purchase
    review_date = order_date + pd.Timedelta(
        days=random.randint(1, 30)
    )

    # Do not generate future review dates
    today = pd.Timestamp.today().normalize()

    if review_date > today:
        continue

    rating = random.choices(
        [1, 2, 3, 4, 5],
        weights=[3, 5, 12, 30, 50],
        k=1
    )[0]

    verified_purchase = True

    review = {
        "review_id": f"REV{review_id_counter:08d}",
        "customer_id": purchase["customer_id"],
        "product_id": purchase["product_id"],
        "order_id": purchase["order_id"],
        "order_item_id": purchase["order_item_id"],
        "rating": rating,
        "review_title": random.choice(review_titles),
        "review_text": random.choice(review_texts),
        "review_status": random.choice(review_statuses),
        "verified_purchase": verified_purchase,
        "review_date": review_date.strftime("%Y-%m-%d"),
        "helpful_votes": random.randint(0, 150),
        "reported_count": random.choices(
            [0, 1, 2, 3, 5],
            weights=[85, 8, 4, 2, 1],
            k=1
        )[0],
        "created_date": review_date.strftime("%Y-%m-%d"),
        "updated_date": review_date.strftime("%Y-%m-%d")
    }

    reviews.append(review)

    review_id_counter += 1

# ============================================================
# CREATE DATAFRAME
# ============================================================

reviews_df = pd.DataFrame(reviews)

print(
    f"\nBase product review records generated: "
    f"{len(reviews_df)}"
)

# ============================================================
# CONTROLLED DATA QUALITY ISSUES
# ============================================================

print("\nInjecting controlled data-quality issues...")

original_count = len(reviews_df)

# ------------------------------------------------------------
# A. Duplicate Review IDs
# ------------------------------------------------------------

duplicate_count = int(
    original_count * random.uniform(0.01, 0.02)
)

if duplicate_count > 0:

    duplicate_rows = reviews_df.sample(
        n=duplicate_count,
        random_state=42
    ).copy()

    reviews_df = pd.concat(
        [reviews_df, duplicate_rows],
        ignore_index=True
    )

# ------------------------------------------------------------
# B. NULL Review Text
# ------------------------------------------------------------

null_text_count = int(
    len(reviews_df) * 0.02
)

if null_text_count > 0:

    null_indices = reviews_df.sample(
        n=null_text_count
    ).index

    reviews_df.loc[
        null_indices,
        "review_text"
    ] = None

# ------------------------------------------------------------
# C. Invalid Ratings
# ------------------------------------------------------------

invalid_rating_count = int(
    len(reviews_df) * 0.01
)

if invalid_rating_count > 0:

    invalid_indices = reviews_df.sample(
        n=invalid_rating_count
    ).index

    reviews_df.loc[
        invalid_indices,
        "rating"
    ] = random.choices(
        [0, 6, 7, -1],
        k=invalid_rating_count
    )

# ------------------------------------------------------------
# D. Invalid Review Status
# ------------------------------------------------------------

invalid_status_count = int(
    len(reviews_df) * 0.01
)

if invalid_status_count > 0:

    invalid_indices = reviews_df.sample(
        n=invalid_status_count
    ).index

    reviews_df.loc[
        invalid_indices,
        "review_status"
    ] = random.choices(
        [
            "INVALID",
            "UNKNOWN",
            "Pending_Validation"
        ],
        k=invalid_status_count
    )

# ------------------------------------------------------------
# E. Invalid Customer IDs
# ------------------------------------------------------------

invalid_customer_count = int(
    len(reviews_df) * 0.01
)

if invalid_customer_count > 0:

    invalid_indices = reviews_df.sample(
        n=invalid_customer_count
    ).index

    reviews_df.loc[
        invalid_indices,
        "customer_id"
    ] = [
        f"CUST_INVALID_{i}"
        for i in range(invalid_customer_count)
    ]

# ------------------------------------------------------------
# F. Invalid Product IDs
# ------------------------------------------------------------

invalid_product_count = int(
    len(reviews_df) * 0.01
)

if invalid_product_count > 0:

    invalid_indices = reviews_df.sample(
        n=invalid_product_count
    ).index

    reviews_df.loc[
        invalid_indices,
        "product_id"
    ] = [
        f"PROD_INVALID_{i}"
        for i in range(invalid_product_count)
    ]

# ------------------------------------------------------------
# G. Future Review Dates
# ------------------------------------------------------------

future_date_count = int(
    len(reviews_df) * 0.01
)

if future_date_count > 0:

    future_indices = reviews_df.sample(
        n=future_date_count
    ).index

    for idx in future_indices:

        future_date = fake.date_between(
            start_date="+30d",
            end_date="+2y"
        )

        reviews_df.loc[
            idx,
            "review_date"
        ] = future_date.strftime("%Y-%m-%d")

# ------------------------------------------------------------
# H. Review Before Order Date
# ------------------------------------------------------------

early_review_count = int(
    len(reviews_df) * 0.01
)

if early_review_count > 0:

    early_indices = reviews_df.sample(
        n=early_review_count
    ).index

    reviews_df.loc[
        early_indices,
        "review_date"
    ] = "2020-01-01"

# ------------------------------------------------------------
# I. Negative Helpful Votes
# ------------------------------------------------------------

negative_vote_count = int(
    len(reviews_df) * 0.005
)

if negative_vote_count > 0:

    negative_indices = reviews_df.sample(
        n=negative_vote_count
    ).index

    reviews_df.loc[
        negative_indices,
        "helpful_votes"
    ] = -random.randint(
        1,
        20
    )

# ============================================================
# SHUFFLE
# ============================================================

reviews_df = reviews_df.sample(
    frac=1
).reset_index(drop=True)

# ============================================================
# SAVE
# ============================================================

reviews_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n==========================================")
print("PRODUCT REVIEW GENERATION COMPLETE")
print("==========================================")
print(f"Total reviews: {len(reviews_df)}")
print(f"Saved to: {OUTPUT_FILE}")
print("==========================================")