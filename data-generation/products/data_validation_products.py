import pandas as pd

df = pd.read_csv("D:/Projects/atlas-commerce-platform/data-generation/products/products_dirty1.csv")

print(df.shape)

print("\nDuplicate Product IDs:")
print(df["product_id"].duplicated().sum())

print("\nDuplicate SKUs:")
print(df["stock_keeping_unit"].duplicated().sum())

print("\nNull Values:")
print(df.isnull().sum())

print("\nInvalid Prices:")
print((df["unit_price"] <= 0).sum())

print("\nInvalid Ratings:")
print(((df["rating"] < 1) | (df["rating"] > 5)).sum())

print("\nInvalid Status:")
print(
    (~df["product_status"].isin([
        "Active",
        "Inactive",
        "Discontinued",
        "Coming Soon"
    ])).sum()
)