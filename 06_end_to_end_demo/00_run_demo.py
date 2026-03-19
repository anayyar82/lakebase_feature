# Databricks notebook source
# MAGIC %md
# MAGIC # HLS Knowledge Graph — End-to-End Demo
# MAGIC
# MAGIC This notebook orchestrates the full pipeline:
# MAGIC
# MAGIC 1. **Lakebase** → Create tables and seed sample data (OLTP)
# MAGIC 2. **Lakehouse Sync** → Enable Zero ETL CDC replication to Delta
# MAGIC 3. **Gold Views** → Create analytics views on top of synced Delta tables
# MAGIC 4. **Graph Views** → Create SQL-based knowledge graph edge views
# MAGIC 5. **Graph Analytics** → Run recursive CTE graph traversals
# MAGIC 6. **Lakebase Internals** → Seed platform metrics and validate
# MAGIC 7. **Validate** → Confirm everything works end to end
# MAGIC
# MAGIC ### Prerequisites
# MAGIC - Lakebase project `hls-knowledge-graph` created in the workspace
# MAGIC - Tables created and seeded via `01_lakebase_setup/` scripts

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

LAKEBASE_PROJECT  = "hls-knowledge-graph"
LAKEBASE_DATABASE = "hls_kg"
CATALOG           = "hls_lakehouse"
SCHEMA            = "knowledge_graph"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Verify Lakebase Tables
# MAGIC
# MAGIC Assumes you have already run:
# MAGIC - `01_lakebase_setup/01_create_lakebase_tables.sql`
# MAGIC - `01_lakebase_setup/02_seed_sample_data.sql`
# MAGIC - `01_lakebase_setup/03_create_indexes.sql`

# COMMAND ----------

print("=" * 60)
print("STEP 1: Verify Lakebase tables are populated")
print("=" * 60)
print()
print("Run the following SQL scripts in the Lakebase SQL Editor")
print("if you haven't already:")
print()
print("  1. 01_lakebase_setup/01_create_lakebase_tables.sql")
print("  2. 01_lakebase_setup/02_seed_sample_data.sql")
print("  3. 01_lakebase_setup/03_create_indexes.sql")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Enable Lakehouse Sync (Zero ETL)

# COMMAND ----------

print("=" * 60)
print("STEP 2: Enable Lakehouse Sync")
print("=" * 60)

# COMMAND ----------

# MAGIC %run ../02_zero_etl_lakehouse_sync/01_enable_lakehouse_sync

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Create Gold-Layer Views

# COMMAND ----------

print("=" * 60)
print("STEP 3: Create gold-layer analytics views")
print("=" * 60)

# COMMAND ----------

# MAGIC %run ../02_zero_etl_lakehouse_sync/02_create_gold_views

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Verify Sync

# COMMAND ----------

print("=" * 60)
print("STEP 4: Verify Lakehouse Sync data")
print("=" * 60)

# COMMAND ----------

# MAGIC %run ../02_zero_etl_lakehouse_sync/03_verify_sync

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Create Knowledge Graph Views

# COMMAND ----------

print("=" * 60)
print("STEP 5: Create SQL knowledge graph views")
print("=" * 60)

# COMMAND ----------

# MAGIC %run ../03_sql_knowledge_graph/02_graph_views

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Run Graph Analytics

# COMMAND ----------

print("=" * 60)
print("STEP 6: Run graph analytics")
print("=" * 60)

# COMMAND ----------

# MAGIC %run ../03_sql_knowledge_graph/03_graph_analytics

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Validate Gold Views (Delta)

# COMMAND ----------

print("=" * 60)
print("STEP 7: Validate gold-layer views")
print("=" * 60)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Treatment Efficacy

# COMMAND ----------

display(spark.table(f"{CATALOG}.{SCHEMA}.gold_treatment_efficacy"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Adverse Events

# COMMAND ----------

display(spark.table(f"{CATALOG}.{SCHEMA}.gold_adverse_events"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Patient 360

# COMMAND ----------

display(spark.table(f"{CATALOG}.{SCHEMA}.gold_patient_360"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Knowledge Graph Edge Counts

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT relationship, COUNT(*) AS edge_count
# MAGIC FROM graph_all_edges
# MAGIC GROUP BY relationship
# MAGIC ORDER BY edge_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC %md
# MAGIC ## Step 8 — Seed Lakebase Internals Metrics

# COMMAND ----------

print("=" * 60)
print("STEP 8: Seed Lakebase internals sample data")
print("=" * 60)

# COMMAND ----------

# MAGIC %run ../05_lakebase_internals/02_seed_metrics_data

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 9 — Validate Lakebase Internals Data

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Autoscaling: scale-to-zero hours
# MAGIC SELECT
# MAGIC     COUNT(*) * 5 / 60.0 AS zero_hours,
# MAGIC     ROUND(COUNT(*) * 5 / 60.0 / (7 * 24) * 100, 1) AS pct_time_at_zero
# MAGIC FROM lakebase_compute_metrics
# MAGIC WHERE compute_units = 0

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Lakehouse Sync: current status
# MAGIC SELECT table_name, sync_mode, status, replication_lag_ms, rows_synced_total
# MAGIC FROM lakebase_sync_status
# MAGIC WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM lakebase_sync_status)
# MAGIC ORDER BY replication_lag_ms DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Branches: active branches
# MAGIC SELECT branch_name, purpose, status, storage_overhead_mb, total_queries
# MAGIC FROM lakebase_branches
# MAGIC ORDER BY created_at DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Governance: denied access attempts
# MAGIC SELECT event_time, principal, resource, detail
# MAGIC FROM lakebase_governance_events
# MAGIC WHERE result = 'denied'
# MAGIC ORDER BY event_time DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC | Layer | Status |
# MAGIC |-------|--------|
# MAGIC | Lakebase (OLTP) | Tables created, data seeded |
# MAGIC | Lakehouse Sync (Zero ETL) | CDC replication enabled |
# MAGIC | Gold Views | Analytics views created |
# MAGIC | SQL Knowledge Graph | Graph views + recursive CTE analytics ready |
# MAGIC | Lakebase Internals | 7 metrics tables with sample data |
# MAGIC | AI/BI | Ready — use dashboard queries and Genie space |

# COMMAND ----------

print("=" * 60)
print("  HLS Knowledge Graph — Demo Complete!")
print("=" * 60)
print()
print("Next steps:")
print("  1. Open AI/BI Dashboards and create visualizations")
print("     using queries from 04_ai_bi_dashboards/01_dashboard_queries.sql")
print()
print("  2. Build Lakebase Internals dashboard using")
print("     05_lakebase_internals/03_lakebase_dashboard_queries.sql")
print()
print("  3. Set up Genie Space following")
print("     04_ai_bi_dashboards/02_genie_space_setup.md")
print()
print("  4. Explore graph traversals with")
print("     03_sql_knowledge_graph/01_graph_traversal_queries.sql")
