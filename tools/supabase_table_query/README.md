# Supabase Realtime Table Query Tool

Query and insert rows in a Supabase Postgres table using the official `@supabase/supabase-js` client. Supports column selection, filtering with multiple operators, ordering, and pagination.

> Closes [#38](https://github.com/tarunjandra/agent-tools-mcp-hub/issues/38)

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `action` | `string` | No | `"query"` to read rows, `"insert"` to add a row (default `"query"`) |
| `table` | `string` | **Yes** | Supabase table name |
| `columns` | `string` | No | Comma-separated columns to select (default `"*"`) |
| `filters` | `array` | No | Filter objects: `{ column, operator, value }` |
| `order_by` | `string` | No | Column to sort results by |
| `ascending` | `boolean` | No | Sort direction (default `true`) |
| `limit` | `integer` | No | Max rows to return, 1–1000 (default `50`) |
| `offset` | `integer` | No | Rows to skip for pagination (default `0`) |
| `row` | `object` | For insert | Key-value object to insert |

### Supported Filter Operators

`eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `like`, `ilike`, `in`

## Environment Variables

| Variable | Description |
| :--- | :--- |
| `SUPABASE_URL` | Your Supabase project URL (e.g. `https://xyzcompany.supabase.co`) |
| `SUPABASE_ANON_KEY` | Your Supabase anonymous (public) API key |

## Installation & Setup

```bash
cd tools/supabase_table_query
npm install
```

## Usage Examples

### Query rows

```typescript
import { queryTable } from "./index";

const result = await queryTable("products", {
  columns: "id,name,price",
  filters: [{ column: "price", operator: "gte", value: 10 }],
  order_by: "price",
  ascending: false,
  limit: 20,
});
console.log(result);
```

### Insert a row

```typescript
import { insertRow } from "./index";

const result = await insertRow("products", {
  name: "New Widget",
  price: 29.99,
  category: "electronics",
});
console.log(result);
```

### Using the dispatcher

```typescript
import { runTool } from "./index";

// Query
const rows = await runTool("query", "users", {
  filters: [{ column: "role", operator: "eq", value: "admin" }],
  limit: 10,
});

// Insert
const inserted = await runTool("insert", "users", {
  row: { name: "Alice", role: "admin" },
});
```
