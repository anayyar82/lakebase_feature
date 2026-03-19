"""Treatment Analytics — Efficacy, outcomes, and comparison dashboards."""

import streamlit as st
import plotly.express as px
from db import run_query_df


def render():
    st.title("Treatment Analytics")
    st.markdown("Analyze treatment efficacy, outcome distributions, and comparative performance.")

    # ── Filters ──────────────────────────────────────────────────────────────

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        types = run_query_df("SELECT DISTINCT treatment_type FROM treatments ORDER BY 1")
        type_list = ["All"] + types["treatment_type"].tolist()
        selected_type = st.selectbox("Treatment Type", type_list)

    with col_f2:
        statuses = ["All", "completed", "active", "discontinued"]
        selected_status = st.selectbox("Status", statuses)

    where = []
    if selected_type != "All":
        where.append(f"t.treatment_type = '{selected_type}'")
    if selected_status != "All":
        where.append(f"t.status = '{selected_status}'")
    where_clause = "WHERE " + " AND ".join(where) if where else ""

    # ── KPIs ─────────────────────────────────────────────────────────────────

    kpi = run_query_df(f"""
        SELECT
            COUNT(DISTINCT t.treatment_id) AS total_treatments,
            COUNT(DISTINCT t.patient_id)   AS unique_patients,
            COUNT(DISTINCT CASE WHEN o.outcome_type = 'improvement' THEN o.outcome_id END) AS improved,
            COUNT(DISTINCT o.outcome_id)   AS total_outcomes
        FROM treatments t
        LEFT JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id
        {where_clause}
    """)

    k = kpi.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Treatments", f"{k['total_treatments']:,}")
    c2.metric("Unique Patients", f"{k['unique_patients']:,}")
    c3.metric("Outcomes Recorded", f"{k['total_outcomes']:,}")
    rate = round(k["improved"] * 100 / k["total_outcomes"], 1) if k["total_outcomes"] > 0 else 0
    c4.metric("Improvement Rate", f"{rate}%")

    st.markdown("---")

    # ── Efficacy by treatment ────────────────────────────────────────────────

    left, right = st.columns(2)

    with left:
        st.subheader("Outcome Distribution by Treatment")
        outcomes = run_query_df(f"""
            SELECT t.treatment_name,
                   o.outcome_type,
                   COUNT(*) AS count
            FROM treatments t
            JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id
            {where_clause}
            GROUP BY t.treatment_name, o.outcome_type
            ORDER BY t.treatment_name
        """)
        if not outcomes.empty:
            fig = px.bar(
                outcomes, x="treatment_name", y="count", color="outcome_type",
                barmode="group",
                color_discrete_map={
                    "improvement": "#2ecc71",
                    "stable": "#f39c12",
                    "progression": "#e74c3c",
                },
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Avg Baseline vs Result by Treatment")
        avg_vals = run_query_df(f"""
            SELECT t.treatment_name,
                   ROUND(AVG(o.baseline_value)::numeric, 2) AS avg_baseline,
                   ROUND(AVG(o.result_value)::numeric, 2) AS avg_result
            FROM treatments t
            JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id
            {where_clause}
            GROUP BY t.treatment_name
            HAVING COUNT(*) >= 2
            ORDER BY t.treatment_name
        """)
        if not avg_vals.empty:
            import pandas as pd
            melted = avg_vals.melt(id_vars="treatment_name", var_name="Metric", value_name="Value")
            fig2 = px.bar(melted, x="treatment_name", y="Value", color="Metric", barmode="group")
            fig2.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig2, use_container_width=True)

    # ── Treatment details table ──────────────────────────────────────────────

    st.subheader("Treatment Detail")
    detail = run_query_df(f"""
        SELECT t.treatment_name, t.treatment_type, t.status,
               COUNT(DISTINCT t.patient_id) AS patients,
               COUNT(DISTINCT o.outcome_id) AS outcomes,
               COUNT(DISTINCT ae.event_id)  AS adverse_events,
               ROUND(AVG(o.baseline_value)::numeric, 2) AS avg_baseline,
               ROUND(AVG(o.result_value)::numeric, 2)   AS avg_result
        FROM treatments t
        LEFT JOIN treatment_outcomes o ON t.treatment_id = o.treatment_id
        LEFT JOIN adverse_events ae ON t.treatment_id = ae.treatment_id
        {where_clause}
        GROUP BY t.treatment_name, t.treatment_type, t.status
        ORDER BY patients DESC
    """)
    if not detail.empty:
        st.dataframe(detail, use_container_width=True, hide_index=True)
