-- =============================================================================
-- HLS Knowledge Graph — Gold-Layer Analytics Views
-- =============================================================================
-- Built on top of the Delta tables auto-synced from Lakebase via Lakehouse Sync.
-- These views power AI/BI dashboards and Genie spaces.
-- =============================================================================

-- Use the synced catalog/schema
USE CATALOG hls_lakehouse;
USE SCHEMA knowledge_graph;

-- ---------------------------------------------------------------------------
-- Patient 360 View
-- Comprehensive patient profile with demographics, diagnosis count, and
-- active treatment count.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold_patient_360 AS
SELECT
    p.patient_id,
    p.mrn,
    p.first_name || ' ' || p.last_name AS patient_name,
    p.date_of_birth,
    FLOOR(DATEDIFF(CURRENT_DATE(), p.date_of_birth) / 365.25) AS age,
    p.gender,
    p.race,
    p.ethnicity,
    p.insurance_type,
    p.zip_code,
    COUNT(DISTINCT d.diagnosis_id)  AS diagnosis_count,
    COUNT(DISTINCT t.treatment_id)  AS treatment_count,
    COUNT(DISTINCT e.encounter_id)  AS encounter_count,
    MIN(e.admission_date)           AS first_encounter,
    MAX(e.admission_date)           AS last_encounter
FROM patients p
LEFT JOIN encounters e  ON p.patient_id = e.patient_id
LEFT JOIN diagnoses d   ON p.patient_id = d.patient_id
LEFT JOIN treatments t  ON p.patient_id = t.patient_id
WHERE p.is_active = TRUE
GROUP BY ALL;

-- ---------------------------------------------------------------------------
-- Treatment Efficacy Summary
-- Aggregates outcomes by treatment, showing improvement rates, average
-- baseline/result values, and adverse event counts.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold_treatment_efficacy AS
SELECT
    t.treatment_name,
    t.treatment_type,
    COUNT(DISTINCT t.treatment_id)                              AS total_administrations,
    COUNT(DISTINCT t.patient_id)                                AS unique_patients,
    COUNT(DISTINCT CASE WHEN o.outcome_type = 'improvement'
                        THEN o.outcome_id END)                  AS improved_count,
    COUNT(DISTINCT CASE WHEN o.outcome_type = 'stable'
                        THEN o.outcome_id END)                  AS stable_count,
    COUNT(DISTINCT CASE WHEN o.outcome_type = 'progression'
                        THEN o.outcome_id END)                  AS progression_count,
    ROUND(
        COUNT(DISTINCT CASE WHEN o.outcome_type = 'improvement'
                            THEN o.outcome_id END) * 100.0
        / NULLIF(COUNT(DISTINCT o.outcome_id), 0), 1
    )                                                           AS improvement_rate_pct,
    AVG(o.baseline_value)                                       AS avg_baseline,
    AVG(o.result_value)                                         AS avg_result,
    COUNT(DISTINCT ae.event_id)                                 AS adverse_event_count,
    COUNT(DISTINCT CASE WHEN ae.severity IN ('severe', 'life-threatening')
                        THEN ae.event_id END)                   AS serious_ae_count
FROM treatments t
LEFT JOIN treatment_outcomes o  ON t.treatment_id = o.treatment_id
LEFT JOIN adverse_events ae     ON t.treatment_id = ae.treatment_id
GROUP BY t.treatment_name, t.treatment_type;

-- ---------------------------------------------------------------------------
-- Adverse Event Dashboard
-- Tracks adverse events by type, severity, CTCAE grade, and associated
-- treatment for safety monitoring.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold_adverse_events AS
SELECT
    ae.event_id,
    p.mrn,
    p.first_name || ' ' || p.last_name  AS patient_name,
    t.treatment_name,
    t.treatment_type,
    ae.event_type,
    ae.severity,
    ae.ctcae_grade,
    ae.onset_date,
    ae.resolution_date,
    CASE
        WHEN ae.resolution_date IS NOT NULL
        THEN DATEDIFF(ae.resolution_date, ae.onset_date)
    END                                  AS duration_days,
    ae.action_taken,
    ae.outcome                           AS ae_outcome,
    prov.first_name || ' ' || prov.last_name AS reported_by_provider
