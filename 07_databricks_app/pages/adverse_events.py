"""Adverse Events Monitor — Safety surveillance dashboard."""

import streamlit as st
import plotly.express as px
from db import run_query_df


def render():
    st.title("Adverse Events Monitor")
    st.markdown("Real-time safety surveillance across all treatments and patients.")

    # ── KPIs ─────────────────────────────────────────────────────────────────

    kpi = run_query_df("""
        SELECT
            COUNT(*)                                                 AS total_events,
            COUNT(DISTINCT patient_id)                               AS affected_patients,
            COUNT(*) FILTER (WHERE severity IN ('severe', 'life-threatening'))  AS serious_count,
            COUNT(*) FILTER (WHERE resolution_date IS NULL)          AS unresolved
        FROM adverse_events
    """)

    k = kpi.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total AEs", f"{k['total_events']:,}")
    c2.metric("Patients Affected", f"{k['affected_patients']:,}")
    c3.metric("Serious (Grade 3+)", f"{k['serious_count']:,}")
    c4.metric("Unresolved", f"{k['unresolved']:,}")

    st.markdown("---")

    # ── Filters ──────────────────────────────────────────────────────────────

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        severities = ["All", "mild", "moderate", "severe", "life-threatening"]
        sel_severity = st.selectbox("Severity", severities)
    with col_f2:
        event_types = run_query_df("SELECT DISTINCT event_type FROM adverse_events ORDER BY 1")
        type_list = ["All"] + event_types["event_type"].tolist()
        sel_event_type = st.selectbox("Event Type", type_list)
    with col_f3:
        actions = ["All", "unresolved only"]
        sel_action = st.selectbox("Resolution", actions)

    where = []
    if sel_severity != "All":
        where.append(f"ae.severity = '{sel_severity}'")
    if sel_event_type != "All":
        where.append(f"ae.event_type = '{sel_event_type}'")
    if sel_action == "unresolved only":
        where.append("ae.resolution_date IS NULL")
    where_clause = "WHERE " + " AND ".join(where) if where else ""

    # ── Charts ───────────────────────────────────────────────────────────────

    left, right = st.columns(2)

    with left:
        st.subheader("AEs by Severity")
        by_sev = run_query_df(f"""
            SELECT ae.severity, COUNT(*) AS count
            FROM adverse_events ae
            {where_clause}
            GROUP BY ae.severity
            ORDER BY CASE ae.severity
                WHEN 'life-threatening' THEN 1
                WHEN 'severe' THEN 2
                WHEN 'moderate' THEN 3
                WHEN 'mild' THEN 4
            END
        """)
        if not by_sev.empty:
            fig = px.pie(
                by_sev, names="severity", values="count",
                color="severity",
                color_discrete_map={
                    "mild": "#2ecc71", "moderate": "#f39c12",
                    "severe": "#e67e22", "life-threatening": "#e74c3c",
                },
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("AEs by Treatment")
        by_tx = run_query_df(f"""
            SELECT t.treatment_name, COUNT(*) AS count
            FROM adverse_events ae
            JOIN treatments t ON ae.treatment_id = t.treatment_id
            {where_clause}
            GROUP BY t.treatment_name
            ORDER BY count DESC
            LIMIT 15
        """)
        if not by_tx.empty:
            fig2 = px.bar(by_tx, x="treatment_name", y="count", color="count",
                          color_continuous_scale="Reds")
            fig2.update_layout(xaxis_tickangle=-45, height=350, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # ── CTCAE grade distribution ─────────────────────────────────────────────

    st.subheader("CTCAE Grade Distribution")
    grades = run_query_df(f"""
        SELECT ae.ctcae_grade, ae.event_type, COUNT(*) AS count
        FROM adverse_events ae
        {where_clause}
        GROUP BY ae.ctcae_grade, ae.event_type
        ORDER BY ae.ctcae_grade
    """)
    if not grades.empty:
        fig3 = px.bar(grades, x="ctcae_grade", y="count", color="event_type",
                      barmode="stack")
        fig3.update_layout(height=350)
        st.plotly_chart(fig3, use_container_width=True)

    # ── Detail table ─────────────────────────────────────────────────────────

    st.subheader("Adverse Event Detail")
    detail = run_query_df(f"""
        SELECT
            ae.event_id,
            p.mrn,
            p.first_name || ' ' || p.last_name AS patient_name,
            t.treatment_name,
            ae.event_type,
            ae.severity,
            ae.ctcae_grade,
            ae.onset_date,
            ae.resolution_date,
            ae.action_taken,
            ae.outcome
        FROM adverse_events ae
        JOIN patients p ON ae.patient_id = p.patient_id
        JOIN treatments t ON ae.treatment_id = t.treatment_id
        {where_clause}
        ORDER BY ae.onset_date DESC
        LIMIT 100
    """)
    if not detail.empty:
        st.dataframe(detail, use_container_width=True, hide_index=True)
