import assert from "node:assert/strict";
import test from "node:test";
import { change24h, topPools } from "./index.ts";

test("change24h uses a point at least one day old", () => {
  const now = 1_700_000_000;
  assert.equal(change24h([
    { date: now - 86_400, totalLiquidityUSD: 100 },
    { date: now, totalLiquidityUSD: 125 }
  ]), 25);
});

test("change24h returns null without a daily comparison point", () => {
  assert.equal(change24h([
    { date: 1_700_000_000 - 3_600, totalLiquidityUSD: 100 },
    { date: 1_700_000_000, totalLiquidityUSD: 125 }
  ]), null);
});

test("topPools orders matching pools by APY", () => {
  const result = topPools([
    { project: "aave", chain: "Ethereum", symbol: "USDC", tvlUsd: 1_000_000, apy: 2 },
    { project: "aave", chain: "Ethereum", symbol: "DAI", tvlUsd: 100_000, apy: 12 }
  ]);
  assert.equal(result[0].symbol, "DAI");
});
