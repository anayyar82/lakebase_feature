# Databricks notebook source
# MAGIC %md
# MAGIC # Enable Lakehouse Sync (Zero ETL)
# MAGIC
# MAGIC Configures continuous CDC replication from **Lakebase Postgres** tables into
# MAGIC **Unity Catalog managed Delta tables**. No external pipelines, no Spark jobs,
# MAGIC no scheduling — data flows automatically with seconds of latency.
# MAGIC
# MAGIC ### How it works
# MAGIC 1. Lakebase captures row-level changes via its built-in CDC mechanism
# MAGIC 2. Changes replicate into Delta tables registered in Unity Catalog
# MAGIC 3. Three sync modes: **Snapshot** (one-time), **Triggered** (scheduled), **Continuous** (real-time)
# MAGIC
# MAGIC ### Prerequisites
# MAGIC - Lakebase project created with tables populated
# MAGIC - Unity Catalog catalog + schema created for synced tables
# MAGIC - `CREATE TABLE` permission on the target schema

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

LAKEBASE_PROJECT  = "hls-knowledge-graph"         # Your Lakebase project name
LAKEBASE_DATABASE = "hls_kg"                       # Postgres database name
CATALOG           = "users"                        # Unity Catalog catalog
SCHEMA            = "ankur_nayyar"                 # Unity Catalog schema
SYNC_MODE         = "continuous"                   # snapshot | triggered | continuous

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
# MAGIC ## Step 1 — Create the Unity Catalog target schema

# COMMAND ----------

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

print(f"Target schema ready: {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Enable Lakehouse Sync for each table
# MAGIC
# MAGIC Uses the `ALTER DATABASE INSTANCE ... ENABLE LAKEHOUSE_SYNC` SQL syntax.
# MAGIC Each source table in Lakebase gets a corresponding managed Delta table in
# MAGIC Unity Catalog. CDC changes replicate automatically.

# COMMAND ----------

for table_name in TABLES_TO_SYNC:
    sync_sql = f"""
    ALTER DATABASE INSTANCE `{LAKEBASE_PROJECT}`
    ENABLE LAKEHOUSE_SYNC
    FOR TABLE `{LAKEBASE_DATABASE}`.`public`.`{table_name}`
    INTO `{CATALOG}`.`{SCHEMA}`.`{table_name}`
    SYNC_MODE = {SYNC_MODE.upper()}
    """
    print(f"Enabling {SYNC_MODE} sync: {table_name} → {CATALOG}.{SCHEMA}.{table_name}")
    spark.sql(sync_sql)

print("\nLakehouse Sync enabled for all tables.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Verify sync status

# COMMAND ----------

status_df = spark.sql(f"""
    SHOW LAKEHOUSE_SYNC STATUS
    ON DATABASE INSTANCE `{LAKEBASE_PROJECT}`
""")

display(status_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Validate data landed in Delta

# COMMAND ----------

for table_name in TABLES_TO_SYNC:
    count = spark.table(f"{CATALOG}.{SCHEMA}.{table_name}").count()
    print(f"  {table_name:25s} → {count:>6,} rows")

print("\nZero ETL replication verified.")
