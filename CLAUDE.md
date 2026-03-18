# Solana MCP Server — Projektanweisungen

## Projektübersicht
MCP-Server der AI-Agents Zugriff auf Solana-Blockchain-Daten gibt (Wallets, Token-Preise, DeFi-Yields, Sicherheitschecks).

## Tech Stack
- Python 3.13
- MCP SDK (FastMCP)
- httpx (async HTTP)
- Helius, Jupiter, CoinGecko, Raydium, Orca, RugCheck APIs

## Konventionen
- Code-Kommentare auf Deutsch
- Variablennamen auf Englisch
- Ein API-Client pro Datei in `src/clients/`
- Ein Tool-Modul pro Themengruppe in `src/tools/`

## Architektur
- `src/server.py` — FastMCP Server, registriert alle Tools
- `src/config.py` — Lädt .env, stellt Settings bereit
- `src/clients/` — Async HTTP-Clients für externe APIs
- `src/tools/` — MCP-Tool-Definitionen (nutzen Clients)

## Wichtige Hinweise
- Helius Free Tier: 1M Credits/Monat
- CoinGecko Free: 30 Calls/Min, 10.000/Monat
- Server läuft standardmäßig über stdio-Transport
