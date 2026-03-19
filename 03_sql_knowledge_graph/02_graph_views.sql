-- =============================================================================
-- HLS Knowledge Graph — Materialized Graph Views
-- =============================================================================
-- Pre-computed graph relationship views that make it easy to query the
-- knowledge graph without writing recursive CTEs every time.
-- These views model the same relationships a graph database would store
-- as edges, but using standard SQL on Delta tables.
-- =============================================================================

USE CATALOG hls_lakehouse;
USE SCHEMA knowledge_graph;

-- ---------------------------------------------------------------------------
-- EDGE VIEW: Patient → Treatment (with diagnosis context)
-- Models the graph: (Patient)-[:RECEIVED_TREATMENT]->(Treatment)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW graph_patient_treatments AS
SELECT
    p.patient_id,
    p.mrn,
    p.first_name || ' ' || p.last_name AS patient_name,
    p.gender,
    FLOOR(DATEDIFF(CURRENT_DATE(), p.date_of_birth) / 365.25) AS age,
    t.treatment_id,
    t.treatment_name,
    t.treatment_type,
    t.start_date,
    t.end_date,
    t.dosage,
    t.frequency,
    t.route,
    t.status AS treatment_status,
    d.icd10_code,
    d.description AS diagnosis,
    d.diagnosis_type,
    prov.first_name || ' ' || prov.last_name AS ordering_provider,
    prov.specialty AS provider_specialty
FROM patients p
JOIN treatments t   ON p.patient_id = t.patient_id
JOIN encounters e   ON t.encounter_id = e.encounter_id
LEFT JOIN diagnoses d ON p.patient_id = d.patient_id AND d.diagnosis_type = 'primary'
JOIN providers prov ON t.provider_id = prov.provider_id;

-- ---------------------------------------------------------------------------
-- EDGE VIEW: Treatment → Outcome
-- Models: (Treatment)-[:HAS_OUTCOME]->(Outcome)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW graph_treatment_outcomes AS
SELECT
    t.treatment_id,
    t.treatment_name,
    t.treatment_type,
    t.patient_id,
    p.mrn,
    p.first_name || ' ' || p.last_name AS patient_name,
    o.outcome_id,
    o.outcome_type,
    o.outcome_measure,
    o.baseline_value,
    o.result_value,
    o.unit,
    o.assessment_date,
    CASE
        WHEN o.baseline_value IS NOT NULL AND o.baseline_value != 0
        THEN ROUND((o.result_value - o.baseline_value) / o.baseline_value * 100, 1)
    END AS pct_change,
    prov.first_name || ' ' || prov.last_name AS assessed_by
FROM treatments t
JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id
JOIN patients p           ON t.patient_id = p.patient_id
LEFT JOIN providers prov  ON o.assessed_by = prov.provider_id;

-- ---------------------------------------------------------------------------
-- EDGE VIEW: Treatment → Adverse Event
-- Models: (Treatment)-[:CAUSED_EVENT]->(AdverseEvent)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW graph_treatment_adverse_events AS
SELECT
    t.treatment_id,
    t.treatment_name,
    t.treatment_type,
    t.patient_id,
    p.mrn,
    p.first_name || ' ' || p.last_name AS patient_name,
    ae.event_id,
    ae.event_type,
    ae.severity,
    ae.ctcae_grade,
    ae.onset_date,
    ae.resolution_date,
    DATEDIFF(COALESCE(ae.resolution_date, CURRENT_DATE()), ae.onset_date) AS duration_days,
    ae.action_taken,
    ae.outcome AS ae_outcome
FROM treatments t
JOIN adverse_events ae ON t.treatment_id = ae.treatment_id
JOIN patients p        ON t.patient_id = p.patient_id;

-- ---------------------------------------------------------------------------
-- EDGE VIEW: Provider → Patient (care relationship)
-- Models: (Provider)-[:TREATS]->(Patient)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW graph_provider_patients AS
SELECT DISTINCT
    prov.provider_id,
    prov.first_name || ' ' || prov.last_name AS provider_name,
    prov.npi,
    prov.specialty,
    prov.department,
    p.patient_id,
    p.mrn,
    p.first_name || ' ' || p.last_name AS patient_name,
    COUNT(DISTINCT e.encounter_id) AS encounter_count,
    MIN(e.admission_date) AS first_encounter,
    MAX(e.admission_date) AS last_encounter
FROM providers prov
JOIN encounters e ON prov.provider_id = e.provider_id
JOIN patients p   ON e.patient_id = p.patient_id
GROUP BY ALL;

