# Databricks notebook source
# MAGIC %md
# MAGIC # Enable Lakehouse Sync (Zero ETL)
# MAGIC
# MAGIC Configures continuous CDC replication from **Lakebase Postgres** tables into
# MAGIC **Unity Catalog managed Delta tables**. No external pipelines, no Spark jobs,
# MAGIC no scheduling — data flows automatically with seconds of latency.
# MAGIC
# MAGIC ### How it works
# MAGIC 1. Lakebase captures row-level changes via its built-in WAL-based CDC (`wal2delta`)
# MAGIC 2. Changes replicate into Delta tables named `lb_<table>_history` in Unity Catalog
# MAGIC 3. Each change is appended as SCD Type 2 history (full audit trail)
# MAGIC
# MAGIC ### Architecture
# MAGIC ```
# MAGIC Lakebase Postgres ──(CDC / wal2delta)──► Unity Catalog Delta Tables
# MAGIC   public.patients                         users.ankur_nayyar.lb_patients_history
# MAGIC   public.treatments                       users.ankur_nayyar.lb_treatments_history
# MAGIC   ...                                     ...
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

LAKEBASE_PROJECT  = "hls-knowledge-graph"         # Your Lakebase project name
LAKEBASE_DATABASE = "postgres"                     # Postgres database name (default)
CATALOG           = "users"                        # Unity Catalog target catalog
SCHEMA            = "ankur_nayyar"                 # Unity Catalog target schema

TABLES_TO_SYNC = [
    "patients",
    "providers",
    "encounters",
    "diagnoses",
    "treatments",
    "medications",
    "treatment_outcomes",
    "adverse_events",
    "lab_results",
]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Set REPLICA IDENTITY FULL on Lakebase tables
# MAGIC
# MAGIC **Run these commands in the Lakebase SQL Editor** (not in this notebook).
# MAGIC
# MAGIC Lakehouse Sync requires `REPLICA IDENTITY FULL` on each table so that CDC
# MAGIC captures complete before/after images of every row change.

# COMMAND ----------

print("=" * 70)
print("Run the following SQL in the LAKEBASE SQL EDITOR")
print("(Lakebase project → SQL Editor tab)")
print("=" * 70)
print()
for table_name in TABLES_TO_SYNC:
    print(f'ALTER TABLE public.{table_name} REPLICA IDENTITY FULL;')

print()
print("-- Verify replica identity is set:")
print("""
SELECT n.nspname AS table_schema,
       c.relname AS table_name,
       CASE c.relreplident
         WHEN 'd' THEN 'default'
         WHEN 'n' THEN 'nothing'
         WHEN 'f' THEN 'full'
         WHEN 'i' THEN 'index'
       END AS replica_identity
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
  AND n.nspname = 'public'
ORDER BY c.relname;
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Enable Lakehouse Sync in the Lakebase UI
# MAGIC
# MAGIC 1. Go to your **Lakebase project** in the Databricks workspace
# MAGIC 2. Click the **Lakehouse Sync** tab (or find it under project settings)
# MAGIC 3. Select the **target Unity Catalog catalog** → `users`
# MAGIC 4. Select the **target schema** → `ankur_nayyar`
# MAGIC 5. The tables in your `public` schema will appear — enable sync for each
# MAGIC 6. Synced Delta tables will be created as `lb_<table_name>_history`
# MAGIC
# MAGIC > **Note**: Lakehouse Sync is currently in **Beta**. It is enabled via the
# MAGIC > Lakebase UI — there is no SQL or API command to enable it programmatically.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Verify sync status from Lakebase SQL Editor
# MAGIC
# MAGIC Run this in the **Lakebase SQL Editor** to see which tables are being synced:

# COMMAND ----------

print("Run in LAKEBASE SQL EDITOR:")
print()
print("SELECT * FROM wal2delta.tables;")
print()
print("-- Check for unsupported data types (if any):")
print("""
SELECT c.table_schema, c.table_name, c.column_name, c.udt_name AS data_type
FROM information_schema.columns c
JOIN pg_catalog.pg_type t ON t.typname = c.udt_name
WHERE c.table_schema = 'public'
  AND c.table_name IN (SELECT tablename FROM pg_tables WHERE schemaname = c.table_schema)
  AND NOT (
    c.udt_name IN ('bool', 'int2', 'int4', 'int8', 'text', 'varchar', 'bpchar',
                    'jsonb', 'numeric', 'date', 'timestamp', 'timestamptz',
                    'real', 'float4', 'float8')
    OR t.typcategory = 'E'
  )
ORDER BY c.table_schema, c.table_name, c.ordinal_position;
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Create the Unity Catalog target schema (if needed)

# COMMAND ----------

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
print(f"Target schema ready: {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Validate synced Delta tables
# MAGIC
# MAGIC After Lakehouse Sync is enabled, Delta tables named `lb_<table>_history`
# MAGIC appear in your target schema. This cell checks for them.

# COMMAND ----------

import time

print(f"Checking for synced tables in {CATALOG}.{SCHEMA}...\n")

synced_tables = []
missing_tables = []

for table_name in TABLES_TO_SYNC:
    delta_table = f"lb_{table_name}_history"
    fqn = f"{CATALOG}.{SCHEMA}.{delta_table}"
    try:
        count = spark.table(fqn).count()
        print(f"  ✓ {delta_table:40s} → {count:>6,} rows")
        synced_tables.append(table_name)
    except Exception:
        print(f"  ✗ {delta_table:40s} → not found yet")
        missing_tables.append(table_name)

print(f"\n{'─' * 50}")
print(f"Synced:  {len(synced_tables)}/{len(TABLES_TO_SYNC)} tables")
if missing_tables:
    print(f"Missing: {', '.join(missing_tables)}")
    print("\nIf tables are missing, verify Lakehouse Sync is enabled in the Lakebase UI")
    print("and wait a few minutes for the initial sync to complete.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Query the latest snapshot from a synced table
# MAGIC
# MAGIC Lakehouse Sync writes SCD Type 2 history. Use this pattern to get the
# MAGIC current state (latest version of each row, excluding deletes):

# COMMAND ----------

sample_table = f"{CATALOG}.{SCHEMA}.lb_patients_history"

try:
    latest_df = spark.sql(f"""
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY _lsn DESC) AS rn
            FROM {sample_table}
            WHERE _change_type IN ('insert', 'update_postimage', 'delete')
        )
        WHERE rn = 1
          AND _change_type != 'delete'
    """)

    print(f"Current patient count: {latest_df.count()}")
    display(latest_df.limit(10))
except Exception as e:
    print(f"Table {sample_table} not available yet.")
    print(f"Enable Lakehouse Sync first (see Steps 1-2 above).")
    print(f"\nError: {e}")
