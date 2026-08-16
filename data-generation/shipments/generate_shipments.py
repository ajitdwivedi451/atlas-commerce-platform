import os
import random
import pandas as pd
from faker import Faker
from datetime import timedelta

fake = Faker()

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

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

OUTPUT_DIR = os.path.join(
    BASE_DIR, "shipments"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "shipments.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD EXISTING DATASETS
# ============================================================

print("Loading existing datasets...")

orders_df = pd.read_csv(ORDERS_FILE)
addresses_df = pd.read_csv(ADDRESSES_FILE)
warehouses_df = pd.read_csv(WAREHOUSES_FILE)

print(f"Orders loaded: {len(orders_df)}")
print(f"Addresses loaded: {len(addresses_df)}")
print(f"Warehouses loaded: {len(warehouses_df)}")


# ============================================================
# PREPARE DATA
# ============================================================

orders_df["order_date"] = pd.to_datetime(
    orders_df["order_date"]
)

addresses_df["customer_id"] = (
    addresses_df["customer_id"].astype(str)
)

orders_df["customer_id"] = (
    orders_df["customer_id"].astype(str)
)

warehouses_df["warehouse_id"] = (
    warehouses_df["warehouse_id"].astype(str)
)


# Only orders that can realistically be shipped
eligible_statuses = [
    "Confirmed",
    "Processing",
    "Shipped",
    "Delivered",
    "Returned"
]

eligible_orders = orders_df[
    orders_df["order_status"].isin(eligible_statuses)
].copy()

print(f"Eligible orders: {len(eligible_orders)}")


# ============================================================
# CREATE CUSTOMER → ADDRESS MAPPING
# ============================================================

customer_addresses = {}

for customer_id, group in addresses_df.groupby("customer_id"):

    valid_addresses = group[
        group["address_id"].notna()
    ]

    if len(valid_addresses) > 0:

        customer_addresses[customer_id] = (
            valid_addresses[
                "address_id"
            ].astype(str).tolist()
        )


# ============================================================
# WAREHOUSE LIST
# ============================================================

warehouse_ids = (
    warehouses_df["warehouse_id"]
    .astype(str)
    .tolist()
)


# ============================================================
# BUSINESS VALUES
# ============================================================

shipment_statuses = [
    "Processing",
    "Shipped",
    "In Transit",
    "Out for Delivery",
    "Delivered",
    "Failed",
    "Returned"
]

carriers = [
    "FedEx",
    "DHL",
    "UPS",
    "Blue Dart",
    "Delhivery",
    "Aramex",
    "Australia Post",
    "Japan Post"
]

shipping_methods = [
    "Standard",
    "Express",
    "Same Day",
    "Next Day"
]

failure_reasons = [
    "Customer Unavailable",
    "Incorrect Address",
    "Damaged Package",
    "Carrier Delay",
    "Delivery Area Unreachable",
    "Package Lost"
]


# ============================================================
# GENERATE BASE SHIPMENTS
# ============================================================

shipments = []

shipment_counter = 1

print("\nGenerating realistic shipment transactions...")


for _, order in eligible_orders.iterrows():

    customer_id = order["customer_id"]

    # --------------------------------------------------------
    # Customer must have an address
    # --------------------------------------------------------

    if customer_id not in customer_addresses:
        continue

    address_list = customer_addresses[customer_id]

    # Prefer shipping address from order
    order_shipping_address = str(
        order["shipping_address_id"]
    )

    if (
        order_shipping_address != "nan"
        and order_shipping_address in address_list
    ):
        shipping_address_id = order_shipping_address
    else:
        shipping_address_id = random.choice(
            address_list
        )


    # --------------------------------------------------------
    # Partial shipment simulation
    # --------------------------------------------------------

    if random.random() < 0.08:
        number_of_shipments = random.choice([2, 2, 3])
    else:
        number_of_shipments = 1


    for shipment_number in range(
        number_of_shipments
    ):

        order_date = order["order_date"]

        # Shipment normally happens after order
        shipment_date = order_date + timedelta(
            days=random.randint(1, 3)
        )

        shipping_method = random.choices(
            shipping_methods,
            weights=[60, 25, 10, 5],
            k=1
        )[0]

        # Delivery estimate based on shipping method
        delivery_days = {
            "Standard": random.randint(4, 8),
            "Express": random.randint(2, 4),
            "Same Day": 1,
            "Next Day": 2
        }

        estimated_date = (
            shipment_date
            + timedelta(
                days=delivery_days[shipping_method]
            )
        )

        # ----------------------------------------------------
        # Determine shipment status
        # ----------------------------------------------------

        if order["order_status"] == "Delivered":

            status = random.choices(
                [
                    "Delivered",
                    "Returned"
                ],
                weights=[95, 5],
                k=1
            )[0]

        elif order["order_status"] == "Returned":

            status = "Returned"

        elif order["order_status"] == "Shipped":

            status = random.choice([
                "Shipped",
                "In Transit",
                "Out for Delivery",
                "Delivered"
            ])

        else:

            status = random.choice([
                "Processing",
                "Shipped",
                "In Transit"
            ])


        # ----------------------------------------------------
        # Actual delivery date
        # ----------------------------------------------------

        actual_delivery_date = None

        if status == "Delivered":

            actual_delivery_date = (
                estimated_date
                + timedelta(
                    days=random.randint(-2, 3)
                )
            )

        elif status == "Returned":

            actual_delivery_date = (
                estimated_date
                + timedelta(
                    days=random.randint(0, 7)
                )
            )


        # ----------------------------------------------------
        # Failed shipment
        # ----------------------------------------------------

        failure_reason = None

        if status == "Failed":

            failure_reason = random.choice(
                failure_reasons
            )


        # ----------------------------------------------------
        # Delivery attempts
        # ----------------------------------------------------

        if status in [
            "Delivered",
            "Returned"
        ]:

            delivery_attempts = random.choices(
                [1, 2, 3],
                weights=[75, 20, 5],
                k=1
            )[0]

        elif status == "Failed":

            delivery_attempts = random.randint(
                1, 3
            )

        else:

            delivery_attempts = 0


        # ----------------------------------------------------
        # Shipping cost
        # ----------------------------------------------------

        shipping_cost = round(
            random.uniform(5, 35),
            2
        )


        # ----------------------------------------------------
        # Currency comes from ORDER
        # ----------------------------------------------------

        currency = order["currency"]


        # ----------------------------------------------------
        # Tracking number
        # ----------------------------------------------------

        tracking_number = (
            f"TRK"
            f"{fake.random_number(digits=12):012d}"
        )


        # ----------------------------------------------------
        # Create shipment
        # ----------------------------------------------------

        shipment = {

            "shipment_id":
                f"SHIP{shipment_counter:08d}",

            "order_id":
                order["order_id"],

            "customer_id":
                customer_id,

            "warehouse_id":
                random.choice(warehouse_ids),

            "shipping_address_id":
                shipping_address_id,

            "shipment_status":
                status,

            "carrier":
                random.choice(carriers),

            "tracking_number":
                tracking_number,

            "shipping_method":
                shipping_method,

            "shipment_date":
                shipment_date.strftime("%Y-%m-%d"),

            "estimated_delivery_date":
                estimated_date.strftime("%Y-%m-%d"),

            "actual_delivery_date":
                (
                    actual_delivery_date.strftime("%Y-%m-%d")
                    if actual_delivery_date
                    else None
                ),

            "shipping_cost":
                shipping_cost,

            "currency":
                currency,

            "delivery_attempts":
                delivery_attempts,

            "failure_reason":
                failure_reason,

            "created_date":
                shipment_date.strftime("%Y-%m-%d"),
            "updated_date":
                (
                    shipment_date.strftime("%Y-%m-%d")
                    if shipment_date > pd.Timestamp.today()
                    else fake.date_between(
                        start_date=shipment_date.date(),
                        end_date=pd.Timestamp.today().date()
                    ).strftime("%Y-%m-%d")
                )

            # "updated_date":
            #     fake.date_between(
            #         start_date=shipment_date,
            #         end_date="today"
            #     ).strftime("%Y-%m-%d")
            
            
        }

        shipments.append(shipment)

        shipment_counter += 1


print(
    f"\nBase shipment records generated: "
    f"{len(shipments)}"
)


# ============================================================
# CONTROLLED DATA QUALITY ISSUES
# ============================================================

print(
    "\nInjecting controlled data-quality issues..."
)


# ------------------------------------------------------------
# Duplicate Shipment IDs
# ------------------------------------------------------------

num_duplicates = int(
    len(shipments) * random.uniform(0.01, 0.015)
)

duplicates = random.choices(
    shipments,
    k=num_duplicates
)

shipments.extend(duplicates)


# ------------------------------------------------------------
# Inject issues
# ------------------------------------------------------------

for shipment in shipments:

    chance = random.random()

    # --------------------------------------------------------
    # NULL TRACKING NUMBER
    # --------------------------------------------------------

    if chance < 0.03:

        shipment["tracking_number"] = None


    # --------------------------------------------------------
    # INVALID WAREHOUSE
    # --------------------------------------------------------

    elif chance < 0.04:

        shipment["warehouse_id"] = (
            f"WH_INVALID_{random.randint(1,999)}"
        )


    # --------------------------------------------------------
    # INVALID ORDER
    # --------------------------------------------------------

    elif chance < 0.05:

        shipment["order_id"] = (
            f"ORD_INVALID_{random.randint(1,999)}"
        )


    # --------------------------------------------------------
    # FUTURE SHIPMENT DATE
    # --------------------------------------------------------

    elif chance < 0.06:

        future_date = (
            pd.Timestamp.today()
            + pd.Timedelta(
                days=random.randint(30, 365)
            )
        )

        shipment["shipment_date"] = (
            future_date.strftime("%Y-%m-%d")
        )


    # --------------------------------------------------------
    # INVALID STATUS
    # --------------------------------------------------------

    elif chance < 0.07:

        shipment["shipment_status"] = random.choice([
            "UNKNOWN",
            "INVALID",
            "Pending_Validation"
        ])


    # --------------------------------------------------------
    # DATE INCONSISTENCY
    # --------------------------------------------------------

    elif chance < 0.08:

        shipment["actual_delivery_date"] = (
            shipment["shipment_date"]
        )


    # --------------------------------------------------------
    # MISSING FAILURE REASON
    # --------------------------------------------------------

    elif chance < 0.09:

        if shipment["shipment_status"] == "Failed":

            shipment["failure_reason"] = None


# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(shipments)


# ============================================================
# SAVE
# ============================================================

df = pd.DataFrame(shipments)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n==========================================")
print("SHIPMENT GENERATION COMPLETE")
print("==========================================")

print(
    f"Total shipment records: {len(df)}"
)

print(
    f"Saved to: {OUTPUT_FILE}"
)