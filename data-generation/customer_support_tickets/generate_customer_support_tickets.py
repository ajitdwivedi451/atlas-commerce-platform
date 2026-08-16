import os
import random
import uuid
import pandas as pd
from faker import Faker

fake = Faker()

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

CUSTOMERS_FILE = os.path.join(BASE_DIR, "customers", "customers.csv")
ORDERS_FILE = os.path.join(BASE_DIR, "orders", "orders.csv")
ORDER_ITEMS_FILE = os.path.join(BASE_DIR, "order_items", "order_items.csv")
PRODUCTS_FILE = os.path.join(BASE_DIR, "products", "products.csv")
PAYMENTS_FILE = os.path.join(BASE_DIR, "payments", "payments.csv")
SHIPMENTS_FILE = os.path.join(BASE_DIR, "shipments", "shipments.csv")
RETURNS_FILE = os.path.join(BASE_DIR, "returns", "returns.csv")

OUTPUT_DIR = os.path.join(BASE_DIR, "customer_support_tickets")
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "customer_support_tickets.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_TICKETS = 25000


# ============================================================
# LOAD DATASETS
# ============================================================

print("Loading existing datasets...")

customers = pd.read_csv(CUSTOMERS_FILE, low_memory=False)
orders = pd.read_csv(ORDERS_FILE, low_memory=False)
order_items = pd.read_csv(ORDER_ITEMS_FILE, low_memory=False)
products = pd.read_csv(PRODUCTS_FILE, low_memory=False)
payments = pd.read_csv(PAYMENTS_FILE, low_memory=False)
shipments = pd.read_csv(SHIPMENTS_FILE, low_memory=False)
returns = pd.read_csv(RETURNS_FILE, low_memory=False)

print(f"Customers loaded: {len(customers)}")
print(f"Orders loaded: {len(orders)}")
print(f"Order Items loaded: {len(order_items)}")
print(f"Products loaded: {len(products)}")
print(f"Payments loaded: {len(payments)}")
print(f"Shipments loaded: {len(shipments)}")
print(f"Returns loaded: {len(returns)}")


# ============================================================
# NORMALIZE DATES
# ============================================================

orders["order_date"] = pd.to_datetime(
    orders["order_date"], errors="coerce"
)

payments["payment_date"] = pd.to_datetime(
    payments["payment_date"], errors="coerce"
)

shipments["shipment_date"] = pd.to_datetime(
    shipments["shipment_date"], errors="coerce"
)

returns["return_date"] = pd.to_datetime(
    returns["return_date"], errors="coerce"
)


# ============================================================
# LOOKUP MAPS
# ============================================================

customer_ids = customers["customer_id"].dropna().tolist()
product_ids = products["product_id"].dropna().tolist()

orders_by_customer = (
    orders.groupby("customer_id")
    .apply(lambda x: x.to_dict("records"), include_groups=False)
    .to_dict()
)

order_items_by_order = (
    order_items.groupby("order_id")
    .apply(lambda x: x.to_dict("records"), include_groups=False)
    .to_dict()
)

shipments_by_order = (
    shipments.groupby("order_id")
    .apply(lambda x: x.to_dict("records"), include_groups=False)
    .to_dict()
)

returns_by_order = (
    returns.groupby("order_id")
    .apply(lambda x: x.to_dict("records"), include_groups=False)
    .to_dict()
)

payments_by_order = (
    payments.groupby("order_id")
    .apply(lambda x: x.to_dict("records"), include_groups=False)
    .to_dict()
)


# ============================================================
# BUSINESS VALUES
# ============================================================

ticket_categories = [
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
]

category_weights = [
    18, 12, 18, 12, 10, 8, 8, 5, 4, 3, 2
]

