# Deploying the HLS Knowledge Graph Databricks App

## Prerequisites

- Lakebase project created with HLS tables populated (Steps 01)
- Databricks workspace with Apps enabled
- Serverless compute enabled

## Option A: Deploy from Template UI (Recommended)

1. **Go to** your Databricks workspace → click **+ New App**
2. **Select** the **Streamlit** template (or start from scratch)
3. **Add Lakebase resource**:
   - Select your Lakebase project, branch (`production`), and database (`databricks_postgres`)
   - This auto-creates a service principal with database permissions
   - Connection details are injected as environment variables
4. **Upload the app code**:
   - Upload all files from this `07_databricks_app/` folder to the app
   - Or sync via CLI (see below)
5. **Deploy** and wait ~2-3 minutes

## Option B: Deploy via Databricks CLI

```bash
# Authenticate
databricks auth login --host https://e2-demo-field-eng.cloud.databricks.com

# Sync code to workspace
databricks sync ./07_databricks_app /Workspace/Users/ankur.nayyar@databricks.com/hls-app

# Deploy
databricks apps deploy hls-knowledge-graph \
  --source-code-path /Workspace/Users/ankur.nayyar@databricks.com/hls-app
```

## Database Authentication Setup

The app uses OAuth tokens for Lakebase authentication. When added as a resource,
Databricks auto-configures this. For manual setup:

```sql
-- Run in Lakebase SQL Editor:
CREATE EXTENSION IF NOT EXISTS databricks_auth;

-- Replace <CLIENT_ID> with your app's service principal ID
SELECT databricks_create_role('<CLIENT_ID>', 'service_principal');

GRANT CONNECT ON DATABASE databricks_postgres TO "<CLIENT_ID>";
GRANT USAGE ON SCHEMA public TO "<CLIENT_ID>";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "<CLIENT_ID>";
```

## Environment Variables

These are auto-injected when Lakebase is added as an app resource:

| Variable | Description |
|----------|-------------|
| `PGHOST` | Lakebase endpoint hostname |
| `PGDATABASE` | Database name (default: `databricks_postgres`) |
| `PGUSER` | Service principal client ID |
| `PGPORT` | Port (default: `5432`) |
| `PGSSLMODE` | SSL mode (default: `require`) |
| `ENDPOINT_NAME` | Lakebase endpoint path for token generation |

## Local Development

```bash
# Set environment variables
export PGHOST="<your-lakebase-endpoint>"
export PGDATABASE="databricks_postgres"
export PGUSER="your.email@databricks.com"
export PGPORT="5432"
export PGSSLMODE="require"
export ENDPOINT_NAME="projects/<id>/branches/<id>/endpoints/<id>"

# Install and run
pip install -r requirements.txt
streamlit run app.py
```

## App Pages

| Page | Description |
|------|-------------|
| **Overview** | KPI cards, encounter/diagnosis/treatment distributions |
| **Patient 360** | Search patients, view full clinical profile with tabs |
| **Treatment Analytics** | Efficacy rates, outcome distributions, comparisons |
| **Adverse Events** | Safety surveillance — severity, CTCAE grades, trends |
| **Lab Results** | Abnormal flags, longitudinal trends, patient-level tracking |
| **Knowledge Graph** | Interactive visual graph of patient clinical journeys |
