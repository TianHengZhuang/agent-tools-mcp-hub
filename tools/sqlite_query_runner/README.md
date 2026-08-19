# SQLite Query Runner Tool

Safely execute SQL queries against local SQLite database files with parameterized execution, schema introspection, and read-only safeguards.

## Features

- **Read-Only Protection**: Blocks DDL/DML write statements (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`) when `read_only=True` (default).
- **Parameterized Queries**: Prevents SQL injection vulnerabilities by passing tuples/lists of parameters.
- **Structured JSON Output**: Returns structured list of key-value row mappings alongside column schemas and execution time telemetry.
- **Configurable Limits**: Cap maximum returned rows via `max_rows` (default `100`) to protect agent memory.

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `database_path` | `string` | **Yes** | — | Path to the SQLite database file (`.db`, `.sqlite`, `.sqlite3`) |
| `query` | `string` | **Yes** | — | SQL query string (e.g. `SELECT`, `PRAGMA table_info`, `EXPLAIN`) |
| `params` | `array` | No | `[]` | Positional parameter values for parameterized SQL execution |
| `read_only` | `boolean` | No | `true` | When true, enforces strict read-only query validation |
| `max_rows` | `integer` | No | `100` | Maximum number of rows to retrieve |

## Example Usage

### 1. Simple Query with Parameter Binding
```json
{
  "database_path": "/path/to/app.db",
  "query": "SELECT id, username, email FROM users WHERE status = ? LIMIT 10",
  "params": ["active"],
  "read_only": true
}
```

### 2. Schema Introspection
```json
{
  "database_path": "/path/to/app.db",
  "query": "PRAGMA table_info(users);",
  "read_only": true
}
```

### Response Format
```json
{
  "status": "success",
  "database": "app.db",
  "columns": ["id", "username", "email"],
  "rows": [
    { "id": 1, "username": "alice", "email": "alice@example.com" },
    { "id": 2, "username": "bob", "email": "bob@example.com" }
  ],
  "row_count": 2,
  "has_more": false,
  "execution_time_ms": 1.24
}
```