subcategories = {
    "Order": [
        "Order Status",
        "Order Modification",
        "Wrong Item",
        "Missing Item",
        "Order Information"
    ],

    "Payment": [
        "Payment Failed",
        "Payment Pending",
        "Payment Not Reflected",
        "Duplicate Payment",
        "Payment Reversed"
    ],

    "Delivery": [
        "Late Delivery",
        "Package Not Received",
        "Wrong Address",
        "Delivery Attempt Failed",
        "Damaged Package"
    ],

    "Shipment": [
        "Tracking Issue",
        "Shipment Delayed",
        "Carrier Issue",
        "Shipment Status"
    ],

    "Return": [
        "Return Request",
        "Return Pickup",
        "Return Status",
        "Return Rejected",
        "Exchange Request"
    ],

    "Refund": [
        "Refund Pending",
        "Refund Not Received",
        "Partial Refund",
        "Refund Failed"
    ],

    "Product": [
        "Product Defect",
        "Product Information",
        "Wrong Product",
        "Product Quality"
    ],

    "Account": [
        "Login Issue",
        "Account Update",
        "Password Reset",
        "Profile Issue"
    ],

    "Cancellation": [
        "Cancel Order",
        "Cancellation Request",
        "Cancellation Status"
    ],

    "Technical": [
        "Website Error",
        "Mobile App Issue",
        "Checkout Error"
    ],

    "Other": [
        "General Inquiry",
        "Other Issue"
    ]
}

priorities = [
    "Low",
    "Medium",
    "High",
    "Urgent"
]

priority_weights = [20, 50, 25, 5]

channels = [
    "Email",
    "Phone",
    "Chat",
    "Web"
]

channel_weights = [30, 20, 35, 15]

statuses = [
    "Open",
    "In Progress",
    "Waiting for Customer",
    "Resolved",
    "Closed",
    "Reopened"
]

teams = [
    "Order Support",
    "Payment Support",
    "Logistics Support",
    "Returns Team",
    "Product Support",
    "Account Support",
    "Technical Support"
]

agents = [
    f"AGENT{i:04d}"
    for i in range(1, 101)
]

resolution_types = [
    "Information Provided",
    "Refund",
    "Replacement",
    "Exchange",
    "Order Cancellation",
    "Address Update",
    "Technical Fix",
    "No Action Required"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value):
    if pd.isna(value):
        return None
    return value


def choose_order_for_customer(customer_id):

    customer_orders = orders_by_customer.get(customer_id, [])

    if not customer_orders:
        return None

    return random.choice(customer_orders)


def generate_subject(category, subcategory):

    subjects = {
        "Payment": [
            "Payment failed for my order",
            "Payment is still pending",
            "Payment was deducted but order is not confirmed",
            "Duplicate payment issue"
        ],

        "Delivery": [
            "My order has not arrived",
            "Delivery is delayed",
            "Package was not delivered",
            "Delivery attempt failed"
        ],

        "Shipment": [
            "Tracking information is not updating",
            "Shipment is delayed",
            "Where is my shipment?",
            "Carrier has not delivered my package"
        ],

        "Return": [
            "I want to return my product",
            "Return pickup has not happened",
            "Return status update required",
            "Exchange request"
        ],

        "Refund": [
            "Refund has not been received",
            "Refund is pending",
            "Refund amount is incorrect",
            "Refund failed"
        ],

        "Product": [
            "Product arrived damaged",
            "Product quality issue",
            "Wrong product received",
            "Product information required"
        ],

        "Order": [
            "Question about my order",
            "I want to modify my order",
            "Order information required",
            "Missing item from my order"
        ],

        "Cancellation": [
            "I want to cancel my order",
            "Cancellation request",
            "Order cancellation status"
        ],

        "Account": [
            "Unable to access my account",
            "Account information update",
            "Login problem"
        ],

        "Technical": [
            "Website is not working",
            "Checkout page error",
            "Mobile application issue"
        ],

        "Other": [
            "General inquiry",
            "I need assistance"
        ]
    }

    return random.choice(
        subjects.get(category, ["Customer support request"])
    )


