-- =============================================================================
-- HLS Knowledge Graph — AI/BI Dashboard Queries
-- =============================================================================
-- Use these queries in Databricks AI/BI Dashboards. Each query maps to a
-- specific dashboard widget. All queries run directly against Lakebase tables.
--
-- Run in: Lakebase SQL Editor OR Databricks SQL (if Lakebase is registered
-- as a Unity Catalog catalog).
-- =============================================================================

-- ---------------------------------------------------------------------------
-- WIDGET 1: Patient Demographics Overview
-- ---------------------------------------------------------------------------

-- 1a. Age distribution
SELECT
    CASE
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) < 40 THEN '< 40'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) BETWEEN 40 AND 54 THEN '40–54'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) BETWEEN 55 AND 64 THEN '55–64'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) BETWEEN 65 AND 74 THEN '65–74'
        ELSE '75+'
    END AS age_group,
    COUNT(*) AS patient_count
FROM patients
WHERE is_active = TRUE
GROUP BY 1
ORDER BY 1;

-- 1b. Gender distribution
SELECT gender, COUNT(*) AS patient_count
FROM patients
WHERE is_active = TRUE
GROUP BY gender;

-- 1c. Insurance mix
SELECT insurance_type, COUNT(*) AS patient_count
FROM patients
WHERE is_active = TRUE
GROUP BY insurance_type
ORDER BY patient_count DESC;

-- ---------------------------------------------------------------------------
-- WIDGET 2: Treatment Efficacy Scorecard
-- ---------------------------------------------------------------------------

SELECT
    t.treatment_name,
    t.treatment_type,
    COUNT(DISTINCT t.patient_id) AS unique_patients,
    COUNT(DISTINCT CASE WHEN o.outcome_type = 'improvement' THEN o.outcome_id END) AS improved,
    COUNT(DISTINCT CASE WHEN o.outcome_type = 'stable' THEN o.outcome_id END) AS stable,
    COUNT(DISTINCT CASE WHEN o.outcome_type = 'progression' THEN o.outcome_id END) AS progression,
    ROUND(
        COUNT(DISTINCT CASE WHEN o.outcome_type = 'improvement' THEN o.outcome_id END) * 100.0
        / NULLIF(COUNT(DISTINCT o.outcome_id), 0), 1
    ) AS improvement_rate_pct,
    COUNT(DISTINCT ae.event_id) AS adverse_event_count,
    COUNT(DISTINCT CASE WHEN ae.severity IN ('severe', 'life-threatening') THEN ae.event_id END) AS serious_ae_count
FROM treatments t
LEFT JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id
LEFT JOIN adverse_events ae ON t.treatment_id = ae.treatment_id
GROUP BY t.treatment_name, t.treatment_type
ORDER BY improvement_rate_pct DESC NULLS LAST;

-- ---------------------------------------------------------------------------
-- WIDGET 3: Outcome Trends Over Time
-- ---------------------------------------------------------------------------

SELECT
    p.first_name || ' ' || p.last_name AS patient_name,
    t.treatment_name,
    o.outcome_measure,
    o.assessment_date,
    o.baseline_value,
    o.result_value,
    o.unit,
    CASE
        WHEN o.baseline_value IS NOT NULL AND o.baseline_value != 0
        THEN ROUND((o.result_value - o.baseline_value) / o.baseline_value * 100, 1)
    END AS pct_change
FROM treatment_outcomes o
JOIN patients p ON o.patient_id = p.patient_id
JOIN treatments t ON o.treatment_id = t.treatment_id
ORDER BY patient_name, outcome_measure, assessment_date;

-- ---------------------------------------------------------------------------
-- WIDGET 4: Adverse Event Monitor
-- ---------------------------------------------------------------------------

SELECT
    t.treatment_name,
    ae.event_type,
    ae.severity,
    ae.ctcae_grade,
    COUNT(*) AS event_count,
    ROUND(AVG(
        CASE WHEN ae.resolution_date IS NOT NULL
             THEN ae.resolution_date - ae.onset_date
        END
    ), 1) AS avg_duration_days
