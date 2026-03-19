# Healthcare / Life Sciences Knowledge Graph

A **fully Databricks-native** project that builds a **knowledge graph** connecting **patients**, **treatments**, and **outcomes** using Databricks Lakebase, Zero ETL (Lakehouse Sync), SQL recursive CTEs, and AI/BI.

No external graph database required — the knowledge graph runs entirely on Databricks SQL.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        OPERATIONAL LAYER                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              Databricks Lakebase (Postgres)                      │   │
│  │  ┌────────────┐  ┌────────────────┐  ┌───────────────────────┐  │   │
│  │  │  patients   │  │  treatments    │  │  treatment_outcomes   │  │   │
│  │  │  providers  │  │  medications   │  │  adverse_events       │  │   │
│  │  │  encounters │  │  diagnoses     │  │  lab_results          │  │   │
│  │  └────────────┘  └────────────────┘  └───────────────────────┘  │   │
│  └──────────────────────────┬───────────────────────────────────────┘   │
│                             │ Lakehouse Sync (CDC)                      │
│                             │ Zero ETL — no pipelines needed            │
│                             ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              Unity Catalog (Delta Tables)                        │   │
│  │         Managed tables auto-synced via Change Data Capture       │   │
│  └──────┬────────────────────────┬──────────────────┬───────────────┘   │
│         │                        │                  │                   │
│         ▼                        ▼                  ▼                   │
│  ┌────────────────┐  ┌───────────────────┐  ┌────────────────────┐     │
│  │ SQL Knowledge  │  │ AI/BI Dashboards  │  │ Lakebase Internals │     │
│  │ Graph          │  │ & Genie           │  │ Dashboard          │     │
│  │ (Recursive     │  │                   │  │                    │     │
│  │  CTEs)         │  │ • Treatment       │  │ • Autoscaling      │     │
│  │                │  │   efficacy        │  │ • Lakehouse Sync   │     │
│  │ Patient ──▶    │  │ • Patient         │  │ • Branching        │     │
│  │  Treatment ──▶ │  │   outcomes        │  │ • Query perf       │     │
│  │   Outcome      │  │ • Adverse events  │  │ • Governance       │     │
│  └────────────────┘  └───────────────────┘  └────────────────────┘     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │               Databricks App (Streamlit)                         │   │
│  │  Patient 360 │ Treatment Analytics │ Adverse Events │ Lab Trends │   │
│  │  Knowledge Graph Explorer │ Overview Dashboard                   │   │
│  │  Connects directly to Lakebase via OAuth + psycopg              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
HLS Knowledge Graph/
│
├── 01_lakebase_setup/
│   ├── 01_create_lakebase_tables.sql       # Lakebase Postgres DDL
│   ├── 02_seed_sample_data.sql             # Realistic sample data
│   └── 03_create_indexes.sql               # Performance indexes
│
├── 02_zero_etl_lakehouse_sync/
│   ├── 01_enable_lakehouse_sync.py         # Enable CDC replication
│   ├── 02_create_gold_views.sql            # Gold-layer analytics views
│   └── 03_verify_sync.py                   # Sync status verification
│
├── 03_sql_knowledge_graph/
│   ├── 01_graph_traversal_queries.sql      # Recursive CTE graph queries
│   ├── 02_graph_views.sql                  # Materialized graph edge views
│   └── 03_graph_analytics.py              # Graph analytics notebook
│
├── 04_ai_bi_dashboards/
│   ├── 01_dashboard_queries.sql            # SQL for AI/BI dashboards
│   ├── 02_genie_space_setup.md             # Genie space configuration
│   └── 03_sample_genie_questions.md        # Example natural-language questions
│
├── 05_lakebase_internals/
│   ├── 01_create_metrics_tables.sql        # Lakebase monitoring table DDL
│   ├── 02_seed_metrics_data.py             # Generate 7 days of sample metrics
│   └── 03_lakebase_dashboard_queries.sql   # 25+ dashboard widget queries
│
├── 06_end_to_end_demo/
│   └── 00_run_demo.py                      # Full orchestration notebook
│
└── 07_databricks_app/
    ├── app.yaml                            # Databricks App configuration
    ├── app.py                              # Main Streamlit application
    ├── db.py                               # Lakebase connection (OAuth + pool)
    ├── requirements.txt                    # Python dependencies
    ├── SETUP.md                            # Deployment instructions
    └── pages/
        ├── overview.py                     # KPI dashboard
        ├── patient_360.py                  # Patient search & detail view
        ├── treatment_analytics.py          # Treatment efficacy analysis
        ├── adverse_events.py               # Safety surveillance
        ├── lab_results.py                  # Lab trends & abnormal flags
        └── knowledge_graph.py              # Interactive graph explorer
