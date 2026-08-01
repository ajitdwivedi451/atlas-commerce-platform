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