FROM adverse_events ae
JOIN patients p       ON ae.patient_id   = p.patient_id
JOIN treatments t     ON ae.treatment_id = t.treatment_id
LEFT JOIN providers prov ON ae.reported_by = prov.provider_id;

-- ---------------------------------------------------------------------------
-- Patient Outcomes Timeline
-- Longitudinal view of how patient measures change over time for each
-- treatment, useful for trend analysis.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold_outcomes_timeline AS
SELECT
    p.mrn,
    p.first_name || ' ' || p.last_name  AS patient_name,
    t.treatment_name,
    o.outcome_measure,
    o.baseline_value,
    o.result_value,
    o.unit,
    o.outcome_type,
    o.assessment_date,
    CASE
        WHEN o.baseline_value IS NOT NULL AND o.baseline_value != 0
        THEN ROUND((o.result_value - o.baseline_value) / o.baseline_value * 100, 1)
    END                                  AS pct_change,
    prov.first_name || ' ' || prov.last_name AS assessed_by_provider
FROM treatment_outcomes o
JOIN patients p     ON o.patient_id   = p.patient_id
JOIN treatments t   ON o.treatment_id = t.treatment_id
LEFT JOIN providers prov ON o.assessed_by = prov.provider_id;

-- ---------------------------------------------------------------------------
-- Provider Activity Summary
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold_provider_activity AS
SELECT
    prov.provider_id,
    prov.first_name || ' ' || prov.last_name AS provider_name,
    prov.npi,
    prov.specialty,
    prov.department,
    COUNT(DISTINCT e.encounter_id)   AS encounter_count,
    COUNT(DISTINCT e.patient_id)     AS unique_patients,
    COUNT(DISTINCT t.treatment_id)   AS treatments_ordered,
    MIN(e.admission_date)            AS first_encounter,
    MAX(e.admission_date)            AS last_encounter
FROM providers prov
LEFT JOIN encounters e  ON prov.provider_id = e.provider_id
LEFT JOIN treatments t  ON prov.provider_id = t.provider_id
GROUP BY ALL;

-- ---------------------------------------------------------------------------
-- Diagnosis Cohort View
-- Enables cohort analysis: group patients by ICD-10 diagnosis with
-- demographics and treatment information.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold_diagnosis_cohorts AS
SELECT
    d.icd10_code,
    d.description                        AS diagnosis_description,
    d.status                             AS diagnosis_status,
    p.patient_id,
    p.mrn,
    p.first_name || ' ' || p.last_name   AS patient_name,
    FLOOR(DATEDIFF(CURRENT_DATE(), p.date_of_birth) / 365.25) AS age,
    p.gender,
    p.race,
    p.insurance_type,
    d.diagnosed_date,
    d.resolved_date
FROM diagnoses d
JOIN patients p ON d.patient_id = p.patient_id;

-- ---------------------------------------------------------------------------
-- Lab Results with Trends
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold_lab_trends AS
SELECT
    p.mrn,
    p.first_name || ' ' || p.last_name AS patient_name,
    lr.test_name,
    lr.loinc_code,
    lr.result_value,
    lr.unit,
    lr.reference_low,
    lr.reference_high,
    lr.abnormal_flag,
    lr.collected_date,
    LAG(lr.result_value) OVER (
        PARTITION BY lr.patient_id, lr.test_name
        ORDER BY lr.collected_date
    ) AS previous_value,
    lr.result_value - LAG(lr.result_value) OVER (
        PARTITION BY lr.patient_id, lr.test_name
        ORDER BY lr.collected_date
    ) AS change_from_previous
FROM lab_results lr
JOIN patients p ON lr.patient_id = p.patient_id;
