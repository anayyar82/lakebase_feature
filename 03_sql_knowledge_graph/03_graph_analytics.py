# Databricks notebook source
# MAGIC %md
# MAGIC # Graph Analytics via SQL
# MAGIC
# MAGIC Runs graph-style analytics using **SQL recursive CTEs** and the
# MAGIC pre-built graph views — no external graph database needed.
# MAGIC Everything runs on Databricks SQL over the Delta tables synced
# MAGIC from Lakebase via Zero ETL.

# COMMAND ----------

CATALOG = "hls_lakehouse"
SCHEMA  = "knowledge_graph"

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Knowledge Graph Statistics
# MAGIC
# MAGIC Count nodes and edges in the SQL-based knowledge graph.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT relationship, COUNT(*) AS edge_count
# MAGIC FROM graph_all_edges
# MAGIC GROUP BY relationship
# MAGIC ORDER BY edge_count DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT source_type AS node_type, COUNT(DISTINCT source_id) AS node_count
# MAGIC FROM graph_all_edges
# MAGIC GROUP BY source_type
# MAGIC UNION ALL
# MAGIC SELECT target_type, COUNT(DISTINCT target_id)
# MAGIC FROM graph_all_edges
# MAGIC GROUP BY target_type
# MAGIC ORDER BY node_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Patient Treatment Journey (Recursive CTE)
# MAGIC
# MAGIC Traces the full path from patient → encounter → treatment → outcome
# MAGIC for Eleanor Mitchell (breast cancer journey).

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH RECURSIVE patient_journey AS (
# MAGIC     SELECT
# MAGIC         p.patient_id,
# MAGIC         p.mrn,
# MAGIC         CAST('Patient: ' || p.first_name || ' ' || p.last_name AS STRING) AS path,
# MAGIC         1 AS depth,
# MAGIC         'patient' AS current_node_type,
# MAGIC         p.patient_id AS current_id
# MAGIC     FROM patients p
# MAGIC     WHERE p.mrn = 'MRN-100001'
# MAGIC
# MAGIC     UNION ALL
# MAGIC
# MAGIC     SELECT
# MAGIC         pj.patient_id, pj.mrn,
# MAGIC         pj.path || ' → Encounter(' || e.encounter_type || ')',
# MAGIC         pj.depth + 1, 'encounter', e.encounter_id
# MAGIC     FROM patient_journey pj
# MAGIC     JOIN encounters e ON pj.current_id = e.patient_id
# MAGIC     WHERE pj.current_node_type = 'patient' AND pj.depth < 5
# MAGIC
# MAGIC     UNION ALL
# MAGIC
# MAGIC     SELECT
# MAGIC         pj.patient_id, pj.mrn,
# MAGIC         pj.path || ' → Treatment(' || t.treatment_name || ')',
# MAGIC         pj.depth + 1, 'treatment', t.treatment_id
# MAGIC     FROM patient_journey pj
# MAGIC     JOIN treatments t ON pj.current_id = t.encounter_id
# MAGIC     WHERE pj.current_node_type = 'encounter' AND pj.depth < 5
# MAGIC
# MAGIC     UNION ALL
# MAGIC
# MAGIC     SELECT
# MAGIC         pj.patient_id, pj.mrn,
# MAGIC         pj.path || ' → Outcome(' || o.outcome_type || ': ' || o.outcome_measure || ')',
# MAGIC         pj.depth + 1, 'outcome', o.outcome_id
# MAGIC     FROM patient_journey pj
# MAGIC     JOIN treatment_outcomes o ON pj.current_id = o.treatment_id
# MAGIC     WHERE pj.current_node_type = 'treatment' AND pj.depth < 5
# MAGIC )
# MAGIC SELECT path, depth
# MAGIC FROM patient_journey
# MAGIC WHERE current_node_type = 'outcome'
# MAGIC ORDER BY depth, path

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Patient Similarity (Jaccard Index)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM graph_patient_similarity
# MAGIC ORDER BY jaccard_similarity DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Comorbidity Network

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM graph_comorbidities
# MAGIC ORDER BY co_occurrence_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Provider Collaboration Network

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     provider_name,
# MAGIC     specialty,
# MAGIC     patient_name AS shared_patient,
# MAGIC     encounter_count
# MAGIC FROM graph_provider_patients
# MAGIC ORDER BY provider_name, encounter_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Cancer Treatment Pathways (Diagnosis → Treatment → Outcome)

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH RECURSIVE clinical_pathway AS (
# MAGIC     SELECT
# MAGIC         d.patient_id,
# MAGIC         d.diagnosis_id AS current_id,
# MAGIC         d.icd10_code || ': ' || d.description AS path,
# MAGIC         1 AS depth,
# MAGIC         'diagnosis' AS node_type
# MAGIC     FROM diagnoses d
# MAGIC     WHERE d.icd10_code LIKE 'C%'
# MAGIC
# MAGIC     UNION ALL
# MAGIC
# MAGIC     SELECT
# MAGIC         cp.patient_id, t.treatment_id,
# MAGIC         cp.path || ' → ' || t.treatment_name,
# MAGIC         cp.depth + 1, 'treatment'
# MAGIC     FROM clinical_pathway cp
# MAGIC     JOIN treatments t ON cp.patient_id = t.patient_id
# MAGIC     WHERE cp.node_type = 'diagnosis' AND cp.depth < 4
# MAGIC
# MAGIC     UNION ALL
# MAGIC
# MAGIC     SELECT
# MAGIC         cp.patient_id, o.outcome_id,
# MAGIC         cp.path || ' → ' || o.outcome_type || '(' || o.outcome_measure || ')',
# MAGIC         cp.depth + 1, 'outcome'
# MAGIC     FROM clinical_pathway cp
# MAGIC     JOIN treatment_outcomes o ON cp.current_id = o.treatment_id
# MAGIC     WHERE cp.node_type = 'treatment' AND cp.depth < 4
# MAGIC )
# MAGIC SELECT
# MAGIC     p.mrn,
# MAGIC     p.first_name || ' ' || p.last_name AS patient_name,
# MAGIC     path AS clinical_pathway,
# MAGIC     depth
# MAGIC FROM clinical_pathway cp
# MAGIC JOIN patients p ON cp.patient_id = p.patient_id
# MAGIC WHERE node_type = 'outcome'
# MAGIC ORDER BY p.mrn

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Treatment Efficacy with Safety Profile

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     gto.treatment_name,
# MAGIC     COUNT(DISTINCT gto.outcome_id)  AS total_outcomes,
# MAGIC     SUM(CASE WHEN gto.outcome_type = 'improvement' THEN 1 ELSE 0 END) AS improvements,
# MAGIC     ROUND(
# MAGIC         SUM(CASE WHEN gto.outcome_type = 'improvement' THEN 1 ELSE 0 END) * 100.0
# MAGIC         / COUNT(DISTINCT gto.outcome_id), 1
# MAGIC     ) AS improvement_rate_pct,
# MAGIC     COUNT(DISTINCT gtae.event_id) AS total_adverse_events,
# MAGIC     COUNT(DISTINCT CASE WHEN gtae.ctcae_grade >= 3 THEN gtae.event_id END) AS serious_aes
# MAGIC FROM graph_treatment_outcomes gto
# MAGIC LEFT JOIN graph_treatment_adverse_events gtae
# MAGIC     ON gto.treatment_id = gtae.treatment_id
# MAGIC GROUP BY gto.treatment_name
# MAGIC ORDER BY improvement_rate_pct DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Severe AE Trace (Recursive: Diagnosis → Treatment → Adverse Event)

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH RECURSIVE ae_trace AS (
# MAGIC     SELECT
# MAGIC         ae.event_id,
# MAGIC         ae.treatment_id AS current_id,
# MAGIC         ae.event_type || ' (grade ' || CAST(ae.ctcae_grade AS STRING) || ')' AS trace,
# MAGIC         ae.patient_id,
# MAGIC         1 AS depth,
# MAGIC         'adverse_event' AS node_type
# MAGIC     FROM adverse_events ae
# MAGIC     WHERE ae.ctcae_grade >= 3
# MAGIC
# MAGIC     UNION ALL
# MAGIC
# MAGIC     SELECT
# MAGIC         at.event_id, t.treatment_id,
# MAGIC         t.treatment_name || ' → ' || at.trace,
# MAGIC         at.patient_id, at.depth + 1, 'treatment'
# MAGIC     FROM ae_trace at
# MAGIC     JOIN treatments t ON at.current_id = t.treatment_id
# MAGIC     WHERE at.node_type = 'adverse_event' AND at.depth < 5
# MAGIC
# MAGIC     UNION ALL
# MAGIC
# MAGIC     SELECT
# MAGIC         at.event_id, d.diagnosis_id,
# MAGIC         d.icd10_code || ' → ' || at.trace,
# MAGIC         at.patient_id, at.depth + 1, 'diagnosis'
# MAGIC     FROM ae_trace at
# MAGIC     JOIN diagnoses d ON at.patient_id = d.patient_id AND d.diagnosis_type = 'primary'
# MAGIC     WHERE at.node_type = 'treatment' AND at.depth < 5
# MAGIC )
# MAGIC SELECT
# MAGIC     p.mrn,
# MAGIC     p.first_name || ' ' || p.last_name AS patient_name,
# MAGIC     trace AS full_trace
# MAGIC FROM ae_trace at
# MAGIC JOIN patients p ON at.patient_id = p.patient_id
# MAGIC WHERE node_type = 'diagnosis'
# MAGIC ORDER BY p.mrn
