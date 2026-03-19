# Databricks notebook source
# MAGIC %md
# MAGIC # Verify Lakehouse Sync Status
# MAGIC
# MAGIC Confirms that Lakebase → Delta CDC replication is healthy and data is
# MAGIC flowing correctly. Run this after enabling sync or as a periodic health check.

# COMMAND ----------

CATALOG = "hls_lakehouse"
SCHEMA  = "knowledge_graph"

TABLES = [
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
# MAGIC ## Sync status overview

# COMMAND ----------

sync_status = spark.sql("""
    SHOW LAKEHOUSE_SYNC STATUS
    ON DATABASE INSTANCE `hls-knowledge-graph`
""")

display(sync_status)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Row counts: Lakebase vs Delta
# MAGIC
# MAGIC Compares row counts between the source Postgres tables and the synced
# MAGIC Delta tables to confirm data completeness.

# COMMAND ----------

from pyspark.sql import Row

results = []
for table in TABLES:
    delta_count = spark.table(f"{CATALOG}.{SCHEMA}.{table}").count()
    results.append(Row(
        table_name=table,
        delta_row_count=delta_count,
    ))

results_df = spark.createDataFrame(results)
display(results_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample data preview — patients

# COMMAND ----------

display(spark.table(f"{CATALOG}.{SCHEMA}.patients").limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample data preview — treatments with outcomes

# COMMAND ----------

display(spark.sql(f"""
    SELECT
        t.treatment_name,
        t.treatment_type,
        t.status,
        o.outcome_type,
        o.outcome_measure,
        o.baseline_value,
        o.result_value,
        o.unit
    FROM {CATALOG}.{SCHEMA}.treatments t
    LEFT JOIN {CATALOG}.{SCHEMA}.treatment_outcomes o
        ON t.treatment_id = o.treatment_id
    ORDER BY t.treatment_name
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold views validation

# COMMAND ----------

gold_views = [
    "gold_patient_360",
    "gold_treatment_efficacy",
    "gold_adverse_events",
    "gold_outcomes_timeline",
    "gold_provider_activity",
    "gold_diagnosis_cohorts",
    "gold_lab_trends",
]

for view in gold_views:
    count = spark.table(f"{CATALOG}.{SCHEMA}.{view}").count()
    print(f"  {view:30s} → {count:>6,} rows")