-- ---------------------------------------------------------------------------
-- EDGE VIEW: Diagnosis co-occurrence (comorbidity edges)
-- Models: (Diagnosis)-[:CO_OCCURS_WITH]->(Diagnosis)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW graph_comorbidities AS
SELECT
    d1.icd10_code AS diagnosis_1_code,
    d1.description AS diagnosis_1,
    d2.icd10_code AS diagnosis_2_code,
    d2.description AS diagnosis_2,
    COUNT(DISTINCT d1.patient_id) AS co_occurrence_count
FROM diagnoses d1
JOIN diagnoses d2
    ON  d1.patient_id = d2.patient_id
    AND d1.icd10_code < d2.icd10_code
GROUP BY d1.icd10_code, d1.description,
         d2.icd10_code, d2.description;

-- ---------------------------------------------------------------------------
-- EDGE VIEW: Patient similarity (Jaccard on treatments)
-- Models: (Patient)-[:SIMILAR_TO {jaccard: 0.xx}]->(Patient)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW graph_patient_similarity AS
WITH patient_treatments AS (
    SELECT patient_id, COLLECT_SET(treatment_name) AS treatment_set
    FROM treatments
    GROUP BY patient_id
)
SELECT
    p1.mrn AS patient_1_mrn,
    p1.first_name || ' ' || p1.last_name AS patient_1,
    p2.mrn AS patient_2_mrn,
    p2.first_name || ' ' || p2.last_name AS patient_2,
    SIZE(ARRAY_INTERSECT(a.treatment_set, b.treatment_set)) AS shared_treatments,
    SIZE(ARRAY_UNION(a.treatment_set, b.treatment_set)) AS total_distinct_treatments,
    ROUND(
        SIZE(ARRAY_INTERSECT(a.treatment_set, b.treatment_set))
        / SIZE(ARRAY_UNION(a.treatment_set, b.treatment_set)), 3
    ) AS jaccard_similarity
FROM patient_treatments a
CROSS JOIN patient_treatments b
JOIN patients p1 ON a.patient_id = p1.patient_id
JOIN patients p2 ON b.patient_id = p2.patient_id
WHERE a.patient_id < b.patient_id
  AND SIZE(ARRAY_INTERSECT(a.treatment_set, b.treatment_set)) > 0;

-- ---------------------------------------------------------------------------
-- FULL KNOWLEDGE GRAPH EDGE LIST
-- Unified view of all edges in the knowledge graph — useful for
-- visualization tools or export to any graph format.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW graph_all_edges AS

-- Patient → Encounter
SELECT
    p.patient_id AS source_id, 'Patient' AS source_type, p.mrn AS source_label,
    e.encounter_id AS target_id, 'Encounter' AS target_type, e.encounter_type AS target_label,
    'HAS_ENCOUNTER' AS relationship
FROM patients p JOIN encounters e ON p.patient_id = e.patient_id

UNION ALL

-- Encounter → Provider
SELECT
    e.encounter_id, 'Encounter', e.encounter_type,
    prov.provider_id, 'Provider', prov.first_name || ' ' || prov.last_name,
    'ATTENDED_BY'
FROM encounters e JOIN providers prov ON e.provider_id = prov.provider_id

UNION ALL

-- Patient → Diagnosis
SELECT
    p.patient_id, 'Patient', p.mrn,
    d.diagnosis_id, 'Diagnosis', d.icd10_code || ': ' || d.description,
    'DIAGNOSED_WITH'
FROM patients p JOIN diagnoses d ON p.patient_id = d.patient_id

UNION ALL

-- Patient → Treatment
SELECT
    p.patient_id, 'Patient', p.mrn,
    t.treatment_id, 'Treatment', t.treatment_name,
    'RECEIVED_TREATMENT'
FROM patients p JOIN treatments t ON p.patient_id = t.patient_id

UNION ALL

-- Treatment → Outcome
SELECT
    t.treatment_id, 'Treatment', t.treatment_name,
    o.outcome_id, 'Outcome', o.outcome_type || ': ' || o.outcome_measure,
    'HAS_OUTCOME'
FROM treatments t JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id

UNION ALL

-- Treatment → Adverse Event
SELECT
    t.treatment_id, 'Treatment', t.treatment_name,
    ae.event_id, 'AdverseEvent', ae.event_type || ' (' || ae.severity || ')',
    'CAUSED_EVENT'
FROM treatments t JOIN adverse_events ae ON t.treatment_id = ae.treatment_id

UNION ALL

-- Patient → Lab Result
SELECT
    p.patient_id, 'Patient', p.mrn,
    lr.lab_id, 'LabResult', lr.test_name,
    'HAS_LAB_RESULT'
FROM patients p JOIN lab_results lr ON p.patient_id = lr.patient_id;
