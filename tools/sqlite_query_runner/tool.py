#!/usr/bin/env python3
"""
SQLite Query Runner Tool for Agent Tools & MCP Hub.
Executes parameterized queries safely with read-only safeguards and structured row output.
"""
from typing import Any, Dict, List, Optional
import os
import sqlite3
import time


DISALLOWED_READONLY_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
    "TRUNCATE", "REPLACE", "VACUUM", "ATTACH", "DETACH"
}


def is_safe_readonly_query(sql: str) -> bool:
    """Validate whether an SQL string is purely read-only."""
    cleaned = sql.strip().rstrip(";").upper()
    tokens = cleaned.split()
    if not tokens:
        return False
    first_token = tokens[0]
    if first_token in {"SELECT", "PRAGMA", "EXPLAIN", "WITH"}:
        for kw in DISALLOWED_READONLY_KEYWORDS:
            if f" {kw} " in f" {cleaned} ":
                return False
        return True
    return False


def execute_sqlite_query(
    database_path: str,
    query: str,
    params: Optional[List[Any]] = None,
    read_only: bool = True,
    max_rows: int = 100
) -> Dict[str, Any]:
    """
    Execute a query against a local SQLite database file.

    Args:
        database_path: Path to the SQLite file.
        query: SQL string to execute.
        params: Optional parameter list for parameterized queries.
        read_only: If True, blocks write/destructive SQL statements.
        max_rows: Maximum number of rows to return.

    Returns:
        Dictionary containing columns, rows, row_count, execution_time_ms, and status.
    """
    start_time = time.perf_counter()
    normalized_path = os.path.expanduser(database_path)

    if not os.path.exists(normalized_path) and read_only:
        return {
            "status": "error",
            "error": f"Database file not found: {database_path}",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": 0.0
        }

    if read_only and not is_safe_readonly_query(query):
        return {
            "status": "error",
            "error": "Write and DDL operations are prohibited when read_only=True.",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": 0.0
        }

    conn = None
    try:
        if read_only:
            # Connect in URI read-only mode if file exists
            uri_path = f"file:{os.path.abspath(normalized_path)}?mode=ro"
            conn = sqlite3.connect(uri_path, uri=True, timeout=10.0)
        else:
            conn = sqlite3.connect(normalized_path, timeout=10.0)

        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_params = tuple(params) if params is not None else ()
        cursor.execute(query, query_params)

        if cursor.description:
            columns = [col[0] for col in cursor.description]
            raw_rows = cursor.fetchmany(max_rows)
            rows = [dict(row) for row in raw_rows]
            row_count = len(rows)
        else:
            columns = []
            rows = []
            row_count = cursor.rowcount if cursor.rowcount != -1 else 0
            if not read_only:
                conn.commit()

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

        return {
            "status": "success",
            "database": os.path.basename(normalized_path),
            "columns": columns,
            "rows": rows,
            "row_count": row_count,
            "has_more": len(rows) == max_rows,
            "execution_time_ms": elapsed_ms
        }

    except sqlite3.Error as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)
        return {
            "status": "error",
            "error": f"SQLite error: {str(e)}",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": elapsed_ms
        }
    finally:
        if conn:
            conn.close()


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    """Standard entry point for MCP agent tools."""
    db_path = params.get("database_path", "")
    query = params.get("query", "")
    sql_params = params.get("params")
    read_only = params.get("read_only", True)
    max_rows = params.get("max_rows", 100)

    return execute_sqlite_query(
        database_path=db_path,
        query=query,
        params=sql_params,
        read_only=read_only,
        max_rows=max_rows
    )


if __name__ == "__main__":
    # Self-test using in-memory / temporary sqlite db
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db = tmp.name

    try:
        init_conn = sqlite3.connect(tmp_db)
        init_conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, role TEXT);")
        init_conn.execute("INSERT INTO users (name, role) VALUES ('Alice', 'Admin'), ('Bob', 'Developer');")
        init_conn.commit()
        init_conn.close()

        res = run({"database_path": tmp_db, "query": "SELECT * FROM users WHERE role = ?", "params": ["Developer"]})
        print("Test Result:", res)
        assert res["status"] == "success"
        assert res["row_count"] == 1
        assert res["rows"][0]["name"] == "Bob"
        print("✅ Self-test passed successfully!")
    finally:
        if os.path.exists(tmp_db):
            os.remove(tmp_db)
