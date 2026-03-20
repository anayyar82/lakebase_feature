"""
HLS Knowledge Graph — Databricks App
=====================================
Multi-page Streamlit application powered by Databricks Lakebase.
Provides real-time patient analytics, treatment monitoring, and
knowledge graph exploration against the live OLTP database.
"""

import streamlit as st

st.set_page_config(
    page_title="HLS Knowledge Graph",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar navigation ──────────────────────────────────────────────────────

PAGES = {
    "Overview": "overview",
    "Data Entry": "data_entry",
    "Patient 360": "patient_360",
    "Treatment Analytics": "treatment_analytics",
    "Adverse Events": "adverse_events",
    "Lab Results": "lab_results",
    "Knowledge Graph": "knowledge_graph",
}

st.sidebar.title("HLS Knowledge Graph")
st.sidebar.markdown("---")
selection = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

# ── Page routing ─────────────────────────────────────────────────────────────

if PAGES[selection] == "overview":
    from pages import overview
    overview.render()
elif PAGES[selection] == "data_entry":
    from pages import data_entry
    data_entry.render()
elif PAGES[selection] == "patient_360":
    from pages import patient_360
    patient_360.render()
elif PAGES[selection] == "treatment_analytics":
    from pages import treatment_analytics
    treatment_analytics.render()
elif PAGES[selection] == "adverse_events":
    from pages import adverse_events
    adverse_events.render()
elif PAGES[selection] == "lab_results":
    from pages import lab_results
    lab_results.render()
elif PAGES[selection] == "knowledge_graph":
    from pages import knowledge_graph
    knowledge_graph.render()

# ── Footer ───────────────────────────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.caption("Powered by Databricks Lakebase + Databricks Apps")
