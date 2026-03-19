# Databricks notebook source
# MAGIC %md
# MAGIC # Seed Lakebase Internals — Sample Metrics Data
# MAGIC
# MAGIC Generates realistic time-series data for all Lakebase monitoring tables.
# MAGIC This simulates 7 days of Lakebase operation for the HLS Knowledge Graph
# MAGIC project, including autoscaling events, CDC sync, branching, and governance.

# COMMAND ----------

CATALOG = "users"
SCHEMA  = "ankur_nayyar"

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Autoscaling Compute Metrics (7 days, 5-minute intervals)

# COMMAND ----------

from pyspark.sql.types import *
from pyspark.sql import Row
from datetime import datetime, timedelta
import random

random.seed(42)

base_time = datetime(2026, 3, 12, 0, 0, 0)
compute_rows = []

for i in range(7 * 24 * 12):  # 7 days, 5-min intervals = 2016 rows
    ts = base_time + timedelta(minutes=i * 5)
    hour = ts.hour
    day_of_week = ts.weekday()

    # Simulate realistic usage pattern:
    # Night (0-6): scale to zero
    # Morning ramp (6-9): scale up
    # Business hours (9-17): high usage with spikes
    # Evening (17-22): moderate
    # Late night (22-24): wind down

    if 0 <= hour < 6:
        cu = 0.0
        cpu = 0.0
        event = "scale_to_zero" if i > 0 and compute_rows[-1].compute_units > 0 else None
    elif 6 <= hour < 7:
        cu = round(random.uniform(1.0, 2.0), 1)
        cpu = round(random.uniform(10, 25), 2)
        event = "wake_up" if compute_rows and compute_rows[-1].compute_units == 0 else None
    elif 7 <= hour < 9:
        cu = round(random.uniform(2.0, 4.0), 1)
        cpu = round(random.uniform(20, 45), 2)
        event = "scale_up" if compute_rows and compute_rows[-1].compute_units < cu - 1 else None
    elif 9 <= hour < 17:
        # Business hours — higher load, occasional spikes
        base_cu = 4.0
        if hour == 10 or hour == 14:  # Morning standup data load, afternoon batch
            base_cu = 8.0
        if day_of_week == 0:  # Monday morning rush
            base_cu += 2.0
        cu = round(min(base_cu + random.uniform(-1, 2), 16.0), 1)
        cpu = round(min(random.uniform(35, 75) + (base_cu * 3), 95), 2)
        event = "scale_up" if compute_rows and cu > compute_rows[-1].compute_units + 2 else (
            "scale_down" if compute_rows and cu < compute_rows[-1].compute_units - 2 else None
        )
    elif 17 <= hour < 22:
        cu = round(random.uniform(1.5, 3.0), 1)
        cpu = round(random.uniform(10, 30), 2)
        event = "scale_down" if compute_rows and compute_rows[-1].compute_units > cu + 2 else None
    else:
        cu = round(random.uniform(0.5, 1.5), 1)
        cpu = round(random.uniform(5, 15), 2)
        event = "scale_down" if compute_rows and compute_rows[-1].compute_units > 2 else None

    mem_alloc = round(cu * 2, 2)
    mem_used = round(mem_alloc * random.uniform(0.3, 0.8), 2) if cu > 0 else 0
    mem_cached = round(mem_alloc * random.uniform(0.1, 0.3), 2) if cu > 0 else 0
    working_set = round(mem_used * random.uniform(0.5, 0.9), 2) if cu > 0 else 0

    compute_rows.append(Row(
        timestamp=ts,
        compute_units=cu,
        cpu_percent=cpu,
        memory_allocated_gb=mem_alloc,
        memory_used_gb=mem_used,
        memory_cached_gb=mem_cached,
        working_set_gb=working_set,
        scale_event=event,
    ))

