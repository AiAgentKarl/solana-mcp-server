"""Token-Tools — Preise und Metadaten für Solana-Tokens."""

from mcp.server.fastmcp import FastMCP

from src.analytics import track_call
from src.clients.helius import HeliusClient
from src.clients.jupiter import JupiterClient
from src.clients.coingecko import CoinGeckoClient

_helius = HeliusClient()
_jupiter = JupiterClient()
_coingecko = CoinGeckoClient()

# Bekannte Token-Mint-Adressen für häufige Abfragen
KNOWN_TOKENS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "ORCA": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
    "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
}


def _resolve_token(token_input: str) -> str:
    """Symbol oder Mint-Adresse auflösen — gibt immer eine Mint-Adresse zurück."""
    upper = token_input.upper()
    if upper in KNOWN_TOKENS:
        return KNOWN_TOKENS[upper]
    return token_input


def register_token_tools(mcp: FastMCP):
    """Token-bezogene MCP-Tools registrieren."""

    @mcp.tool()
    async def get_token_price(token: str) -> dict:
        """Aktuellen USD-Preis eines Solana-Tokens abfragen.

        Nutzt Jupiter als primäre Quelle, CoinGecko als Fallback.

        Args:
            token: Token-Symbol (z.B. "SOL", "BONK") oder Mint-Adresse
        """
        track_call("get_token_price")
        mint = _resolve_token(token)

        # Jupiter v3 als primäre Preisquelle
        try:
            data = await _jupiter.get_price([mint])
            if mint in data:
                token_data = data[mint]
                price = token_data.get("usdPrice")
                if price is not None:
                    price_change = token_data.get("priceChange24h", 0)
                    return {
                        "token": token,
                        "mint": mint,
                        "price_usd": float(price),
                        "price_change_24h_percent": price_change,
                        "source": "jupiter_v3",
                    }
        except Exception:
            pass  # Fallback zu CoinGecko

        # CoinGecko als Fallback
        try:
            data = await _coingecko.get_token_price([mint])
            if mint.lower() in data:
                price = data[mint.lower()].get("usd", 0)
                return {
                    "token": token,
                    "mint": mint,
                    "price_usd": price,
                    "source": "coingecko",
                    "confidence": "medium",
                }
        except Exception:
            pass

        return {"error": f"Preis für '{token}' konnte nicht ermittelt werden."}

    @mcp.tool()
    async def get_token_info(token: str) -> dict:
        """Metadaten eines Solana-Tokens abfragen.

        Gibt Name, Symbol, Supply, Decimals und Authorities zurück.

        Args:
            token: Token-Symbol (z.B. "SOL", "JUP") oder Mint-Adresse
        """
        track_call("get_token_info")
        mint = _resolve_token(token)

        try:
            asset = await _helius.get_asset(mint)

            # Relevante Infos extrahieren
            content = asset.get("content", {})
            metadata = content.get("metadata", {})
            token_info = asset.get("token_info", {})
            authorities = asset.get("authorities", [])
            supply = token_info.get("supply", 0)
            decimals = token_info.get("decimals", 0)
            human_supply = supply / (10**decimals) if decimals > 0 else supply

            # Mint Authority und Freeze Authority prüfen
            mint_authority = None
            freeze_authority = None
            for auth in authorities:
                scopes = auth.get("scopes", [])
                if "full" in scopes:
                    mint_authority = auth.get("address")
                if "freeze" in scopes:
                    freeze_authority = auth.get("address")

            return {
                "mint": mint,
                "name": metadata.get("name", "Unbekannt"),
                "symbol": metadata.get("symbol", "???"),
                "decimals": decimals,
                "total_supply": human_supply,
                "price_info": token_info.get("price_info", {}),
                "mint_authority": mint_authority,
                "freeze_authority": freeze_authority,
                "mutable": asset.get("mutable", False),
            }
        except Exception as e:
            return {"error": f"Token-Info konnte nicht abgerufen werden: {e}"}
