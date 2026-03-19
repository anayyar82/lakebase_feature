"""Knowledge Graph Explorer — Visualize patient clinical journeys as a graph."""

import streamlit as st
import plotly.graph_objects as go
from db import run_query_df


def render():
    st.title("Knowledge Graph Explorer")
    st.markdown(
        "Explore patient clinical journeys as a connected graph — "
        "encounters, diagnoses, treatments, outcomes, and adverse events."
    )

    # ── Select patient ───────────────────────────────────────────────────────

    search = st.text_input("Search patient (name or MRN)", key="kg_search")
    if not search:
        st.info("Enter a patient name or MRN to explore their knowledge graph.")
        return

    patients = run_query_df("""
        SELECT patient_id, mrn,
               first_name || ' ' || last_name AS name
        FROM patients
        WHERE is_active = TRUE
          AND (
              LOWER(first_name) LIKE LOWER(%s)
              OR LOWER(last_name) LIKE LOWER(%s)
              OR LOWER(mrn) LIKE LOWER(%s)
          )
        LIMIT 20
    """, (f"%{search}%", f"%{search}%", f"%{search}%"))

    if patients.empty:
        st.warning("No patients found.")
        return

    sel = st.selectbox(
        "Patient", range(len(patients)),
        format_func=lambda i: f"{patients.iloc[i]['mrn']} — {patients.iloc[i]['name']}",
        key="kg_patient",
    )
    pid = int(patients.iloc[sel]["patient_id"])
    patient_name = patients.iloc[sel]["name"]

    st.markdown("---")

    # ── Gather graph data ────────────────────────────────────────────────────

    encounters = run_query_df("""
        SELECT encounter_id, encounter_type, admission_date::text AS label
        FROM encounters WHERE patient_id = %s
    """, (pid,))

    diagnoses = run_query_df("""
        SELECT diagnosis_id, icd10_code, description
        FROM diagnoses WHERE patient_id = %s
    """, (pid,))

    treatments = run_query_df("""
        SELECT treatment_id, treatment_name, treatment_type
        FROM treatments WHERE patient_id = %s
    """, (pid,))

    outcomes = run_query_df("""
        SELECT o.outcome_id, o.outcome_type, o.outcome_measure, o.treatment_id
        FROM treatment_outcomes o
        WHERE o.patient_id = %s
    """, (pid,))

    adverse = run_query_df("""
        SELECT ae.event_id, ae.event_type, ae.severity, ae.treatment_id
        FROM adverse_events ae
        WHERE ae.patient_id = %s
    """, (pid,))

    # ── Build graph ──────────────────────────────────────────────────────────

    nodes = []
    edges = []
    node_colors = []
    node_sizes = []

    color_map = {
        "patient": "#3498db",
        "encounter": "#2ecc71",
        "diagnosis": "#9b59b6",
        "treatment": "#e67e22",
        "outcome": "#1abc9c",
        "adverse_event": "#e74c3c",
    }

    patient_node = f"Patient: {patient_name}"
    nodes.append(patient_node)
    node_colors.append(color_map["patient"])
    node_sizes.append(30)

    for _, e in encounters.iterrows():
        label = f"Enc: {e['encounter_type']}\n{e['label']}"
        nodes.append(label)
        node_colors.append(color_map["encounter"])
        node_sizes.append(18)
        edges.append((patient_node, label))

    for _, d in diagnoses.iterrows():
        label = f"Dx: {d['icd10_code']}\n{d['description'][:30]}"
        nodes.append(label)
        node_colors.append(color_map["diagnosis"])
        node_sizes.append(18)
        edges.append((patient_node, label))

    tx_node_map = {}
    for _, t in treatments.iterrows():
        label = f"Tx: {t['treatment_name']}"
        nodes.append(label)
        node_colors.append(color_map["treatment"])
        node_sizes.append(20)
        edges.append((patient_node, label))
        tx_node_map[t["treatment_id"]] = label

    for _, o in outcomes.iterrows():
        label = f"Out: {o['outcome_type']}\n{o['outcome_measure'][:25]}"
        nodes.append(label)
        node_colors.append(color_map["outcome"])
        node_sizes.append(14)
        tx_label = tx_node_map.get(o["treatment_id"])
        if tx_label:
            edges.append((tx_label, label))

    for _, a in adverse.iterrows():
        label = f"AE: {a['event_type']}\n({a['severity']})"
        nodes.append(label)
        node_colors.append(color_map["adverse_event"])
        node_sizes.append(16)
        tx_label = tx_node_map.get(a["treatment_id"])
        if tx_label:
            edges.append((tx_label, label))

    if len(nodes) <= 1:
        st.info("No clinical data found for this patient.")
        return

    # ── Layout (simple circular) ─────────────────────────────────────────────

    import math
    n = len(nodes)
    positions = {}
    for i, node in enumerate(nodes):
        if i == 0:
            positions[node] = (0, 0)
        else:
            angle = 2 * math.pi * (i - 1) / (n - 1)
            radius = 2 + (i % 3) * 0.5
            positions[node] = (radius * math.cos(angle), radius * math.sin(angle))

    # ── Draw with Plotly ─────────────────────────────────────────────────────

    edge_x, edge_y = [], []
    for src, tgt in edges:
        x0, y0 = positions[src]
        x1, y1 = positions[tgt]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=1, color="#bdc3c7"),
        hoverinfo="none",
    )

    node_x = [positions[n][0] for n in nodes]
    node_y = [positions[n][1] for n in nodes]
    node_text = [n.replace("\n", "<br>") for n in nodes]

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        marker=dict(size=node_sizes, color=node_colors, line=dict(width=1, color="white")),
        text=node_text, textposition="top center", textfont=dict(size=9),
        hoverinfo="text",
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=f"Clinical Knowledge Graph — {patient_name}",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600,
            margin=dict(l=20, r=20, t=50, b=20),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Legend ────────────────────────────────────────────────────────────────

    st.markdown("**Legend:**")
    legend_cols = st.columns(6)
    for i, (entity, color) in enumerate(color_map.items()):
        legend_cols[i].markdown(
            f'<span style="color:{color}; font-size:20px;">●</span> {entity.replace("_", " ").title()}',
            unsafe_allow_html=True,
        )

    # ── Summary stats ────────────────────────────────────────────────────────

    st.markdown("---")
    st.subheader("Graph Summary")
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    sc1.metric("Encounters", len(encounters))
    sc2.metric("Diagnoses", len(diagnoses))
    sc3.metric("Treatments", len(treatments))
    sc4.metric("Outcomes", len(outcomes))
    sc5.metric("Adverse Events", len(adverse))
