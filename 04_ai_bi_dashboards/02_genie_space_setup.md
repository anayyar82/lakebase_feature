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

Add the following Unity Catalog tables/views to the Genie space:

| Table / View | Description |
|---|---|
| `hls_lakehouse.knowledge_graph.gold_patient_360` | Patient demographics + summary stats |
| `hls_lakehouse.knowledge_graph.gold_treatment_efficacy` | Treatment effectiveness metrics |
| `hls_lakehouse.knowledge_graph.gold_adverse_events` | Adverse event details |
| `hls_lakehouse.knowledge_graph.gold_outcomes_timeline` | Longitudinal outcome tracking |
| `hls_lakehouse.knowledge_graph.gold_provider_activity` | Provider workload and panel |
| `hls_lakehouse.knowledge_graph.gold_diagnosis_cohorts` | Diagnosis cohort demographics |
| `hls_lakehouse.knowledge_graph.gold_lab_trends` | Lab result trends with change tracking |
| `hls_lakehouse.knowledge_graph.treatments` | Raw treatment records |
| `hls_lakehouse.knowledge_graph.patients` | Raw patient records |

## Step 3 — Configure Genie Instructions

Paste the following into the **Instructions** field of your Genie space. These
instructions teach Genie about the domain, data model, and expected question
patterns.

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
- gold_patient_360: One row per patient with demographics and summary counts
- gold_treatment_efficacy: One row per treatment with improvement rates and AE counts
- gold_adverse_events: One row per adverse event with patient and treatment context
- gold_outcomes_timeline: One row per outcome assessment with baseline/result values
- gold_provider_activity: One row per provider with encounter and treatment counts
- gold_diagnosis_cohorts: One row per patient-diagnosis pair with demographics
- gold_lab_trends: One row per lab result with previous value and change

TERMINOLOGY:
- "Improvement rate" = percentage of outcomes that are type 'improvement'
- "Serious AE" = adverse events with CTCAE grade >= 3
- "Response rate" for cancer = RECIST improvement (target lesion shrinkage ≥ 30%)
- When asked about "efficacy", use gold_treatment_efficacy
- When asked about "side effects", use gold_adverse_events
- When asked about "labs" or "bloodwork", use gold_lab_trends
- When asked about a specific patient, use gold_patient_360 or filter by MRN

DEFAULTS:
- Show patient counts unless asked for specific names
- Round percentages to one decimal place
- Sort results by relevance (highest count, most recent, etc.)
- When comparing treatments, include both efficacy and safety metrics
```

## Step 4 — Add Sample Questions

Add these as **sample questions** in the Genie space to help users get started:

1. "Which treatments have the highest improvement rate?"
2. "Show me all adverse events for chemotherapy patients"
3. "How many patients are being treated for breast cancer?"
4. "What is the HbA1c trend for patient MRN-100002?"
5. "Which providers treat the most patients?"
6. "Compare adverse event rates between Pembrolizumab and Doxorubicin"
7. "List all patients over 70 with active cancer diagnoses"
8. "What percentage of treatments have severe adverse events?"
9. "Show the treatment pathway for patient MRN-100001"
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
1. Identify the relevant table (`gold_treatment_efficacy`)
2. Filter for cancer-related treatments
3. Return a ranked list with improvement rates and adverse event counts
