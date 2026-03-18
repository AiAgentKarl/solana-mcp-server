"""DeFi-Tools — Yield-Vergleiche und Pool-Daten auf Solana."""

from mcp.server.fastmcp import FastMCP

from src.clients.raydium import RaydiumClient
from src.clients.orca import OrcaClient

_raydium = RaydiumClient()
_orca = OrcaClient()


def register_defi_tools(mcp: FastMCP):
    """DeFi-bezogene MCP-Tools registrieren."""

    @mcp.tool()
    async def get_defi_yields(
        sort_by: str = "apr", limit: int = 10
    ) -> dict:
        """Top DeFi-Pool-Yields auf Solana abrufen (Raydium + Orca).

        Zeigt die besten Yield-Möglichkeiten über mehrere DEXs.

        Args:
            sort_by: Sortierung — "apr" (Rendite), "tvl" (Liquidität)
                oder "volume" (Handelsvolumen). Standard: "apr"
            limit: Anzahl der Ergebnisse pro DEX (Standard: 10, Maximum: 25)
        """
        limit = min(limit, 25)
        pools = []

        # Raydium Pools abrufen
        try:
            sort_field = {
                "apr": "apr24h",
                "tvl": "tvl",
                "volume": "volume24h",
            }.get(sort_by, "apr24h")

            ray_data = await _raydium.get_pool_list(
                sort_field=sort_field, sort_type="desc", page_size=limit
            )
            for pool in ray_data.get("data", []):
                pools.append({
                    "protocol": "Raydium",
                    "pool_id": pool.get("id", ""),
                    "token_a": pool.get("mintA", {}).get("symbol", "?"),
                    "token_b": pool.get("mintB", {}).get("symbol", "?"),
                    "apr_24h": pool.get("day", {}).get("apr", 0),
                    "apr_7d": pool.get("week", {}).get("apr", 0),
                    "tvl": pool.get("tvl", 0),
                    "volume_24h": pool.get("day", {}).get("volume", 0),
                    "fee_24h": pool.get("day", {}).get("feeApr", 0),
                    "pool_type": pool.get("type", "unknown"),
                })
        except Exception as e:
            pools.append({"protocol": "Raydium", "error": str(e)})

        # Orca Whirlpools abrufen
        try:
            orca_pools = await _orca.get_whirlpools(limit=limit)
            for pool in orca_pools:
                # Orca-Datenformat verarbeiten
                pools.append({
                    "protocol": "Orca",
                    "pool_id": pool.get("address", ""),
                    "token_a": pool.get("tokenA", {}).get("symbol", "?"),
                    "token_b": pool.get("tokenB", {}).get("symbol", "?"),
                    "apr_24h": pool.get("totalApr", {}).get("day", 0),
                    "apr_7d": pool.get("totalApr", {}).get("week", 0),
                    "tvl": pool.get("tvl", 0),
                    "volume_24h": pool.get("volume", {}).get("day", 0),
                    "fee_24h": pool.get("feeApr", {}).get("day", 0),
                    "pool_type": "concentrated",
                })
        except Exception as e:
            pools.append({"protocol": "Orca", "error": str(e)})

        # Nach gewähltem Kriterium sortieren
        sort_key = {
            "apr": "apr_24h",
            "tvl": "tvl",
            "volume": "volume_24h",
        }.get(sort_by, "apr_24h")

        valid_pools = [p for p in pools if "error" not in p]
        error_pools = [p for p in pools if "error" in p]
        valid_pools.sort(key=lambda p: p.get(sort_key, 0), reverse=True)

        return {
            "pool_count": len(valid_pools),
            "sorted_by": sort_by,
            "pools": valid_pools[:limit],
            "errors": error_pools if error_pools else None,
        }

    @mcp.tool()
    async def compare_yields(token: str, limit: int = 10) -> dict:
        """Yield-Vergleich für einen bestimmten Token über alle Solana-DEXs.

        Sucht alle Pools die den Token enthalten und vergleicht APRs.

        Args:
            token: Token-Symbol (z.B. "SOL", "USDC") oder Mint-Adresse
            limit: Maximale Anzahl Pools pro DEX (Standard: 10)
        """
        from src.tools.token import _resolve_token
        mint = _resolve_token(token)
        limit = min(limit, 25)

        pools = []

        # Raydium — Pools mit diesem Token suchen
        try:
            ray_data = await _raydium.search_pools_by_mint(mint)
            for pool in ray_data.get("data", [])[:limit]:
                pools.append({
                    "protocol": "Raydium",
                    "pool_id": pool.get("id", ""),
                    "token_a": pool.get("mintA", {}).get("symbol", "?"),
                    "token_b": pool.get("mintB", {}).get("symbol", "?"),
                    "apr_24h": pool.get("day", {}).get("apr", 0),
                    "apr_7d": pool.get("week", {}).get("apr", 0),
                    "tvl": pool.get("tvl", 0),
                    "volume_24h": pool.get("day", {}).get("volume", 0),
                    "pool_type": pool.get("type", "unknown"),
                })
        except Exception as e:
            pools.append({"protocol": "Raydium", "error": str(e)})

        # Orca — Pools mit diesem Token suchen
        try:
            orca_pools = await _orca.search_pools_by_token(mint)
            for pool in orca_pools[:limit]:
                pools.append({
                    "protocol": "Orca",
                    "pool_id": pool.get("address", ""),
                    "token_a": pool.get("tokenA", {}).get("symbol", "?"),
                    "token_b": pool.get("tokenB", {}).get("symbol", "?"),
                    "apr_24h": pool.get("totalApr", {}).get("day", 0),
                    "apr_7d": pool.get("totalApr", {}).get("week", 0),
                    "tvl": pool.get("tvl", 0),
                    "volume_24h": pool.get("volume", {}).get("day", 0),
                    "pool_type": "concentrated",
                })
        except Exception as e:
            pools.append({"protocol": "Orca", "error": str(e)})

        # Nach APR sortieren
        valid_pools = [p for p in pools if "error" not in p]
        error_pools = [p for p in pools if "error" in p]
        valid_pools.sort(key=lambda p: p.get("apr_24h", 0), reverse=True)

        return {
            "token": token,
            "mint": mint,
            "pool_count": len(valid_pools),
            "pools": valid_pools,
            "errors": error_pools if error_pools else None,
        }
