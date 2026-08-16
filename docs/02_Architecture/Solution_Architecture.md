# Solution Architecture

## Business Source Systems

| Source System | Data | Type |
|--------------|------|------|
| E-Commerce Website | Orders, Customers | Batch + Streaming |
| Mobile Application | Clickstream, User Activity | Streaming |
| Marketplace Sellers | Product Catalog | Batch |
| Warehouse Management System (WMS) | Inventory | Batch |
| Order Management System (OMS) | Orders | Batch |
| Payment Gateway | Payments | Streaming |
| Logistics Partner | Shipments | Batch |
| CRM System | Customer Profiles | Batch |


---

# Data Classification

| Source | Processing Type | Azure Service |
|---------|-----------------|---------------|
| Website Orders | Streaming | Event Hub |
| Mobile Clickstream | Streaming | Event Hub |
| Payment Events | Streaming | Event Hub |
| Product Catalog | Batch | Azure Data Factory |
| Inventory | Batch | Azure Data Factory |
| Customer Master | Batch + CDC | Azure Data Factory |
| Warehouse Data | Batch | Azure Data Factory |
| Shipment Data | Batch | Azure Data Factory |

---

# High-Level Azure Service Mapping

| Layer | Azure Service | Responsibility |
|--------|---------------|----------------|
| Data Sources | Website, Mobile App, ERP, WMS, OMS | Generate operational data |
| Batch Ingestion | Azure Data Factory | Scheduled ingestion from source systems |
| Streaming Ingestion | Azure Event Hubs | Real-time event ingestion |
| Data Lake | Azure Data Lake Storage Gen2 | Centralized storage for raw and curated data |
| Processing | Azure Databricks | Batch and streaming data transformation |
| Storage Format | Delta Lake | ACID-compliant storage and versioning |
| Governance | Unity Catalog | Data governance, cataloging and access control |
| Orchestration | Azure Data Factory + Databricks Workflows | Pipeline orchestration and scheduling |
| Enterprise Warehouse | Azure Synapse Analytics | Enterprise analytical workloads |
| Cloud Data Warehouse | Snowflake | External analytical platform and advanced analytics |
| Reporting | Power BI | Business dashboards and executive reporting |
| Secrets Management | Azure Key Vault | Secure storage of credentials and secrets |
| Monitoring | Azure Monitor + Log Analytics | Monitoring, diagnostics and alerting |
| DevOps | Azure DevOps + GitHub | Agile planning, version control and CI/CD |

# Enterprise Data Flow

## Batch Data Flow

```
Business Source Systems
        │
        ▼
Azure Data Factory
        │
        ▼
Azure Data Lake Storage Gen2 (Bronze)
        │
        ▼
Azure Databricks
        │
        ▼
Silver Layer
        │
        ▼
Gold Layer
        │
        ├──────────────► Azure Synapse Analytics
        │
        ├──────────────► Snowflake
        │
        ▼
Power BI
```

---

## Streaming Data Flow

```
Website / Mobile Application
            │
            ▼
Azure Event Hubs
            │
            ▼
Azure Databricks Structured Streaming
            │
            ▼
Delta Lake (Bronze)
            │
            ▼
Silver Layer
            │
            ▼
Gold Layer
            │
            ▼
Power BI
```
Final architecture Diagram
Business Systems
        │
 ┌──────┴────────┐
 │               │
Batch       Streaming
 │               │
ADF        Event Hubs
 └──────┬────────┘
        │
ADLS Gen2 (Bronze)
        │
Databricks
        │
Delta Lake
        │
Unity Catalog
        │
Silver
        │
Gold
   ┌────┴────┐
   │         │
Synapse   Snowflake
      │
   Power BI

Supporting:
• Azure Key Vault
• Microsoft Entra ID
• Azure Monitor
• Log Analytics
• Azure DevOps
• GitHub

## Master Enterprise Data Model – ERD

### Purpose

The Master ERD defines the logical relationships between the source-system datasets
used by the Atlas Commerce International (ACI) e-commerce platform.

The model supports:

- Customer and customer profile management
- Product and inventory management
- Order and order-item processing
- Payment processing
- Shipment and fulfillment tracking
- Returns and refunds
- Product reviews
- Customer support
- Digital clickstream analytics

The source datasets intentionally contain controlled data-quality issues so that
the downstream Azure Data Engineering pipeline can demonstrate validation,
quarantine, cleansing, referential-integrity handling, and business-rule
validation.

### Source Dataset Model

| Dataset | Primary Key | Main Foreign Keys |
|---|---|---|
| Customers | customer_id | — |
| Customer Addresses | address_id | customer_id |
| Customer Payment Methods | payment_method_id | customer_id |
| Products | product_id | — |
| Orders | order_id | customer_id, shipping_address_id, billing_address_id, payment_method_id |
| Order Items | order_item_id | order_id, product_id |
| Warehouses | warehouse_id | — |
| Inventory | inventory_id | product_id, warehouse_id |
| Payments | payment_id | order_id, customer_id, payment_method_id |
| Shipments | shipment_id | order_id, customer_id, warehouse_id, shipping_address_id |
| Shipment Items | shipment_item_id | shipment_id, order_id, order_item_id, product_id |
| Product Reviews | review_id | customer_id, product_id, order_id, order_item_id |
| Returns | return_id | order_id, order_item_id, customer_id, product_id, shipment_id |
| Customer Support Tickets | ticket_id | customer_id, order_id, order_item_id, product_id, payment_id, shipment_id, return_id |
| Clickstream Events | event_id | customer_id, product_id, order_id |

