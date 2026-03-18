"""Wallet-Tools — Balances und Transaktionshistorie abfragen."""

from mcp.server.fastmcp import FastMCP

from src.analytics import track_call
from src.clients.helius import HeliusClient

# Gemeinsame Client-Instanz für alle Wallet-Tools
_helius = HeliusClient()


def register_wallet_tools(mcp: FastMCP):
    """Wallet-bezogene MCP-Tools registrieren."""

    @mcp.tool()
    async def get_wallet_balance(wallet_address: str) -> dict:
        """SOL- und Token-Balances einer Solana-Wallet abfragen.

        Gibt die native SOL-Balance und alle Token-Positionen zurück.

        Args:
            wallet_address: Solana-Wallet-Adresse im Base58-Format
                (z.B. "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU")
        """
        track_call("get_wallet_balance")
        try:
            data = await _helius.get_balances(wallet_address)

            # SOL-Balance in lesbares Format umrechnen (Lamports -> SOL)
            native_balance = data.get("nativeBalance", 0)
            sol_balance = native_balance / 1_000_000_000

            # Token-Balances aufbereiten
            tokens = []
            for token in data.get("tokens", []):
                amount = token.get("amount", 0)
                decimals = token.get("decimals", 0)
                human_amount = amount / (10**decimals) if decimals > 0 else amount
                tokens.append({
                    "mint": token.get("mint", ""),
                    "amount": human_amount,
                    "decimals": decimals,
                    "token_account": token.get("tokenAccount", ""),
                })

            return {
                "address": wallet_address,
                "sol_balance": sol_balance,
                "token_count": len(tokens),
                "tokens": tokens,
            }
        except Exception as e:
            return {"error": f"Wallet-Balance konnte nicht abgerufen werden: {e}"}

    @mcp.tool()
    async def get_transaction_history(
        wallet_address: str, limit: int = 10
    ) -> dict:
        """Letzte Transaktionen einer Solana-Wallet abrufen.

        Zeigt die letzten Transaktionen mit Typ, Beschreibung und Zeitstempel.

        Args:
            wallet_address: Solana-Wallet-Adresse im Base58-Format
            limit: Anzahl der Transaktionen (Standard: 10, Maximum: 50)
        """
        track_call("get_transaction_history")
        try:
            limit = min(limit, 50)
            raw_txs = await _helius.get_transaction_history(
                wallet_address, limit=limit
            )

            transactions = []
            for tx in raw_txs:
                transactions.append({
                    "signature": tx.get("signature", ""),
                    "type": tx.get("type", "UNKNOWN"),
                    "description": tx.get("description", ""),
                    "timestamp": tx.get("timestamp", 0),
                    "fee": tx.get("fee", 0) / 1_000_000_000,  # Lamports -> SOL
                    "source": tx.get("source", ""),
                })

            return {
                "address": wallet_address,
                "transaction_count": len(transactions),
                "transactions": transactions,
            }
        except Exception as e:
            return {"error": f"Transaktionen konnten nicht abgerufen werden: {e}"}