def generate_description(category, subcategory):

    descriptions = {
        "Payment":
            "Customer reported an issue related to payment processing for the order.",

        "Delivery":
            "Customer contacted support regarding delivery status or delivery delay.",

        "Shipment":
            "Customer requested assistance regarding shipment tracking or carrier status.",

        "Return":
            "Customer requested assistance with the product return process.",

        "Refund":
            "Customer contacted support regarding refund processing or refund status.",

        "Product":
            "Customer reported an issue or requested information about a purchased product.",

        "Order":
            "Customer contacted support regarding an existing order.",

        "Cancellation":
            "Customer requested information or assistance with order cancellation.",

        "Account":
            "Customer reported an issue related to their customer account.",

        "Technical":
            "Customer reported a technical issue while using the commerce platform.",

        "Other":
            "Customer contacted support regarding a general inquiry."
    }

    base = descriptions.get(
        category,
        "Customer contacted customer support."
    )

    return f"{base} Specific issue: {subcategory}."


# ============================================================
# GENERATE BASE TICKETS
# ============================================================

print("\nGenerating realistic customer support tickets...")

tickets = []

for i in range(1, NUM_TICKETS + 1):

    ticket_id = f"TKT{i:06d}"

    customer_id = random.choice(customer_ids)

    order = choose_order_for_customer(customer_id)

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category = random.choices(
        ticket_categories,
        weights=category_weights,
        k=1
    )[0]

    subcategory = random.choice(
        subcategories[category]
    )

    # --------------------------------------------------------
    # RELATIONSHIP
    # --------------------------------------------------------

    order_id = None
    order_item_id = None
    product_id = None
    payment_id = None
    shipment_id = None
    return_id = None

    # Most operational tickets relate to an order
    if category != "Account" and category != "Technical":

        if order:

            order_id = order["order_id"]

            # Order item
            order_items_for_order = order_items_by_order.get(
                order_id, []
            )

            if order_items_for_order:

                order_item = random.choice(
                    order_items_for_order
                )

                order_item_id = order_item.get(
                    "order_item_id"
                )

                product_id = order_item.get(
                    "product_id"
                )

    # --------------------------------------------------------
    # CATEGORY-SPECIFIC RELATIONSHIPS
    # --------------------------------------------------------

    if category == "Payment" and order_id:

        payment_records = payments_by_order.get(
            order_id, []
        )

        if payment_records:

            payment = random.choice(
                payment_records
            )

            payment_id = payment.get(
                "payment_id"
            )

    elif category in ["Delivery", "Shipment"] and order_id:

        shipment_records = shipments_by_order.get(
            order_id, []
        )

        if shipment_records:

            shipment = random.choice(
                shipment_records
            )

            shipment_id = shipment.get(
                "shipment_id"
            )

    elif category in ["Return", "Refund"] and order_id:

        return_records = returns_by_order.get(
            order_id, []
        )

        if return_records:

            return_record = random.choice(
                return_records
            )

            return_id = return_record.get(
                "return_id"
            )

            shipment_id = clean_value(
                return_record.get("shipment_id")
            )

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if order and pd.notna(order["order_date"]):

        order_date = pd.Timestamp(order["order_date"])
        today = pd.Timestamp.today().normalize()

        if order_date <= today:

            ticket_date = fake.date_between(
                start_date=order_date,
                end_date=today
            )

        else:

            # Future order → avoid invalid Faker date range
            ticket_date = order_date + pd.Timedelta(
                days=random.randint(0, 30)
            )

    else:

        ticket_date = fake.date_between(
            start_date="-3y",
            end_date="today"
        )

    ticket_datetime = pd.Timestamp(ticket_date)

    # --------------------------------------------------------
    # PRIORITY / CHANNEL
    # --------------------------------------------------------

    priority = random.choices(
        priorities,
        weights=priority_weights,
        k=1
    )[0]

    channel = random.choices(
        channels,
        weights=channel_weights,
        k=1
    )[0]

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status = random.choices(
        statuses,
        weights=[15, 20, 8, 20, 32, 5],
        k=1
    )[0]

    # --------------------------------------------------------
    # RESPONSE / RESOLUTION DATES
    # --------------------------------------------------------

    first_response_date = None
    resolved_date = None

    if status in [
        "In Progress",
        "Waiting for Customer",
        "Resolved",
        "Closed",
        "Reopened"
    ]:

        response_delay = random.randint(1, 48)

        first_response_date = (
            ticket_datetime
            + pd.Timedelta(hours=response_delay)
        )

    if status in [
        "Resolved",
        "Closed"
    ]:

        resolution_delay = random.randint(1, 7)

        resolved_date = (
            ticket_datetime
            + pd.Timedelta(days=resolution_delay)
        )

        # Make sure resolution happens after response
        if first_response_date and resolved_date < first_response_date:

            resolved_date = (
                first_response_date
                + pd.Timedelta(days=1)
            )

    # --------------------------------------------------------
    # SATISFACTION
    # --------------------------------------------------------

    satisfaction_score = None

    if status in ["Resolved", "Closed"]:

        satisfaction_score = random.choices(
            [1, 2, 3, 4, 5],
            weights=[3, 5, 12, 30, 50],
            k=1
        )[0]

    reopened_count = 0

    if status == "Reopened":

        reopened_count = random.randint(1, 3)

    # --------------------------------------------------------
    # ASSIGNMENT
    # --------------------------------------------------------

    assigned_agent = random.choice(agents)

    assigned_team = random.choice(teams)

    # --------------------------------------------------------
    # RESOLUTION
    # --------------------------------------------------------

    resolution_type = None

    if status in ["Resolved", "Closed"]:

        resolution_type = random.choice(
            resolution_types
        )

    created_date = ticket_datetime

    updated_date = (
        resolved_date
        if resolved_date is not None
        else ticket_datetime
    )

    ticket = {

        "ticket_id": ticket_id,

        "customer_id": customer_id,

        "order_id": order_id,

        "order_item_id": order_item_id,

        "product_id": product_id,

        "payment_id": payment_id,

        "shipment_id": shipment_id,

        "return_id": return_id,

        "ticket_date": ticket_datetime.strftime(
            "%Y-%m-%d"
        ),

        "ticket_category": category,

        "ticket_subcategory": subcategory,

        "priority": priority,

        "channel": channel,

        "subject": generate_subject(
            category,
            subcategory
        ),

        "description": generate_description(
            category,
            subcategory
        ),

        "ticket_status": status,

        "assigned_team": assigned_team,

        "assigned_agent": assigned_agent,

        "first_response_date": (
            first_response_date.strftime("%Y-%m-%d %H:%M:%S")
            if first_response_date is not None
            else None
        ),

        "resolved_date": (
            resolved_date.strftime("%Y-%m-%d %H:%M:%S")
            if resolved_date is not None
            else None
        ),

        "resolution_type": resolution_type,

        "customer_satisfaction_score":
            satisfaction_score,

        "reopened_count":
            reopened_count,

        "created_date":
            created_date.strftime("%Y-%m-%d %H:%M:%S"),

        "updated_date":
            updated_date.strftime("%Y-%m-%d %H:%M:%S")
    }

    tickets.append(ticket)


