"""Data Entry — Add new records to Lakebase and see them instantly across all tabs."""

import streamlit as st
from datetime import date, datetime
from db import run_query_df, run_execute


def render():
    st.title("Data Entry")
    st.markdown(
        "Add new records directly to **Lakebase**. Changes appear immediately "
        "across all dashboard tabs — no sync delay."
    )

    tab_patient, tab_encounter, tab_diagnosis, tab_treatment, tab_lab, tab_ae = st.tabs(
        ["New Patient", "New Encounter", "New Diagnosis",
         "New Treatment", "New Lab Result", "New Adverse Event"]
    )

    # ── New Patient ──────────────────────────────────────────────────────────

    with tab_patient:
        st.subheader("Register a New Patient")
        with st.form("new_patient", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                mrn = st.text_input("MRN *", placeholder="MRN-200001")
                first_name = st.text_input("First Name *")
                last_name = st.text_input("Last Name *")
                dob = st.date_input("Date of Birth *", value=date(1970, 1, 1),
                                    min_value=date(1920, 1, 1), max_value=date.today())
            with col2:
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                race = st.selectbox("Race", ["White", "Black or African American",
                                             "Asian", "Other"])
                ethnicity = st.selectbox("Ethnicity", ["Not Hispanic", "Hispanic/Latino"])
                insurance = st.selectbox("Insurance", ["Medicare", "Commercial",
                                                       "Medicaid", "Self-pay"])
            zip_code = st.text_input("ZIP Code", placeholder="60601")

            if st.form_submit_button("Add Patient", type="primary"):
                if not mrn or not first_name or not last_name:
                    st.error("MRN, First Name, and Last Name are required.")
                else:
                    try:
                        run_execute("""
                            INSERT INTO patients (mrn, first_name, last_name, date_of_birth,
                                                  gender, race, ethnicity, insurance_type, zip_code)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (mrn, first_name, last_name, dob, gender, race,
                              ethnicity, insurance, zip_code or None))
                        st.success(f"Patient **{first_name} {last_name}** ({mrn}) added!")
                    except Exception as e:
                        st.error(f"Failed: {e}")

    # ── New Encounter ────────────────────────────────────────────────────────

    with tab_encounter:
        st.subheader("Record a New Encounter")

        patients = run_query_df("""
            SELECT patient_id, mrn, first_name || ' ' || last_name AS name
            FROM patients WHERE is_active = TRUE ORDER BY last_name
        """)
        providers = run_query_df("""
            SELECT provider_id, first_name || ' ' || last_name AS name, specialty
            FROM providers WHERE is_active = TRUE ORDER BY last_name
        """)

        if patients.empty or providers.empty:
            st.warning("Need at least one patient and one provider.")
        else:
            with st.form("new_encounter", clear_on_submit=True):
                pt_idx = st.selectbox(
                    "Patient *", range(len(patients)),
                    format_func=lambda i: f"{patients.iloc[i]['mrn']} — {patients.iloc[i]['name']}",
                    key="enc_patient",
                )
                pr_idx = st.selectbox(
                    "Provider *", range(len(providers)),
                    format_func=lambda i: f"{providers.iloc[i]['name']} ({providers.iloc[i]['specialty']})",
                    key="enc_provider",
                )
                col1, col2 = st.columns(2)
                with col1:
                    enc_type = st.selectbox("Encounter Type", ["outpatient", "inpatient",
                                                               "emergency", "telehealth"])
                    admission = st.date_input("Admission Date *", value=date.today())
                with col2:
                    complaint = st.text_input("Chief Complaint")
                    disposition = st.selectbox("Disposition", ["discharged", "transferred",
                                                               "admitted", "expired"])

                if st.form_submit_button("Add Encounter", type="primary"):
                    try:
                        run_execute("""
                            INSERT INTO encounters (patient_id, provider_id, encounter_type,
                                                    admission_date, chief_complaint, disposition)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (str(patients.iloc[pt_idx]["patient_id"]),
                              str(providers.iloc[pr_idx]["provider_id"]),
                              enc_type, admission, complaint or None, disposition))
                        st.success(f"Encounter added for **{patients.iloc[pt_idx]['name']}**!")
                    except Exception as e:
                        st.error(f"Failed: {e}")

    # ── New Diagnosis ────────────────────────────────────────────────────────

    with tab_diagnosis:
        st.subheader("Add a Diagnosis")

        patients_dx = run_query_df("""
            SELECT patient_id, mrn, first_name || ' ' || last_name AS name
            FROM patients WHERE is_active = TRUE ORDER BY last_name
        """)
        encounters_dx = run_query_df("""
            SELECT e.encounter_id, p.mrn,
                   p.first_name || ' ' || p.last_name AS patient_name,
                   e.encounter_type, e.admission_date::text AS adm
            FROM encounters e JOIN patients p ON e.patient_id = p.patient_id
            ORDER BY e.admission_date DESC LIMIT 50
        """)

        if patients_dx.empty or encounters_dx.empty:
            st.warning("Need at least one patient with an encounter.")
        else:
            with st.form("new_diagnosis", clear_on_submit=True):
                enc_idx = st.selectbox(
                    "Encounter *", range(len(encounters_dx)),
                    format_func=lambda i: (
                        f"{encounters_dx.iloc[i]['mrn']} — "
                        f"{encounters_dx.iloc[i]['patient_name']} — "
                        f"{encounters_dx.iloc[i]['encounter_type']} ({encounters_dx.iloc[i]['adm']})"
                    ),
                )
                col1, col2 = st.columns(2)
                with col1:
                    icd10 = st.text_input("ICD-10 Code *", placeholder="C50.911")
                    description = st.text_input("Description *", placeholder="Malignant neoplasm...")
                with col2:
                    dx_type = st.selectbox("Diagnosis Type", ["primary", "secondary", "admitting"])
                    dx_status = st.selectbox("Status", ["active", "chronic", "resolved"])
                dx_date = st.date_input("Diagnosed Date", value=date.today())

                enc_row = encounters_dx.iloc[enc_idx]
                pt_id = run_query_df("""
                    SELECT patient_id FROM encounters WHERE encounter_id = %s
                """, (str(enc_row["encounter_id"]),))

                if st.form_submit_button("Add Diagnosis", type="primary"):
                    if not icd10 or not description:
                        st.error("ICD-10 code and description are required.")
                    else:
                        try:
                            run_execute("""
                                INSERT INTO diagnoses (encounter_id, patient_id, icd10_code,
                                                      description, diagnosis_type, diagnosed_date, status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (str(enc_row["encounter_id"]),
                                  str(pt_id.iloc[0]["patient_id"]),
                                  icd10, description, dx_type, dx_date, dx_status))
                            st.success(f"Diagnosis **{icd10}** added!")
                        except Exception as e:
                            st.error(f"Failed: {e}")

    # ── New Treatment ────────────────────────────────────────────────────────

    with tab_treatment:
        st.subheader("Add a Treatment")

        encounters_tx = run_query_df("""
            SELECT e.encounter_id, e.patient_id, e.provider_id,
                   p.mrn, p.first_name || ' ' || p.last_name AS patient_name,
                   e.encounter_type, e.admission_date::text AS adm
            FROM encounters e JOIN patients p ON e.patient_id = p.patient_id
            ORDER BY e.admission_date DESC LIMIT 50
        """)

        if encounters_tx.empty:
            st.warning("Need at least one encounter.")
        else:
            with st.form("new_treatment", clear_on_submit=True):
                enc_idx = st.selectbox(
                    "Encounter *", range(len(encounters_tx)),
                    format_func=lambda i: (
                        f"{encounters_tx.iloc[i]['mrn']} — "
                        f"{encounters_tx.iloc[i]['patient_name']} — "
                        f"{encounters_tx.iloc[i]['encounter_type']} ({encounters_tx.iloc[i]['adm']})"
                    ),
                    key="tx_enc",
                )
                col1, col2 = st.columns(2)
                with col1:
                    tx_type = st.selectbox("Treatment Type", ["medication", "procedure",
                                                              "therapy", "surgery"])
                    tx_name = st.text_input("Treatment Name *", placeholder="Metformin")
                    dosage = st.text_input("Dosage", placeholder="1000mg")
                with col2:
                    frequency = st.text_input("Frequency", placeholder="twice daily")
                    route = st.selectbox("Route", ["oral", "IV", "subcutaneous",
                                                   "topical", "intramuscular", "other"])
                    tx_status = st.selectbox("Status", ["active", "completed", "discontinued"])
                start_date = st.date_input("Start Date", value=date.today())

                enc_row = encounters_tx.iloc[enc_idx]

                if st.form_submit_button("Add Treatment", type="primary"):
                    if not tx_name:
                        st.error("Treatment name is required.")
                    else:
                        try:
                            run_execute("""
                                INSERT INTO treatments (encounter_id, patient_id, provider_id,
                                                       treatment_type, treatment_name,
                                                       start_date, dosage, frequency, route, status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (str(enc_row["encounter_id"]),
                                  str(enc_row["patient_id"]),
                                  str(enc_row["provider_id"]),
                                  tx_type, tx_name, start_date,
                                  dosage or None, frequency or None, route, tx_status))
                            st.success(f"Treatment **{tx_name}** added!")
                        except Exception as e:
                            st.error(f"Failed: {e}")

    # ── New Lab Result ───────────────────────────────────────────────────────

    with tab_lab:
        st.subheader("Add a Lab Result")

        encounters_lab = run_query_df("""
            SELECT e.encounter_id, e.patient_id,
                   p.mrn, p.first_name || ' ' || p.last_name AS patient_name,
                   e.admission_date::text AS adm
            FROM encounters e JOIN patients p ON e.patient_id = p.patient_id
            ORDER BY e.admission_date DESC LIMIT 50
        """)

        if encounters_lab.empty:
            st.warning("Need at least one encounter.")
        else:
            with st.form("new_lab", clear_on_submit=True):
                enc_idx = st.selectbox(
                    "Encounter *", range(len(encounters_lab)),
                    format_func=lambda i: (
                        f"{encounters_lab.iloc[i]['mrn']} — "
                        f"{encounters_lab.iloc[i]['patient_name']} ({encounters_lab.iloc[i]['adm']})"
                    ),
                    key="lab_enc",
                )
                col1, col2 = st.columns(2)
                with col1:
                    test_name = st.text_input("Test Name *", placeholder="HbA1c")
                    loinc = st.text_input("LOINC Code", placeholder="4548-4")
                    result_val = st.number_input("Result Value *", format="%.4f")
                with col2:
                    unit = st.text_input("Unit", placeholder="%")
                    ref_low = st.number_input("Reference Low", format="%.4f", value=0.0)
                    ref_high = st.number_input("Reference High", format="%.4f", value=0.0)
                col3, col4 = st.columns(2)
                with col3:
                    flag = st.selectbox("Abnormal Flag", ["N", "H", "L", "HH", "LL"])
                with col4:
                    collected = st.date_input("Collected Date", value=date.today())

                enc_row = encounters_lab.iloc[enc_idx]

                if st.form_submit_button("Add Lab Result", type="primary"):
                    if not test_name:
                        st.error("Test name is required.")
                    else:
                        try:
                            run_execute("""
                                INSERT INTO lab_results (encounter_id, patient_id, test_name,
                                                        loinc_code, result_value, unit,
                                                        reference_low, reference_high,
                                                        abnormal_flag, collected_date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (str(enc_row["encounter_id"]),
                                  str(enc_row["patient_id"]),
                                  test_name, loinc or None, result_val, unit or None,
                                  ref_low or None, ref_high or None, flag,
                                  datetime.combine(collected, datetime.min.time())))
                            st.success(f"Lab result **{test_name}** = {result_val} added!")
                        except Exception as e:
                            st.error(f"Failed: {e}")

    # ── New Adverse Event ────────────────────────────────────────────────────

    with tab_ae:
        st.subheader("Report an Adverse Event")

        treatments_ae = run_query_df("""
            SELECT t.treatment_id, t.patient_id, t.treatment_name,
                   p.mrn, p.first_name || ' ' || p.last_name AS patient_name
            FROM treatments t JOIN patients p ON t.patient_id = p.patient_id
            WHERE t.status = 'active'
            ORDER BY t.start_date DESC LIMIT 50
        """)

        if treatments_ae.empty:
            st.warning("Need at least one active treatment.")
        else:
            with st.form("new_ae", clear_on_submit=True):
                tx_idx = st.selectbox(
                    "Treatment *", range(len(treatments_ae)),
                    format_func=lambda i: (
                        f"{treatments_ae.iloc[i]['mrn']} — "
                        f"{treatments_ae.iloc[i]['patient_name']} — "
                        f"{treatments_ae.iloc[i]['treatment_name']}"
                    ),
                    key="ae_tx",
                )
                col1, col2 = st.columns(2)
                with col1:
                    event_type = st.text_input("Event Type *", placeholder="Nausea")
                    severity = st.selectbox("Severity", ["mild", "moderate", "severe",
                                                         "life-threatening"])
                    ctcae = st.number_input("CTCAE Grade", min_value=1, max_value=5, value=1)
                with col2:
                    onset = st.date_input("Onset Date", value=date.today())
                    action = st.text_input("Action Taken", placeholder="Dose reduced")
                    outcome = st.selectbox("Outcome", ["ongoing", "resolved", "fatal"])

                tx_row = treatments_ae.iloc[tx_idx]

                if st.form_submit_button("Report Adverse Event", type="primary"):
                    if not event_type:
                        st.error("Event type is required.")
                    else:
                        try:
                            run_execute("""
                                INSERT INTO adverse_events (treatment_id, patient_id, event_type,
                                                           severity, ctcae_grade, onset_date,
                                                           action_taken, outcome)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (str(tx_row["treatment_id"]),
                                  str(tx_row["patient_id"]),
                                  event_type, severity, ctcae, onset,
                                  action or None, outcome))
                            st.success(f"Adverse event **{event_type}** reported!")
                        except Exception as e:
                            st.error(f"Failed: {e}")

    # ── Recent activity ──────────────────────────────────────────────────────

    st.markdown("---")
    st.subheader("Recently Added Records")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**Latest Patients**")
        recent_patients = run_query_df("""
            SELECT mrn, first_name || ' ' || last_name AS name,
                   gender, insurance_type, created_at
            FROM patients ORDER BY created_at DESC LIMIT 5
        """)
        if not recent_patients.empty:
            st.dataframe(recent_patients, use_container_width=True, hide_index=True)

    with col_r2:
        st.markdown("**Latest Encounters**")
        recent_enc = run_query_df("""
            SELECT p.mrn,
                   p.first_name || ' ' || p.last_name AS patient_name,
                   e.encounter_type, e.admission_date, e.created_at
            FROM encounters e JOIN patients p ON e.patient_id = p.patient_id
            ORDER BY e.created_at DESC LIMIT 5
        """)
        if not recent_enc.empty:
            st.dataframe(recent_enc, use_container_width=True, hide_index=True)
