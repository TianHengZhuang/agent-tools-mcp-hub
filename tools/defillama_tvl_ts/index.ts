const API = "https://api.llama.fi";
const YIELDS_API = "https://yields.llama.fi";

interface ProtocolResponse {
  name?: string;
  symbol?: string;
  tvl?: Array<{ date: number; totalLiquidityUSD: number }>;
  chainTvls?: Record<string, { tvl?: Array<{ date: number; totalLiquidityUSD: number }> }>;
}

interface ChainResponse {
  name: string;
  tvl: number;
  tokenSymbol?: string;
  chainId?: string;
}

interface Pool {
  pool?: string;
  project?: string;
  chain?: string;
  symbol?: string;
  tvlUsd?: number;
  apy?: number | null;
  apyBase?: number | null;
  apyReward?: number | null;
}

interface PoolsResponse { data?: Pool[] }

export interface ExplorerResult {
  success: boolean;
  data?: {
    query: string;
    query_type: "protocol" | "chain";
    tvl_usd: number;
    change_24h_percent: number | null;
    chain_distribution: Record<string, number>;
    top_yield_pools: Array<Record<string, string | number | null>>;
  };
  error?: string;
}

function normalise(value: string): string {
  return value.trim().replace(/^https?:\/\/defillama\.com\/[^/]+\//i, "").replace(/^\/+|\/+$/g, "");
}

async function request<T>(path: string, base = API): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base}${path}`, {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(15_000)
    });
  } catch (error) {
    throw new Error(`Network error contacting DefiLlama: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (!response.ok) throw new Error(`DefiLlama API returned HTTP ${response.status} for ${path}`);
  return (await response.json()) as T;
}

export function change24h(history: Array<{ date: number; totalLiquidityUSD: number }>): number | null {
  if (history.length < 2) return null;
  const ordered = [...history].sort((a, b) => a.date - b.date);
  const currentPoint = ordered[ordered.length - 1];
  const previousPoint = [...ordered].reverse().find((point) => currentPoint.date - point.date >= 23 * 60 * 60);
  if (!previousPoint) return null;
  const current = currentPoint.totalLiquidityUSD;
  const previous = previousPoint.totalLiquidityUSD;
  return previous === 0 ? null : Number((((current - previous) / previous) * 100).toFixed(2));
}

export function topPools(pools: Pool[]): Array<Record<string, string | number | null>> {
  return pools
    .filter((pool) => typeof pool.tvlUsd === "number" && typeof pool.apy === "number")
    .sort((a, b) => (b.apy ?? 0) - (a.apy ?? 0))
    .slice(0, 10)
    .map((pool) => ({
      project: pool.project ?? "",
      chain: pool.chain ?? "",
      symbol: pool.symbol ?? "",
      tvl_usd: pool.tvlUsd ?? 0,
      apy_percent: pool.apy ?? null,
      apy_base_percent: pool.apyBase ?? null,
      apy_reward_percent: pool.apyReward ?? null
    }));
}

export async function runTool(query: string): Promise<ExplorerResult> {
  const value = normalise(query);
  if (!value || value.includes("/") || value.length > 100) {
    return { success: false, error: "query must be a protocol slug or chain name, such as 'aave' or 'Ethereum'." };
  }

  try {
    let queryType: "protocol" | "chain" = "protocol";
    let tvl = 0;
    let change: number | null = null;
    const distribution: Record<string, number> = {};

    try {
      const protocol = await request<ProtocolResponse>(`/protocol/${encodeURIComponent(value)}`);
      const history = protocol.tvl ?? [];
      tvl = history.at(-1)?.totalLiquidityUSD ?? 0;
      change = change24h(history);
      for (const [chain, chainData] of Object.entries(protocol.chainTvls ?? {})) {
        distribution[chain] = chainData.tvl?.at(-1)?.totalLiquidityUSD ?? 0;
      }
    } catch (protocolError) {
      if (!(protocolError instanceof Error) || !protocolError.message.includes("HTTP 404")) throw protocolError;
      const chains = await request<ChainResponse[]>("/v2/chains");
      const chain = chains.find((item) => item.name.toLowerCase() === value.toLowerCase());
      if (!chain) throw protocolError;
      queryType = "chain";
      tvl = chain.tvl;
      distribution[chain.name] = chain.tvl;
      const history = await request<Array<{ date: number; tvl: number }>>(
        `/v2/historicalChainTvl/${encodeURIComponent(chain.name)}`
      );
      change = change24h(history.map((point) => ({ date: point.date, totalLiquidityUSD: point.tvl })));
    }

    const pools = await request<PoolsResponse>("/pools", YIELDS_API);
    const matchingPools = (pools.data ?? []).filter((pool) =>
      queryType === "chain" ? pool.chain?.toLowerCase() === value.toLowerCase() :
        pool.project?.toLowerCase() === value.toLowerCase()
    );

    return { success: true, data: {
      query: value,
      query_type: queryType,
      tvl_usd: tvl,
      change_24h_percent: change,
      chain_distribution: distribution,
      top_yield_pools: topPools(matchingPools)
    } };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : String(error) };
  }
}

if (typeof require !== "undefined" && typeof module !== "undefined" && require.main === module) {
  runTool(process.argv[2] ?? "Ethereum").then((result) => console.log(JSON.stringify(result, null, 2)));
}
