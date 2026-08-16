import pandas as pd

df = pd.read_csv("customers.csv")

print("\nCountry / Currency:")
print(
    df.groupby(["country", "currency"])
      .size()
)

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nDuplicate customer IDs:")
print(df["customer_id"].duplicated().sum())

print("\nNull values:")
print(df.isnull().sum())

print("\nInvalid emails:")
print((~df["email"].fillna("").str.contains("@")).sum())

print("\nCustomer status:")
print(df["customer_status"].value_counts())

print("\nLoyalty tier:")
print(df["loyalty_tier"].value_counts())