### Relationship and Cardinality Mapping

| Parent | Child | Cardinality | Relationship |
|---|---|---:|---|
| Customers | Customer Addresses | 1:N | One customer can have multiple addresses |
| Customers | Customer Payment Methods | 1:N | One customer can have multiple payment methods |
| Customers | Orders | 1:N | One customer can place multiple orders |
| Customers | Payments | 1:N | One customer can make multiple payment transactions |
| Customers | Product Reviews | 1:N | One customer can create multiple reviews |
| Customers | Returns | 1:N | One customer can create multiple returns |
| Customers | Support Tickets | 1:N | One customer can create multiple tickets |
| Customers | Clickstream Events | 1:N | One customer can generate multiple events |
| Products | Order Items | 1:N | One product can appear in multiple order items |
| Products | Inventory | 1:N | One product can exist in multiple warehouses |
| Products | Product Reviews | 1:N | One product can have multiple reviews |
| Products | Shipment Items | 1:N | One product can appear in multiple shipments |
| Products | Returns | 1:N | One product can have multiple returns |
| Orders | Order Items | 1:N | One order contains multiple items |
| Orders | Payments | 1:N | One order can have multiple payment transactions |
| Orders | Shipments | 1:N | One order can be fulfilled through multiple shipments |
| Orders | Product Reviews | 1:N | One order can be associated with multiple reviews |
| Orders | Returns | 1:N | One order can contain multiple returned items |
| Orders | Support Tickets | 1:N | One order can generate multiple support tickets |
| Orders | Clickstream Events | 1:N | An order may be associated with multiple events |
| Order Items | Shipment Items | 1:N | One order item can be fulfilled across shipments |
| Order Items | Product Reviews | 1:N | An order item can have review records |
| Order Items | Returns | 1:N | An order item can generate return records |
| Warehouses | Inventory | 1:N | One warehouse stores many product inventory records |
| Warehouses | Shipments | 1:N | One warehouse can fulfill many shipments |
| Customer Payment Methods | Orders | 1:N | One payment method can be used by multiple orders |
| Customer Payment Methods | Payments | 1:N | One payment method can generate multiple payments |
| Shipments | Shipment Items | 1:N | One shipment contains multiple shipment items |
| Shipments | Returns | 1:N | A shipment can be associated with return transactions |
| Shipments | Support Tickets | 1:N | A shipment can generate multiple support tickets |
| Payments | Support Tickets | 1:N | A payment can generate support tickets |
| Returns | Support Tickets | 1:N | A return can generate support tickets |

### Logical ERD

```mermaid
erDiagram

    CUSTOMERS ||--o{ CUSTOMER_ADDRESSES : has
    CUSTOMERS ||--o{ CUSTOMER_PAYMENT_METHODS : owns
    CUSTOMERS ||--o{ ORDERS : places
    CUSTOMERS ||--o{ PAYMENTS : makes
    CUSTOMERS ||--o{ PRODUCT_REVIEWS : writes
    CUSTOMERS ||--o{ RETURNS : creates
    CUSTOMERS ||--o{ SUPPORT_TICKETS : raises
    CUSTOMERS ||--o{ CLICKSTREAM_EVENTS : generates

    PRODUCTS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ INVENTORY : stocked_in
    PRODUCTS ||--o{ PRODUCT_REVIEWS : receives
    PRODUCTS ||--o{ SHIPMENT_ITEMS : shipped_as
    PRODUCTS ||--o{ RETURNS : returned_as

    ORDERS ||--|{ ORDER_ITEMS : contains
    ORDERS ||--o{ PAYMENTS : has
    ORDERS ||--o{ SHIPMENTS : fulfilled_by
    ORDERS ||--o{ PRODUCT_REVIEWS : generates
    ORDERS ||--o{ RETURNS : generates
    ORDERS ||--o{ SUPPORT_TICKETS : generates
    ORDERS ||--o{ CLICKSTREAM_EVENTS : associated_with

    ORDER_ITEMS ||--o{ SHIPMENT_ITEMS : fulfilled_as
    ORDER_ITEMS ||--o{ PRODUCT_REVIEWS : reviewed_in
    ORDER_ITEMS ||--o{ RETURNS : returned_in

    WAREHOUSES ||--o{ INVENTORY : stores
    WAREHOUSES ||--o{ SHIPMENTS : fulfills

    CUSTOMER_PAYMENT_METHODS ||--o{ ORDERS : used_by
    CUSTOMER_PAYMENT_METHODS ||--o{ PAYMENTS : processes

    SHIPMENTS ||--|{ SHIPMENT_ITEMS : contains
    SHIPMENTS ||--o{ RETURNS : associated_with
    SHIPMENTS ||--o{ SUPPORT_TICKETS : generates

    PAYMENTS ||--o{ SUPPORT_TICKETS : generates
    RETURNS ||--o{ SUPPORT_TICKETS : generates