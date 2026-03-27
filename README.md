# solana-mcp-server

**Solana blockchain data for AI agents** — wallet balances, token prices, DeFi yields, whale tracking, and token safety checks.

[![PyPI version](https://badge.fury.io/py/solana-mcp-server.svg)](https://pypi.org/project/solana-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Smithery](https://smithery.ai/badge/@AiAgentKarl/solana-mcp-server)](https://smithery.ai/server/@AiAgentKarl/solana-mcp-server)

> Real-time Solana data from **Helius, Jupiter, CoinGecko, Raydium, Orca, and RugCheck**. Scam-pools auto-filtered (< $1,000 TVL).

## Quick Start

```bash
pip install solana-mcp-server
```

Add to your MCP client config:

```json
{
  "mcpServers": {
    "solana": {
      "command": "solana-server",
      "env": {
        "HELIUS_API_KEY": "your-free-key-from-helius.dev"
      }
    }
  }
}
```

Get your free Helius key at [dev.helius.xyz](https://dev.helius.xyz) (1M credits/month free).

## What Can You Do?

**Ask your AI agent things like:**
- *"What tokens does this wallet hold?"*
- *"What's the current price of SOL?"*
- *"Show me the best DeFi yields on Solana right now"*
- *"Is this token safe? Check the RugCheck score"*
- *"What are whales doing with JUP?"*

## 11 Tools

| Tool | What it does |
|------|-------------|
| `get_wallet_balance` | SOL + token balances of any wallet |
| `get_transaction_history` | Recent transactions with type and description |
| `get_token_price` | Current USD price (Jupiter primary, CoinGecko fallback) |
| `get_token_info` | Token metadata: name, symbol, supply, decimals |
| `get_defi_yields` | Top DeFi pool APRs from Raydium + Orca |
| `compare_yields` | Compare yields for a specific token across DEXs |
| `check_token_safety` | RugCheck score, holder concentration, mint/freeze authority |
| `get_whale_transactions` | Large transactions for a token |
| `track_smart_wallet` | Track a whale wallet's holdings and activity |
| `analyze_wallet_portfolio` | Full portfolio analysis with USD values |
| `get_usage_stats` | Server usage statistics |

## API Keys

| API | Free Tier | Key Required? |
|-----|-----------|---------------|
| Helius | 1M credits/month | **Yes** (free) |
| Jupiter | Unlimited | No |
| CoinGecko | 30 calls/min | No |
| Raydium | Unlimited | No |
| Orca | Unlimited | No |
| RugCheck | Unlimited | No |

## Architecture

```
src/
├── server.py       # FastMCP server
├── config.py       # API key config via .env
├── clients/        # Async HTTP clients (one per API)
└── tools/          # MCP tool definitions (wallet, token, defi, safety)
```

## Related Servers

- [cybersecurity-mcp-server](https://pypi.org/project/cybersecurity-mcp-server/) — CVE database & vulnerability intelligence
- [news-aggregator-mcp-server](https://pypi.org/project/news-aggregator-mcp-server/) — Multi-source news aggregation

## License

MIT