compute_df = spark.createDataFrame(compute_rows)
compute_df.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.lakebase_compute_metrics")
print(f"Wrote {compute_df.count():,} compute metric rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Connection Metrics

# COMMAND ----------

conn_rows = []
sources = ["application", "lakehouse_sync", "admin", "genie"]

for i in range(7 * 24 * 12):
    ts = base_time + timedelta(minutes=i * 5)
    hour = ts.hour

    if 0 <= hour < 6:
        active = random.randint(0, 1)
        idle = random.randint(0, 2)
    elif 9 <= hour < 17:
        active = random.randint(5, 25)
        idle = random.randint(3, 10)
    else:
        active = random.randint(1, 8)
        idle = random.randint(1, 5)

    total = active + idle
    source = random.choice(sources)

    conn_rows.append(Row(
        timestamp=ts,
        active_connections=active,
        idle_connections=idle,
        total_connections=total,
        max_connections=100,
        connection_source=source,
    ))

conn_df = spark.createDataFrame(conn_rows)
conn_df.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.lakebase_connection_metrics")
print(f"Wrote {conn_df.count():,} connection metric rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Query Performance Stats

# COMMAND ----------

queries = [
    ("q001", "SELECT * FROM patients WHERE mrn = $1",                          "SELECT",  1250, 0.8,  0.2, 15.0, 1250, 99.2),
    ("q002", "SELECT * FROM treatments WHERE patient_id = $1",                 "SELECT",   980, 1.2,  0.3, 22.0,  980, 98.5),
    ("q003", "SELECT * FROM lab_results WHERE patient_id = $1 ORDER BY ...",   "SELECT",   870, 2.1,  0.5, 35.0, 4200, 97.8),
    ("q004", "INSERT INTO encounters (...) VALUES (...)",                       "INSERT",   340, 1.5,  0.8, 12.0,  340, 95.0),
    ("q005", "UPDATE treatments SET status = $1 WHERE treatment_id = $2",      "UPDATE",   180, 1.8,  0.6, 18.0,  180, 96.2),
    ("q006", "SELECT p.*, d.* FROM patients p JOIN diagnoses d ON ...",        "SELECT",   560, 3.5,  1.2, 45.0, 1400, 94.5),
    ("q007", "SELECT t.*, o.* FROM treatments t JOIN treatment_outcomes ...",   "SELECT",   720, 2.8,  0.9, 38.0, 2100, 96.8),
    ("q008", "SELECT * FROM adverse_events WHERE severity = $1",               "SELECT",   430, 1.1,  0.3, 8.0,   430, 99.5),
    ("q009", "WITH RECURSIVE patient_journey AS (...) SELECT path ...",         "SELECT",    95, 18.5, 5.2, 85.0,  380, 88.2),
    ("q010", "SELECT * FROM gold_patient_360",                                 "SELECT",   310, 4.2,  1.5, 52.0, 3100, 93.1),
    ("q011", "SELECT * FROM gold_treatment_efficacy",                          "SELECT",   280, 5.8,  2.1, 65.0,  840, 91.5),
    ("q012", "INSERT INTO lab_results (...) VALUES (...)",                      "INSERT",   620, 1.2,  0.5, 9.0,   620, 97.0),
    ("q013", "SELECT * FROM graph_all_edges",                                  "SELECT",    85, 12.3, 4.5, 72.0, 8500, 89.5),
    ("q014", "DELETE FROM adverse_events WHERE event_id = $1",                 "DELETE",    15, 0.9,  0.3, 5.0,    15, 99.8),
    ("q015", "SELECT COUNT(*) FROM patients WHERE is_active = true",           "SELECT",  2100, 0.3,  0.1, 2.0,  2100, 99.9),
]

query_rows = []
for day in range(7):
    snap_time = base_time + timedelta(days=day, hours=23, minutes=59)
    for qid, text, qtype, calls, mean, mn, mx, rows, cache in queries:
        daily_calls = int(calls * random.uniform(0.7, 1.3))
        daily_mean = round(mean * random.uniform(0.8, 1.2), 2)
        total = round(daily_calls * daily_mean, 2)
        blks_hit = int(daily_calls * cache / 100 * random.uniform(80, 120))
        blks_read = int(daily_calls * (100 - cache) / 100 * random.uniform(80, 120))
        hit_ratio = round(blks_hit / max(blks_hit + blks_read, 1) * 100, 2)

        query_rows.append(Row(
            query_id=qid,
            query_text=text,
            query_type=qtype,
            calls=daily_calls,
            total_time_ms=total,
            mean_time_ms=daily_mean,
            min_time_ms=round(mn * random.uniform(0.8, 1.2), 2),
            max_time_ms=round(mx * random.uniform(0.8, 1.5), 2),
            rows_returned=int(rows * random.uniform(0.8, 1.2)),
            shared_blks_hit=blks_hit,
            shared_blks_read=blks_read,
            cache_hit_ratio=hit_ratio,
            snapshot_time=snap_time,
        ))

query_df = spark.createDataFrame(query_rows)
query_df.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.lakebase_query_stats")
print(f"Wrote {query_df.count():,} query stat rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Lakehouse Sync Status

# COMMAND ----------

tables = [
    "patients", "providers", "encounters", "diagnoses",
    "treatments", "medications", "treatment_outcomes",
    "adverse_events", "lab_results",
]

source_counts = {
    "patients": 10, "providers": 8, "encounters": 15, "diagnoses": 9,
    "treatments": 16, "medications": 7, "treatment_outcomes": 10,
    "adverse_events": 10, "lab_results": 17,
}

sync_rows = []
for day in range(7):
    snap_time = base_time + timedelta(days=day, hours=12)
    for tbl in tables:
        src = source_counts[tbl] + day * random.randint(0, 3)
        lag = random.randint(200, 3500) if random.random() > 0.1 else random.randint(5000, 15000)
        synced = src * (day + 1) * random.randint(1, 3)

        sync_rows.append(Row(
            table_name=tbl,
            sync_mode="continuous",
            status="active" if lag < 10000 else "initializing",
            source_row_count=src,
            target_row_count=src,
            last_sync_lsn=f"0/{hex(1000000 + day * 50000 + random.randint(0, 10000))[2:].upper()}",
            replication_lag_ms=lag,
            rows_synced_total=synced,
            last_sync_timestamp=snap_time - timedelta(milliseconds=lag),
            snapshot_time=snap_time,
        ))

sync_df = spark.createDataFrame(sync_rows)
sync_df.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.lakebase_sync_status")
print(f"Wrote {sync_df.count():,} sync status rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Branch Activity

# COMMAND ----------

branch_rows = [
    Row(branch_id="br-main",    branch_name="main",                  parent_branch=None,    created_at=datetime(2026,1,15,9,0),  created_by="admin@lakeside.org",         purpose="production",   status="active",  ttl_hours=None, expires_at=None,                        storage_overhead_mb=0.0,    total_queries=45200, deleted_at=None),
    Row(branch_id="br-dev-001", branch_name="dev/feature-labs-v2",   parent_branch="main",  created_at=datetime(2026,3,12,10,15), created_by="sarah.chen@lakeside.org",    purpose="development",  status="active",  ttl_hours=168,  expires_at=datetime(2026,3,19,10,15),   storage_overhead_mb=2.4,    total_queries=1250,  deleted_at=None),
    Row(branch_id="br-dev-002", branch_name="dev/chemo-dosing-model",parent_branch="main",  created_at=datetime(2026,3,13,14,30), created_by="james.okonkwo@lakeside.org", purpose="experiment",   status="active",  ttl_hours=72,   expires_at=datetime(2026,3,16,14,30),   storage_overhead_mb=0.8,    total_queries=340,   deleted_at=None),
    Row(branch_id="br-ci-001",  branch_name="ci/pr-142-schema-test", parent_branch="main",  created_at=datetime(2026,3,14,8,0),   created_by="ci-bot@lakeside.org",        purpose="ci_cd",        status="expired", ttl_hours=4,    expires_at=datetime(2026,3,14,12,0),    storage_overhead_mb=0.1,    total_queries=85,    deleted_at=datetime(2026,3,14,12,0)),
    Row(branch_id="br-ci-002",  branch_name="ci/pr-143-outcome-fix", parent_branch="main",  created_at=datetime(2026,3,15,9,30),  created_by="ci-bot@lakeside.org",        purpose="ci_cd",        status="expired", ttl_hours=4,    expires_at=datetime(2026,3,15,13,30),   storage_overhead_mb=0.1,    total_queries=92,    deleted_at=datetime(2026,3,15,13,30)),
    Row(branch_id="br-audit",   branch_name="audit/q1-2026-freeze",  parent_branch="main",  created_at=datetime(2026,3,16,6,0),   created_by="compliance@lakeside.org",    purpose="audit",        status="active",  ttl_hours=720,  expires_at=datetime(2026,4,15,6,0),     storage_overhead_mb=0.0,    total_queries=520,   deleted_at=None),
    Row(branch_id="br-test-001",branch_name="test/load-test-10k",    parent_branch="main",  created_at=datetime(2026,3,17,11,0),  created_by="maria.rodriguez@lakeside.org",purpose="testing",     status="deleted", ttl_hours=24,   expires_at=datetime(2026,3,18,11,0),    storage_overhead_mb=45.2,   total_queries=8900,  deleted_at=datetime(2026,3,18,11,0)),
    Row(branch_id="br-dev-003", branch_name="dev/readmission-predict",parent_branch="main", created_at=datetime(2026,3,18,9,0),   created_by="priya.sharma@lakeside.org",  purpose="experiment",   status="active",  ttl_hours=168,  expires_at=datetime(2026,3,25,9,0),     storage_overhead_mb=1.2,    total_queries=180,   deleted_at=None),
]

branch_df = spark.createDataFrame(branch_rows)
branch_df.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.lakebase_branches")
print(f"Wrote {branch_df.count():,} branch rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Row Operations (DML throughput)

# COMMAND ----------

op_rows = []
for i in range(7 * 24 * 12):
    ts = base_time + timedelta(minutes=i * 5)
    hour = ts.hour

    for tbl in ["patients", "encounters", "treatments", "lab_results", "adverse_events"]:
        if 0 <= hour < 6:
            ins, upd, dlt = 0, 0, 0
        elif 9 <= hour < 17:
            if tbl == "lab_results":
                ins = random.randint(5, 40)
            elif tbl == "encounters":
                ins = random.randint(2, 15)
            elif tbl == "treatments":
                ins = random.randint(1, 8)
            elif tbl == "patients":
                ins = random.randint(0, 3)
            else:
                ins = random.randint(0, 5)
            upd = random.randint(0, max(ins // 2, 1))
            dlt = random.randint(0, 1)
        else:
            ins = random.randint(0, 3)
            upd = random.randint(0, 1)
            dlt = 0

        if ins + upd + dlt > 0:
            op_rows.append(Row(
                timestamp=ts,
                table_name=tbl,
                inserts=ins,
                updates=upd,
                deletes=dlt,
                total_operations=ins + upd + dlt,
            ))

ops_df = spark.createDataFrame(op_rows)
ops_df.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.lakebase_row_operations")
print(f"Wrote {ops_df.count():,} row operation entries")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Governance Events

# COMMAND ----------

import uuid

gov_rows = []
principals = [
    "sarah.chen@lakeside.org", "james.okonkwo@lakeside.org",
    "maria.rodriguez@lakeside.org", "analyst_group", "executive_group",
    "ci-bot@lakeside.org", "compliance@lakeside.org",
]

event_templates = [
    ("query",        "SELECT",  "patients",                   "Patient lookup by MRN",                    "allowed"),
    ("query",        "SELECT",  "patients.phone",             "PII column access",                        "masked"),
    ("query",        "SELECT",  "patients.email",             "PII column access",                        "masked"),
    ("query",        "SELECT",  "treatments",                 "Treatment history query",                  "allowed"),
    ("query",        "SELECT",  "gold_patient_360",           "Patient 360 dashboard query",              "allowed"),
    ("query",        "SELECT",  "adverse_events",             "Adverse event monitoring",                 "allowed"),
    ("row_filter",   "SELECT",  "patients",                   "Provider row filter applied",              "allowed"),
    ("mask_applied", "SELECT",  "patients.phone",             "Phone masked to XXX-XXX-XXXX",             "masked"),
    ("mask_applied", "SELECT",  "patients.email",             "Email masked to x***@domain",              "masked"),
    ("grant",        "GRANT",   "gold_treatment_efficacy",    "GRANT SELECT to analyst_group",            "allowed"),
    ("revoke",       "REVOKE",  "patients.email",             "REVOKE SELECT on PII column",              "allowed"),
    ("query",        "SELECT",  "lab_results",                "Lab trend analysis",                       "allowed"),
    ("query",        "SELECT",  "gold_adverse_events",        "Safety dashboard query",                   "allowed"),
    ("query",        "SELECT",  "patients",                   "Unauthorized attempt — missing permission","denied"),
]

for day in range(7):
    num_events = random.randint(80, 200)
    for _ in range(num_events):
        tmpl = random.choice(event_templates)
        ts = base_time + timedelta(
            days=day,
            hours=random.randint(7, 22),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        gov_rows.append(Row(
            event_id=str(uuid.uuid4()),
            event_time=ts,
            event_type=tmpl[0],
            principal=random.choice(principals),
            action=tmpl[1],
            resource=tmpl[2],
            detail=tmpl[3],
            result=tmpl[4],
        ))

gov_df = spark.createDataFrame(gov_rows)
gov_df.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.lakebase_governance_events")
print(f"Wrote {gov_df.count():,} governance event rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

metrics_tables = [
    "lakebase_compute_metrics",
    "lakebase_connection_metrics",
    "lakebase_query_stats",
    "lakebase_sync_status",
    "lakebase_branches",
    "lakebase_row_operations",
    "lakebase_governance_events",
]

print("Lakebase internals sample data loaded:")
print()
for tbl in metrics_tables:
    count = spark.table(f"{CATALOG}.{SCHEMA}.{tbl}").count()
    print(f"  {tbl:35s} → {count:>6,} rows")
