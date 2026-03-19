"""Patient 360 — Comprehensive patient profile search and detail view."""

import streamlit as st
from db import run_query_df


def render():
    st.title("Patient 360")
    st.markdown("Search for a patient to view their complete clinical profile.")

    # ── Search ───────────────────────────────────────────────────────────────

    search = st.text_input("Search by name or MRN", placeholder="e.g. Smith or MRN-001")

    if not search:
        st.info("Enter a patient name or MRN above to get started.")
        return

    patients = run_query_df("""
        SELECT patient_id, mrn,
               first_name || ' ' || last_name AS patient_name,
               date_of_birth, gender, insurance_type
        FROM patients
        WHERE is_active = TRUE
          AND (
              LOWER(first_name) LIKE LOWER(%s)
              OR LOWER(last_name) LIKE LOWER(%s)
              OR LOWER(mrn) LIKE LOWER(%s)
          )
        ORDER BY last_name, first_name
        LIMIT 50
    """, (f"%{search}%", f"%{search}%", f"%{search}%"))

    if patients.empty:
        st.warning("No patients found.")
        return

    st.subheader(f"Found {len(patients)} patient(s)")
    selected_idx = st.selectbox(
        "Select a patient",
        range(len(patients)),
        format_func=lambda i: f"{patients.iloc[i]['mrn']} — {patients.iloc[i]['patient_name']}",
    )
    pid = int(patients.iloc[selected_idx]["patient_id"])

    st.markdown("---")

    # ── Demographics ─────────────────────────────────────────────────────────

    demo = run_query_df("""
        SELECT mrn, first_name, last_name, date_of_birth, gender,
               race, ethnicity, insurance_type, zip_code,
               EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) AS age
        FROM patients WHERE patient_id = %s
    """, (pid,))

    if not demo.empty:
        d = demo.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Age", int(d["age"]))
        c2.metric("Gender", d["gender"])
        c3.metric("Insurance", d["insurance_type"])
        c4.metric("ZIP", d["zip_code"])

    # ── Tabs ─────────────────────────────────────────────────────────────────

    tab_enc, tab_dx, tab_tx, tab_meds, tab_labs, tab_ae = st.tabs(
        ["Encounters", "Diagnoses", "Treatments", "Medications", "Lab Results", "Adverse Events"]
    )

    with tab_enc:
        enc = run_query_df("""
            SELECT e.encounter_id, e.encounter_type, e.admission_date,
                   e.discharge_date, e.status,
                   pr.first_name || ' ' || pr.last_name AS provider,
                   pr.specialty
            FROM encounters e
            JOIN providers pr ON e.provider_id = pr.provider_id
            WHERE e.patient_id = %s
            ORDER BY e.admission_date DESC
        """, (pid,))
        if enc.empty:
            st.info("No encounters.")
        else:
            st.dataframe(enc, use_container_width=True, hide_index=True)

    with tab_dx:
        dx = run_query_df("""
            SELECT icd10_code, description, status,
                   diagnosed_date, resolved_date
            FROM diagnoses
            WHERE patient_id = %s
            ORDER BY diagnosed_date DESC
        """, (pid,))
        if dx.empty:
            st.info("No diagnoses.")
        else:
            st.dataframe(dx, use_container_width=True, hide_index=True)

    with tab_tx:
        tx = run_query_df("""
            SELECT t.treatment_name, t.treatment_type, t.status,
                   t.start_date, t.end_date, t.dosage, t.frequency,
                   o.outcome_type, o.outcome_measure,
                   o.baseline_value, o.result_value, o.unit
            FROM treatments t
            LEFT JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id
            WHERE t.patient_id = %s
            ORDER BY t.start_date DESC
        """, (pid,))
        if tx.empty:
            st.info("No treatments.")
        else:
            st.dataframe(tx, use_container_width=True, hide_index=True)

    with tab_meds:
        meds = run_query_df("""
            SELECT medication_name, ndc_code, dosage, route,
                   frequency, start_date, end_date, status,
                   prescribing_reason
            FROM medications
            WHERE patient_id = %s
            ORDER BY start_date DESC
        """, (pid,))
        if meds.empty:
            st.info("No medications.")
        else:
            st.dataframe(meds, use_container_width=True, hide_index=True)

    with tab_labs:
        labs = run_query_df("""
            SELECT test_name, loinc_code, result_value, unit,
                   reference_low, reference_high, abnormal_flag,
                   collected_date
            FROM lab_results
            WHERE patient_id = %s
            ORDER BY collected_date DESC
        """, (pid,))
        if labs.empty:
            st.info("No lab results.")
        else:
            st.dataframe(labs, use_container_width=True, hide_index=True)

    with tab_ae:
        ae = run_query_df("""
            SELECT ae.event_type, ae.severity, ae.ctcae_grade,
                   ae.onset_date, ae.resolution_date,
                   ae.action_taken, ae.outcome,
                   t.treatment_name
            FROM adverse_events ae
            JOIN treatments t ON ae.treatment_id = t.treatment_id
            WHERE ae.patient_id = %s
            ORDER BY ae.onset_date DESC
        """, (pid,))
        if ae.empty:
            st.info("No adverse events.")
        else:
            st.dataframe(ae, use_container_width=True, hide_index=True)
