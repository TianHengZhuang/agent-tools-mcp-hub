/**
 * Supabase Realtime Table Query Tool for AI Agents & MCP Hub.
 * Queries rows from a Supabase Postgres table using @supabase/supabase-js.
 */

import { createClient, SupabaseClient } from "@supabase/supabase-js";

interface QueryResult {
  success: boolean;
  data?: Record<string, unknown>[];
  count?: number;
  table?: string;
  error?: string;
}

type SupabaseRow = Record<string, unknown>;

interface FilterOption {
  column: string;
  operator: "eq" | "neq" | "gt" | "gte" | "lt" | "lte" | "like" | "ilike" | "in";
  value: unknown;
}

function getClient(
  supabaseUrl?: string,
  supabaseKey?: string
): { client: SupabaseClient } | { error: string } {
  const url = supabaseUrl || process.env.SUPABASE_URL;
  const key = supabaseKey || process.env.SUPABASE_ANON_KEY;

  if (!url) {
    return {
      error:
        "Supabase URL is required. Pass supabase_url or set the SUPABASE_URL environment variable.",
    };
  }
  if (!key) {
    return {
      error:
        "Supabase anon key is required. Pass supabase_key or set the SUPABASE_ANON_KEY environment variable.",
    };
  }

  return { client: createClient(url, key) };
}

function applyFilter(
  query: any,
  filter: FilterOption
): any {
  const { column, operator, value } = filter;
  switch (operator) {
    case "eq":
      return query.eq(column, value);
    case "neq":
      return query.neq(column, value);
    case "gt":
      return query.gt(column, value);
    case "gte":
      return query.gte(column, value);
    case "lt":
      return query.lt(column, value);
    case "lte":
      return query.lte(column, value);
    case "like":
      return query.like(column, value);
    case "ilike":
      return query.ilike(column, value);
    case "in":
      return query.in(column, Array.isArray(value) ? value : [value]);
    default:
      return query;
  }
}

/**
 * Queries rows from a Supabase Postgres table with optional filtering,
 * column selection, ordering, and pagination.
 */
async function queryTable(
  table: string,
  options: {
    columns?: string;
    filters?: FilterOption[];
    order_by?: string;
    ascending?: boolean;
    limit?: number;
    offset?: number;
    supabase_url?: string;
    supabase_key?: string;
  } = {}
): Promise<QueryResult> {
  if (!table || !table.trim()) {
    return { success: false, error: "Table name is required." };
  }

  const result = getClient(options.supabase_url, options.supabase_key);
  if ("error" in result) {
    return { success: false, error: result.error };
  }

  const { client } = result;
  const selectColumns = options.columns?.trim() || "*";
  const limit = Math.min(Math.max(options.limit ?? 50, 1), 1000);
  const offset = Math.max(options.offset ?? 0, 0);

  try {
    let query = client.from(table.trim()).select(selectColumns, { count: "exact" }) as any;

    if (options.filters && Array.isArray(options.filters)) {
      for (const filter of options.filters) {
        if (filter.column && filter.operator) {
          query = applyFilter(query, filter);
        }
      }
    }

    if (options.order_by) {
      query = query.order(options.order_by, {
        ascending: options.ascending ?? true,
      });
    }

    query = query.range(offset, offset + limit - 1);

    const { data, error, count } = await query;

    if (error) {
      return {
        success: false,
        error: `Supabase query error: ${error.message} (code: ${error.code})`,
      };
    }

    return {
      success: true,
      table: table.trim(),
      count: count ?? (data?.length || 0),
      data: (data as SupabaseRow[]) || [],
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      success: false,
      error: `Unexpected error querying Supabase: ${message}`,
    };
  }
}

/**
 * Inserts a single row into a Supabase table and returns the created record.
 */
async function insertRow(
  table: string,
  row: Record<string, unknown>,
  options: {
    supabase_url?: string;
    supabase_key?: string;
  } = {}
): Promise<QueryResult> {
  if (!table || !table.trim()) {
    return { success: false, error: "Table name is required." };
  }
  if (!row || Object.keys(row).length === 0) {
    return { success: false, error: "Row data cannot be empty." };
  }

  const result = getClient(options.supabase_url, options.supabase_key);
  if ("error" in result) {
    return { success: false, error: result.error };
  }

  try {
    const { data, error } = await (result.client
      .from(table.trim())
      .insert(row)
      .select() as any);

    if (error) {
      return {
        success: false,
        error: `Supabase insert error: ${error.message} (code: ${error.code})`,
      };
    }

    return {
      success: true,
      table: table.trim(),
      count: data?.length || 0,
      data: (data as SupabaseRow[]) || [],
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      success: false,
      error: `Unexpected error inserting row: ${message}`,
    };
  }
}

/**
 * Main dispatcher entrypoint for agent frameworks.
 */
async function runTool(
  action: string,
  table: string,
  options: Record<string, any> = {}
): Promise<QueryResult> {
  switch (action) {
    case "query":
      return queryTable(table, options);
    case "insert":
      return insertRow(table, options.row || {}, options);
    default:
      return {
        success: false,
        error: `Invalid action '${action}'. Must be 'query' or 'insert'.`,
      };
  }
}

export { queryTable, insertRow, runTool };

// Self-test when run directly
(async () => {
  console.log("Supabase Table Query Tool loaded.");
  console.log(
    "Set SUPABASE_URL and SUPABASE_ANON_KEY to run a live query.\n"
  );
  console.log("Example (expected graceful error without credentials):");
  const result = await runTool("query", "users", { limit: 5 });
  console.log(JSON.stringify(result, null, 2));
})();