print(
    f"Base support tickets generated: {len(tickets)}"
)


# ============================================================
# CONTROLLED DATA QUALITY ISSUES
# ============================================================

print("\nInjecting controlled data-quality issues...")

dirty_count = int(
    len(tickets) * random.uniform(0.015, 0.025)
)

for _ in range(dirty_count):

    ticket = random.choice(tickets)

    issue = random.choice([
        "duplicate_id",
        "invalid_customer",
        "invalid_order",
        "invalid_product",
        "invalid_shipment",
        "invalid_return",
        "invalid_status",
        "invalid_priority",
        "future_date",
        "invalid_satisfaction",
        "negative_reopen",
        "date_relationship"
    ])

    # --------------------------------------------------------
    # Duplicate ID
    # --------------------------------------------------------

    if issue == "duplicate_id":

        duplicate = random.choice(tickets)

        ticket["ticket_id"] = duplicate["ticket_id"]

    # --------------------------------------------------------
    # Invalid customer
    # --------------------------------------------------------

    elif issue == "invalid_customer":

        ticket["customer_id"] = (
            f"CUST_INVALID_{random.randint(1,999)}"
        )

    # --------------------------------------------------------
    # Invalid order
    # --------------------------------------------------------

    elif issue == "invalid_order":

        ticket["order_id"] = (
            f"ORD_INVALID_{random.randint(1,999)}"
        )

    # --------------------------------------------------------
    # Invalid product
    # --------------------------------------------------------

    elif issue == "invalid_product":

        ticket["product_id"] = (
            f"PROD_INVALID_{random.randint(1,999)}"
        )

    # --------------------------------------------------------
    # Invalid shipment
    # --------------------------------------------------------

    elif issue == "invalid_shipment":

        ticket["shipment_id"] = (
            f"SHIP_INVALID_{random.randint(1,999)}"
        )

    # --------------------------------------------------------
    # Invalid return
    # --------------------------------------------------------

    elif issue == "invalid_return":

        ticket["return_id"] = (
            f"RET_INVALID_{random.randint(1,999)}"
        )

    # --------------------------------------------------------
    # Invalid status
    # --------------------------------------------------------

    elif issue == "invalid_status":

        ticket["ticket_status"] = random.choice([
            "UNKNOWN",
            "INVALID",
            "Pending_Validation"
        ])

    # --------------------------------------------------------
    # Invalid priority
    # --------------------------------------------------------

    elif issue == "invalid_priority":

        ticket["priority"] = random.choice([
            "Critical",
            "Unknown",
            "P0"
        ])

    # --------------------------------------------------------
    # Future date
    # --------------------------------------------------------

    elif issue == "future_date":

        future_date = fake.date_between(
            start_date="+1y",
            end_date="+2y"
        )

        ticket["ticket_date"] = future_date.strftime(
            "%Y-%m-%d"
        )

    # --------------------------------------------------------
    # Invalid satisfaction
    # --------------------------------------------------------

    elif issue == "invalid_satisfaction":

        ticket["customer_satisfaction_score"] = random.choice([
            -1,
            0,
            6,
            10
        ])

    # --------------------------------------------------------
    # Negative reopened count
    # --------------------------------------------------------

    elif issue == "negative_reopen":

        ticket["reopened_count"] = random.randint(
            -5,
            -1
        )

    # --------------------------------------------------------
    # Date relationship issue
    # --------------------------------------------------------

    elif issue == "date_relationship":

        ticket["resolved_date"] = (
            "2020-01-01 00:00:00"
        )


# ============================================================
# CONTROLLED NULLS
# ============================================================

# Some NULLs are legitimate business values.
# Additional controlled NULLs are introduced for data-quality
# engineering practice.

null_injections = int(
    len(tickets) * 0.01
)

for _ in range(null_injections):

    ticket = random.choice(tickets)

    column = random.choice([
        "assigned_agent",
        "description",
        "customer_satisfaction_score",
        "first_response_date"
    ])

    ticket[column] = None


# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(tickets)


# ============================================================
# SAVE
# ============================================================

df = pd.DataFrame(tickets)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n==========================================")
print("CUSTOMER SUPPORT TICKET GENERATION COMPLETE")
print("==========================================")

print(f"Total tickets: {len(df)}")

print(f"Saved to:")
print(OUTPUT_FILE)

print("==========================================")