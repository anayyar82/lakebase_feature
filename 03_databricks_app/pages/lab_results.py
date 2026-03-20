"""Lab Results Tracker — Trends, abnormal flags, and longitudinal analysis."""

import streamlit as st
import plotly.express as px
from db import run_query_df


def render():
    st.title("Lab Results Tracker")
    st.markdown("Monitor lab trends, flag abnormal values, and track longitudinal changes.")

    # ── KPIs ─────────────────────────────────────────────────────────────────

    kpi = run_query_df("""
        SELECT
            COUNT(*)                              AS total_results,
            COUNT(DISTINCT patient_id)            AS patients_tested,
            COUNT(DISTINCT test_name)             AS unique_tests,
            COUNT(*) FILTER (WHERE abnormal_flag != 'N')
                                                  AS abnormal_count
        FROM lab_results
    """)

    k = kpi.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Results", f"{k['total_results']:,}")
    c2.metric("Patients Tested", f"{k['patients_tested']:,}")
    c3.metric("Unique Tests", f"{k['unique_tests']:,}")
    c4.metric("Abnormal Results", f"{k['abnormal_count']:,}")

    st.markdown("---")

    # ── Filter by test ───────────────────────────────────────────────────────
    # abnormal_flag values: N (normal), H (high), L (low), HH (critical high), LL (critical low)

    tests = run_query_df("SELECT DISTINCT test_name FROM lab_results ORDER BY 1")
    test_list = tests["test_name"].tolist()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_test = st.selectbox("Lab Test", ["All"] + test_list)
    with col_f2:
        flag_options = {"All": None, "Normal (N)": "N", "High (H)": "H",
                        "Low (L)": "L", "Critical High (HH)": "HH", "Critical Low (LL)": "LL"}
        flag_label = st.selectbox("Abnormal Flag", list(flag_options.keys()))
        flag_value = flag_options[flag_label]

    where = []
    if selected_test != "All":
        where.append(f"lr.test_name = '{selected_test}'")
    if flag_value is not None:
        where.append(f"lr.abnormal_flag = '{flag_value}'")
    where_clause = "WHERE " + " AND ".join(where) if where else ""

    # ── Abnormal distribution ────────────────────────────────────────────────

    left, right = st.columns(2)

    with left:
        st.subheader("Results by Abnormal Flag")
        flags = run_query_df(f"""
            SELECT
                CASE lr.abnormal_flag
                    WHEN 'N'  THEN 'Normal'
                    WHEN 'H'  THEN 'High'
                    WHEN 'L'  THEN 'Low'
                    WHEN 'HH' THEN 'Critical High'
                    WHEN 'LL' THEN 'Critical Low'
                    ELSE lr.abnormal_flag
                END AS flag_label,
                COUNT(*) AS count
            FROM lab_results lr
            {where_clause}
            GROUP BY lr.abnormal_flag
            ORDER BY count DESC
        """)
        if not flags.empty:
            fig = px.pie(
                flags, names="flag_label", values="count",
                color="flag_label",
                color_discrete_map={
                    "Normal": "#2ecc71", "High": "#e67e22",
                    "Low": "#3498db", "Critical High": "#e74c3c",
                    "Critical Low": "#9b59b6",
                },
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Top Tests with Abnormal Results")
        top_abnormal = run_query_df("""
            SELECT test_name,
                   COUNT(*) FILTER (WHERE abnormal_flag != 'N') AS abnormal,
                   COUNT(*) AS total,
                   ROUND(
                       COUNT(*) FILTER (WHERE abnormal_flag != 'N') * 100.0 / COUNT(*), 1
                   ) AS abnormal_pct
            FROM lab_results
            GROUP BY test_name
            HAVING COUNT(*) FILTER (WHERE abnormal_flag != 'N') > 0
            ORDER BY abnormal DESC
            LIMIT 10
        """)
        if not top_abnormal.empty:
            fig2 = px.bar(top_abnormal, x="test_name", y="abnormal_pct",
                          color="abnormal_pct", color_continuous_scale="YlOrRd")
            fig2.update_layout(xaxis_tickangle=-45, height=350,
                               yaxis_title="% Abnormal", showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # ── Patient trend (select a patient + test) ─────────────────────────────

    st.subheader("Patient Lab Trend")
    st.markdown("Select a patient to view longitudinal lab values.")

    patient_search = st.text_input("Search patient (name or MRN)", key="lab_patient_search")
    if patient_search:
        pts = run_query_df("""
            SELECT DISTINCT p.patient_id,
                   p.mrn,
                   p.first_name || ' ' || p.last_name AS name
            FROM patients p
            JOIN lab_results lr ON p.patient_id = lr.patient_id
            WHERE LOWER(p.first_name) LIKE LOWER(%s)
               OR LOWER(p.last_name) LIKE LOWER(%s)
               OR LOWER(p.mrn) LIKE LOWER(%s)
            LIMIT 20
        """, (f"%{patient_search}%", f"%{patient_search}%", f"%{patient_search}%"))

        if not pts.empty:
            sel = st.selectbox(
                "Patient", range(len(pts)),
                format_func=lambda i: f"{pts.iloc[i]['mrn']} — {pts.iloc[i]['name']}",
                key="lab_pt_select",
            )
            pid = str(pts.iloc[sel]["patient_id"])

            pt_tests = run_query_df("""
                SELECT DISTINCT test_name FROM lab_results
                WHERE patient_id = %s ORDER BY 1
            """, (pid,))
            sel_test = st.selectbox("Test", pt_tests["test_name"].tolist(), key="lab_trend_test")

            trend = run_query_df("""
                SELECT collected_date, result_value, unit,
                       reference_low, reference_high, abnormal_flag
                FROM lab_results
                WHERE patient_id = %s AND test_name = %s
                ORDER BY collected_date
            """, (pid, sel_test))

            if not trend.empty:
                fig3 = px.line(trend, x="collected_date", y="result_value",
                               markers=True, title=f"{sel_test} over time")
                if trend["reference_low"].notna().any():
                    fig3.add_hline(y=float(trend["reference_low"].iloc[0]),
                                   line_dash="dash", line_color="blue",
                                   annotation_text="Low ref")
                if trend["reference_high"].notna().any():
                    fig3.add_hline(y=float(trend["reference_high"].iloc[0]),
                                   line_dash="dash", line_color="red",
                                   annotation_text="High ref")
                fig3.update_layout(height=350)
                st.plotly_chart(fig3, use_container_width=True)

    # ── Detail table ─────────────────────────────────────────────────────────

    st.subheader("Lab Results Detail")
    detail = run_query_df(f"""
        SELECT
            p.mrn,
            p.first_name || ' ' || p.last_name AS patient_name,
            lr.test_name,
            lr.loinc_code,
            lr.result_value,
            lr.unit,
            lr.reference_low,
            lr.reference_high,
            lr.abnormal_flag,
            lr.collected_date
        FROM lab_results lr
        JOIN patients p ON lr.patient_id = p.patient_id
        {where_clause}
        ORDER BY lr.collected_date DESC
        LIMIT 100
    """)
    if not detail.empty:
        st.dataframe(detail, use_container_width=True, hide_index=True)
