-- =============================================================================
-- Lakebase Internals — AI/BI Dashboard Queries
-- =============================================================================
-- Drop these into Databricks AI/BI Dashboard widgets to showcase Lakebase
-- platform capabilities. Each section = one dashboard widget.
-- =============================================================================

USE CATALOG hls_lakehouse;
USE SCHEMA knowledge_graph;

-- =====================================================================
-- SECTION A: AUTOSCALING & COMPUTE
-- =====================================================================

-- ---------------------------------------------------------------------------
-- A1. KPI Cards — Current Lakebase State
-- ---------------------------------------------------------------------------
SELECT
    (SELECT ROUND(compute_units, 1) FROM lakebase_compute_metrics
     ORDER BY timestamp DESC LIMIT 1)                      AS current_compute_units,
    (SELECT ROUND(cpu_percent, 1) FROM lakebase_compute_metrics
     ORDER BY timestamp DESC LIMIT 1)                      AS current_cpu_pct,
    (SELECT ROUND(memory_used_gb, 1) FROM lakebase_compute_metrics
     ORDER BY timestamp DESC LIMIT 1)                      AS current_memory_gb,
    (SELECT active_connections FROM lakebase_connection_metrics
     ORDER BY timestamp DESC LIMIT 1)                      AS current_connections,
    (SELECT COUNT(*) FROM lakebase_branches
     WHERE status = 'active')                              AS active_branches,
    (SELECT COUNT(*) FROM lakebase_sync_status
     WHERE status = 'active'
       AND snapshot_time = (SELECT MAX(snapshot_time) FROM lakebase_sync_status))
                                                           AS tables_syncing;

-- ---------------------------------------------------------------------------
-- A2. Compute Units Over Time (Line Chart)
-- Shows autoscaling in action — scale-to-zero at night, ramp up during
-- business hours, spike handling.
-- ---------------------------------------------------------------------------
SELECT
    timestamp,
    compute_units,
    cpu_percent,
    memory_used_gb,
    scale_event
FROM lakebase_compute_metrics
ORDER BY timestamp;

-- ---------------------------------------------------------------------------
-- A3. Scale Events Timeline (Event Chart)
-- Highlights when Lakebase scaled up, down, to zero, and woke up.
-- ---------------------------------------------------------------------------
SELECT
    timestamp,
    scale_event,
    compute_units AS cu_after_event,
    cpu_percent
FROM lakebase_compute_metrics
WHERE scale_event IS NOT NULL
ORDER BY timestamp;

-- ---------------------------------------------------------------------------
-- A4. Cost Savings — Scale-to-Zero Hours (Counter / KPI)
-- Hours the database spent at zero compute = $0 cost.
-- ---------------------------------------------------------------------------
SELECT
    COUNT(*) * 5 / 60.0                            AS total_zero_hours,
    ROUND(COUNT(*) * 5 / 60.0 / (7 * 24) * 100, 1) AS pct_time_at_zero,
    ROUND(COUNT(*) * 5 / 60.0 * 0.35, 2)           AS estimated_savings_usd
FROM lakebase_compute_metrics
WHERE compute_units = 0;

-- ---------------------------------------------------------------------------
-- A5. Compute Distribution by Hour (Heatmap)
-- Average CU usage by hour of day — shows usage patterns.
-- ---------------------------------------------------------------------------
SELECT
    HOUR(timestamp)        AS hour_of_day,
    ROUND(AVG(compute_units), 2) AS avg_cu,
    ROUND(AVG(cpu_percent), 2)   AS avg_cpu,
    ROUND(MAX(compute_units), 1) AS peak_cu
FROM lakebase_compute_metrics
GROUP BY HOUR(timestamp)
ORDER BY hour_of_day;


-- =====================================================================
-- SECTION B: LAKEHOUSE SYNC (ZERO ETL)
-- =====================================================================

-- ---------------------------------------------------------------------------
-- B1. Sync Status Overview (Table / Status Indicators)
-- Current state of CDC replication for each table.
-- ---------------------------------------------------------------------------
SELECT
    table_name,
    sync_mode,
    status,
    source_row_count,
    target_row_count,
    CASE WHEN source_row_count = target_row_count THEN 'in_sync' ELSE 'lag' END AS sync_state,
    replication_lag_ms,
    CASE
        WHEN replication_lag_ms < 1000  THEN 'excellent (< 1s)'
        WHEN replication_lag_ms < 5000  THEN 'good (< 5s)'
        WHEN replication_lag_ms < 10000 THEN 'acceptable (< 10s)'
        ELSE 'degraded (> 10s)'
    END AS lag_category,
    rows_synced_total,
    last_sync_timestamp
