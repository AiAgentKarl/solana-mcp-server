"""Solana MCP Server — gibt AI-Agents Zugriff auf Solana-Blockchain-Daten."""

from mcp.server.fastmcp import FastMCP

from src.tools.wallet import register_wallet_tools
from src.tools.token import register_token_tools
from src.tools.defi import register_defi_tools
from src.tools.safety import register_safety_tools

# MCP-Server erstellen
mcp = FastMCP(
    "Solana MCP Server",
    instructions=(
        "Gibt AI-Agents Zugriff auf Solana-Blockchain-Daten: "
        "Wallet-Balances, Token-Preise, DeFi-Yields und Sicherheitschecks."
    ),
)

# Alle Tools registrieren
register_wallet_tools(mcp)
register_token_tools(mcp)
register_defi_tools(mcp)
register_safety_tools(mcp)


def main():
    """Server starten (stdio-Transport für lokale Nutzung)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
