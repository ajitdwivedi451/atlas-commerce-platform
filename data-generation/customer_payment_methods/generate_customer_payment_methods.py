import pandas as pd
import random
import os
from faker import Faker

fake = Faker()

# ============================================================
# 1. PATHS
# ============================================================

customer_file = (
    r"D:\Projects\atlas-commerce-platform"
    r"\data-generation\customers\customers.csv"
)

output_dir = (
    r"D:\Projects\atlas-commerce-platform"
    r"\data-generation\customer_payment_methods"
)

os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(
    output_dir,
    "customer_payment_methods.csv"
)


# ============================================================
# 2. READ CUSTOMER MASTER
# ============================================================

customers_df = pd.read_csv(customer_file)

print(f"Loaded {len(customers_df)} customer records.")


# ============================================================
# 3. COUNTRY → CURRENCY
# ============================================================

currency_map = {
    "India": "INR",
    "United States": "USD",
    "United Kingdom": "GBP",
    "United Arab Emirates": "AED",
    "Australia": "AUD",
    "France": "EUR",
    "Singapore": "SGD",
    "Japan": "JPY"
}


# ============================================================
# 4. PAYMENT OPTIONS
# ============================================================

payment_options = {
    "India": {
        "UPI": ["PhonePe", "Google Pay", "Paytm"],
        "CARD": ["Visa", "Mastercard", "RuPay"],
        "BANK_TRANSFER": ["HDFC Bank", "ICICI Bank", "SBI"]
    },

    "United States": {
        "CARD": ["Visa", "Mastercard", "American Express"],
        "WALLET": ["PayPal"],
        "BANK_TRANSFER": ["Chase", "Bank of America"]
    },

    "United Kingdom": {
        "CARD": ["Visa", "Mastercard"],
        "WALLET": ["PayPal"],
        "BANK_TRANSFER": ["Barclays", "HSBC"]
    },

    "United Arab Emirates": {
        "CARD": ["Visa", "Mastercard"],
        "WALLET": ["PayPal"],
        "BANK_TRANSFER": ["Emirates NBD", "ADCB"]
    },

    "Australia": {
        "CARD": ["Visa", "Mastercard"],
        "WALLET": ["PayPal"],
        "BANK_TRANSFER": ["ANZ", "Commonwealth Bank"]
    },

    "France": {
        "CARD": ["Visa", "Mastercard"],
        "WALLET": ["PayPal"],
        "BANK_TRANSFER": ["BNP Paribas", "Crédit Agricole"]
    },

    "Singapore": {
        "CARD": ["Visa", "Mastercard"],
        "WALLET": ["PayPal"],
        "BANK_TRANSFER": ["DBS", "OCBC"]
    },

    "Japan": {
        "CARD": ["Visa", "Mastercard", "JCB"],
        "WALLET": ["PayPal"],
        "BANK_TRANSFER": ["MUFG", "SMBC"]
    }
}


# ============================================================
# 5. GENERATE PAYMENT METHODS
# ============================================================

payment_methods = []

payment_id_counter = 1

