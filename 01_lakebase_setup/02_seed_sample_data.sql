-- =============================================================================
-- HLS Knowledge Graph — Sample Data
-- =============================================================================
-- Realistic synthetic healthcare data covering oncology, cardiology, and
-- endocrinology use cases. All data is fictional.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- PROVIDERS
-- ---------------------------------------------------------------------------
INSERT INTO providers (provider_id, npi, first_name, last_name, specialty, department, facility_name) VALUES
    ('a1b2c3d4-0001-4000-8000-000000000001', '1234567890', 'Sarah',   'Chen',      'Medical Oncology',   'Cancer Center',       'Lakeside Medical Center'),
    ('a1b2c3d4-0001-4000-8000-000000000002', '1234567891', 'James',   'Okonkwo',   'Cardiology',         'Heart & Vascular',    'Lakeside Medical Center'),
    ('a1b2c3d4-0001-4000-8000-000000000003', '1234567892', 'Maria',   'Rodriguez',  'Endocrinology',      'Diabetes Center',     'Lakeside Medical Center'),
    ('a1b2c3d4-0001-4000-8000-000000000004', '1234567893', 'David',   'Kim',        'Pulmonology',        'Respiratory Medicine','Lakeside Medical Center'),
    ('a1b2c3d4-0001-4000-8000-000000000005', '1234567894', 'Priya',   'Sharma',     'Radiation Oncology', 'Cancer Center',       'Lakeside Medical Center'),
    ('a1b2c3d4-0001-4000-8000-000000000006', '1234567895', 'Robert',  'Williams',   'General Surgery',    'Surgical Services',   'Lakeside Medical Center'),
    ('a1b2c3d4-0001-4000-8000-000000000007', '1234567896', 'Angela',  'Thompson',   'Neurology',          'Neurosciences',       'Lakeside Medical Center'),
    ('a1b2c3d4-0001-4000-8000-000000000008', '1234567897', 'Michael', 'Patel',      'Hematology',         'Cancer Center',       'Lakeside Medical Center');

-- ---------------------------------------------------------------------------
-- PATIENTS
-- ---------------------------------------------------------------------------
INSERT INTO patients (patient_id, mrn, first_name, last_name, date_of_birth, gender, race, ethnicity, insurance_type, zip_code) VALUES
    ('b2c3d4e5-0001-4000-8000-000000000001', 'MRN-100001', 'Eleanor',  'Mitchell',   '1958-03-14', 'Female', 'White',                    'Not Hispanic',     'Medicare',    '60601'),
    ('b2c3d4e5-0001-4000-8000-000000000002', 'MRN-100002', 'Marcus',   'Johnson',    '1972-07-22', 'Male',   'Black or African American','Not Hispanic',     'Commercial',  '60614'),
    ('b2c3d4e5-0001-4000-8000-000000000003', 'MRN-100003', 'Aisha',    'Rahman',     '1965-11-09', 'Female', 'Asian',                    'Not Hispanic',     'Medicare',    '60657'),
    ('b2c3d4e5-0001-4000-8000-000000000004', 'MRN-100004', 'Carlos',   'Gutierrez',  '1980-01-30', 'Male',   'White',                    'Hispanic/Latino',  'Commercial',  '60622'),
    ('b2c3d4e5-0001-4000-8000-000000000005', 'MRN-100005', 'Dorothy',  'Nguyen',     '1945-06-18', 'Female', 'Asian',                    'Not Hispanic',     'Medicare',    '60640'),
    ('b2c3d4e5-0001-4000-8000-000000000006', 'MRN-100006', 'William',  'Foster',     '1955-09-02', 'Male',   'White',                    'Not Hispanic',     'Medicare',    '60618'),
    ('b2c3d4e5-0001-4000-8000-000000000007', 'MRN-100007', 'Fatima',   'Al-Hassan',  '1988-04-11', 'Female', 'Other',                    'Not Hispanic',     'Commercial',  '60647'),
    ('b2c3d4e5-0001-4000-8000-000000000008', 'MRN-100008', 'Thomas',   'O''Brien',   '1970-12-25', 'Male',   'White',                    'Not Hispanic',     'Commercial',  '60654'),
    ('b2c3d4e5-0001-4000-8000-000000000009', 'MRN-100009', 'Lakshmi',  'Venkatesh',  '1962-08-07', 'Female', 'Asian',                    'Not Hispanic',     'Medicaid',    '60609'),
    ('b2c3d4e5-0001-4000-8000-000000000010', 'MRN-100010', 'Jerome',   'Washington', '1950-02-19', 'Male',   'Black or African American','Not Hispanic',     'Medicare',    '60621');

