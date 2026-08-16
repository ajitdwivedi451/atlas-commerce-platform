import pandas as pd
import random
import os
from faker import Faker

fake = Faker()

# ============================================================
# CONFIGURATION
# ============================================================

NUM_WAREHOUSES = 45

BASE_DIR = r"D:\Projects\atlas-commerce-platform\data-generation"

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "warehouses"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "warehouses.csv"
)


# ============================================================
# ENTERPRISE LOCATION MASTER
# ============================================================

location_master = {
    "India": {
        "Maharashtra": {
            "Mumbai": ["400001", "400070", "400703"],
            "Pune": ["411001", "411014", "411057"]
        },
        "Karnataka": {
            "Bangalore": ["560001", "560037", "560068"]
        },
        "Delhi": {
            "New Delhi": ["110001", "110020", "110037"]
        },
        "Gujarat": {
            "Ahmedabad": ["380001", "380015", "382405"]
        },
        "Uttar Pradesh": {
            "Noida": ["201301", "201305", "201310"],
            "Lucknow": ["226001", "226010"]
        }
    },

    "United States": {
        "California": {
            "Los Angeles": ["90001", "90012", "90045"],
            "San Francisco": ["94102", "94105", "94124"]
        },
        "Texas": {
            "Houston": ["77001", "77002", "77032"],
            "Dallas": ["75201", "75212", "75247"]
        },
        "New York": {
            "New York City": ["10001", "10010", "10018"]
        }
    },

    "United Kingdom": {
        "England": {
            "London": ["EC1A 1BB", "E1 6AN", "NW1 6XE"],
            "Manchester": ["M1 1AE", "M2 5DB", "M4 1HQ"]
        }
    },

    "Australia": {
        "New South Wales": {
            "Sydney": ["2000", "2010", "2148"]
        },
        "Victoria": {
            "Melbourne": ["3000", "3051", "3121"]
        },
        "Queensland": {
            "Brisbane": ["4000", "4006", "4101"]
        }
    },

    "France": {
        "Île-de-France": {
            "Paris": ["75001", "75008", "75015"]
        },
        "Auvergne-Rhône-Alpes": {
            "Lyon": ["69001", "69003", "69007"]
        }
    },

    "Singapore": {
        "Central Region": {
            "Singapore": ["018956", "048624", "238801"]
        }
    },

    "United Arab Emirates": {
        "Dubai": {
            "Dubai": ["00000"]
        },
        "Abu Dhabi": {
            "Abu Dhabi City": ["00000"]
        }
    },

    "Japan": {
        "Tokyo": {
            "Tokyo": ["100-0001", "105-0001", "160-0022"]
        },
        "Osaka": {
            "Osaka City": ["530-0001", "542-0076"]
        }
    }
}


# ============================================================
# WAREHOUSE TYPES
# ============================================================

warehouse_types = [
    "Fulfillment Center",
    "Distribution Center",
    "Regional Warehouse",
    "Cold Storage",
    "Micro Fulfillment Center"
]

warehouse_statuses = [
    "Active",
    "Active",
    "Active",
    "Inactive",
    "Maintenance"
]


# ============================================================
# COUNTRY → WAREHOUSE COUNT
# ============================================================

country_distribution = {
    "India": 10,
    "United States": 10,
    "United Kingdom": 5,
    "Australia": 5,
    "France": 4,
    "Singapore": 4,
    "United Arab Emirates": 4,
    "Japan": 3
}


# ============================================================
# GENERATE WAREHOUSES
# ============================================================

warehouses = []

warehouse_counter = 1

print("Generating enterprise warehouse master data...")


