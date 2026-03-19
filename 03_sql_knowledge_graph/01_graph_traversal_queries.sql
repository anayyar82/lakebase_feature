-- =============================================================================
-- HLS Knowledge Graph — SQL Recursive CTE Graph Queries
-- =============================================================================
-- Pure SQL graph traversals over the Delta tables synced from Lakebase.
-- No external graph database required — runs entirely on Databricks SQL.
--
-- Recursive CTEs enable:
--   • Multi-hop path traversal (patient → treatment → outcome chains)
--   • Reachability analysis (which entities connect to which)
--   • Shortest-path discovery across clinical relationships
--   • Cycle-safe graph walks with depth limits
-- =============================================================================

USE CATALOG hls_lakehouse;
USE SCHEMA knowledge_graph;

-- ---------------------------------------------------------------------------
-- 1. PATIENT TREATMENT JOURNEY (recursive path traversal)
--    Walks the full chain: Patient → Encounter → Treatment → Outcome
--    for a specific patient, building the path as a string.
-- ---------------------------------------------------------------------------

WITH RECURSIVE patient_journey AS (
    -- Anchor: start from the patient
    SELECT
        p.patient_id,
        p.mrn,
        p.first_name || ' ' || p.last_name AS patient_name,
        CAST('Patient: ' || p.first_name || ' ' || p.last_name AS STRING) AS path,
        1 AS depth,
        'patient' AS current_node_type,
        p.patient_id AS current_id
    FROM patients p
    WHERE p.mrn = 'MRN-100001'

    UNION ALL

    -- Hop 1: Patient → Encounters
    SELECT
        pj.patient_id,
        pj.mrn,
        pj.patient_name,
        pj.path || ' → Encounter(' || e.encounter_type || ': ' || COALESCE(e.chief_complaint, 'N/A') || ')',
        pj.depth + 1,
        'encounter',
        e.encounter_id
    FROM patient_journey pj
    JOIN encounters e ON pj.current_id = e.patient_id
    WHERE pj.current_node_type = 'patient'
      AND pj.depth < 5

    UNION ALL

    -- Hop 2: Encounter → Treatments
    SELECT
        pj.patient_id,
        pj.mrn,
        pj.patient_name,
        pj.path || ' → Treatment(' || t.treatment_name || ')',
        pj.depth + 1,
        'treatment',
        t.treatment_id
    FROM patient_journey pj
    JOIN treatments t ON pj.current_id = t.encounter_id
    WHERE pj.current_node_type = 'encounter'
      AND pj.depth < 5

    UNION ALL

    -- Hop 3: Treatment → Outcomes
    SELECT
        pj.patient_id,
        pj.mrn,
        pj.patient_name,
        pj.path || ' → Outcome(' || o.outcome_type || ': ' || o.outcome_measure || ' = ' || CAST(o.result_value AS STRING) || ' ' || o.unit || ')',
        pj.depth + 1,
        'outcome',
        o.outcome_id
    FROM patient_journey pj
    JOIN treatment_outcomes o ON pj.current_id = o.treatment_id
    WHERE pj.current_node_type = 'treatment'
      AND pj.depth < 5
)
SELECT path, depth
FROM patient_journey
WHERE current_node_type = 'outcome'
ORDER BY depth, path;


-- ---------------------------------------------------------------------------
-- 2. TREATMENT-OUTCOME CHAIN (recursive)
--    For each treatment, recursively collect all downstream outcomes
--    and adverse events, building a treatment impact tree.
-- ---------------------------------------------------------------------------

WITH RECURSIVE treatment_impact AS (
    -- Anchor: all treatments
    SELECT
        t.treatment_id,
        t.treatment_name,
        t.patient_id,
        CAST(t.treatment_name AS STRING) AS impact_chain,
        1 AS depth,
        'treatment' AS node_type

    FROM treatments t

    UNION ALL

    -- Hop: Treatment → Outcomes
    SELECT
        ti.treatment_id,
        ti.treatment_name,
        ti.patient_id,
        ti.impact_chain || ' → ' || o.outcome_type || '(' || o.outcome_measure || ': ' ||
            CAST(o.baseline_value AS STRING) || ' → ' || CAST(o.result_value AS STRING) || ' ' || o.unit || ')',
        ti.depth + 1,
        'outcome'
    FROM treatment_impact ti
    JOIN treatment_outcomes o ON ti.treatment_id = o.treatment_id
    WHERE ti.node_type = 'treatment'
      AND ti.depth < 4

    UNION ALL

    -- Hop: Treatment → Adverse Events
    SELECT
        ti.treatment_id,
        ti.treatment_name,
        ti.patient_id,
        ti.impact_chain || ' → AE(' || ae.event_type || ', ' || ae.severity || ', grade ' || CAST(ae.ctcae_grade AS STRING) || ')',
        ti.depth + 1,
        'adverse_event'
    FROM treatment_impact ti
    JOIN adverse_events ae ON ti.treatment_id = ae.treatment_id
    WHERE ti.node_type = 'treatment'
      AND ti.depth < 4
)
SELECT
    p.mrn,
    p.first_name || ' ' || p.last_name AS patient_name,
    treatment_name,
    impact_chain,
    node_type AS terminal_node,
    depth
