-- =============================================================================
-- Lakebase Internals — Metrics & Monitoring Tables
-- =============================================================================
-- Creates Delta tables that simulate the Lakebase monitoring data you'd see
-- in the Lakebase Metrics dashboard. Populate with sample data to build
-- AI/BI dashboards that showcase Lakebase's key platform capabilities.
-- =============================================================================

USE CATALOG users;
USE SCHEMA ankur_nayyar;

-- ---------------------------------------------------------------------------
-- AUTOSCALING METRICS
-- Tracks compute unit allocation, CPU, memory over time.
-- Demonstrates scale-to-zero and dynamic autoscaling.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE lakebase_compute_metrics (
    timestamp           TIMESTAMP,
    compute_units       DECIMAL(4,1),     -- 0 (scale-to-zero) to 32 CU
    cpu_percent         DECIMAL(5,2),
    memory_allocated_gb DECIMAL(6,2),
    memory_used_gb      DECIMAL(6,2),
    memory_cached_gb    DECIMAL(6,2),
    working_set_gb      DECIMAL(6,2),
    scale_event         STRING            -- 'scale_up', 'scale_down', 'scale_to_zero', 'wake_up', NULL
);

-- ---------------------------------------------------------------------------
-- CONNECTION METRICS
-- Active, idle, and total connections over time.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE lakebase_connection_metrics (
    timestamp           TIMESTAMP,
    active_connections  INT,
    idle_connections    INT,
    total_connections   INT,
    max_connections     INT,
    connection_source   STRING            -- 'application', 'lakehouse_sync', 'admin', 'genie'
);

-- ---------------------------------------------------------------------------
-- QUERY PERFORMANCE
-- Simulates pg_stat_statements data — top queries, latency, throughput.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE lakebase_query_stats (
    query_id            STRING,
    query_text          STRING,
    query_type          STRING,           -- 'SELECT', 'INSERT', 'UPDATE', 'DELETE'
    calls               BIGINT,
    total_time_ms       DECIMAL(12,2),
    mean_time_ms        DECIMAL(10,2),
    min_time_ms         DECIMAL(10,2),
    max_time_ms         DECIMAL(10,2),
    rows_returned       BIGINT,
    shared_blks_hit     BIGINT,           -- cache hits
    shared_blks_read    BIGINT,           -- disk reads
    cache_hit_ratio     DECIMAL(5,2),
    snapshot_time       TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- LAKEHOUSE SYNC STATUS
-- Tracks CDC replication state for each table.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE lakebase_sync_status (
    table_name          STRING,
    sync_mode           STRING,           -- 'continuous', 'triggered', 'snapshot'
    status              STRING,           -- 'active', 'initializing', 'paused', 'error'
    source_row_count    BIGINT,
    target_row_count    BIGINT,
    last_sync_lsn       STRING,           -- Postgres log sequence number
    replication_lag_ms  BIGINT,
    rows_synced_total   BIGINT,
    last_sync_timestamp TIMESTAMP,
    snapshot_time       TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- BRANCH ACTIVITY
-- Tracks Lakebase branching events — create, delete, TTL expiry.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE lakebase_branches (
    branch_id           STRING,
    branch_name         STRING,
    parent_branch       STRING,
    created_at          TIMESTAMP,
    created_by          STRING,
    purpose             STRING,           -- 'development', 'testing', 'ci_cd', 'audit', 'experiment'
    status              STRING,           -- 'active', 'expired', 'deleted'
    ttl_hours           INT,
    expires_at          TIMESTAMP,
    storage_overhead_mb DECIMAL(10,2),    -- copy-on-write overhead
    total_queries       BIGINT,
    deleted_at          TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- ROW OPERATIONS
-- Insert / update / delete throughput over time.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE lakebase_row_operations (
    timestamp           TIMESTAMP,
    table_name          STRING,
    inserts             BIGINT,
    updates             BIGINT,
    deletes             BIGINT,
    total_operations    BIGINT
);

-- ---------------------------------------------------------------------------
-- UNITY CATALOG GOVERNANCE
-- Tracks access control, masking, and audit events.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE lakebase_governance_events (
    event_id            STRING,
    event_time          TIMESTAMP,
    event_type          STRING,           -- 'query', 'grant', 'revoke', 'mask_applied', 'row_filter'
    principal           STRING,           -- user or group
    action              STRING,           -- 'SELECT', 'INSERT', 'GRANT', etc.
    resource            STRING,           -- table or column
    detail              STRING,
    result              STRING            -- 'allowed', 'denied', 'masked'
);