-- ---------------------------------------------------------------------------
-- ENCOUNTERS
-- ---------------------------------------------------------------------------

-- Eleanor Mitchell — Breast cancer journey
INSERT INTO encounters (encounter_id, patient_id, provider_id, encounter_type, admission_date, discharge_date, facility_name, chief_complaint, disposition) VALUES
    ('c3d4e5f6-0001-4000-8000-000000000001', 'b2c3d4e5-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'outpatient',  '2025-01-15 09:00:00-06', NULL,                          'Lakeside Medical Center', 'Abnormal mammogram findings',          'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000002', 'b2c3d4e5-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'outpatient',  '2025-02-10 10:00:00-06', NULL,                          'Lakeside Medical Center', 'Biopsy results review — Stage II IDC', 'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000003', 'b2c3d4e5-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000006', 'inpatient',   '2025-03-05 06:30:00-06', '2025-03-08 14:00:00-06',      'Lakeside Medical Center', 'Lumpectomy with sentinel node biopsy', 'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'outpatient',  '2025-04-01 08:30:00-05', NULL,                          'Lakeside Medical Center', 'Chemotherapy cycle 1 — AC regimen',    'discharged');

-- Marcus Johnson — Type 2 diabetes management
INSERT INTO encounters (encounter_id, patient_id, provider_id, encounter_type, admission_date, discharge_date, facility_name, chief_complaint, disposition) VALUES
    ('c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000003', 'outpatient',  '2025-01-08 14:00:00-06', NULL,                          'Lakeside Medical Center', 'Elevated HbA1c at 9.2%',               'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000006', 'b2c3d4e5-0001-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000003', 'outpatient',  '2025-04-10 14:00:00-05', NULL,                          'Lakeside Medical Center', '3-month HbA1c recheck',                'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000007', 'b2c3d4e5-0001-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000003', 'outpatient',  '2025-07-15 14:00:00-05', NULL,                          'Lakeside Medical Center', '6-month diabetes follow-up',           'discharged');

-- Aisha Rahman — NSCLC treatment
INSERT INTO encounters (encounter_id, patient_id, provider_id, encounter_type, admission_date, discharge_date, facility_name, chief_complaint, disposition) VALUES
    ('c3d4e5f6-0001-4000-8000-000000000008', 'b2c3d4e5-0001-4000-8000-000000000003', 'a1b2c3d4-0001-4000-8000-000000000004', 'outpatient',  '2025-02-01 11:00:00-06', NULL,                          'Lakeside Medical Center', 'Persistent cough, CT findings',        'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000009', 'b2c3d4e5-0001-4000-8000-000000000003', 'a1b2c3d4-0001-4000-8000-000000000001', 'outpatient',  '2025-03-01 09:00:00-06', NULL,                          'Lakeside Medical Center', 'Stage IIIA NSCLC — treatment planning', 'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000010', 'b2c3d4e5-0001-4000-8000-000000000003', 'a1b2c3d4-0001-4000-8000-000000000001', 'outpatient',  '2025-03-20 08:00:00-05', NULL,                          'Lakeside Medical Center', 'Immunotherapy cycle 1 — Pembrolizumab','discharged');

-- William Foster — CHF management
INSERT INTO encounters (encounter_id, patient_id, provider_id, encounter_type, admission_date, discharge_date, facility_name, chief_complaint, disposition) VALUES
    ('c3d4e5f6-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', 'a1b2c3d4-0001-4000-8000-000000000002', 'emergency',   '2025-01-20 22:30:00-06', '2025-01-25 11:00:00-06',      'Lakeside Medical Center', 'Acute dyspnea, peripheral edema',      'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000012', 'b2c3d4e5-0001-4000-8000-000000000006', 'a1b2c3d4-0001-4000-8000-000000000002', 'outpatient',  '2025-02-15 10:00:00-06', NULL,                          'Lakeside Medical Center', 'Post-discharge CHF follow-up',         'discharged');

-- Jerome Washington — Prostate cancer
INSERT INTO encounters (encounter_id, patient_id, provider_id, encounter_type, admission_date, discharge_date, facility_name, chief_complaint, disposition) VALUES
    ('c3d4e5f6-0001-4000-8000-000000000013', 'b2c3d4e5-0001-4000-8000-000000000010', 'a1b2c3d4-0001-4000-8000-000000000001', 'outpatient',  '2025-01-22 09:30:00-06', NULL,                          'Lakeside Medical Center', 'Elevated PSA, Gleason 7',              'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000014', 'b2c3d4e5-0001-4000-8000-000000000010', 'a1b2c3d4-0001-4000-8000-000000000005', 'outpatient',  '2025-02-20 08:00:00-06', NULL,                          'Lakeside Medical Center', 'Radiation therapy planning',            'discharged'),
    ('c3d4e5f6-0001-4000-8000-000000000015', 'b2c3d4e5-0001-4000-8000-000000000010', 'a1b2c3d4-0001-4000-8000-000000000005', 'outpatient',  '2025-03-10 07:30:00-05', NULL,                          'Lakeside Medical Center', 'Radiation therapy session 1',           'discharged');

-- ---------------------------------------------------------------------------
-- DIAGNOSES
-- ---------------------------------------------------------------------------
INSERT INTO diagnoses (encounter_id, patient_id, icd10_code, description, diagnosis_type, diagnosed_date, status) VALUES
    -- Eleanor — Breast cancer
    ('c3d4e5f6-0001-4000-8000-000000000002', 'b2c3d4e5-0001-4000-8000-000000000001', 'C50.911',  'Malignant neoplasm of unspecified site of right female breast', 'primary',   '2025-02-10', 'active'),
    ('c3d4e5f6-0001-4000-8000-000000000002', 'b2c3d4e5-0001-4000-8000-000000000001', 'E11.9',    'Type 2 diabetes mellitus without complications',               'secondary', '2025-02-10', 'chronic'),
    -- Marcus — Diabetes
    ('c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'E11.65',   'Type 2 diabetes mellitus with hyperglycemia',                  'primary',   '2025-01-08', 'active'),
    ('c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'I10',      'Essential hypertension',                                        'secondary', '2025-01-08', 'chronic'),
    ('c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'E78.5',    'Dyslipidemia, unspecified',                                     'secondary', '2025-01-08', 'chronic'),
    -- Aisha — Lung cancer
    ('c3d4e5f6-0001-4000-8000-000000000009', 'b2c3d4e5-0001-4000-8000-000000000003', 'C34.90',   'Malignant neoplasm of unspecified part of unspecified bronchus or lung', 'primary', '2025-03-01', 'active'),
    -- William — CHF
    ('c3d4e5f6-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', 'I50.9',    'Heart failure, unspecified',                                     'primary',   '2025-01-20', 'active'),
    ('c3d4e5f6-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', 'I10',      'Essential hypertension',                                        'secondary', '2025-01-20', 'chronic'),
    -- Jerome — Prostate cancer
    ('c3d4e5f6-0001-4000-8000-000000000013', 'b2c3d4e5-0001-4000-8000-000000000010', 'C61',      'Malignant neoplasm of prostate',                                'primary',   '2025-01-22', 'active');

-- ---------------------------------------------------------------------------
-- TREATMENTS
-- ---------------------------------------------------------------------------
INSERT INTO treatments (treatment_id, encounter_id, patient_id, provider_id, treatment_type, treatment_name, cpt_code, start_date, end_date, dosage, frequency, route, status) VALUES
    -- Eleanor — Surgery + Chemo
    ('d4e5f6a7-0001-4000-8000-000000000001', 'c3d4e5f6-0001-4000-8000-000000000003', 'b2c3d4e5-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000006', 'surgery',    'Lumpectomy with sentinel lymph node biopsy',  '19301', '2025-03-05', '2025-03-05', NULL,                  'once',         NULL,            'completed'),
    ('d4e5f6a7-0001-4000-8000-000000000002', 'c3d4e5f6-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'medication', 'Doxorubicin + Cyclophosphamide (AC regimen)', '96413', '2025-04-01', '2025-07-15', '60mg/m² + 600mg/m²', 'every 21 days','IV',             'active'),
    ('d4e5f6a7-0001-4000-8000-000000000003', 'c3d4e5f6-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'medication', 'Ondansetron (anti-emetic)',                    NULL,    '2025-04-01', NULL,         '8mg',                'PRN',          'oral',           'active'),

    -- Marcus — Diabetes medications
    ('d4e5f6a7-0001-4000-8000-000000000004', 'c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000003', 'medication', 'Metformin',                                   NULL,    '2025-01-08', NULL,         '1000mg',             'twice daily',  'oral',           'active'),
    ('d4e5f6a7-0001-4000-8000-000000000005', 'c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000003', 'medication', 'Semaglutide (Ozempic)',                        NULL,    '2025-01-08', NULL,         '0.5mg',              'weekly',       'subcutaneous',   'active'),
    ('d4e5f6a7-0001-4000-8000-000000000006', 'c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000003', 'medication', 'Lisinopril',                                  NULL,    '2025-01-08', NULL,         '20mg',               'once daily',   'oral',           'active'),
    ('d4e5f6a7-0001-4000-8000-000000000007', 'c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000003', 'medication', 'Atorvastatin',                                NULL,    '2025-01-08', NULL,         '40mg',               'once daily',   'oral',           'active'),

    -- Aisha — Immunotherapy
    ('d4e5f6a7-0001-4000-8000-000000000008', 'c3d4e5f6-0001-4000-8000-000000000010', 'b2c3d4e5-0001-4000-8000-000000000003', 'a1b2c3d4-0001-4000-8000-000000000001', 'medication', 'Pembrolizumab (Keytruda)',                    '96413', '2025-03-20', NULL,         '200mg',              'every 21 days','IV',             'active'),
    ('d4e5f6a7-0001-4000-8000-000000000009', 'c3d4e5f6-0001-4000-8000-000000000010', 'b2c3d4e5-0001-4000-8000-000000000003', 'a1b2c3d4-0001-4000-8000-000000000001', 'medication', 'Carboplatin + Pemetrexed',                    '96413', '2025-03-20', NULL,         'AUC 5 + 500mg/m²',  'every 21 days','IV',             'active'),

    -- William — CHF medications
    ('d4e5f6a7-0001-4000-8000-000000000010', 'c3d4e5f6-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', 'a1b2c3d4-0001-4000-8000-000000000002', 'medication', 'Sacubitril/Valsartan (Entresto)',              NULL,    '2025-01-21', NULL,         '49/51mg',            'twice daily',  'oral',           'active'),
    ('d4e5f6a7-0001-4000-8000-000000000011', 'c3d4e5f6-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', 'a1b2c3d4-0001-4000-8000-000000000002', 'medication', 'Furosemide',                                  NULL,    '2025-01-21', NULL,         '40mg',               'once daily',   'oral',           'active'),
    ('d4e5f6a7-0001-4000-8000-000000000012', 'c3d4e5f6-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', 'a1b2c3d4-0001-4000-8000-000000000002', 'medication', 'Carvedilol',                                  NULL,    '2025-01-21', NULL,         '12.5mg',             'twice daily',  'oral',           'active'),
    ('d4e5f6a7-0001-4000-8000-000000000013', 'c3d4e5f6-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', 'a1b2c3d4-0001-4000-8000-000000000002', 'medication', 'Spironolactone',                              NULL,    '2025-01-21', NULL,         '25mg',               'once daily',   'oral',           'active'),

    -- Jerome — Radiation + ADT
    ('d4e5f6a7-0001-4000-8000-000000000014', 'c3d4e5f6-0001-4000-8000-000000000014', 'b2c3d4e5-0001-4000-8000-000000000010', 'a1b2c3d4-0001-4000-8000-000000000005', 'procedure',  'External beam radiation therapy (EBRT)',       '77385', '2025-03-10', '2025-05-01', '2 Gy/fraction',     'daily x 39',   NULL,            'active'),
    ('d4e5f6a7-0001-4000-8000-000000000015', 'c3d4e5f6-0001-4000-8000-000000000014', 'b2c3d4e5-0001-4000-8000-000000000010', 'a1b2c3d4-0001-4000-8000-000000000001', 'medication', 'Leuprolide (Lupron) — ADT',                   NULL,    '2025-02-20', NULL,         '22.5mg',             'every 3 months','subcutaneous',  'active');

-- ---------------------------------------------------------------------------
-- TREATMENT OUTCOMES
-- ---------------------------------------------------------------------------
INSERT INTO treatment_outcomes (treatment_id, patient_id, outcome_type, outcome_measure, baseline_value, result_value, unit, assessment_date, assessed_by) VALUES
    -- Eleanor — Post-surgery pathology
    ('d4e5f6a7-0001-4000-8000-000000000001', 'b2c3d4e5-0001-4000-8000-000000000001', 'improvement', 'Surgical margins',      NULL,  0,     'mm (closest margin)', '2025-03-12', 'a1b2c3d4-0001-4000-8000-000000000006'),
    ('d4e5f6a7-0001-4000-8000-000000000001', 'b2c3d4e5-0001-4000-8000-000000000001', 'stable',      'Sentinel node status',  NULL,  0,     'positive nodes',      '2025-03-12', 'a1b2c3d4-0001-4000-8000-000000000006'),

    -- Marcus — HbA1c improvement
    ('d4e5f6a7-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000002', 'improvement', 'HbA1c',                 9.20,  7.80,  '%',                   '2025-04-10', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('d4e5f6a7-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000002', 'improvement', 'HbA1c',                 7.80,  6.90,  '%',                   '2025-07-15', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('d4e5f6a7-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'improvement', 'Body weight',           105.0, 98.5,  'kg',                  '2025-07-15', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('d4e5f6a7-0001-4000-8000-000000000006', 'b2c3d4e5-0001-4000-8000-000000000002', 'improvement', 'Blood pressure',        152.0, 128.0, 'mmHg systolic',       '2025-07-15', 'a1b2c3d4-0001-4000-8000-000000000003'),

    -- Aisha — Tumor response to immunotherapy
    ('d4e5f6a7-0001-4000-8000-000000000008', 'b2c3d4e5-0001-4000-8000-000000000003', 'improvement', 'RECIST 1.1 (target lesion)', 45.0, 32.0, 'mm', '2025-05-15', 'a1b2c3d4-0001-4000-8000-000000000001'),

    -- William — Ejection fraction improvement
    ('d4e5f6a7-0001-4000-8000-000000000010', 'b2c3d4e5-0001-4000-8000-000000000006', 'improvement', 'LVEF (echocardiogram)', 25.0,  35.0,  '%',                   '2025-04-15', 'a1b2c3d4-0001-4000-8000-000000000002'),
    ('d4e5f6a7-0001-4000-8000-000000000010', 'b2c3d4e5-0001-4000-8000-000000000006', 'improvement', 'BNP',                   1850.0, 420.0,'pg/mL',               '2025-04-15', 'a1b2c3d4-0001-4000-8000-000000000002'),

    -- Jerome — PSA response
    ('d4e5f6a7-0001-4000-8000-000000000015', 'b2c3d4e5-0001-4000-8000-000000000010', 'improvement', 'PSA',                   12.5,  4.2,   'ng/mL',               '2025-05-20', 'a1b2c3d4-0001-4000-8000-000000000001');

-- ---------------------------------------------------------------------------
-- ADVERSE EVENTS
-- ---------------------------------------------------------------------------
INSERT INTO adverse_events (treatment_id, patient_id, event_type, severity, ctcae_grade, onset_date, resolution_date, action_taken, outcome, reported_by) VALUES
    -- Eleanor — Chemo side effects
    ('d4e5f6a7-0001-4000-8000-000000000002', 'b2c3d4e5-0001-4000-8000-000000000001', 'Nausea',                  'moderate',         2, '2025-04-02', '2025-04-05', 'Anti-emetic prescribed',     'resolved',  'a1b2c3d4-0001-4000-8000-000000000001'),
    ('d4e5f6a7-0001-4000-8000-000000000002', 'b2c3d4e5-0001-4000-8000-000000000001', 'Neutropenia',             'severe',           3, '2025-04-12', '2025-04-20', 'G-CSF administered',         'resolved',  'a1b2c3d4-0001-4000-8000-000000000001'),
    ('d4e5f6a7-0001-4000-8000-000000000002', 'b2c3d4e5-0001-4000-8000-000000000001', 'Fatigue',                 'moderate',         2, '2025-04-03', NULL,          'Dose maintained',            'ongoing',   'a1b2c3d4-0001-4000-8000-000000000001'),

    -- Marcus — GI side effects from Metformin
    ('d4e5f6a7-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000002', 'Diarrhea',                'mild',             1, '2025-01-12', '2025-01-25', 'Switched to extended release','resolved',  'a1b2c3d4-0001-4000-8000-000000000003'),
    ('d4e5f6a7-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'Injection site reaction', 'mild',             1, '2025-01-15', '2025-01-16', 'Site rotation counseling',    'resolved',  'a1b2c3d4-0001-4000-8000-000000000003'),

    -- Aisha — Immunotherapy side effects
    ('d4e5f6a7-0001-4000-8000-000000000008', 'b2c3d4e5-0001-4000-8000-000000000003', 'Hypothyroidism',          'moderate',         2, '2025-05-01', NULL,          'Levothyroxine started',      'ongoing',   'a1b2c3d4-0001-4000-8000-000000000001'),
    ('d4e5f6a7-0001-4000-8000-000000000008', 'b2c3d4e5-0001-4000-8000-000000000003', 'Rash (maculopapular)',    'mild',             1, '2025-04-10', '2025-04-18', 'Topical corticosteroid',     'resolved',  'a1b2c3d4-0001-4000-8000-000000000001'),

    -- Jerome — Radiation side effects
    ('d4e5f6a7-0001-4000-8000-000000000014', 'b2c3d4e5-0001-4000-8000-000000000010', 'Urinary frequency',       'mild',             1, '2025-03-25', NULL,          'Alpha-blocker prescribed',   'ongoing',   'a1b2c3d4-0001-4000-8000-000000000005'),
    ('d4e5f6a7-0001-4000-8000-000000000014', 'b2c3d4e5-0001-4000-8000-000000000010', 'Fatigue',                 'mild',             1, '2025-04-01', NULL,          'Activity modification',      'ongoing',   'a1b2c3d4-0001-4000-8000-000000000005');

-- ---------------------------------------------------------------------------
-- LAB RESULTS
-- ---------------------------------------------------------------------------
INSERT INTO lab_results (encounter_id, patient_id, test_name, loinc_code, result_value, unit, reference_low, reference_high, abnormal_flag, collected_date, resulted_date, ordering_provider) VALUES
    -- Eleanor — Pre-chemo labs
    ('c3d4e5f6-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000001', 'WBC',               '6690-2',  6.8,    '10^3/uL', 4.5,    11.0,   'N',  '2025-03-30 07:00:00-05', '2025-03-30 14:00:00-05', 'a1b2c3d4-0001-4000-8000-000000000001'),
    ('c3d4e5f6-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000001', 'Hemoglobin',        '718-7',   12.1,   'g/dL',    12.0,   16.0,   'N',  '2025-03-30 07:00:00-05', '2025-03-30 14:00:00-05', 'a1b2c3d4-0001-4000-8000-000000000001'),
    ('c3d4e5f6-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000001', 'Platelet count',    '777-3',   210.0,  '10^3/uL', 150.0,  400.0,  'N',  '2025-03-30 07:00:00-05', '2025-03-30 14:00:00-05', 'a1b2c3d4-0001-4000-8000-000000000001'),
    ('c3d4e5f6-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000001', 'Creatinine',        '2160-0',  0.9,    'mg/dL',   0.6,    1.2,    'N',  '2025-03-30 07:00:00-05', '2025-03-30 14:00:00-05', 'a1b2c3d4-0001-4000-8000-000000000001'),

    -- Marcus — Metabolic panel
    ('c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'HbA1c',             '4548-4',  9.2,    '%',       4.0,    5.6,    'HH', '2025-01-08 08:00:00-06', '2025-01-08 16:00:00-06', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'Fasting glucose',   '1558-6',  186.0,  'mg/dL',   70.0,   100.0,  'HH', '2025-01-08 08:00:00-06', '2025-01-08 16:00:00-06', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'LDL Cholesterol',   '2089-1',  162.0,  'mg/dL',   0.0,    100.0,  'H',  '2025-01-08 08:00:00-06', '2025-01-08 16:00:00-06', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('c3d4e5f6-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', 'Creatinine',        '2160-0',  1.1,    'mg/dL',   0.7,    1.3,    'N',  '2025-01-08 08:00:00-06', '2025-01-08 16:00:00-06', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('c3d4e5f6-0001-4000-8000-000000000006', 'b2c3d4e5-0001-4000-8000-000000000002', 'HbA1c',             '4548-4',  7.8,    '%',       4.0,    5.6,    'H',  '2025-04-10 08:00:00-05', '2025-04-10 16:00:00-05', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('c3d4e5f6-0001-4000-8000-000000000007', 'b2c3d4e5-0001-4000-8000-000000000002', 'HbA1c',             '4548-4',  6.9,    '%',       4.0,    5.6,    'H',  '2025-07-15 08:00:00-05', '2025-07-15 16:00:00-05', 'a1b2c3d4-0001-4000-8000-000000000003'),

    -- William — Cardiac labs
    ('c3d4e5f6-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', 'BNP',               '42637-9', 1850.0, 'pg/mL',   0.0,    100.0,  'HH', '2025-01-20 23:00:00-06', '2025-01-21 02:00:00-06', 'a1b2c3d4-0001-4000-8000-000000000002'),
    ('c3d4e5f6-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', 'Troponin I',        '10839-9', 0.04,   'ng/mL',   0.0,    0.04,   'N',  '2025-01-20 23:00:00-06', '2025-01-21 02:00:00-06', 'a1b2c3d4-0001-4000-8000-000000000002'),
    ('c3d4e5f6-0001-4000-8000-000000000012', 'b2c3d4e5-0001-4000-8000-000000000006', 'BNP',               '42637-9', 420.0,  'pg/mL',   0.0,    100.0,  'H',  '2025-02-15 08:00:00-06', '2025-02-15 14:00:00-06', 'a1b2c3d4-0001-4000-8000-000000000002'),

    -- Jerome — PSA
    ('c3d4e5f6-0001-4000-8000-000000000013', 'b2c3d4e5-0001-4000-8000-000000000010', 'PSA',               '2857-1',  12.5,   'ng/mL',   0.0,    4.0,    'HH', '2025-01-22 07:30:00-06', '2025-01-22 14:00:00-06', 'a1b2c3d4-0001-4000-8000-000000000001');

-- ---------------------------------------------------------------------------
-- MEDICATIONS (prescription detail)
-- ---------------------------------------------------------------------------
INSERT INTO medications (treatment_id, patient_id, ndc_code, drug_name, generic_name, dosage_form, strength, quantity, refills_remaining, prescribed_date, prescriber_id) VALUES
    ('d4e5f6a7-0001-4000-8000-000000000004', 'b2c3d4e5-0001-4000-8000-000000000002', '00378-0234-01', 'Metformin HCl ER', 'Metformin',         'tablet',    '1000mg', 60,  5, '2025-01-08', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('d4e5f6a7-0001-4000-8000-000000000005', 'b2c3d4e5-0001-4000-8000-000000000002', '00169-4132-12', 'Ozempic',          'Semaglutide',       'injection', '0.5mg',  1,   2, '2025-01-08', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('d4e5f6a7-0001-4000-8000-000000000006', 'b2c3d4e5-0001-4000-8000-000000000002', '00093-1040-01', 'Lisinopril',       'Lisinopril',        'tablet',    '20mg',   30,  5, '2025-01-08', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('d4e5f6a7-0001-4000-8000-000000000007', 'b2c3d4e5-0001-4000-8000-000000000002', '00071-0155-23', 'Lipitor',          'Atorvastatin',      'tablet',    '40mg',   30,  5, '2025-01-08', 'a1b2c3d4-0001-4000-8000-000000000003'),
    ('d4e5f6a7-0001-4000-8000-000000000010', 'b2c3d4e5-0001-4000-8000-000000000006', '00078-0696-20', 'Entresto',         'Sacubitril/Valsartan','tablet',  '49/51mg',60,  5, '2025-01-21', 'a1b2c3d4-0001-4000-8000-000000000002'),
    ('d4e5f6a7-0001-4000-8000-000000000011', 'b2c3d4e5-0001-4000-8000-000000000006', '00054-4299-25', 'Furosemide',       'Furosemide',        'tablet',    '40mg',   30,  5, '2025-01-21', 'a1b2c3d4-0001-4000-8000-000000000002'),
    ('d4e5f6a7-0001-4000-8000-000000000012', 'b2c3d4e5-0001-4000-8000-000000000006', '00007-4141-20', 'Coreg',            'Carvedilol',        'tablet',    '12.5mg', 60,  5, '2025-01-21', 'a1b2c3d4-0001-4000-8000-000000000002');
