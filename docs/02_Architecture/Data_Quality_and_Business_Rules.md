# Data Quality & Business Rules

## 1. Purpose

This document defines the consolidated data-quality rules and business
validation rules for the source datasets generated for the Atlas Commerce
International (ACI) e-commerce platform.

The source datasets intentionally contain controlled data-quality issues.
These issues simulate realistic enterprise source-system problems and will
be handled during downstream Bronze-to-Silver processing.

---

## 2. Data Quality Dimensions

The platform validates the following dimensions:

| Dimension | Purpose |
|---|---|
| Completeness | Identify missing mandatory values |
| Uniqueness | Detect duplicate primary/business keys |
| Validity | Validate allowed values and formats |
| Accuracy | Validate values against business rules |
| Consistency | Validate relationships between datasets |
| Referential Integrity | Validate PK/FK relationships |
| Timeliness | Validate event and transaction dates |
| Integrity | Detect orphan and contradictory records |

---

## 3. Dataset-Level Rules

### 3.1 Customers

Key rules:

- `customer_id` must be unique.
- `customer_id` must not be NULL.
- Email should follow a valid email pattern.
- Customer status must belong to the supported status domain.
- Loyalty tier must belong to the supported loyalty hierarchy.
- Date of birth must represent a valid customer age.
- Registration date must not be earlier than the date of birth.
- Controlled duplicates, NULLs and invalid values are retained for downstream DQ processing.

---

### 3.2 Customer Addresses

Key rules:

- `address_id` must be unique.
- `customer_id` must reference an existing customer.
- Address type should belong to the supported domain.
- `city`, `state` and `country` should be geographically consistent.
- Postal code should be valid for the associated country where applicable.
- Only valid/default address records should be selected for downstream consumption.
- `valid_to` may be NULL for currently active addresses.
- Multiple addresses per customer are allowed.

---

### 3.3 Customer Payment Methods

Key rules:

- `payment_method_id` must be unique.
- `customer_id` must reference an existing customer.
- Payment method type must belong to the supported domain.
- Provider should be compatible with the payment method.
- Currency must be a supported currency.
- Masked payment references must not contain raw sensitive payment information.
- Multiple payment methods per customer are allowed.
- A customer may have one or more default methods according to source-system rules.

---

### 3.4 Products

Key rules:

- `product_id` must be unique.
- Product identifiers must not be NULL.
- Product price must be non-negative.
- Product category/subcategory relationships must be valid.
- Product status must belong to the supported domain.
- Product attributes must follow the expected schema.
- Invalid product records should be quarantined during Silver processing.

---

### 3.5 Orders

Key rules:

- `order_id` must be unique.
- `customer_id` must reference an existing customer.
- Shipping and billing addresses should belong to the same customer.
- Payment method should belong to the same customer.
- Order status must belong to the supported status domain.
- Order date must be valid.
- Monetary amounts must not be negative.
- `total_amount` must be consistent with subtotal, discount, tax and shipping.
- Currency must be supported.
- Sales channel must belong to the supported channel domain.

---

### 3.6 Order Items

Key rules:

- `order_item_id` must be unique.
- `order_id` must reference an existing order.
- `product_id` must reference an existing product.
- Product relationship must be consistent with the referenced order item.
- Quantity must be positive for active order items.
- Unit price must be non-negative.
- Currency should match the associated order.
- Item totals should be mathematically consistent.
- Orphan order items must be quarantined.

---

### 3.7 Warehouses

Key rules:

- `warehouse_id` must be unique.
- `warehouse_code` must be unique.
- Warehouse type must belong to the supported domain.
- Warehouse status must belong to the supported domain.
- Capacity must be non-negative.
- Country/state/city relationships should be valid.

---

### 3.8 Inventory

Key rules:

- `inventory_id` must be unique.
- `product_id` must reference an existing product.
- `warehouse_id` must reference an existing warehouse.
- Available, reserved, damaged and in-transit quantities must be non-negative.
- Reserved quantity should not exceed available inventory unless explicitly supported by source-system semantics.
- Reorder level and reorder quantity should be non-negative.
- Inventory status must belong to the supported domain.
- Updated/restocked dates must not contain invalid future values.

---

### 3.9 Payments

Key rules:

- `payment_id` must be unique.
- `order_id` must reference an existing order.
- `customer_id` must match the customer associated with the order.
- `payment_method_id` must reference an existing payment method.
- Payment method must belong to the same customer.
- Payment currency should match the associated order currency.
- Payment amount must be non-negative after excluding intentionally injected errors.
- Completed payment amount must not exceed the applicable order amount.
- Refund transactions must follow refund business rules.
- Failed payments should contain an appropriate failure reason where applicable.
- Processed date should not precede payment date.