FROM treatment_impact ti
JOIN patients p ON ti.patient_id = p.patient_id
WHERE depth > 1
ORDER BY p.mrn, treatment_name, depth;


-- ---------------------------------------------------------------------------
-- 3. SHARED TREATMENT PATHWAYS
--    Find pairs of patients who received the same treatments.
--    Uses self-join + aggregation (no recursion needed here, but
--    models the graph pattern: Patient ← Treatment → Patient).
-- ---------------------------------------------------------------------------

SELECT
    p1.mrn                                    AS patient_1_mrn,
    p1.first_name || ' ' || p1.last_name      AS patient_1,
    p2.mrn                                    AS patient_2_mrn,
    p2.first_name || ' ' || p2.last_name      AS patient_2,
    COLLECT_SET(t1.treatment_name)             AS shared_treatments,
    COUNT(DISTINCT t1.treatment_id)            AS overlap_count
FROM treatments t1
JOIN treatments t2
    ON  t1.treatment_name = t2.treatment_name
    AND t1.patient_id < t2.patient_id
JOIN patients p1 ON t1.patient_id = p1.patient_id
JOIN patients p2 ON t2.patient_id = p2.patient_id
GROUP BY p1.mrn, p1.first_name, p1.last_name,
         p2.mrn, p2.first_name, p2.last_name
HAVING COUNT(DISTINCT t1.treatment_name) >= 1
ORDER BY overlap_count DESC;


-- ---------------------------------------------------------------------------
-- 4. PROVIDER COLLABORATION NETWORK
--    Walk the implicit graph: Provider → Encounter → Patient → Encounter → Provider
--    to find providers who co-manage the same patients.
-- ---------------------------------------------------------------------------

WITH provider_patients AS (
    SELECT DISTINCT
        prov.provider_id,
        prov.first_name || ' ' || prov.last_name AS provider_name,
        prov.specialty,
        e.patient_id
    FROM providers prov
    JOIN encounters e ON prov.provider_id = e.provider_id
)
SELECT
    pp1.provider_name                 AS provider_1,
    pp1.specialty                     AS specialty_1,
    pp2.provider_name                 AS provider_2,
    pp2.specialty                     AS specialty_2,
    COUNT(DISTINCT pp1.patient_id)    AS shared_patients,
    COLLECT_SET(p.mrn)                AS shared_patient_mrns
FROM provider_patients pp1
JOIN provider_patients pp2
    ON  pp1.patient_id = pp2.patient_id
    AND pp1.provider_id < pp2.provider_id
JOIN patients p ON pp1.patient_id = p.patient_id
GROUP BY pp1.provider_name, pp1.specialty,
         pp2.provider_name, pp2.specialty
ORDER BY shared_patients DESC;


-- ---------------------------------------------------------------------------
-- 5. DIAGNOSIS → TREATMENT → OUTCOME PATHWAY (recursive 3-hop)
--    Full clinical pathway traversal for cancer patients.
-- ---------------------------------------------------------------------------

WITH RECURSIVE clinical_pathway AS (
    -- Anchor: cancer diagnoses
    SELECT
        d.patient_id,
        d.diagnosis_id AS current_id,
        d.icd10_code || ': ' || d.description AS path,
        1 AS depth,
        'diagnosis' AS node_type
    FROM diagnoses d
    WHERE d.icd10_code LIKE 'C%'

    UNION ALL

    -- Hop: Diagnosis → Treatments (via patient)
    SELECT
        cp.patient_id,
        t.treatment_id,
        cp.path || ' → ' || t.treatment_type || '(' || t.treatment_name || ')',
        cp.depth + 1,
        'treatment'
    FROM clinical_pathway cp
    JOIN treatments t ON cp.patient_id = t.patient_id
    WHERE cp.node_type = 'diagnosis'
      AND cp.depth < 4

    UNION ALL

    -- Hop: Treatment → Outcomes
    SELECT
        cp.patient_id,
        o.outcome_id,
        cp.path || ' → ' || o.outcome_type || '(' || o.outcome_measure || ': ' || CAST(o.result_value AS STRING) || ' ' || o.unit || ')',
        cp.depth + 1,
        'outcome'
    FROM clinical_pathway cp
    JOIN treatment_outcomes o ON cp.current_id = o.treatment_id
    WHERE cp.node_type = 'treatment'
      AND cp.depth < 4
)
SELECT
    p.mrn,
    p.first_name || ' ' || p.last_name AS patient_name,
    path AS clinical_pathway,
    depth
