# Healthcare / Life Sciences Knowledge Graph

A **Databricks-native** healthcare analytics project connecting **patients**, **treatments**, and **outcomes** using **Databricks Lakebase**, **AI/BI Dashboards**, and a **Databricks App**.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │               Databricks Lakebase (Postgres)                       │  │
│  │                                                                    │  │
│  │  patients │ providers │ encounters │ diagnoses │ treatments        │  │
│  │  medications │ treatment_outcomes │ adverse_events │ lab_results   │  │
│  │                                                                    │  │
│  │  Serverless • Autoscaling • Scale-to-zero • Sub-ms reads          │  │
│  └────────────────────┬──────────────────────┬────────────────────────┘  │
│                       │                      │                           │
│                       ▼                      ▼                           │
│  ┌──────────────────────────┐  ┌──────────────────────────────────────┐  │
│  │   AI/BI Dashboards       │  │   Databricks App (Streamlit)         │  │
│  │   & Genie                │  │                                      │  │
│  │                          │  │   Overview │ Patient 360 │ Treatment │  │
│  │   • Treatment efficacy   │  │   Analytics │ Adverse Events │ Labs  │  │
│  │   • Patient demographics │  │   Knowledge Graph Explorer           │  │
│  │   • Adverse events       │  │                                      │  │
│  │   • Lab results          │  │   OAuth-authenticated direct         │  │
│  │   • Natural language Q&A │  │   connection to Lakebase             │  │
│  └──────────────────────────┘  └──────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
HLS Knowledge Graph/
│
├── 01_lakebase_setup/
│   ├── 01_create_lakebase_tables.sql       # Lakebase Postgres DDL (9 tables)
│   ├── 02_seed_sample_data.sql             # Realistic synthetic healthcare data
│   └── 03_create_indexes.sql               # Performance indexes
│
├── 02_ai_bi_dashboards/
│   ├── 01_dashboard_queries.sql            # 10 dashboard widget queries
│   ├── 02_genie_space_setup.md             # Genie space configuration guide
│   └── 03_sample_genie_questions.md        # Example natural-language questions
│
└── 03_databricks_app/
    ├── app.yaml                            # Databricks App configuration
    ├── app.py                              # Main Streamlit application
    ├── db.py                               # Lakebase connection (OAuth + pool)
    ├── requirements.txt                    # Python dependencies
    ├── SETUP.md                            # Deployment instructions
    └── pages/
        ├── overview.py                     # KPI dashboard
        ├── patient_360.py                  # Patient search & clinical profile
        ├── treatment_analytics.py          # Treatment efficacy analysis
        ├── adverse_events.py               # Safety surveillance
        ├── lab_results.py                  # Lab trends & abnormal flags
        └── knowledge_graph.py              # Interactive patient journey graph
```

## Prerequisites

| Component | Requirement |
|-----------|-------------|
| Databricks Workspace | Premium or Enterprise tier |
| Lakebase | Enabled in workspace |
| Databricks Apps | Enabled for Streamlit deployment |

## Quick Start

1. **Create a Lakebase project** in the Databricks UI (Apps → Lakebase → Create project)
2. **Run the DDL** — paste `01_lakebase_setup/01_create_lakebase_tables.sql` into the Lakebase SQL Editor
3. **Seed data** — run `01_lakebase_setup/02_seed_sample_data.sql` in the Lakebase SQL Editor
4. **Create indexes** — run `01_lakebase_setup/03_create_indexes.sql`
5. **Build AI/BI dashboards** — use queries from `02_ai_bi_dashboards/01_dashboard_queries.sql`
6. **Set up Genie** — follow `02_ai_bi_dashboards/02_genie_space_setup.md`
7. **Deploy the Databricks App** — follow `03_databricks_app/SETUP.md`

## Key Components

### Lakebase (OLTP)
Serverless Postgres database natively integrated with Databricks. Stores the operational healthcare data — patient records, treatment orders, encounter logs — with sub-millisecond read latency. Supports autoscaling, scale-to-zero, instant branching, and point-in-time restore.

### AI/BI (Dashboards + Genie)
- **Dashboards**: 10 pre-built widget queries covering patient demographics, treatment efficacy, adverse event monitoring, lab results, provider activity, and diagnosis cohorts
- **Genie**: Natural language interface where clinicians and analysts ask questions like _"Which treatments had the highest improvement rate for cancer patients?"_

### Databricks App (Streamlit)
Interactive 6-page web application deployed on Databricks Apps, connecting directly to Lakebase via OAuth-authenticated Postgres. Pages: Overview dashboard, Patient 360 (search + full clinical profile), Treatment Analytics (efficacy comparisons), Adverse Events Monitor (safety surveillance), Lab Results Tracker (trends + abnormal flags), and Knowledge Graph Explorer (interactive visual graph of patient clinical journeys).
