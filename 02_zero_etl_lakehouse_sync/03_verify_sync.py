# Databricks notebook source
# MAGIC %md
# MAGIC # Verify Lakehouse Sync Status
# MAGIC
# MAGIC Confirms that Lakebase → Delta CDC replication is healthy and data is
# MAGIC flowing correctly. Run this after enabling Lakehouse Sync in the UI.

# COMMAND ----------

CATALOG = "users"
SCHEMA  = "ankur_nayyar"

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
# MAGIC ## Check synced history tables
# MAGIC
# MAGIC Lakehouse Sync creates Delta tables named `lb_<table>_history` in your
# MAGIC target schema. This cell checks that they exist and reports row counts.

# COMMAND ----------

from pyspark.sql import Row

results = []
for table in TABLES:
    history_table = f"lb_{table}_history"
    fqn = f"{CATALOG}.{SCHEMA}.{history_table}"
    try:
        count = spark.table(fqn).count()
        results.append(Row(
            source_table=table,
            delta_history_table=history_table,
            row_count=count,
            status="✓ synced"
        ))
    except Exception:
        results.append(Row(
            source_table=table,
            delta_history_table=history_table,
            row_count=0,
            status="✗ not found"
        ))

results_df = spark.createDataFrame(results)
display(results_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify current-state views
# MAGIC
# MAGIC After running `02_create_gold_views.sql`, current-state views should exist
# MAGIC that deduplicate from `lb_*_history` to the latest row.

# COMMAND ----------

for table in TABLES:
    fqn = f"{CATALOG}.{SCHEMA}.{table}"
    try:
        count = spark.table(fqn).count()
        print(f"  ✓ {table:25s} → {count:>6,} rows (current state)")
    except Exception:
        print(f"  ✗ {table:25s} → view not found (run 02_create_gold_views.sql first)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample data preview — patients

# COMMAND ----------

try:
    display(spark.table(f"{CATALOG}.{SCHEMA}.patients").limit(10))
except Exception as e:
    print(f"patients view not available: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample data preview — treatments with outcomes

# COMMAND ----------

try:
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
except Exception as e:
    print(f"Query failed — ensure Lakehouse Sync is enabled and gold views are created.")
    print(f"Error: {e}")

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
    fqn = f"{CATALOG}.{SCHEMA}.{view}"
    try:
        count = spark.table(fqn).count()
        print(f"  ✓ {view:30s} → {count:>6,} rows")
    except Exception:
        print(f"  ✗ {view:30s} → not found (run 02_create_gold_views.sql)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Lakebase SQL Editor: Check wal2delta status
# MAGIC
# MAGIC Run this query in the **Lakebase SQL Editor** (not here) to see sync details:
# MAGIC ```sql
# MAGIC SELECT * FROM wal2delta.tables;
# MAGIC ```