---

### 3.10 Shipments

Key rules:

- `shipment_id` must be unique.
- `order_id` must reference an existing order.
- `customer_id` must match the order customer.
- `warehouse_id` must reference an existing warehouse.
- `shipping_address_id` must belong to the order/customer.
- Shipment date must not precede order date.
- Actual delivery date must not precede shipment date.
- Delivered shipments should have an actual delivery date.
- Non-delivered shipments normally should not have an actual delivery date.
- Shipping cost must be non-negative.
- Shipment currency should match the associated order.
- Delivery attempts must be non-negative.
- Invalid shipment statuses must be quarantined.

---

### 3.11 Shipment Items

Key rules:

- `shipment_item_id` must be unique.
- `shipment_id` must reference an existing shipment.
- `order_id` must reference an existing order.
- `order_item_id` must reference an existing order item.
- `product_id` must match the referenced order item.
- Shipment and order relationships must be consistent.
- Quantity shipped must be non-negative.
- Quantity shipped must not exceed ordered quantity.
- Currency must match the associated order.
- Unit price should match the corresponding order item.
- Shipment item status must belong to the supported domain.

---

### 3.12 Product Reviews

Key rules:

- `review_id` must be unique.
- Customer must exist.
- Product must exist.
- Order and order item must exist for verified purchases.
- Order item must belong to the referenced order.
- Product must match the referenced order item.
- Rating must be within the supported range.
- Review date must not precede the order date.
- Review date must not be in the future.
- Helpful and reported vote counts must be non-negative.
- Verified purchase flag must contain a valid boolean value.

---

### 3.13 Returns

Key rules:

- `return_id` must be unique.
- `order_id` must reference an existing order.
- `order_item_id` must reference an existing order item.
- Product must match the referenced order item.
- Customer must match the order customer.
- Shipment should reference a valid shipment where applicable.
- Return date must not precede order date.
- Received date must not precede return date.
- Quantity returned must be positive.
- Returned quantity must not exceed ordered quantity.
- Refund amount must be non-negative.
- Refund currency must be valid.
- Refund/exchange/replacement logic must follow return type.

---

### 3.14 Customer Support Tickets

Key rules:

- `ticket_id` must be unique.
- Customer must reference an existing customer.
- Optional order/payment/shipment/return references must be valid when populated.
- Customer must match the referenced order.
- Product must match the referenced order item.
- Ticket category, priority, channel and status must belong to supported domains.
- Ticket date must not precede the associated order date.
- First response must not precede ticket creation.
- Resolution date must not precede ticket date or first response.
- Closed/resolved tickets should normally contain a resolution date.
- Open/in-progress tickets should normally not contain a resolution date.
- Customer satisfaction scores must be within the supported range.
- Reopened count must be non-negative.

---

### 3.15 Clickstream Events

Key rules:

- `event_id` must be unique.
- Event timestamp must be valid.
- Customer, product and order references are optional depending on event type.
- Referenced customer/product/order must exist when populated.
- Event type must belong to the supported event domain.
- Event timestamps should not contain unrealistic future values.
- Duplicate events should be detected.
- Anonymous events must remain supported.
- Session identifiers should be used to group user activity.

---

# 4. Cross-Dataset Referential Integrity

The following relationships must be validated during Silver processing:

| Parent | Child | Validation |
|---|---|---|
| Customers | Addresses | `customer_id` |
| Customers | Payment Methods | `customer_id` |
| Customers | Orders | `customer_id` |
| Customers | Payments | `customer_id` |
| Products | Order Items | `product_id` |
| Orders | Order Items | `order_id` |
| Products | Inventory | `product_id` |
| Warehouses | Inventory | `warehouse_id` |
| Orders | Payments | `order_id` |
| Orders | Shipments | `order_id` |
| Shipments | Shipment Items | `shipment_id` |
| Order Items | Shipment Items | `order_item_id` |
| Products | Shipment Items | `product_id` |
| Order Items | Reviews | `order_item_id` |
| Orders | Returns | `order_id` |
| Order Items | Returns | `order_item_id` |
| Products | Returns | `product_id` |
| Orders | Support Tickets | `order_id` |

---

# 5. Business Relationship Validation

Beyond simple FK validation, the pipeline must validate relationships such as:

```text
Customer → Order
Customer → Payment Method
Customer → Payment
Order → Order Item
Order → Payment
Order → Shipment
Order Item → Product
Order Item → Shipment Item
Order Item → Return
Shipment → Shipment Item