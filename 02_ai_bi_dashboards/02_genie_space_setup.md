# Genie Space Configuration — HLS Knowledge Graph

## Overview

This guide walks through setting up a **Databricks AI/BI Genie space** so that
clinicians, analysts, and executives can ask natural-language questions about
patients, treatments, outcomes, and adverse events — without writing SQL.

## Step 1 — Create the Genie Space

1. Open your Databricks workspace
2. Navigate to **AI/BI → Genie** in the left sidebar
3. Click **New Genie Space**
4. Name it: `HLS Knowledge Graph`
5. Select the warehouse / SQL warehouse to use for queries

## Step 2 — Add Tables

Add the Lakebase tables to the Genie space. If your Lakebase project is
registered as a Unity Catalog catalog, reference them with the catalog prefix.
Otherwise, connect via the Lakebase SQL warehouse.

| Table | Description |
|---|---|
| `patients` | Patient demographics and contact info |
| `providers` | Provider details, specialty, department |
| `encounters` | Patient-provider encounters |
| `diagnoses` | ICD-10 coded diagnoses |
| `treatments` | Treatment records with dosage and frequency |
| `medications` | Medication prescriptions |
| `treatment_outcomes` | Outcome assessments with baseline/result values |
| `adverse_events` | Adverse events with severity and CTCAE grades |
| `lab_results` | Lab test results with reference ranges |

## Step 3 — Configure Genie Instructions

Paste the following into the **Instructions** field of your Genie space:

```text
You are a clinical data assistant for a healthcare organization. You help
clinicians, analysts, and executives explore patient, treatment, and outcome data.

DOMAIN CONTEXT:
- Patients are identified by MRN (Medical Record Number)
- Diagnoses use ICD-10 codes (e.g., C50.911 = breast cancer, E11.65 = type 2 diabetes)
- Treatments include medications, procedures, surgeries, and therapies
- Outcomes are assessed using clinical measures: RECIST for tumors, HbA1c for diabetes,
  LVEF for heart failure, PSA for prostate cancer
- Adverse events are graded 1-5 using CTCAE (Common Terminology Criteria for Adverse Events)
- Severity levels: mild, moderate, severe, life-threatening

DATA MODEL:
- patients: One row per patient with demographics (MRN, DOB, gender, race, insurance, zip)
- providers: One row per provider with specialty and department
- encounters: One row per patient visit with admission/discharge dates
- diagnoses: One row per diagnosis with ICD-10 code and status
- treatments: One row per treatment with name, type, dosage, start/end dates
- medications: One row per medication prescription with NDC code
- treatment_outcomes: One row per outcome assessment with baseline and result values
- adverse_events: One row per AE with severity, CTCAE grade, onset/resolution dates
- lab_results: One row per lab test with result, reference range, abnormal flag

TERMINOLOGY:
- "Improvement rate" = percentage of outcomes that are type 'improvement'
- "Serious AE" = adverse events with CTCAE grade >= 3
- "Response rate" for cancer = RECIST improvement (target lesion shrinkage ≥ 30%)
- When asked about "side effects", query adverse_events
- When asked about "labs" or "bloodwork", query lab_results
- When asked about a specific patient, filter by MRN or name

QUERY PATTERNS:
- Patient age: EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth))
- Patient full name: first_name || ' ' || last_name
- Active patients: WHERE is_active = TRUE
- Join treatments to outcomes: ON treatment_id
- Join adverse events to treatments: ON treatment_id

DEFAULTS:
- Show patient counts unless asked for specific names
- Round percentages to one decimal place
- Sort results by relevance (highest count, most recent, etc.)
- When comparing treatments, include both efficacy and safety metrics
```

## Step 4 — Add Sample Questions

Add these as **sample questions** to help users get started:

1. "Which treatments have the highest improvement rate?"
2. "Show me all adverse events for chemotherapy patients"
3. "How many patients are being treated for breast cancer?"
4. "What is the HbA1c trend for patient MRN-100002?"
5. "Which providers treat the most patients?"
6. "Compare adverse event rates between Pembrolizumab and Doxorubicin"
7. "List all patients over 70 with active cancer diagnoses"
8. "What percentage of treatments have severe adverse events?"
9. "Show abnormal lab results from this month"
10. "Which diagnoses have the most patients?"

## Step 5 — Set Permissions

1. Click **Share** on the Genie space
2. Add user groups:
   - **Clinicians**: Can Use
   - **Data Analysts**: Can Edit
   - **Executives**: Can Use
3. Genie inherits Unity Catalog permissions — users only see data they have access to

## Step 6 — Verify

Ask a test question like:

> "Which treatments have had the best outcomes for cancer patients?"

Genie should:
1. Identify the relevant tables (`treatments`, `treatment_outcomes`, `diagnoses`)
2. Filter for cancer-related diagnoses (ICD-10 codes starting with C)
3. Return a ranked list with improvement rates and patient counts
