# Sample Genie Questions — HLS Knowledge Graph

Use these questions in the Databricks AI/BI Genie space. They are organized by
persona and complexity level.

---

## Clinician Questions

### Basic
- "How many active patients do we have?"
- "Show me Eleanor Mitchell's treatment history"
- "What medications is patient MRN-100002 currently on?"
- "List all patients with breast cancer"

### Intermediate
- "What is the HbA1c trend for Marcus Johnson over the last 6 months?"
- "Show adverse events for patients on Pembrolizumab"
- "Which patients have abnormal lab results this month?"
- "Compare outcomes for Entresto vs standard CHF therapy"

### Advanced
- "Which treatments for stage III lung cancer had the best RECIST response?"
- "Show me patients who had dose reductions due to adverse events — what were their outcomes?"
- "Are there patients with both diabetes and cancer? What treatments overlap?"
- "What is the average time from diagnosis to first treatment for breast cancer patients?"

---

## Analyst Questions

### Population Health
- "Break down our patient population by age group and insurance type"
- "Which ZIP codes have the most patients?"
- "What is the gender distribution across cancer diagnoses?"
- "Show diagnosis cohort sizes over time"

### Treatment Analytics
- "Rank all treatments by improvement rate"
- "Which treatments have serious adverse event rates above 20%?"
- "What is the average treatment duration by treatment type?"
- "Show me the treatment mix — how many patients are on medication vs procedure vs therapy?"

### Safety Monitoring
- "List all CTCAE grade 3+ adverse events in the last 90 days"
- "Which drugs have the highest adverse event rate per patient?"
- "What actions were taken for severe adverse events?"
- "Show the distribution of adverse events by severity"

---

## Executive Questions

### KPIs
- "What are our total patient, encounter, and treatment counts?"
- "What percentage of treatments resulted in improvement?"
- "How many providers are actively treating patients?"
- "What is our average adverse event rate across all treatments?"

### Benchmarking
- "Compare treatment efficacy across oncology, cardiology, and endocrinology"
- "Which department has the highest encounter volume?"
- "Show provider workload — encounters per provider by specialty"

### Risk
- "Are any treatments trending toward higher adverse event rates?"
- "Which patients have the most encounters in the last 6 months?"
- "Show readmission rates by diagnosis"

---

## Graph Traversal Questions

These questions leverage the SQL knowledge graph views and recursive CTEs:

- "Find patients with similar treatment profiles to MRN-100001"
- "What are the most common comorbidity patterns?"
- "Which treatment pathways lead to the best outcomes for lung cancer?"
- "Show the provider collaboration network for the Cancer Center"
- "Identify treatment sequences that correlate with adverse events"
- "Trace the full journey from diagnosis to outcome for cancer patients"
- "Which providers share the most patients across specialties?"
