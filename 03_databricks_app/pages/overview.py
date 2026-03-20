"""Overview dashboard — KPI cards and system-level metrics."""

import streamlit as st
from db import run_query_df


def render():
    st.title("HLS Knowledge Graph — Overview")
    st.markdown("Real-time operational analytics powered by **Databricks Lakebase**.")

    # ── KPI cards ────────────────────────────────────────────────────────────

    col1, col2, col3, col4, col5 = st.columns(5)

    patients = run_query_df("SELECT COUNT(*) AS cnt FROM patients WHERE is_active = TRUE")
    col1.metric("Active Patients", f"{patients['cnt'].iloc[0]:,}")

    providers = run_query_df("SELECT COUNT(*) AS cnt FROM providers WHERE is_active = TRUE")
    col2.metric("Active Providers", f"{providers['cnt'].iloc[0]:,}")

    encounters = run_query_df("SELECT COUNT(*) AS cnt FROM encounters")
    col3.metric("Total Encounters", f"{encounters['cnt'].iloc[0]:,}")

    treatments = run_query_df("SELECT COUNT(*) AS cnt FROM treatments")
    col4.metric("Treatments", f"{treatments['cnt'].iloc[0]:,}")

    adverse = run_query_df("SELECT COUNT(*) AS cnt FROM adverse_events")
    col5.metric("Adverse Events", f"{adverse['cnt'].iloc[0]:,}")

    st.markdown("---")

    # ── Charts row ───────────────────────────────────────────────────────────

    left, right = st.columns(2)

    with left:
        st.subheader("Encounters by Type")
        enc_type = run_query_df("""
            SELECT encounter_type, COUNT(*) AS count
            FROM encounters
            GROUP BY encounter_type
            ORDER BY count DESC
        """)
        if not enc_type.empty:
            st.bar_chart(enc_type.set_index("encounter_type"))

    with right:
        st.subheader("Diagnoses by Status")
        diag_status = run_query_df("""
            SELECT status, COUNT(*) AS count
            FROM diagnoses
            GROUP BY status
            ORDER BY count DESC
        """)
        if not diag_status.empty:
            st.bar_chart(diag_status.set_index("status"))

    # ── Second row ───────────────────────────────────────────────────────────

    left2, right2 = st.columns(2)

    with left2:
        st.subheader("Patients by Insurance Type")
        insurance = run_query_df("""
            SELECT insurance_type, COUNT(*) AS count
            FROM patients
            WHERE is_active = TRUE
            GROUP BY insurance_type
            ORDER BY count DESC
        """)
        if not insurance.empty:
            st.bar_chart(insurance.set_index("insurance_type"))

    with right2:
        st.subheader("Treatments by Type")
        tx_type = run_query_df("""
            SELECT treatment_type, COUNT(*) AS count
            FROM treatments
            GROUP BY treatment_type
            ORDER BY count DESC
        """)
        if not tx_type.empty:
            st.bar_chart(tx_type.set_index("treatment_type"))

    # ── Recent encounters ────────────────────────────────────────────────────

    st.subheader("Recent Encounters")
    recent = run_query_df("""
        SELECT
            e.encounter_id,
            p.mrn,
            p.first_name || ' ' || p.last_name AS patient_name,
            pr.first_name || ' ' || pr.last_name AS provider_name,
            e.encounter_type,
            e.admission_date,
            e.disposition
        FROM encounters e
        JOIN patients p ON e.patient_id = p.patient_id
        JOIN providers pr ON e.provider_id = pr.provider_id
        ORDER BY e.admission_date DESC
        LIMIT 20
    """)
    if not recent.empty:
        st.dataframe(recent, use_container_width=True, hide_index=True)
