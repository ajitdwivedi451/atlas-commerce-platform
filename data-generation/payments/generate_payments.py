import os
import random
import uuid
import pandas as pd
from faker import Faker

fake = Faker()

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

CUSTOMERS_FILE = os.path.join(
    BASE_DIR,
    "customers",
    "customers.csv"
)

PAYMENT_METHODS_FILE = os.path.join(
    BASE_DIR,
    "customer_payment_methods",
    "customer_payment_methods.csv"
)

ORDERS_FILE = os.path.join(
    BASE_DIR,
    "orders",
    "orders.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "payments"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "payments.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 1. LOAD EXISTING DATASETS
# ============================================================

print("Loading existing datasets...")

customers_df = pd.read_csv(CUSTOMERS_FILE)

payment_methods_df = pd.read_csv(
    PAYMENT_METHODS_FILE
)

orders_df = pd.read_csv(
    ORDERS_FILE
)

print(f"Customers loaded: {len(customers_df)}")
print(f"Payment methods loaded: {len(payment_methods_df)}")
print(f"Orders loaded: {len(orders_df)}")


# ============================================================
# 2. DATA PREPARATION
# ============================================================

orders_df["order_date"] = pd.to_datetime(
    orders_df["order_date"]
)

payment_methods_df["created_date"] = pd.to_datetime(
    payment_methods_df["created_date"]
)

payment_methods_df = payment_methods_df[
    payment_methods_df["status"].eq("Active")
].copy()


# ============================================================
# 3. CUSTOMER → PAYMENT METHOD MAPPING
# ============================================================

payment_methods_by_customer = (
    payment_methods_df
    .groupby("customer_id")
    .apply(
        lambda x: x.to_dict("records")
    )
    .to_dict()
)


# ============================================================
# 4. PAYMENT CONFIGURATION
# ============================================================

failure_reasons = [
    "Insufficient Funds",
    "Card Declined",
    "Payment Gateway Error",
    "Invalid Payment Details",
    "Transaction Timeout",
    "Fraud Suspected",
    "Bank Server Unavailable"
]

payment_statuses = [
    "Completed",
    "Failed",
    "Pending",
    "Cancelled"
]

currencies = [
    "INR",
    "USD",
    "EUR",
    "AUD",
    "AED",
    "SGD",
    "JPY"
]


# ============================================================
# 5. GENERATE REALISTIC PAYMENTS
# ============================================================

payments = []

payment_counter = 1

print("\nGenerating realistic payment transactions...")


for _, order in orders_df.iterrows():

    order_id = order["order_id"]

    customer_id = order["customer_id"]

    order_date = order["order_date"]

    order_currency = order["currency"]

    order_total = round(
        float(order["total_amount"]),
        2
    )


    # --------------------------------------------------------
    # Find customer's valid payment methods
    # --------------------------------------------------------

    customer_methods = (
        payment_methods_by_customer
        .get(customer_id, [])
    )


    # Customer has no active payment method
    if not customer_methods:
        continue


    # --------------------------------------------------------
    # Number of payment attempts
    # --------------------------------------------------------

    attempt_probability = random.random()

    if attempt_probability < 0.75:

        number_of_attempts = 1

    elif attempt_probability < 0.93:

        number_of_attempts = 2

    elif attempt_probability < 0.985:

        number_of_attempts = 3

    else:

        number_of_attempts = random.randint(
            4,
            5
        )


    # --------------------------------------------------------
    # Decide whether order eventually succeeds
    # --------------------------------------------------------

    success_probability = random.random()

    order_has_success = (
        success_probability < 0.86
    )


    successful_payment_created = False


    # ========================================================
    # PAYMENT ATTEMPTS
    # ========================================================

    for attempt_number in range(
        1,
        number_of_attempts + 1
    ):

        payment_method = random.choice(
            customer_methods
        )

        payment_method_id = (
            payment_method[
                "payment_method_id"
            ]
        )

        payment_provider = (
            payment_method[
                "payment_provider"
            ]
        )


        # ----------------------------------------------------
        # Payment date
        # ----------------------------------------------------

        payment_date = (
            order_date
            + pd.Timedelta(
                minutes=random.randint(
                    2,
                    60 * 48
                )
            )
        )


        # ----------------------------------------------------
        # Decide payment status
        # ----------------------------------------------------

        if (
            order_has_success
            and
            attempt_number == number_of_attempts
        ):

            payment_status = "Completed"

        else:

            payment_status = random.choices(
                [
                    "Failed",
                    "Pending",
                    "Cancelled"
                ],
                weights=[
                    0.70,
                    0.20,
                    0.10
                ]
            )[0]


        # ----------------------------------------------------
        # Payment amount
        # ----------------------------------------------------

        if payment_status == "Completed":

            # Successful payment settles the order.
            amount = order_total

        else:

            # Failed/pending attempts normally attempt
            # to charge the same order amount.
            amount = order_total


        # ----------------------------------------------------
        # Failure reason
        # ----------------------------------------------------

        if payment_status == "Failed":

            failure_reason = random.choice(
                failure_reasons
            )

        else:

            failure_reason = None


        # ----------------------------------------------------
        # Processed date
        # ----------------------------------------------------

        if payment_status == "Completed":

            processed_date = (
                payment_date
                + pd.Timedelta(
                    minutes=random.randint(
                        1,
                        30
                    )
                )
            )

        else:

            processed_date = None


        # ----------------------------------------------------
        # Refund
        # ----------------------------------------------------

        refund_amount = 0.0

        payment_type = "Payment"


        # Refund will be generated separately
        # after successful payment.


        # ----------------------------------------------------
        # Transaction reference
        # ----------------------------------------------------

        transaction_reference = (
            f"TXN-"
            f"{uuid.uuid4().hex[:16].upper()}"
        )


        # ----------------------------------------------------
        # Create payment record
        # ----------------------------------------------------

        payment = {

            "payment_id":
                f"PAY{payment_counter:09d}",

            "order_id":
                order_id,

            "customer_id":
                customer_id,

            "payment_method_id":
                payment_method_id,

            "payment_date":
                payment_date,

            "payment_type":
                payment_type,

            "payment_provider":
                payment_provider,

            "currency":
                order_currency,

            "amount":
                amount,

            "payment_status":
                payment_status,

            "transaction_reference":
                transaction_reference,

            "failure_reason":
                failure_reason,

            "refund_amount":
                refund_amount,

            "processed_date":
                processed_date
        }

        payments.append(payment)

        payment_counter += 1


        # ----------------------------------------------------
        # Create refund separately
        # ----------------------------------------------------

        if payment_status == "Completed":

            successful_payment_created = True

            refund_probability = random.random()

            if refund_probability < 0.08:

                refund_amount = round(
                    random.uniform(
                        order_total * 0.10,
                        order_total
                    ),
                    2
                )

                refund_date = (
                    processed_date
                    + pd.Timedelta(
                        days=random.randint(
                            1,
                            30
                        )
                    )
                )

                refund_payment = {

                    "payment_id":
                        f"PAY{payment_counter:09d}",

                    "order_id":
                        order_id,

                    "customer_id":
                        customer_id,

                    "payment_method_id":
                        payment_method_id,

                    "payment_date":
                        refund_date,

                    "payment_type":
                        "Refund",

                    "payment_provider":
                        payment_provider,

                    "currency":
                        order_currency,

                    "amount":
                        -refund_amount,

                    "payment_status":
                        "Completed",

                    "transaction_reference":
                        (
                            f"REF-"
                            f"{uuid.uuid4().hex[:16].upper()}"
                        ),

                    "failure_reason":
                        None,

                    "refund_amount":
                        refund_amount,

                    "processed_date":
                        refund_date
                }

                payments.append(
                    refund_payment
                )

                payment_counter += 1


# ============================================================
# 6. DATAFRAME
# ============================================================

payments_df = pd.DataFrame(
    payments
)

print(
    f"\nBase payment transactions generated: "
    f"{len(payments_df)}"
)


# ============================================================
# 7. CONTROLLED DATA QUALITY ISSUES
# ============================================================

print(
    "\nInjecting controlled data-quality issues..."
)

base_count = len(payments_df)


# ============================================================
# A. DUPLICATE PAYMENT IDs
# ============================================================

duplicate_count = int(
    base_count * 0.01
)

duplicate_indexes = random.sample(
    range(base_count),
    duplicate_count
)

for idx in duplicate_indexes:

    source_idx = random.randint(
        0,
        base_count - 1
    )

    payments_df.loc[
        idx,
        "payment_id"
    ] = payments_df.loc[
        source_idx,
        "payment_id"
    ]


# ============================================================
# B. INVALID ORDER IDs
# ============================================================

invalid_order_count = int(
    base_count * 0.01
)

invalid_order_indexes = random.sample(
    range(base_count),
    invalid_order_count
)

for idx in invalid_order_indexes:

    payments_df.loc[
        idx,
        "order_id"
    ] = (
        f"ORD_INVALID_"
        f"{random.randint(1, 99999)}"
    )


# ============================================================
# C. INVALID PAYMENT METHOD IDs
# ============================================================

invalid_method_count = int(
    base_count * 0.01
)

invalid_method_indexes = random.sample(
    range(base_count),
    invalid_method_count
)

for idx in invalid_method_indexes:

    payments_df.loc[
        idx,
        "payment_method_id"
    ] = (
        f"PM_INVALID_"
        f"{random.randint(1, 99999)}"
    )


# ============================================================
# D. CURRENCY MISMATCH
# ============================================================

currency_count = int(
    base_count * 0.01
)

currency_indexes = random.sample(
    range(base_count),
    currency_count
)

for idx in currency_indexes:

    original_currency = payments_df.loc[
        idx,
        "currency"
    ]

    wrong_currency = random.choice(
        [
            c
            for c in currencies
            if c != original_currency
        ]
    )

    payments_df.loc[
        idx,
        "currency"
    ] = wrong_currency


# ============================================================
# E. NEGATIVE PAYMENT AMOUNT
# ============================================================

negative_count = int(
    base_count * 0.005
)

negative_indexes = random.sample(
    range(base_count),
    negative_count
)

for idx in negative_indexes:

    # Don't modify legitimate refunds
    if payments_df.loc[
        idx,
        "payment_type"
    ] == "Payment":

        payments_df.loc[
            idx,
            "amount"
        ] = -abs(
            payments_df.loc[
                idx,
                "amount"
            ]
        )


# ============================================================
# F. FUTURE PAYMENT DATES
# ============================================================

future_count = int(
    base_count * 0.01
)

future_indexes = random.sample(
    range(base_count),
    future_count
)

for idx in future_indexes:

    payments_df.loc[
        idx,
        "payment_date"
    ] = (
        pd.Timestamp.today()
        + pd.Timedelta(
            days=random.randint(
                30,
                365
            )
        )
    )


# ============================================================
# G. NULL PAYMENT PROVIDERS
# ============================================================

null_provider_count = int(
    base_count * 0.01
)

null_provider_indexes = random.sample(
    range(base_count),
    null_provider_count
)

for idx in null_provider_indexes:

    payments_df.loc[
        idx,
        "payment_provider"
    ] = None


# ============================================================
# 8. SHUFFLE
# ============================================================

payments_df = (
    payments_df
    .sample(frac=1)
    .reset_index(drop=True)
)


# ============================================================
# 9. VALIDATION
# ============================================================

print(
    "\n========== PAYMENT VALIDATION =========="
)

print("\nColumns:")
print(
    list(
        payments_df.columns
    )
)

print("\nTotal Records:")
print(
    len(payments_df)
)

print("\nDuplicate Payment IDs:")
print(
    payments_df[
        "payment_id"
    ].duplicated().sum()
)

print("\nNull Values:")
print(
    payments_df.isnull().sum()
)

print("\nPayment Status:")
print(
    payments_df[
        "payment_status"
    ].value_counts()
)

print("\nPayment Types:")
print(
    payments_df[
        "payment_type"
    ].value_counts()
)

print("\nCurrencies:")
print(
    payments_df[
        "currency"
    ].value_counts()
)

print("\nNegative Amounts:")
print(
    (
        payments_df["amount"]
        < 0
    ).sum()
)

print("\nInvalid Order IDs:")

print(
    (
        ~payments_df[
            "order_id"
        ].isin(
            orders_df[
                "order_id"
            ]
        )
    ).sum()
)

print(
    "\nInvalid Payment Method IDs:"
)

print(
    (
        ~payments_df[
            "payment_method_id"
        ].isin(
            payment_methods_df[
                "payment_method_id"
            ]
        )
    ).sum()
)

print("\nFuture Payment Dates:")

print(
    (
        pd.to_datetime(
            payments_df[
                "payment_date"
            ]
        )
        > pd.Timestamp.today()
    ).sum()
)


# ============================================================
# 10. BUSINESS RELATIONSHIP VALIDATION
# ============================================================

print(
    "\n========== BUSINESS RELATIONSHIP VALIDATION =========="
)


# ------------------------------------------------------------
# Customer ↔ Order
# ------------------------------------------------------------

order_customer_map = (
    orders_df
    .set_index("order_id")
    ["customer_id"]
    .to_dict()
)

payments_df[
    "order_customer_id"
] = (
    payments_df[
        "order_id"
    ].map(
        order_customer_map
    )
)

customer_order_mismatch = (
    payments_df[
        "customer_id"
    ]
    !=
    payments_df[
        "order_customer_id"
    ]
)

print(
    "\nCustomer ↔ Order Mismatches:"
)

print(
    customer_order_mismatch.sum()
)


# ------------------------------------------------------------
# Customer ↔ Payment Method
# ------------------------------------------------------------

payment_method_customer_map = (
    payment_methods_df
    .set_index(
        "payment_method_id"
    )
    ["customer_id"]
    .to_dict()
)

payments_df[
    "payment_method_customer_id"
] = (
    payments_df[
        "payment_method_id"
    ].map(
        payment_method_customer_map
    )
)

customer_payment_method_mismatch = (
    payments_df[
        "customer_id"
    ]
    !=
    payments_df[
        "payment_method_customer_id"
    ]
)

print(
    "\nCustomer ↔ Payment Method Mismatches:"
)

print(
    customer_payment_method_mismatch.sum()
)


# ------------------------------------------------------------
# Currency ↔ Order
# ------------------------------------------------------------

order_currency_map = (
    orders_df
    .set_index(
        "order_id"
    )
    ["currency"]
    .to_dict()
)

payments_df[
    "order_currency"
] = (
    payments_df[
        "order_id"
    ].map(
        order_currency_map
    )
)

currency_mismatch = (
    payments_df[
        "currency"
    ]
    !=
    payments_df[
        "order_currency"
    ]
)

print(
    "\nPayment ↔ Order Currency Mismatches:"
)

print(
    currency_mismatch.sum()
)


# ------------------------------------------------------------
# Completed payment > order total
# ------------------------------------------------------------

order_total_map = (
    orders_df
    .set_index(
        "order_id"
    )
    ["total_amount"]
    .to_dict()
)

payments_df[
    "order_total"
] = (
    payments_df[
        "order_id"
    ].map(
        order_total_map
    )
)

valid_completed = payments_df[
    (
        payments_df[
            "payment_status"
        ]
        == "Completed"
    )
    &
    (
        payments_df[
            "payment_type"
        ]
        == "Payment"
    )
]

completed_over_order = (
    valid_completed[
        "amount"
    ]
    >
    valid_completed[
        "order_total"
    ]
)

print(
    "\nCompleted Payment > Order Total:"
)

print(
    completed_over_order.sum()
)


# ============================================================
# 11. REMOVE VALIDATION HELPER COLUMNS
# ============================================================

payments_df.drop(
    columns=[
        "order_customer_id",
        "payment_method_customer_id",
        "order_currency",
        "order_total"
    ],
    inplace=True
)


# ============================================================
# 12. SAVE
# ============================================================

payments_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    "\n========================================"
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)