FROM clinical_pathway cp
JOIN patients p ON cp.patient_id = p.patient_id
WHERE node_type = 'outcome'
ORDER BY p.mrn, depth;


-- ---------------------------------------------------------------------------
-- 6. COMORBIDITY GRAPH
--    Diagnoses that co-occur in the same patients — models the implicit
--    graph Diagnosis ← Patient → Diagnosis.
-- ---------------------------------------------------------------------------

SELECT
    d1.icd10_code                        AS diagnosis_1_code,
    d1.description                       AS diagnosis_1,
    d2.icd10_code                        AS diagnosis_2_code,
    d2.description                       AS diagnosis_2,
    COUNT(DISTINCT d1.patient_id)         AS co_occurrence_count,
    COLLECT_SET(p.mrn)                    AS patient_mrns
FROM diagnoses d1
JOIN diagnoses d2
    ON  d1.patient_id = d2.patient_id
    AND d1.icd10_code < d2.icd10_code
JOIN patients p ON d1.patient_id = p.patient_id
GROUP BY d1.icd10_code, d1.description,
         d2.icd10_code, d2.description
ORDER BY co_occurrence_count DESC;


-- ---------------------------------------------------------------------------
-- 7. PATIENT SIMILARITY (Jaccard index via SQL)
--    Measures treatment overlap between patients — equivalent to
--    Neo4j's Node Similarity algorithm.
-- ---------------------------------------------------------------------------

WITH patient_treatments AS (
    SELECT patient_id, COLLECT_SET(treatment_name) AS treatment_set
    FROM treatments
    GROUP BY patient_id
),
patient_pairs AS (
    SELECT
        a.patient_id AS patient_1_id,
        b.patient_id AS patient_2_id,
        SIZE(ARRAY_INTERSECT(a.treatment_set, b.treatment_set)) AS intersection_size,
        SIZE(ARRAY_UNION(a.treatment_set, b.treatment_set))     AS union_size
    FROM patient_treatments a
    CROSS JOIN patient_treatments b
    WHERE a.patient_id < b.patient_id
)
SELECT
    p1.mrn                                AS patient_1_mrn,
    p1.first_name || ' ' || p1.last_name  AS patient_1,
    p2.mrn                                AS patient_2_mrn,
    p2.first_name || ' ' || p2.last_name  AS patient_2,
    pp.intersection_size                   AS shared_treatments,
    pp.union_size                          AS total_distinct_treatments,
    ROUND(pp.intersection_size / pp.union_size, 3) AS jaccard_similarity
FROM patient_pairs pp
JOIN patients p1 ON pp.patient_1_id = p1.patient_id
JOIN patients p2 ON pp.patient_2_id = p2.patient_id
WHERE pp.intersection_size > 0
ORDER BY jaccard_similarity DESC;


-- ---------------------------------------------------------------------------
-- 8. ADVERSE EVENT PROPAGATION (recursive)
--    Starting from a treatment with a severe AE, trace backwards to find
--    which diagnosis led to that treatment, and forward to find outcomes.
-- ---------------------------------------------------------------------------

WITH RECURSIVE ae_trace AS (
    -- Anchor: severe adverse events
    SELECT
        ae.event_id,
        ae.treatment_id AS current_id,
        ae.event_type || ' (grade ' || CAST(ae.ctcae_grade AS STRING) || ')' AS trace,
        ae.patient_id,
        1 AS depth,
        'adverse_event' AS node_type
    FROM adverse_events ae
    WHERE ae.ctcae_grade >= 3

    UNION ALL

    -- Walk backwards: AE → Treatment
    SELECT
        at.event_id,
        t.treatment_id,
        t.treatment_name || ' → ' || at.trace,
        at.patient_id,
        at.depth + 1,
        'treatment'
    FROM ae_trace at
    JOIN treatments t ON at.current_id = t.treatment_id
    WHERE at.node_type = 'adverse_event'
      AND at.depth < 5

    UNION ALL

    -- Walk backwards: Treatment → Diagnosis (via patient)
    SELECT
        at.event_id,
        d.diagnosis_id,
        d.icd10_code || '(' || d.description || ') → ' || at.trace,
        at.patient_id,
        at.depth + 1,
        'diagnosis'
    FROM ae_trace at
    JOIN diagnoses d ON at.patient_id = d.patient_id AND d.diagnosis_type = 'primary'
    WHERE at.node_type = 'treatment'
      AND at.depth < 5
)
SELECT
    p.mrn,
    p.first_name || ' ' || p.last_name AS patient_name,
    trace AS full_trace,
    depth
FROM ae_trace at
JOIN patients p ON at.patient_id = p.patient_id
WHERE node_type = 'diagnosis'
ORDER BY p.mrn, depth;
