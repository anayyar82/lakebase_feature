"""
Database connection helper for Databricks Lakebase with OAuth token rotation.

When deployed as a Databricks App, the service principal ID is used as
the Postgres username, and OAuth tokens are generated via the REST API.
"""

import os
import streamlit as st
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

PGHOST = os.environ.get("PGHOST", "ep-hidden-mouse-d1gj4kga.database.us-west-2.cloud.databricks.com")
PGDATABASE = os.environ.get("PGDATABASE", "databricks_postgres")
PGPORT = os.environ.get("PGPORT", "5432")
PGSSLMODE = os.environ.get("PGSSLMODE", "require")
PGUSER = os.environ.get(
    "PGUSER",
    os.environ.get("DATABRICKS_CLIENT_ID", "56dfcd38-371a-40af-b14d-32f7eb8b3b2f"),
)
ENDPOINT_NAME = os.environ.get(
    "ENDPOINT_NAME",
    "projects/lakebaseankur/branches/production/endpoints/primary",
)


def _generate_db_credential() -> str:
    """Generate a fresh Lakebase OAuth token using the Databricks REST API."""
    from databricks.sdk import WorkspaceClient
    import requests

    w = WorkspaceClient()

    api_url = f"{w.config.host}/api/2.0/postgres/credentials"
    headers = w.config.authenticate()
    payload = {"endpoint": ENDPOINT_NAME}

    resp = requests.post(api_url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["token"]


class OAuthConnection(psycopg.Connection):
    """Postgres connection that generates a fresh Databricks OAuth token."""

    @classmethod
    def connect(cls, conninfo="", **kwargs):
        kwargs["password"] = _generate_db_credential()
        return super().connect(conninfo, **kwargs)


@st.cache_resource
def get_pool() -> ConnectionPool:
    """Return a cached connection pool (one per Streamlit server)."""
    return ConnectionPool(
        conninfo=f"dbname={PGDATABASE} user={PGUSER} host={PGHOST} port={PGPORT} sslmode={PGSSLMODE}",
        connection_class=OAuthConnection,
        min_size=1,
        max_size=10,
        open=True,
        kwargs={"row_factory": dict_row},
    )


def run_query(sql: str, params: tuple | None = None) -> list[dict]:
    """Execute a read query and return rows as list of dicts."""
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def run_query_df(sql: str, params: tuple | None = None):
    """Execute a read query and return a pandas DataFrame."""
    import pandas as pd
    rows = run_query(sql, params)
    return pd.DataFrame(rows)