```

## Prerequisites

| Component | Requirement |
|-----------|-------------|
| Databricks Workspace | Premium or Enterprise tier |
| Lakebase | Enabled in workspace (GA as of 2026) |
| Unity Catalog | Configured with a catalog for this project |
| Databricks Runtime | 14.3 LTS+ |

## Quick Start

1. **Create a Lakebase project** in the Databricks UI under the Database section
2. **Run the DDL** in `01_lakebase_setup/01_create_lakebase_tables.sql` via the Lakebase SQL Editor
3. **Seed data** with `01_lakebase_setup/02_seed_sample_data.sql`
4. **Enable Lakehouse Sync** by running `02_zero_etl_lakehouse_sync/01_enable_lakehouse_sync.py`
5. **Create graph views** by running `03_sql_knowledge_graph/02_graph_views.sql`
6. **Explore the graph** with `03_sql_knowledge_graph/03_graph_analytics.py`
7. **Create AI/BI dashboards** using queries from `04_ai_bi_dashboards/01_dashboard_queries.sql`
8. **Seed Lakebase metrics** with `05_lakebase_internals/02_seed_metrics_data.py`
9. **Build Lakebase internals dashboard** using `05_lakebase_internals/03_lakebase_dashboard_queries.sql`
10. **Set up Genie** following `04_ai_bi_dashboards/02_genie_space_setup.md`

## Key Concepts

### Lakebase (OLTP)
Serverless Postgres database natively integrated with Databricks. Decoupled compute-storage architecture (built on Neon). Stores the operational healthcare data — patient records, treatment orders, encounter logs — with sub-millisecond read latency. Supports autoscaling, scale-to-zero, instant branching, and point-in-time restore.

### Zero ETL (Lakehouse Sync)
Continuous CDC replication from Lakebase Postgres into Unity Catalog managed Delta tables. No external pipelines, no Spark jobs, no scheduling. Data flows automatically with seconds of latency. SCD Type 2 history tracking built-in.

### SQL Knowledge Graph (Recursive CTEs)
Graph traversals implemented entirely in Databricks SQL using recursive CTEs. Models the same relationships a graph database would — patient journeys, treatment pathways, comorbidity networks, provider collaboration — but without any external infrastructure. Includes pre-built graph views (`graph_all_edges`, `graph_patient_similarity`, `graph_comorbidities`, etc.) for easy querying.

### Lakebase Internals Dashboard
Dedicated dashboard showcasing Lakebase platform capabilities with 7 days of simulated metrics across 6 feature areas: autoscaling & compute, Lakehouse Sync CDC, branching, query performance, DML throughput, and Unity Catalog governance. 25+ ready-to-use dashboard widget queries.

### Databricks App (Streamlit)
Interactive web application deployed on Databricks Apps, connecting directly to Lakebase via OAuth-authenticated Postgres. Six pages: Overview dashboard, Patient 360 (search + full clinical profile), Treatment Analytics (efficacy comparisons), Adverse Events Monitor (safety surveillance), Lab Results Tracker (trends + abnormal flags), and Knowledge Graph Explorer (interactive visual graph of patient journeys). See `07_databricks_app/SETUP.md` for deployment instructions.

### AI/BI (Dashboards + Genie)
- **Dashboards**: Visual analytics on treatment efficacy, patient outcomes, adverse events, and Lakebase platform health
- **Genie**: Natural language interface where clinicians and analysts ask questions like _"Which treatments had the highest remission rate for stage III lung cancer patients over 65?"_