FROM lakebase_sync_status
WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM lakebase_sync_status)
ORDER BY replication_lag_ms DESC;

-- ---------------------------------------------------------------------------
-- B2. Replication Lag Over Time (Line Chart)
-- ---------------------------------------------------------------------------
SELECT
    snapshot_time,
    table_name,
    replication_lag_ms,
    rows_synced_total
FROM lakebase_sync_status
ORDER BY snapshot_time, table_name;

-- ---------------------------------------------------------------------------
-- B3. Total Rows Synced (KPI)
-- ---------------------------------------------------------------------------
SELECT
    SUM(rows_synced_total) AS total_rows_synced,
    COUNT(DISTINCT table_name) AS tables_synced,
    ROUND(AVG(replication_lag_ms), 0) AS avg_lag_ms
FROM lakebase_sync_status
WHERE snapshot_time = (SELECT MAX(snapshot_time) FROM lakebase_sync_status);

-- ---------------------------------------------------------------------------
-- B4. CDC Throughput by Table (Bar Chart)
-- ---------------------------------------------------------------------------
SELECT
    table_name,
    SUM(rows_synced_total) AS total_synced,
    ROUND(AVG(replication_lag_ms), 0) AS avg_lag_ms
FROM lakebase_sync_status
GROUP BY table_name
ORDER BY total_synced DESC;


-- =====================================================================
-- SECTION C: BRANCHING
-- =====================================================================

-- ---------------------------------------------------------------------------
-- C1. Branch Overview (Table)
-- ---------------------------------------------------------------------------
SELECT
    branch_name,
    parent_branch,
    purpose,
    status,
    created_by,
    created_at,
    ttl_hours,
    expires_at,
    ROUND(storage_overhead_mb, 1) AS storage_overhead_mb,
    total_queries
FROM lakebase_branches
ORDER BY created_at DESC;

-- ---------------------------------------------------------------------------
-- C2. Branch Storage Efficiency (Bar Chart)
-- Copy-on-write = near-zero overhead until data diverges.
-- ---------------------------------------------------------------------------
SELECT
    branch_name,
    purpose,
    ROUND(storage_overhead_mb, 1) AS overhead_mb,
    total_queries,
    CASE
        WHEN storage_overhead_mb < 1   THEN 'minimal (< 1 MB)'
        WHEN storage_overhead_mb < 10  THEN 'light (1-10 MB)'
        WHEN storage_overhead_mb < 100 THEN 'moderate (10-100 MB)'
        ELSE 'heavy (> 100 MB)'
    END AS overhead_category
FROM lakebase_branches
WHERE status != 'deleted'
ORDER BY storage_overhead_mb DESC;

-- ---------------------------------------------------------------------------
-- C3. Branch Usage by Purpose (Pie Chart)
-- ---------------------------------------------------------------------------
SELECT
    purpose,
    COUNT(*) AS branch_count,
    SUM(total_queries) AS total_queries,
    ROUND(SUM(storage_overhead_mb), 1) AS total_overhead_mb
FROM lakebase_branches
GROUP BY purpose
ORDER BY branch_count DESC;


-- =====================================================================
-- SECTION D: QUERY PERFORMANCE
-- =====================================================================

-- ---------------------------------------------------------------------------
-- D1. Top Queries by Latency (Table)
-- ---------------------------------------------------------------------------
SELECT
    query_id,
    query_text,
    query_type,
    SUM(calls)                          AS total_calls,
    ROUND(AVG(mean_time_ms), 2)         AS avg_latency_ms,
    ROUND(MAX(max_time_ms), 2)          AS peak_latency_ms,
    ROUND(AVG(cache_hit_ratio), 1)      AS avg_cache_hit_pct,
    SUM(rows_returned)                  AS total_rows
FROM lakebase_query_stats
GROUP BY query_id, query_text, query_type
ORDER BY avg_latency_ms DESC;

-- ---------------------------------------------------------------------------
-- D2. Query Mix (Pie Chart)
-- ---------------------------------------------------------------------------
SELECT
    query_type,
    SUM(calls)                    AS total_calls,
    ROUND(SUM(total_time_ms), 0)  AS total_time_ms
FROM lakebase_query_stats
GROUP BY query_type
ORDER BY total_calls DESC;

