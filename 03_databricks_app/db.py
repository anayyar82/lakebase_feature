"""
Database connection helper for Databricks Lakebase with OAuth token rotation.

When deployed as a Databricks App, connection details are injected via
environment variables. OAuth tokens auto-rotate before expiration.

For local development, set the env vars manually and authenticate via
`databricks auth login`.
"""

import os
import streamlit as st
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row


def _get_workspace_client():
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient()


class OAuthConnection(psycopg.Connection):
    """Postgres connection that generates a fresh Databricks OAuth token."""

    @classmethod
    def connect(cls, conninfo="", **kwargs):
        endpoint_name = os.environ["ENDPOINT_NAME"]
        w = _get_workspace_client()
        credential = w.postgres.generate_database_credential(endpoint=endpoint_name)
        kwargs["password"] = credential.token
        return super().connect(conninfo, **kwargs)


@st.cache_resource
def get_pool() -> ConnectionPool:
    """Return a cached connection pool (one per Streamlit server)."""
    username = os.environ["PGUSER"]
    host = os.environ["PGHOST"]
    port = os.environ.get("PGPORT", "5432")
    database = os.environ.get("PGDATABASE", "databricks_postgres")
    sslmode = os.environ.get("PGSSLMODE", "require")

    return ConnectionPool(
        conninfo=f"dbname={database} user={username} host={host} port={port} sslmode={sslmode}",
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
