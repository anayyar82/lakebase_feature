-- =============================================================================
-- HLS Knowledge Graph — Lakebase Postgres DDL
-- =============================================================================
-- Run in the Lakebase SQL Editor or via psql connected to your Lakebase instance.
-- These tables form the OLTP backbone: patients, providers, encounters,
-- diagnoses, treatments, medications, outcomes, and adverse events.
-- =============================================================================

-- Extension for UUID generation (built-in on Lakebase Postgres 16+)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- PATIENTS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    patient_id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    mrn                VARCHAR(20) NOT NULL UNIQUE,           -- Medical Record Number
    first_name         VARCHAR(100) NOT NULL,
    last_name          VARCHAR(100) NOT NULL,
    date_of_birth      DATE NOT NULL,
    gender             VARCHAR(20),
    race               VARCHAR(50),
    ethnicity          VARCHAR(50),
    primary_language   VARCHAR(50) DEFAULT 'English',
    insurance_type     VARCHAR(50),
    zip_code           VARCHAR(10),
    phone              VARCHAR(20),
    email              VARCHAR(150),
    is_active          BOOLEAN DEFAULT TRUE,
    created_at         TIMESTAMPTZ DEFAULT now(),
    updated_at         TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- PROVIDERS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS providers (
    provider_id        UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    npi                VARCHAR(10) NOT NULL UNIQUE,           -- National Provider Identifier
    first_name         VARCHAR(100) NOT NULL,
    last_name          VARCHAR(100) NOT NULL,
    specialty          VARCHAR(100) NOT NULL,
    department         VARCHAR(100),
    facility_name      VARCHAR(200),
    is_active          BOOLEAN DEFAULT TRUE,
    created_at         TIMESTAMPTZ DEFAULT now(),
    updated_at         TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- ENCOUNTERS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS encounters (
    encounter_id       UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id         UUID NOT NULL REFERENCES patients(patient_id),
    provider_id        UUID NOT NULL REFERENCES providers(provider_id),
    encounter_type     VARCHAR(50) NOT NULL,                  -- inpatient, outpatient, emergency, telehealth
    admission_date     TIMESTAMPTZ NOT NULL,
    discharge_date     TIMESTAMPTZ,
    facility_name      VARCHAR(200),
    chief_complaint    TEXT,
    disposition        VARCHAR(100),                          -- discharged, transferred, expired
    created_at         TIMESTAMPTZ DEFAULT now(),
    updated_at         TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- DIAGNOSES (ICD-10)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS diagnoses (
    diagnosis_id       UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    encounter_id       UUID NOT NULL REFERENCES encounters(encounter_id),
    patient_id         UUID NOT NULL REFERENCES patients(patient_id),
    icd10_code         VARCHAR(10) NOT NULL,
    description        TEXT NOT NULL,
    diagnosis_type     VARCHAR(20) NOT NULL,                  -- primary, secondary, admitting
    diagnosed_date     DATE NOT NULL,
    resolved_date      DATE,
    status             VARCHAR(20) DEFAULT 'active',          -- active, resolved, chronic
    created_at         TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- TREATMENTS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS treatments (
    treatment_id       UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    encounter_id       UUID NOT NULL REFERENCES encounters(encounter_id),
    patient_id         UUID NOT NULL REFERENCES patients(patient_id),
    provider_id        UUID NOT NULL REFERENCES providers(provider_id),
    treatment_type     VARCHAR(50) NOT NULL,                  -- medication, procedure, therapy, surgery
    treatment_name     VARCHAR(300) NOT NULL,
    cpt_code           VARCHAR(10),                           -- CPT / HCPCS code
    start_date         DATE NOT NULL,
    end_date           DATE,
    dosage             VARCHAR(100),
    frequency          VARCHAR(100),
    route              VARCHAR(50),                           -- oral, IV, subcutaneous, topical
    status             VARCHAR(20) DEFAULT 'active',          -- active, completed, discontinued
    notes              TEXT,
    created_at         TIMESTAMPTZ DEFAULT now(),
    updated_at         TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- MEDICATIONS (prescription-level detail)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medications (
    medication_id      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    treatment_id       UUID REFERENCES treatments(treatment_id),
    patient_id         UUID NOT NULL REFERENCES patients(patient_id),
    ndc_code           VARCHAR(15),                           -- National Drug Code
    drug_name          VARCHAR(300) NOT NULL,
    generic_name       VARCHAR(300),
    dosage_form        VARCHAR(100),                          -- tablet, capsule, injection
    strength           VARCHAR(100),
    quantity           INTEGER,
    refills_remaining  INTEGER DEFAULT 0,
    prescribed_date    DATE NOT NULL,
    expiration_date    DATE,
    prescriber_id      UUID REFERENCES providers(provider_id),
    created_at         TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- TREATMENT OUTCOMES
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS treatment_outcomes (
    outcome_id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    treatment_id       UUID NOT NULL REFERENCES treatments(treatment_id),
    patient_id         UUID NOT NULL REFERENCES patients(patient_id),
    outcome_type       VARCHAR(50) NOT NULL,                  -- remission, improvement, stable, progression, adverse
    outcome_measure    VARCHAR(200),                          -- RECIST, ECOG, HbA1c, etc.
    baseline_value     NUMERIC(10,2),
    result_value       NUMERIC(10,2),
    unit               VARCHAR(50),
    assessment_date    DATE NOT NULL,
    assessed_by        UUID REFERENCES providers(provider_id),
    notes              TEXT,
    created_at         TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- ADVERSE EVENTS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS adverse_events (
    event_id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    treatment_id       UUID NOT NULL REFERENCES treatments(treatment_id),
    patient_id         UUID NOT NULL REFERENCES patients(patient_id),
    event_type         VARCHAR(100) NOT NULL,                 -- nausea, neutropenia, rash, etc.
    severity           VARCHAR(20) NOT NULL,                  -- mild, moderate, severe, life-threatening
    ctcae_grade        INTEGER CHECK (ctcae_grade BETWEEN 1 AND 5),
    onset_date         DATE NOT NULL,
    resolution_date    DATE,
    action_taken       VARCHAR(200),                          -- dose reduced, discontinued, none
    outcome            VARCHAR(100),                          -- resolved, ongoing, fatal
    reported_by        UUID REFERENCES providers(provider_id),
    created_at         TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- LAB RESULTS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lab_results (
    lab_id             UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    encounter_id       UUID REFERENCES encounters(encounter_id),
    patient_id         UUID NOT NULL REFERENCES patients(patient_id),
    test_name          VARCHAR(200) NOT NULL,
    loinc_code         VARCHAR(20),                           -- LOINC code
    result_value       NUMERIC(12,4),
    result_text        VARCHAR(500),
    unit               VARCHAR(50),
    reference_low      NUMERIC(12,4),
    reference_high     NUMERIC(12,4),
    abnormal_flag      VARCHAR(5),                            -- H, L, HH, LL, N
    collected_date     TIMESTAMPTZ NOT NULL,
    resulted_date      TIMESTAMPTZ,
    ordering_provider  UUID REFERENCES providers(provider_id),
    created_at         TIMESTAMPTZ DEFAULT now()
);
