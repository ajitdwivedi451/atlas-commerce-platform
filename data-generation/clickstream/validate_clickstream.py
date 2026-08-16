import os
import random
import uuid
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

CUSTOMER_FILE = os.path.join(
    BASE_DIR, "customers", "customers.csv"
)

PRODUCT_FILE = os.path.join(
    BASE_DIR, "products", "products.csv"
)

ORDER_FILE = os.path.join(
    BASE_DIR, "orders", "orders.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR, "clickstream"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "clickstream_events.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_EVENTS = 500_000

# ============================================================
# LOAD EXISTING DATASETS
# ============================================================

print("Loading existing datasets...")

customers_df = pd.read_csv(CUSTOMER_FILE)
products_df = pd.read_csv(PRODUCT_FILE)
orders_df = pd.read_csv(ORDER_FILE)

print(f"Customers loaded: {len(customers_df)}")
print(f"Products loaded: {len(products_df)}")
print(f"Orders loaded: {len(orders_df)}")

# ============================================================
# NORMALIZE DATES
# ============================================================

customers_df["registration_date"] = pd.to_datetime(
    customers_df["registration_date"],
    errors="coerce"
)

orders_df["order_date"] = pd.to_datetime(
    orders_df["order_date"],
    errors="coerce"
)

# ============================================================
# BUILD LOOKUP STRUCTURES
# ============================================================

customer_records = customers_df.to_dict("records")
product_ids = products_df["product_id"].dropna().tolist()

# Only valid orders
orders_df = orders_df[
    orders_df["customer_id"].isin(
        customers_df["customer_id"]
    )
].copy()

order_records = orders_df.to_dict("records")

# Customer -> Orders mapping
customer_orders = {}

for order in order_records:

    customer_id = order["customer_id"]

    customer_orders.setdefault(
        customer_id,
        []
    ).append(order)

# Customer lookup
customer_lookup = {
    row["customer_id"]: row
    for row in customer_records
}

# Product lookup
product_lookup = {
    row["product_id"]: row
    for row in products_df.to_dict("records")
}

# ============================================================
# EVENT TYPES
# ============================================================

EVENT_TYPES = [
    "PAGE_VIEW",
    "PRODUCT_VIEW",
    "SEARCH",
    "CATEGORY_VIEW",
    "ADD_TO_CART",
    "REMOVE_FROM_CART",
    "WISHLIST_ADD",
    "WISHLIST_REMOVE",
    "CHECKOUT_STARTED",
    "PAYMENT_STARTED",
    "PURCHASE",
    "LOGIN",
    "LOGOUT"
]

EVENT_WEIGHTS = [
    30,
    25,
    10,
    8,
    7,
    3,
    3,
    1,
    3,
    2,
    2,
    2,
    1
]

# ============================================================
# DEVICE / BROWSER / OS
# ============================================================

DEVICE_TYPES = [
    "Mobile",
    "Desktop",
    "Tablet"
]

DEVICE_WEIGHTS = [
    60,
    30,
    10
]

MOBILE_BROWSERS = [
    "Chrome Mobile",
    "Safari Mobile",
    "Samsung Internet"
]

DESKTOP_BROWSERS = [
    "Chrome",
    "Edge",
    "Firefox",
    "Safari"
]

TABLET_BROWSERS = [
    "Chrome",
    "Safari"
]

MOBILE_OS = [
    "Android",
    "iOS"
]

DESKTOP_OS = [
    "Windows",
    "macOS",
    "Linux"
]

TABLET_OS = [
    "iPadOS",
    "Android"
]

# ============================================================
# TRAFFIC SOURCES
# ============================================================

TRAFFIC_SOURCES = [
    "Organic Search",
    "Paid Search",
    "Direct",
    "Social",
    "Email",
    "Affiliate",
    "Referral"
]

TRAFFIC_WEIGHTS = [
    30,
    15,
    25,
    10,
    8,
    5,
    7
]

# ============================================================
# PAGE TYPES
# ============================================================

PAGE_URLS = [
    "/",
    "/home",
    "/products",
    "/category",
    "/search",
    "/cart",
    "/checkout",
    "/wishlist",
    "/account",
    "/offers"
]

# ============================================================
# CAMPAIGNS
# ============================================================

CAMPAIGNS = [
    "CMP-2026-001",
    "CMP-2026-002",
    "CMP-2026-003",
    "CMP-2026-004",
    "CMP-2026-005",
    "CMP-2026-006",
    "CMP-2026-007",
    "CMP-2026-008"
]

# ============================================================
# SEARCH TERMS
# ============================================================

SEARCH_TERMS = [
    "laptop",
    "smartphone",
    "headphones",
    "running shoes",
    "t shirt",
    "watch",
    "backpack",
    "camera",
    "television",
    "gaming",
    "wireless earbuds",
    "office chair"
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_session_id():

    return f"SES-{uuid.uuid4().hex[:12].upper()}"


def generate_event_id():

    return f"EVT-{uuid.uuid4().hex.upper()}"


def generate_ip():

    return fake.ipv4_public()


def choose_device():

    return random.choices(
        DEVICE_TYPES,
        weights=DEVICE_WEIGHTS,
        k=1
    )[0]


def choose_browser_os(device):

    if device == "Mobile":

        browser = random.choice(
            MOBILE_BROWSERS
        )

        operating_system = random.choice(
            MOBILE_OS
        )

    elif device == "Tablet":

        browser = random.choice(
            TABLET_BROWSERS
        )

        operating_system = random.choice(
            TABLET_OS
        )

    else:

        browser = random.choice(
            DESKTOP_BROWSERS
        )

        operating_system = random.choice(
            DESKTOP_OS
        )

    return browser, operating_system


def generate_timestamp(customer):

    registration_date = customer["registration_date"]

    if pd.isna(registration_date):

        start_date = datetime.now() - timedelta(days=365)

    else:

        start_date = registration_date.to_pydatetime()

    end_date = datetime.now()

    if start_date > end_date:

        start_date = end_date - timedelta(days=365)

    return fake.date_time_between(
        start_date=start_date,
        end_date=end_date
    )


# ============================================================
# GENERATION
# ============================================================

print()
print("Generating realistic clickstream events...")
print()

events = []

for i in range(NUM_EVENTS):

    # --------------------------------------------------------
    # SELECT CUSTOMER
    # --------------------------------------------------------

    customer = random.choice(
        customer_records
    )

    customer_id = customer["customer_id"]

    # --------------------------------------------------------
    # SESSION
    # --------------------------------------------------------

    session_id = generate_session_id()

    # --------------------------------------------------------
    # EVENT TYPE
    # --------------------------------------------------------

    event_type = random.choices(
        EVENT_TYPES,
        weights=EVENT_WEIGHTS,
        k=1
    )[0]

    # --------------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------------

    event_timestamp = generate_timestamp(
        customer
    )

    event_date = event_timestamp.date()

    # --------------------------------------------------------
    # DEVICE
    # --------------------------------------------------------

    device_type = choose_device()

    browser, operating_system = choose_browser_os(
        device_type
    )

    # --------------------------------------------------------
    # TRAFFIC SOURCE
    # --------------------------------------------------------

    traffic_source = random.choices(
        TRAFFIC_SOURCES,
        weights=TRAFFIC_WEIGHTS,
        k=1
    )[0]

    # Campaign only for marketing traffic
    if traffic_source in [
        "Paid Search",
        "Social",
        "Email",
        "Affiliate"
    ]:

        campaign_id = random.choice(
            CAMPAIGNS
        )

    else:

        campaign_id = None

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    product_id = None

    if event_type in [
        "PRODUCT_VIEW",
        "ADD_TO_CART",
        "REMOVE_FROM_CART",
        "WISHLIST_ADD",
        "WISHLIST_REMOVE",
        "CHECKOUT_STARTED",
        "PAYMENT_STARTED",
        "PURCHASE"
    ]:

        product_id = random.choice(
            product_ids
        )

    elif random.random() < 0.25:

        product_id = random.choice(
            product_ids
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    order_id = None

    customer_customer_orders = customer_orders.get(
        customer_id,
        []
    )

    if event_type == "PURCHASE":

        if customer_customer_orders:

            selected_order = random.choice(
                customer_customer_orders
            )

            order_id = selected_order["order_id"]

            # Purchase should happen after order
            order_date = selected_order["order_date"]

            if pd.notna(order_date):

                min_time = order_date.to_pydatetime()

                max_time = datetime.now()

                if min_time <= max_time:

                    event_timestamp = fake.date_time_between(
                        start_date=min_time,
                        end_date=max_time
                    )

                    event_date = event_timestamp.date()

    # Some checkout/payment events can be associated with orders
    elif event_type in [
        "CHECKOUT_STARTED",
        "PAYMENT_STARTED"
    ]:

        if customer_customer_orders and random.random() < 0.30:

            selected_order = random.choice(
                customer_customer_orders
            )

            order_id = selected_order["order_id"]

    # --------------------------------------------------------
    # SEARCH QUERY
    # --------------------------------------------------------

    if event_type == "SEARCH":

        search_query = random.choice(
            SEARCH_TERMS
        )

    else:

        search_query = None

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    if event_type in [
        "ADD_TO_CART",
        "REMOVE_FROM_CART",
        "PURCHASE"
    ]:

        quantity = random.randint(
            1,
            5
        )

    else:

        quantity = None

    # --------------------------------------------------------
    # EVENT VALUE / CURRENCY
    # --------------------------------------------------------

    event_value = None
    currency = None

    if product_id and product_id in product_lookup:

        product = product_lookup[
            product_id
        ]

        currency = product.get(
            "currency"
        )

        if event_type in [
            "ADD_TO_CART",
            "PURCHASE"
        ]:

            try:

                price = float(
                    product["unit_price"]
                )

                if quantity:

                    event_value = round(
                        price * quantity,
                        2
                    )

            except:

                event_value = None

    # --------------------------------------------------------
    # CREATE EVENT
    # --------------------------------------------------------

    event = {

        "event_id":
            generate_event_id(),

        "customer_id":
            customer_id,

        "session_id":
            session_id,

        "event_timestamp":
            event_timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "event_date":
            event_date.strftime(
                "%Y-%m-%d"
            ),

        "event_type":
            event_type,

        "product_id":
            product_id,

        "order_id":
            order_id,

        "page_url":
            random.choice(PAGE_URLS),

        "referrer_url":
            random.choice(
                PAGE_URLS
            ),

        "device_type":
            device_type,

        "browser":
            browser,

        "operating_system":
            operating_system,

        "ip_address":
            generate_ip(),

        "country":
            customer["country"],

        "state":
            customer["state"],

        "city":
            customer["city"],

        "traffic_source":
            traffic_source,

        "campaign_id":
            campaign_id,

        "search_query":
            search_query,

        "quantity":
            quantity,

        "event_value":
            event_value,

        "currency":
            currency,

        "is_authenticated":
            random.choices(
                [True, False],
                weights=[75, 25],
                k=1
            )[0],

        "created_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }

    events.append(event)

# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(events)

print(
    f"Base clickstream events generated: {len(df)}"
)

# ============================================================
# CONTROLLED DATA QUALITY ISSUES
# ============================================================

print()
print(
    "Injecting controlled data-quality issues..."
)

# ------------------------------------------------------------
# 1. DUPLICATE EVENTS ~1%
# ------------------------------------------------------------

duplicate_count = int(
    NUM_EVENTS * random.uniform(
        0.01,
        0.02
    )
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

# ------------------------------------------------------------
# 2. NULL CUSTOMER IDs
# ------------------------------------------------------------

null_customer_count = int(
    len(df) * 0.01
)

null_customer_indices = random.sample(
    list(df.index),
    null_customer_count
)

df.loc[
    null_customer_indices,
    "customer_id"
] = None

# ------------------------------------------------------------
# 3. INVALID PRODUCT IDs
# ------------------------------------------------------------

invalid_product_count = int(
    len(df) * 0.01
)

invalid_product_indices = random.sample(
    list(df.index),
    invalid_product_count
)

df.loc[
    invalid_product_indices,
    "product_id"
] = [
    f"PROD_INVALID_{i}"
    for i in range(
        invalid_product_count
    )
]

# ------------------------------------------------------------
# 4. INVALID ORDER IDs
# ------------------------------------------------------------

invalid_order_count = int(
    len(df) * 0.01
)

invalid_order_indices = random.sample(
    list(df.index),
    invalid_order_count
)

df.loc[
    invalid_order_indices,
    "order_id"
] = [
    f"ORD_INVALID_{i}"
    for i in range(
        invalid_order_count
    )
]

# ------------------------------------------------------------
# 5. NULL SESSION IDs
# ------------------------------------------------------------

null_session_count = int(
    len(df) * 0.01
)

null_session_indices = random.sample(
    list(df.index),
    null_session_count
)

df.loc[
    null_session_indices,
    "session_id"
] = None

# ------------------------------------------------------------
# 6. INVALID EVENT TYPES
# ------------------------------------------------------------

invalid_event_count = int(
    len(df) * 0.005
)

invalid_event_indices = random.sample(
    list(df.index),
    invalid_event_count
)

invalid_events = [
    "INVALID_EVENT",
    "UNKNOWN_EVENT",
    "TEST_EVENT"
]

for idx in invalid_event_indices:

    df.loc[
        idx,
        "event_type"
    ] = random.choice(
        invalid_events
    )

# ------------------------------------------------------------
# 7. FUTURE TIMESTAMPS
# ------------------------------------------------------------

future_count = int(
    len(df) * 0.01
)

future_indices = random.sample(
    list(df.index),
    future_count
)

for idx in future_indices:

    future_timestamp = (
        datetime.now()
        + timedelta(
            days=random.randint(
                1,
                365
            )
        )
    )

    df.loc[
        idx,
        "event_timestamp"
    ] = future_timestamp.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

# ------------------------------------------------------------
# 8. LATE ARRIVING EVENTS
# ------------------------------------------------------------

late_count = int(
    len(df) * 0.01
)

late_indices = random.sample(
    list(df.index),
    late_count
)

for idx in late_indices:

    original_created = pd.to_datetime(
        df.loc[
            idx,
            "created_at"
        ]
    )

    late_created = (
        original_created
        + timedelta(
            hours=random.randint(
                6,
                48
            )
        )
    )

    df.loc[
        idx,
        "created_at"
    ] = late_created.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

# ------------------------------------------------------------
# 9. MALFORMED TIMESTAMPS
# ------------------------------------------------------------

malformed_count = int(
    len(df) * 0.005
)

malformed_indices = random.sample(
    list(df.index),
    malformed_count
)

for idx in malformed_indices:

    df.loc[
        idx,
        "event_timestamp"
    ] = "INVALID_TIMESTAMP"

# ------------------------------------------------------------
# 10. NULL QUANTITY
# ------------------------------------------------------------

quantity_count = int(
    len(df) * 0.01
)

quantity_indices = random.sample(
    list(df.index),
    quantity_count
)

df.loc[
    quantity_indices,
    "quantity"
] = None

# ============================================================
# SHUFFLE
# ============================================================

df = df.sample(
    frac=1,
    random_state=42
).reset_index(
    drop=True
)

# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("==========================================")
print("CLICKSTREAM GENERATION COMPLETE")
print("==========================================")
print(
    f"Total events: {len(df)}"
)
print(
    f"Base events: {NUM_EVENTS}"
)
print(
    f"Duplicate events injected: {duplicate_count}"
)
print(
    f"Saved to: {OUTPUT_FILE}"
)
print("==========================================")