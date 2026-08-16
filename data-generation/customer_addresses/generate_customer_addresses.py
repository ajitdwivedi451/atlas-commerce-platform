import pandas as pd
import random
import os
from faker import Faker

fake = Faker()

# ============================================================
# 1. PATHS
# ============================================================

customer_file = r"D:\Projects\atlas-commerce-platform\data-generation\customers\customers.csv"

output_dir = r"D:\Projects\atlas-commerce-platform\data-generation\customer_addresses"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "customer_addresses.csv")


# ============================================================
# 2. READ CUSTOMER MASTER
# ============================================================

customers_df = pd.read_csv(customer_file)

print(f"Loaded {len(customers_df)} customer records.")


# ============================================================
# 3. ADDRESS GENERATION
# ============================================================

addresses = []

address_types = ["Home", "Office", "Other"]

address_id_counter = 1

for _, customer in customers_df.iterrows():

    customer_id = customer["customer_id"]
    country = customer["country"]
    state = customer["state"]
    city = customer["city"]

    # --------------------------------------------------------
    # Each customer gets 1–3 addresses
    # --------------------------------------------------------

    number_of_addresses = random.choices(
        [1, 2, 3],
        weights=[70, 25, 5],
        k=1
    )[0]

    selected_types = random.sample(
        address_types,
        number_of_addresses
    )

    # --------------------------------------------------------
    # Exactly one default address
    # --------------------------------------------------------

    default_address_index = random.randint(
        0,
        number_of_addresses - 1
    )

    for index, address_type in enumerate(selected_types):

        valid_from = fake.date_between(
            start_date="-5y",
            end_date="today"
        )

        # Most addresses are currently active
        if random.random() < 0.90:
            valid_to = None
        else:
            valid_to = fake.date_between(
                start_date=valid_from,
                end_date="today"
            )

        address = {
            "address_id": f"ADDR{address_id_counter:07d}",
            "customer_id": customer_id,

            "address_type": address_type,

            "address_line_1": fake.street_address(),
            "address_line_2": (
                fake.secondary_address()
                if random.random() < 0.40
                else None
            ),

            # IMPORTANT:
            # Location comes from CUSTOMER MASTER
            "city": city,
            "state": state,
            "country": country,

            "postal_code": fake.postcode(),

            "is_default": index == default_address_index,

            "valid_from": valid_from,
            "valid_to": valid_to
        }

        addresses.append(address)

        address_id_counter += 1


# ============================================================
# 4. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(addresses)

print(f"Generated {len(df)} clean address records.")


# ============================================================
# 5. INJECT CONTROLLED DIRTY DATA
# ============================================================

print("Injecting controlled data-quality issues...")

# ------------------------------------------------------------
# A. Duplicate Address IDs (~1%)
# ------------------------------------------------------------

num_duplicates = int(len(df) * 0.015)

duplicate_rows = df.sample(
    n=num_duplicates,
    random_state=42
).copy()

df = pd.concat(
    [df, duplicate_rows],
    ignore_index=True
)


# ------------------------------------------------------------
# B. Null Postal Codes (~2%)
# ------------------------------------------------------------

null_postal_count = int(len(df) * 0.02)

null_postal_indexes = random.sample(
    list(df.index),
    null_postal_count
)

df.loc[
    null_postal_indexes,
    "postal_code"
] = None


# ------------------------------------------------------------
# C. Missing Address Line 2 (~normal business case)
# ------------------------------------------------------------

# Already naturally generated as NULL for many records.


# ------------------------------------------------------------
# D. Invalid Address Type (~1%)
# ------------------------------------------------------------

invalid_type_count = int(len(df) * 0.01)

invalid_type_indexes = random.sample(
    list(df.index),
    invalid_type_count
)

for idx in invalid_type_indexes:
    df.loc[idx, "address_type"] = random.choice([
        "Unknown",
        "Temporary",
        "Invalid_Type"
    ])


# ============================================================
# 6. SHUFFLE
# ============================================================

df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ============================================================
# 7. SAVE
# ============================================================

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# 8. BASIC VALIDATION
# ============================================================

print("\n========== ADDRESS DATA VALIDATION ==========")

print("\nColumns:")
print(df.columns.tolist())

print("\nTotal Records:")
print(len(df))

print("\nDuplicate Address IDs:")
print(
    df["address_id"].duplicated().sum()
)

print("\nNull Values:")
print(
    df.isnull().sum()
)

print("\nAddress Types:")
print(
    df["address_type"].value_counts()
)

print("\nCustomers with Multiple Addresses:")

address_counts = (
    df.groupby("customer_id")
      .size()
)

print(
    (address_counts > 1).sum()
)

print("\nDefault Addresses:")
print(
    df["is_default"].value_counts()
)

print("\n=============================================")
print(f"Saved to: {output_file}")