for _, customer in customers_df.iterrows():

    customer_id = customer["customer_id"]
    country = customer["country"]

    currency = currency_map.get(country, "USD")

    available_methods = payment_options.get(
        country,
        {
            "CARD": ["Visa", "Mastercard"],
            "WALLET": ["PayPal"]
        }
    )

    # --------------------------------------------------------
    # 1–3 payment methods per customer
    # --------------------------------------------------------

    number_of_methods = random.choices(
        [1, 2, 3],
        weights=[65, 30, 5],
        k=1
    )[0]

    method_pool = list(available_methods.keys())

    # Don't select more methods than available
    number_of_methods = min(
        number_of_methods,
        len(method_pool)
    )

    selected_types = random.sample(
        method_pool,
        number_of_methods
    )

    # Exactly one default method
    default_index = random.randint(
        0,
        number_of_methods - 1
    )

    for index, method_type in enumerate(selected_types):

        provider = random.choice(
            available_methods[method_type]
        )

        # ----------------------------------------------------
        # Safe synthetic reference
        # ----------------------------------------------------

        if method_type == "CARD":

            masked_reference = (
                f"**** **** **** "
                f"{random.randint(1000, 9999)}"
            )

        elif method_type == "UPI":

            masked_reference = (
                f"user{random.randint(10000, 99999)}"
                f"@{provider.lower().replace(' ', '')}"
            )

        elif method_type == "WALLET":

            masked_reference = (
                f"wallet_{random.randint(100000, 999999)}"
            )

        else:

            masked_reference = (
                f"bank_ref_{random.randint(100000, 999999)}"
            )

        payment_method = {

            "payment_method_id":
                f"PM{payment_id_counter:07d}",

            "customer_id":
                customer_id,

            "payment_method_type":
                method_type,

            "payment_provider":
                provider,

            "masked_reference":
                masked_reference,

            "currency":
                currency,

            "is_default":
                index == default_index,

            "status":
                random.choices(
                    ["Active", "Inactive"],
                    weights=[90, 10],
                    k=1
                )[0],

            "created_date":
                fake.date_between(
                    start_date="-5y",
                    end_date="today"
                )
        }

        payment_methods.append(payment_method)

        payment_id_counter += 1


# ============================================================
# 6. DATAFRAME
# ============================================================

df = pd.DataFrame(payment_methods)

print(f"\nGenerated {len(df)} clean payment methods.")


# ============================================================
# 7. DIRTY DATA INJECTION
# ============================================================

print("Injecting controlled data-quality issues...")


# ------------------------------------------------------------
# A. Duplicate Payment Method IDs (~1%)
# ------------------------------------------------------------

num_duplicates = int(len(df) * 0.01)

duplicate_rows = df.sample(
    n=num_duplicates,
    random_state=42
).copy()

df = pd.concat(
    [df, duplicate_rows],
    ignore_index=True
)


# ------------------------------------------------------------
# B. Null Payment Provider (~1%)
# ------------------------------------------------------------

num_null_provider = int(len(df) * 0.01)

null_indexes = random.sample(
    list(df.index),
    num_null_provider
)

df.loc[
    null_indexes,
    "payment_provider"
] = None


# ------------------------------------------------------------
# C. Invalid Payment Type (~1%)
# ------------------------------------------------------------

num_invalid_types = int(len(df) * 0.01)

invalid_indexes = random.sample(
    list(df.index),
    num_invalid_types
)

for idx in invalid_indexes:

    df.loc[
        idx,
        "payment_method_type"
    ] = random.choice([
        "CRYPTO",
        "UNKNOWN",
        "INVALID"
    ])


# ------------------------------------------------------------
# D. Invalid Status (~1%)
# ------------------------------------------------------------

num_invalid_status = int(len(df) * 0.01)

invalid_status_indexes = random.sample(
    list(df.index),
    num_invalid_status
)

for idx in invalid_status_indexes:

    df.loc[
        idx,
        "status"
    ] = "Pending_Verification"


# ============================================================
# 8. SHUFFLE
# ============================================================

df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ============================================================
# 9. SAVE
# ============================================================

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# 10. VALIDATION
# ============================================================

print("\n========== PAYMENT METHOD VALIDATION ==========")

print("\nColumns:")
print(df.columns.tolist())

print("\nTotal Records:")
print(len(df))

print("\nDuplicate Payment Method IDs:")
print(
    df["payment_method_id"].duplicated().sum()
)

print("\nNull Values:")
print(
    df.isnull().sum()
)

print("\nPayment Method Types:")
print(
    df["payment_method_type"].value_counts()
)

print("\nPayment Providers:")
print(
    df["payment_provider"].value_counts()
)

print("\nPayment Status:")
print(
    df["status"].value_counts()
)

print("\nDefault Payment Methods:")
print(
    df["is_default"].value_counts()
)

print("\nCustomers with Multiple Payment Methods:")

method_counts = (
    df.groupby("customer_id")
      .size()
)

print(
    (method_counts > 1).sum()
)

print("\n===============================================")

print(f"Saved to: {output_file}")