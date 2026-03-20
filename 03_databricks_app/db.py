"""
Database connection helper for Databricks Lakebase with OAuth token rotation.

When deployed as a Databricks App, the service principal ID is used as
the Postgres username, and OAuth tokens are generated automatically.
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
ENDPOINT_NAME = os.environ.get("ENDPOINT_NAME", "")


def _get_workspace_client():
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient()


def _get_oauth_token() -> str:
    """Generate a fresh OAuth token for Lakebase authentication."""
    w = _get_workspace_client()
    if ENDPOINT_NAME:
        credential = w.postgres.generate_database_credential(endpoint=ENDPOINT_NAME)
        return credential.token
    token = w.config.authenticate()
    return token.get("Authorization", "").replace("Bearer ", "")


class OAuthConnection(psycopg.Connection):
    """Postgres connection that generates a fresh Databricks OAuth token."""

    @classmethod
    def connect(cls, conninfo="", **kwargs):
        kwargs["password"] = _get_oauth_token()
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