for country, warehouse_count in country_distribution.items():

    country_locations = location_master[country]

    for _ in range(warehouse_count):

        state = random.choice(
            list(country_locations.keys())
        )

        city = random.choice(
            list(country_locations[state].keys())
        )

        postal_code = random.choice(
            country_locations[state][city]
        )

        warehouse_type = random.choice(
            warehouse_types
        )

        # Keep Cold Storage less common
        if warehouse_type == "Cold Storage":
            capacity = random.randint(
                20_000,
                150_000
            )
        elif warehouse_type == "Micro Fulfillment Center":
            capacity = random.randint(
                10_000,
                75_000
            )
        else:
            capacity = random.randint(
                100_000,
                1_000_000
            )

        # Enterprise-style naming
        city_code = (
            city
            .replace(" ", "")
            .replace("-", "")
            .upper()[:3]
        )

        warehouse_code = (
            f"WH-{city_code}-{warehouse_counter:03d}"
        )

        warehouse_name = (
            f"{city} "
            f"{warehouse_type}"
        )

        created_date = fake.date_between(
            start_date="-8y",
            end_date="-6m"
        )

        warehouses.append({

            "warehouse_id":
                f"WH{warehouse_counter:05d}",

            "warehouse_code":
                warehouse_code,

            "warehouse_name":
                warehouse_name,

            "warehouse_type":
                warehouse_type,

            "country":
                country,

            "state":
                state,

            "city":
                city,

            "postal_code":
                postal_code,

            "capacity_units":
                capacity,

            "warehouse_status":
                random.choice(
                    warehouse_statuses
                ),

            "created_date":
                created_date
        })

        warehouse_counter += 1


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(warehouses)


# ============================================================
# CONTROLLED DATA QUALITY ISSUES
# ============================================================

print("Injecting controlled source-system issues...")


# ------------------------------------------------------------
# Duplicate Warehouse IDs ~1%
# ------------------------------------------------------------

duplicate_count = max(1, int(len(df) * 0.01))

if duplicate_count > 0:

    duplicates = df.sample(
        n=duplicate_count,
        random_state=42
    )

    df = pd.concat(
        [df, duplicates],
        ignore_index=True
    )


# ------------------------------------------------------------
# Null postal codes ~1%
# ------------------------------------------------------------

null_count = max(1, int(len(df) * 0.02))

if null_count > 0:

    indexes = random.sample(
        list(df.index),
        null_count
    )

    df.loc[
        indexes,
        "postal_code"
    ] = None


# ------------------------------------------------------------
# Invalid warehouse status ~1%
# ------------------------------------------------------------

invalid_count = int(
    len(df) * 0.01
)

if invalid_count > 0:

    indexes = random.sample(
        list(df.index),
        invalid_count
    )

    for index in indexes:

        df.loc[
            index,
            "warehouse_status"
        ] = random.choice([
            "UNKNOWN",
            "INVALID_STATUS",
            "Pending_Approval"
        ])


# ------------------------------------------------------------
# Invalid capacity ~1%
# ------------------------------------------------------------

invalid_capacity_count = int(
    len(df) * 0.01
)

if invalid_capacity_count > 0:

    indexes = random.sample(
        list(df.index),
        invalid_capacity_count
    )

    for index in indexes:

        df.loc[
            index,
            "capacity_units"
        ] = random.choice([
            -1000,
            -50000,
            0
        ])


# ============================================================
# SHUFFLE
# ============================================================

df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# VALIDATION
# ============================================================

print("\n========== WAREHOUSE VALIDATION ==========")

print("\nColumns:")
print(df.columns.tolist())

print("\nTotal Records:")
print(len(df))

print("\nDuplicate Warehouse IDs:")
print(
    df["warehouse_id"].duplicated().sum()
)

print("\nDuplicate Warehouse Codes:")
print(
    df["warehouse_code"].duplicated().sum()
)

print("\nNull Values:")
print(
    df.isnull().sum()
)

print("\nWarehouse Types:")
print(
    df["warehouse_type"].value_counts()
)

print("\nWarehouse Status:")
print(
    df["warehouse_status"].value_counts()
)

print("\nCountry Distribution:")
print(
    df["country"].value_counts()
)

print("\nInvalid Capacity:")
print(
    (df["capacity_units"] <= 0).sum()
)

print("\n===========================================")

print(f"\nSaved to:")
print(OUTPUT_FILE)