FROM adverse_events ae
JOIN treatments t ON ae.treatment_id = t.treatment_id
GROUP BY t.treatment_name, ae.event_type, ae.severity, ae.ctcae_grade
ORDER BY ae.ctcae_grade DESC, event_count DESC;

-- ---------------------------------------------------------------------------
-- WIDGET 5: Adverse Events by Severity (Donut Chart)
-- ---------------------------------------------------------------------------

SELECT
    severity,
    COUNT(*) AS event_count
FROM adverse_events
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
-- ---------------------------------------------------------------------------

SELECT
    prov.first_name || ' ' || prov.last_name AS provider_name,
    prov.specialty,
    prov.department,
    COUNT(DISTINCT e.encounter_id) AS encounter_count,
    COUNT(DISTINCT e.patient_id) AS unique_patients,
    COUNT(DISTINCT t.treatment_id) AS treatments_ordered
FROM providers prov
LEFT JOIN encounters e ON prov.provider_id = e.provider_id
LEFT JOIN treatments t ON prov.provider_id = t.provider_id
GROUP BY prov.provider_id, prov.first_name, prov.last_name, prov.specialty, prov.department
ORDER BY encounter_count DESC;

-- ---------------------------------------------------------------------------
-- WIDGET 7: Diagnosis Cohort Breakdown
-- ---------------------------------------------------------------------------

SELECT
    d.icd10_code,
    d.description AS diagnosis_description,
    p.gender,
    CASE
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 55 THEN '< 55'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) BETWEEN 55 AND 64 THEN '55–64'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) BETWEEN 65 AND 74 THEN '65–74'
        ELSE '75+'
    END AS age_group,
    COUNT(*) AS patient_count
FROM diagnoses d
JOIN patients p ON d.patient_id = p.patient_id
WHERE d.status = 'active'
GROUP BY 1, 2, 3, 4
ORDER BY patient_count DESC;

-- ---------------------------------------------------------------------------
-- WIDGET 8: Lab Results with Abnormal Flags
-- ---------------------------------------------------------------------------

SELECT
    p.first_name || ' ' || p.last_name AS patient_name,
    lr.test_name,
    lr.collected_date,
    lr.result_value,
    lr.unit,
    lr.reference_low,
    lr.reference_high,
    lr.abnormal_flag
FROM lab_results lr
JOIN patients p ON lr.patient_id = p.patient_id
WHERE lr.abnormal_flag != 'normal'
ORDER BY lr.collected_date DESC
LIMIT 200;

-- ---------------------------------------------------------------------------
-- WIDGET 9: Key Metrics (KPI Cards)
-- ---------------------------------------------------------------------------

SELECT 'Total Patients' AS metric, COUNT(DISTINCT patient_id)::TEXT AS value FROM patients WHERE is_active = TRUE
UNION ALL
SELECT 'Active Treatments', COUNT(*)::TEXT FROM treatments WHERE status = 'active'
UNION ALL
SELECT 'Total Encounters', COUNT(*)::TEXT FROM encounters
UNION ALL
SELECT 'Adverse Events', COUNT(*)::TEXT FROM adverse_events
UNION ALL
SELECT 'Severe AEs (≥ G3)', COUNT(*)::TEXT FROM adverse_events WHERE ctcae_grade >= 3;

-- ---------------------------------------------------------------------------
-- WIDGET 10: Cancer Treatment Pipeline (Diagnosis → Treatment → Outcome)
-- ---------------------------------------------------------------------------

SELECT
    d.description AS diagnosis,
    t.treatment_name,
    o.outcome_type,
    COUNT(DISTINCT p.patient_id) AS patient_count
FROM patients p
JOIN diagnoses d ON p.patient_id = d.patient_id
JOIN treatments t ON p.patient_id = t.patient_id
LEFT JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id
WHERE d.icd10_code LIKE 'C%'
GROUP BY d.description, t.treatment_name, o.outcome_type
ORDER BY patient_count DESC;
