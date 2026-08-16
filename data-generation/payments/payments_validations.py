# ============================================================
# BUSINESS RELATIONSHIP VALIDATION
# ============================================================

print("\n========== BUSINESS RELATIONSHIP VALIDATION ==========")

# ------------------------------------------------------------
# 1. Payment Customer vs Order Customer
# ------------------------------------------------------------

order_customer_map = orders_df.set_index(
    "order_id"
)["customer_id"].to_dict()

payments_df["order_customer_id"] = (
    payments_df["order_id"]
    .map(order_customer_map)
)

customer_mismatch = (
    payments_df["customer_id"]
    != payments_df["order_customer_id"]
)

print(
    "\nCustomer ↔ Order Mismatches:"
)

print(
    customer_mismatch.sum()
)


# ------------------------------------------------------------
# 2. Payment Method Customer vs Payment Customer
# ------------------------------------------------------------

payment_method_customer_map = (
    payment_methods_df
    .set_index("payment_method_id")
    ["customer_id"]
    .to_dict()
)

payments_df["payment_method_customer_id"] = (
    payments_df["payment_method_id"]
    .map(payment_method_customer_map)
)

payment_method_mismatch = (
    payments_df["customer_id"]
    != payments_df["payment_method_customer_id"]
)

print(
    "\nCustomer ↔ Payment Method Mismatches:"
)

print(
    payment_method_mismatch.sum()
)


# ------------------------------------------------------------
# 3. Currency mismatch with Order
# ------------------------------------------------------------

order_currency_map = (
    orders_df
    .set_index("order_id")
    ["currency"]
    .to_dict()
)

payments_df["order_currency"] = (
    payments_df["order_id"]
    .map(order_currency_map)
)

currency_mismatch = (
    payments_df["currency"]
    != payments_df["order_currency"]
)

print(
    "\nPayment ↔ Order Currency Mismatches:"
)

print(
    currency_mismatch.sum()
)


# ------------------------------------------------------------
# 4. Payment Amount vs Order Total
# ------------------------------------------------------------

order_total_map = (
    orders_df
    .set_index("order_id")
    ["total_amount"]
    .to_dict()
)

payments_df["order_total"] = (
    payments_df["order_id"]
    .map(order_total_map)
)

completed_payments = payments_df[
    payments_df["payment_status"] == "Completed"
]

amount_difference = (
    completed_payments["amount"]
    - completed_payments["order_total"]
).abs()

print(
    "\nCompleted Payments > Order Total:"
)

print(
    (
        amount_difference
        > 0.01
    ).sum()
)


print("\n======================================================")