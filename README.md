# Solana MCP Server

<!-- mcp-name: io.github.aiagentkarl/solana-mcp-server -->

MCP-Server der AI-Agents Zugriff auf Solana-Blockchain-Daten gibt: Wallet-Balances, Token-Preise, DeFi-Yields und Sicherheitschecks.

[![Smithery](https://smithery.ai/badge/@AiAgentKarl/solana-mcp-server)](https://smithery.ai/server/@AiAgentKarl/solana-mcp-server)

[![solana-mcp-server MCP server](https://glama.ai/mcp/servers/AiAgentKarl/solana-mcp-server/badges/card.svg)](https://glama.ai/mcp/servers/AiAgentKarl/solana-mcp-server)

## Features

| Tool | Beschreibung |
|------|-------------|
| `get_wallet_balance` | SOL- und Token-Balances einer Wallet abfragen |
| `get_transaction_history` | Letzte Transaktionen einer Wallet (Enhanced Transactions) |
| `get_token_price` | Aktueller Token-Preis via Jupiter (CoinGecko als Fallback) |
| `get_token_info` | Token-Metadaten: Name, Symbol, Supply, Decimals |
| `get_defi_yields` | Top DeFi-Pool-APYs von Raydium und Orca |
| `compare_yields` | Yield-Vergleich für einen bestimmten Token über mehrere Protokolle |
| `check_token_safety` | Sicherheitscheck: RugCheck-Score, Holder-Konzentration, Authorities |

## Schnellstart

### 1. Repository klonen und einrichten

```bash
git clone https://github.com/AiAgentKarl/solana-mcp-server.git
cd solana-mcp-server

# Virtual Environment erstellen
python -m venv .venv

# Aktivieren
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2. API-Keys besorgen

| API | URL | Kosten | Benötigt? |
|-----|-----|--------|-----------|
| Helius | https://dev.helius.xyz | Kostenlos (1M Credits/Mo) | Ja |
| Jupiter | https://portal.jup.ag | Kostenlos | Ja |
| CoinGecko | — | Kostenlos (30 Calls/Min) | Nein (kein Key nötig) |
| Raydium | — | Kostenlos | Nein (kein Key nötig) |
| Orca | — | Kostenlos | Nein (kein Key nötig) |
| RugCheck | — | Kostenlos | Nein (API öffentlich) |

### 3. Environment-Datei anlegen

Erstelle eine `.env` oder `keys.env` im Projektordner:

```env
HELIUS_API_KEY=dein-helius-key
JUPITER_API_KEY=dein-jupiter-key
```

### 4. Server starten

```bash
# Mit MCP Inspector testen (Web-UI zum Ausprobieren)
mcp dev src/server.py

# Oder direkt starten (stdio-Transport)
python -m src.server
```

## Integration

### Claude Code / Claude Desktop

Erstelle eine `.mcp.json` im Projektordner (oder `claude_desktop_config.json` für Claude Desktop):

```json
{
  "mcpServers": {
    "solana": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "src.server"],
      "env": {
        "HELIUS_API_KEY": "dein-helius-key",
        "JUPITER_API_KEY": "dein-jupiter-key"
      }
    }
  }
}
```

### Andere MCP-Clients

Der Server nutzt den **stdio-Transport** (Standard MCP). Jeder MCP-kompatible Client kann ihn einbinden — einfach `python -m src.server` als Kommando konfigurieren.

## Architektur

```
src/
├── server.py          # FastMCP Server — registriert alle Tools
├── config.py          # Lädt API-Keys aus .env, Settings via Pydantic
├── clients/           # Ein async HTTP-Client pro API
│   ├── helius.py      # Helius (Wallet, Transactions, DAS)
│   ├── jupiter.py     # Jupiter (Token-Preise)
│   ├── coingecko.py   # CoinGecko (Preis-Fallback)
│   ├── raydium.py     # Raydium (DeFi-Pools)
│   ├── orca.py        # Orca (Whirlpools)
│   └── rugcheck.py    # RugCheck (Token-Sicherheit)
└── tools/             # MCP-Tool-Definitionen
    ├── wallet.py      # get_wallet_balance, get_transaction_history
    ├── token.py       # get_token_price, get_token_info
    ├── defi.py        # get_defi_yields, compare_yields
    └── safety.py      # check_token_safety
```

## Tech Stack

- **Python 3.13** + async/await
- **MCP SDK** (FastMCP) — Tool-Registrierung und Transport
- **httpx** — Async HTTP-Client
- **Pydantic** — Settings-Validierung

## API-Hinweise

- **Helius Free Tier**: 1M Credits/Monat — reicht für normale Nutzung
- **CoinGecko Free**: 30 Calls/Min, 10.000/Monat — wird nur als Fallback genutzt
- **Raydium API**: Gelegentlich 500 Errors (serverseitig, nicht unser Problem)
- **RugCheck**: Kein API-Key nötig, API ist öffentlich
- **Scam-Filter**: DeFi-Pools mit < $1.000 TVL werden automatisch gefiltert

## Lizenz

MIT