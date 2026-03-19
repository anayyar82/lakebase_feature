-- =============================================================================
-- HLS Knowledge Graph — AI/BI Dashboard Queries
-- =============================================================================
-- Use these queries in Databricks AI/BI Dashboards. Each query maps to a
-- specific dashboard widget. All queries reference the gold-layer views
-- created by Lakehouse Sync + gold views.
-- =============================================================================

USE CATALOG users;
USE SCHEMA ankur_nayyar;

-- ---------------------------------------------------------------------------
-- WIDGET 1: Patient Demographics Overview
-- Bar/pie charts showing patient distribution by age group, gender, race
-- ---------------------------------------------------------------------------

-- 1a. Age distribution
SELECT
    CASE
        WHEN age < 40 THEN '< 40'
        WHEN age BETWEEN 40 AND 54 THEN '40–54'
        WHEN age BETWEEN 55 AND 64 THEN '55–64'
        WHEN age BETWEEN 65 AND 74 THEN '65–74'
        ELSE '75+'
    END AS age_group,
    COUNT(*) AS patient_count
FROM gold_patient_360
GROUP BY 1
ORDER BY 1;

-- 1b. Gender distribution
SELECT gender, COUNT(*) AS patient_count
FROM gold_patient_360
GROUP BY gender;

-- 1c. Insurance mix
SELECT insurance_type, COUNT(*) AS patient_count
FROM gold_patient_360
GROUP BY insurance_type
ORDER BY patient_count DESC;

-- ---------------------------------------------------------------------------
-- WIDGET 2: Treatment Efficacy Scorecard
-- KPI cards / horizontal bar chart
-- ---------------------------------------------------------------------------

SELECT
    treatment_name,
    treatment_type,
    unique_patients,
    improvement_rate_pct,
    adverse_event_count,
    serious_ae_count
FROM gold_treatment_efficacy
ORDER BY improvement_rate_pct DESC;

-- ---------------------------------------------------------------------------
-- WIDGET 3: Outcome Trends Over Time
-- Line chart showing patient outcome trajectories
-- ---------------------------------------------------------------------------

SELECT
    patient_name,
    treatment_name,
    outcome_measure,
    assessment_date,
    baseline_value,
    result_value,
    pct_change,
    unit
FROM gold_outcomes_timeline
ORDER BY patient_name, outcome_measure, assessment_date;

-- ---------------------------------------------------------------------------
-- WIDGET 4: Adverse Event Monitor
-- Heatmap / table showing AE severity by treatment
-- ---------------------------------------------------------------------------

SELECT
    treatment_name,
    event_type,
    severity,
    ctcae_grade,
    COUNT(*) AS event_count,
    AVG(duration_days) AS avg_duration_days
FROM gold_adverse_events
GROUP BY treatment_name, event_type, severity, ctcae_grade
ORDER BY ctcae_grade DESC, event_count DESC;

-- ---------------------------------------------------------------------------
-- WIDGET 5: Adverse Events by Severity (Donut Chart)
-- ---------------------------------------------------------------------------

SELECT
    severity,
    COUNT(*) AS event_count
FROM gold_adverse_events
GROUP BY severity
ORDER BY
    CASE severity
        WHEN 'mild' THEN 1
        WHEN 'moderate' THEN 2
        WHEN 'severe' THEN 3
        WHEN 'life-threatening' THEN 4
    END;

-- ---------------------------------------------------------------------------
-- WIDGET 6: Provider Activity Dashboard
-- Table / bar chart
-- ---------------------------------------------------------------------------

SELECT
    provider_name,
    specialty,
    department,
    encounter_count,
    unique_patients,
    treatments_ordered
FROM gold_provider_activity
ORDER BY encounter_count DESC;

-- ---------------------------------------------------------------------------
-- WIDGET 7: Diagnosis Cohort Breakdown
-- Treemap / stacked bar
-- ---------------------------------------------------------------------------

SELECT
    icd10_code,
    diagnosis_description,
    gender,
    CASE
        WHEN age < 55 THEN '< 55'
        WHEN age BETWEEN 55 AND 64 THEN '55–64'
        WHEN age BETWEEN 65 AND 74 THEN '65–74'
        ELSE '75+'
    END AS age_group,
    COUNT(*) AS patient_count
FROM gold_diagnosis_cohorts
WHERE diagnosis_status = 'active'
GROUP BY 1, 2, 3, 4
ORDER BY patient_count DESC;

-- ---------------------------------------------------------------------------
-- WIDGET 8: Lab Result Trends
-- Sparklines / line chart per patient per test
-- ---------------------------------------------------------------------------

SELECT
    patient_name,
    test_name,
    collected_date,
    result_value,
    unit,
    reference_low,
    reference_high,
    abnormal_flag,
    previous_value,
    change_from_previous
FROM gold_lab_trends
WHERE abnormal_flag != 'N' OR abnormal_flag IS NULL
ORDER BY patient_name, test_name, collected_date;

-- ---------------------------------------------------------------------------
-- WIDGET 9: Key Metrics (KPI Cards)
-- ---------------------------------------------------------------------------

SELECT 'Total Patients'     AS metric, CAST(COUNT(DISTINCT patient_id) AS STRING) AS value FROM patients
UNION ALL
SELECT 'Active Treatments'  AS metric, CAST(COUNT(*) AS STRING) FROM treatments WHERE status = 'active'
UNION ALL
SELECT 'Total Encounters'   AS metric, CAST(COUNT(*) AS STRING) FROM encounters
UNION ALL
SELECT 'Adverse Events'     AS metric, CAST(COUNT(*) AS STRING) FROM adverse_events
UNION ALL
SELECT 'Severe AEs (≥ G3)'  AS metric, CAST(COUNT(*) AS STRING) FROM adverse_events WHERE ctcae_grade >= 3;

-- ---------------------------------------------------------------------------
-- WIDGET 10: Cancer Treatment Pipeline
-- Sankey-style: Diagnosis → Treatment → Outcome
-- ---------------------------------------------------------------------------

SELECT
    d.description AS diagnosis,
    t.treatment_name,
    o.outcome_type,
    COUNT(DISTINCT p.patient_id) AS patient_count
FROM patients p
JOIN diagnoses d            ON p.patient_id = d.patient_id
JOIN treatments t           ON p.patient_id = t.patient_id
LEFT JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id
WHERE d.icd10_code LIKE 'C%'
GROUP BY d.description, t.treatment_name, o.outcome_type
ORDER BY patient_count DESC;
