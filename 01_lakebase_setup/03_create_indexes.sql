-- =============================================================================
-- HLS Knowledge Graph — Lakebase Performance Indexes
-- =============================================================================
-- Optimized for common access patterns: patient lookups, encounter history,
-- treatment tracking, outcome analysis, and adverse event monitoring.
-- =============================================================================

-- PATIENTS
CREATE INDEX idx_patients_mrn          ON patients (mrn);
CREATE INDEX idx_patients_dob          ON patients (date_of_birth);
CREATE INDEX idx_patients_zip          ON patients (zip_code);
CREATE INDEX idx_patients_active       ON patients (is_active) WHERE is_active = TRUE;

-- PROVIDERS
CREATE INDEX idx_providers_specialty   ON providers (specialty);
CREATE INDEX idx_providers_npi         ON providers (npi);

-- ENCOUNTERS
CREATE INDEX idx_encounters_patient    ON encounters (patient_id);
CREATE INDEX idx_encounters_provider   ON encounters (provider_id);
CREATE INDEX idx_encounters_admission  ON encounters (admission_date);
CREATE INDEX idx_encounters_type       ON encounters (encounter_type);
CREATE INDEX idx_encounters_pat_date   ON encounters (patient_id, admission_date DESC);

-- DIAGNOSES
CREATE INDEX idx_diagnoses_patient     ON diagnoses (patient_id);
CREATE INDEX idx_diagnoses_encounter   ON diagnoses (encounter_id);
CREATE INDEX idx_diagnoses_icd10       ON diagnoses (icd10_code);
CREATE INDEX idx_diagnoses_status      ON diagnoses (status);
CREATE INDEX idx_diagnoses_pat_icd     ON diagnoses (patient_id, icd10_code);

-- TREATMENTS
CREATE INDEX idx_treatments_patient    ON treatments (patient_id);
CREATE INDEX idx_treatments_encounter  ON treatments (encounter_id);
CREATE INDEX idx_treatments_provider   ON treatments (provider_id);
CREATE INDEX idx_treatments_type       ON treatments (treatment_type);
CREATE INDEX idx_treatments_status     ON treatments (status);
CREATE INDEX idx_treatments_name       ON treatments (treatment_name);
CREATE INDEX idx_treatments_pat_type   ON treatments (patient_id, treatment_type);

-- MEDICATIONS
CREATE INDEX idx_medications_patient   ON medications (patient_id);
CREATE INDEX idx_medications_treatment ON medications (treatment_id);
CREATE INDEX idx_medications_drug      ON medications (drug_name);
CREATE INDEX idx_medications_ndc       ON medications (ndc_code);

-- TREATMENT OUTCOMES
CREATE INDEX idx_outcomes_treatment    ON treatment_outcomes (treatment_id);
CREATE INDEX idx_outcomes_patient      ON treatment_outcomes (patient_id);
CREATE INDEX idx_outcomes_type         ON treatment_outcomes (outcome_type);
CREATE INDEX idx_outcomes_date         ON treatment_outcomes (assessment_date);
CREATE INDEX idx_outcomes_measure      ON treatment_outcomes (outcome_measure);

-- ADVERSE EVENTS
CREATE INDEX idx_adverse_treatment     ON adverse_events (treatment_id);
CREATE INDEX idx_adverse_patient       ON adverse_events (patient_id);
CREATE INDEX idx_adverse_severity      ON adverse_events (severity);
CREATE INDEX idx_adverse_grade         ON adverse_events (ctcae_grade);
CREATE INDEX idx_adverse_type          ON adverse_events (event_type);
CREATE INDEX idx_adverse_onset         ON adverse_events (onset_date);

-- LAB RESULTS
CREATE INDEX idx_labs_patient          ON lab_results (patient_id);
CREATE INDEX idx_labs_encounter        ON lab_results (encounter_id);
CREATE INDEX idx_labs_test             ON lab_results (test_name);
CREATE INDEX idx_labs_loinc            ON lab_results (loinc_code);
CREATE INDEX idx_labs_collected        ON lab_results (collected_date);
CREATE INDEX idx_labs_abnormal         ON lab_results (abnormal_flag) WHERE abnormal_flag != 'N';
CREATE INDEX idx_labs_pat_test         ON lab_results (patient_id, test_name, collected_date DESC);