-- ---------------------------------------------------------------------------
-- D3. Cache Hit Ratio Trend (Line Chart)
-- ---------------------------------------------------------------------------
SELECT
    snapshot_time,
    ROUND(AVG(cache_hit_ratio), 2) AS avg_cache_hit_pct,
    SUM(shared_blks_hit) AS total_cache_hits,
    SUM(shared_blks_read) AS total_disk_reads
FROM lakebase_query_stats
GROUP BY snapshot_time
ORDER BY snapshot_time;

-- ---------------------------------------------------------------------------
-- D4. Latency by Query Type (Box Plot / Bar)
-- ---------------------------------------------------------------------------
SELECT
    query_type,
    ROUND(AVG(mean_time_ms), 2)   AS avg_ms,
    ROUND(MIN(min_time_ms), 2)    AS min_ms,
    ROUND(MAX(max_time_ms), 2)    AS max_ms,
    SUM(calls)                    AS total_calls
FROM lakebase_query_stats
GROUP BY query_type
ORDER BY avg_ms DESC;


-- =====================================================================
-- SECTION E: ROW OPERATIONS (DML THROUGHPUT)
-- =====================================================================

-- ---------------------------------------------------------------------------
-- E1. Operations Over Time (Stacked Area Chart)
-- ---------------------------------------------------------------------------
SELECT
    timestamp,
    SUM(inserts)  AS total_inserts,
    SUM(updates)  AS total_updates,
    SUM(deletes)  AS total_deletes,
    SUM(total_operations) AS total_ops
FROM lakebase_row_operations
GROUP BY timestamp
ORDER BY timestamp;

-- ---------------------------------------------------------------------------
-- E2. Operations by Table (Bar Chart)
-- ---------------------------------------------------------------------------
SELECT
    table_name,
    SUM(inserts)  AS total_inserts,
    SUM(updates)  AS total_updates,
    SUM(deletes)  AS total_deletes,
    SUM(total_operations) AS total_ops
FROM lakebase_row_operations
GROUP BY table_name
ORDER BY total_ops DESC;


-- =====================================================================
-- SECTION F: GOVERNANCE & SECURITY
-- =====================================================================

-- ---------------------------------------------------------------------------
-- F1. Governance Event Summary (KPI Cards)
-- ---------------------------------------------------------------------------
SELECT
    COUNT(*)                                                           AS total_events,
    COUNT(CASE WHEN result = 'allowed' THEN 1 END)                     AS allowed,
    COUNT(CASE WHEN result = 'denied' THEN 1 END)                      AS denied,
    COUNT(CASE WHEN result = 'masked' THEN 1 END)                      AS masked,
    ROUND(COUNT(CASE WHEN result = 'denied' THEN 1 END) * 100.0
          / COUNT(*), 1)                                                AS denial_rate_pct
FROM lakebase_governance_events;

-- ---------------------------------------------------------------------------
-- F2. Governance Events Over Time (Stacked Bar)
-- ---------------------------------------------------------------------------
SELECT
    DATE(event_time)  AS event_date,
    result,
    COUNT(*)          AS event_count
FROM lakebase_governance_events
GROUP BY DATE(event_time), result
ORDER BY event_date, result;

-- ---------------------------------------------------------------------------
-- F3. PII Access & Masking (Table)
-- Shows which PII columns are being accessed and masked.
-- ---------------------------------------------------------------------------
SELECT
    resource,
    principal,
    COUNT(*)                                               AS access_count,
    COUNT(CASE WHEN result = 'masked' THEN 1 END)          AS times_masked,
    COUNT(CASE WHEN result = 'denied' THEN 1 END)          AS times_denied
FROM lakebase_governance_events
WHERE resource LIKE 'patients.%'
   OR event_type IN ('mask_applied', 'row_filter')
GROUP BY resource, principal
ORDER BY access_count DESC;

-- ---------------------------------------------------------------------------
-- F4. Access by Principal (Bar Chart)
-- ---------------------------------------------------------------------------
SELECT
    principal,
    COUNT(*)                                               AS total_events,
    COUNT(CASE WHEN result = 'allowed' THEN 1 END)         AS allowed,
    COUNT(CASE WHEN result = 'masked' THEN 1 END)          AS masked,
    COUNT(CASE WHEN result = 'denied' THEN 1 END)          AS denied
FROM lakebase_governance_events
GROUP BY principal
ORDER BY total_events DESC;

-- ---------------------------------------------------------------------------
-- F5. Denied Access Attempts (Alert Table)
-- ---------------------------------------------------------------------------
SELECT
    event_time,
    principal,
    action,
    resource,
    detail
FROM lakebase_governance_events
WHERE result = 'denied'
ORDER BY event_time DESC;
