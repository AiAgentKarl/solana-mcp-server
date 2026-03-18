# Solana MCP Server

MCP-Server der AI-Agents Zugriff auf Solana-Blockchain-Daten gibt.

## Tools

| Tool | Beschreibung |
|------|-------------|
| `get_wallet_balance` | SOL + Token-Balances einer Wallet |
| `get_transaction_history` | Letzte Transaktionen einer Wallet |
| `get_token_price` | Aktueller Token-Preis (Jupiter + CoinGecko) |
| `get_token_info` | Token-Metadaten (Name, Symbol, Supply) |
| `get_defi_yields` | Top DeFi-Pool-APYs (Raydium + Orca) |
| `compare_yields` | Yield-Vergleich für einen Token |
| `check_token_safety` | Sicherheitscheck (RugCheck + On-Chain) |

## Setup

```bash
# Virtual Environment erstellen
python -m venv .venv

# Aktivieren (Windows)
.venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# .env anlegen (API-Keys eintragen)
copy .env.example .env
```

## API-Keys besorgen

| API | URL | Kosten |
|-----|-----|--------|
| Helius | https://dev.helius.xyz | Kostenlos (1M Credits/Mo) |
| Jupiter | https://portal.jup.ag | Kostenlos |
| RugCheck | https://rugcheck.xyz | Kostenlos |

CoinGecko, Raydium und Orca brauchen keinen API-Key.

## Server starten

```bash
# Mit MCP Inspector testen (Web-UI)
mcp dev src/server.py

# Oder direkt starten (stdio-Transport)
python -m src.server
```

## In Claude Desktop einbinden

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "solana": {
      "command": "python",
      "args": ["C:/Users/Chris1/Desktop/Claude_Tests/Crypto_Bot/src/server.py"],
      "env": {
        "HELIUS_API_KEY": "dein-key",
        "JUPITER_API_KEY": "dein-key",
        "RUGCHECK_API_KEY": "dein-key"
      }
    }
  }
}
```

## Lizenz

MIT
