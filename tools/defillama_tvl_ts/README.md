# DefiLlama TVL & Yields Explorer (TypeScript)

Fetches current TVL, 24-hour change, chain distribution, and the ten largest yield pools for a DeFi protocol or chain through the free DefiLlama REST API.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | Yes | Protocol slug or chain name, such as `aave` or `Ethereum`. |

## Installation and usage

```bash
cd tools/defillama_tvl_ts
npm install
npm start -- aave
npm start -- Ethereum
```

The tool needs no API key. It returns `{ success: false, error }` for invalid input, unavailable protocols/chains, API errors, and network failures.
