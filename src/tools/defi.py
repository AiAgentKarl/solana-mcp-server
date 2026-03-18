"""DeFi-Tools — Yield-Vergleiche und Pool-Daten auf Solana."""

from mcp.server.fastmcp import FastMCP

from src.clients.raydium import RaydiumClient
from src.clients.orca import OrcaClient

_raydium = RaydiumClient()
_orca = OrcaClient()

# Mindest-TVL um Scam-Pools rauszufiltern (Pools mit $0 TVL sind wertlos)
MIN_TVL_USD = 1000


def _parse_raydium_pool(pool: dict) -> dict:
    """Raydium Pool-Daten in einheitliches Format bringen."""
    tvl = pool.get("tvl", 0) or 0
    return {
        "protocol": "Raydium",
        "pool_id": pool.get("id", ""),
        "token_a": pool.get("mintA", {}).get("symbol", "?"),
        "token_b": pool.get("mintB", {}).get("symbol", "?"),
        "apr_24h": pool.get("day", {}).get("apr", 0) or 0,
        "apr_7d": pool.get("week", {}).get("apr", 0) or 0,
        "tvl": tvl,
        "volume_24h": pool.get("day", {}).get("volume", 0) or 0,
        "pool_type": pool.get("type", "unknown"),
    }


def _parse_orca_pool(pool: dict) -> dict:
    """Orca Pool-Daten in einheitliches Format bringen."""
    stats_24h = pool.get("stats", {}).get("24h", {})
    stats_7d = pool.get("stats", {}).get("7d", {})
    tvl = pool.get("tvlUsdc", 0) or 0

    # yieldOverTvl ist ein Dezimalwert (0.002 = 0.2% pro Tag)
    # Auf annualisierte APR umrechnen: daily * 365
    daily_yield = float(stats_24h.get("yieldOverTvl", 0) or 0)
    weekly_yield = float(stats_7d.get("yieldOverTvl", 0) or 0)
    apr_24h = daily_yield * 365 * 100  # In Prozent
    apr_7d = (weekly_yield / 7) * 365 * 100 if weekly_yield else 0

    return {
        "protocol": "Orca",
        "pool_id": pool.get("address", ""),
        "token_a": pool.get("tokenA", {}).get("symbol", "?"),
        "token_b": pool.get("tokenB", {}).get("symbol", "?"),
        "apr_24h": round(apr_24h, 2),
        "apr_7d": round(apr_7d, 2),
        "tvl": float(tvl),
        "volume_24h": float(stats_24h.get("volume", 0) or 0),
        "pool_type": "concentrated",
    }


def register_defi_tools(mcp: FastMCP):
    """DeFi-bezogene MCP-Tools registrieren."""

    @mcp.tool()
    async def get_defi_yields(
        sort_by: str = "apr", limit: int = 10
    ) -> dict:
        """Top DeFi-Pool-Yields auf Solana abrufen (Raydium + Orca).

        Zeigt die besten Yield-Möglichkeiten über mehrere DEXs.
        Filtert Scam-Pools automatisch raus (Mindest-TVL: $1.000).

        Args:
            sort_by: Sortierung — "apr" (Rendite), "tvl" (Liquidität)
                oder "volume" (Handelsvolumen). Standard: "apr"
            limit: Anzahl der Ergebnisse gesamt (Standard: 10, Maximum: 25)
        """
        limit = min(limit, 25)
        pools = []

        # Raydium Pools abrufen (mehr holen, weil wir filtern)
        try:
            sort_field = {
                "apr": "apr24h",
                "tvl": "tvl",
                "volume": "volume24h",
            }.get(sort_by, "apr24h")

            ray_data = await _raydium.get_pool_list(
                sort_field=sort_field, sort_type="desc", page_size=50
            )
            for pool in ray_data.get("data", []):
                parsed = _parse_raydium_pool(pool)
                if parsed["tvl"] >= MIN_TVL_USD:
                    pools.append(parsed)
        except Exception as e:
            pools.append({"protocol": "Raydium", "error": str(e)})

        # Orca Whirlpools abrufen
        try:
            orca_pools = await _orca.get_whirlpools(limit=50)
            for pool in orca_pools:
                parsed = _parse_orca_pool(pool)
                if parsed["tvl"] >= MIN_TVL_USD:
                    pools.append(parsed)
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
            "pool_count": len(valid_pools[:limit]),
            "sorted_by": sort_by,
            "min_tvl_filter": f"${MIN_TVL_USD:,}",
            "pools": valid_pools[:limit],
            "errors": error_pools if error_pools else None,
        }

    @mcp.tool()
    async def compare_yields(token: str, limit: int = 10) -> dict:
        """Yield-Vergleich für einen bestimmten Token über alle Solana-DEXs.

        Sucht alle Pools die den Token enthalten und vergleicht APRs.
        Filtert Scam-Pools automatisch raus.

        Args:
            token: Token-Symbol (z.B. "SOL", "USDC") oder Mint-Adresse
            limit: Maximale Anzahl Pools gesamt (Standard: 10)
        """
        from src.tools.token import _resolve_token
        mint = _resolve_token(token)
        limit = min(limit, 25)

        pools = []

        # Raydium — Pools mit diesem Token suchen
        try:
            ray_data = await _raydium.search_pools_by_mint(mint)
            for pool in ray_data.get("data", []):
                parsed = _parse_raydium_pool(pool)
                if parsed["tvl"] >= MIN_TVL_USD:
                    pools.append(parsed)
        except Exception as e:
            pools.append({"protocol": "Raydium", "error": str(e)})

        # Orca — Pools mit diesem Token suchen (Symbol + Mint)
        try:
            # Orca-Suche funktioniert besser mit Symbol als mit Mint
            search_query = token.upper() if len(token) <= 10 else mint
            orca_pools = await _orca.search_pools_by_token(search_query)
            for pool in orca_pools:
                parsed = _parse_orca_pool(pool)
                if parsed["tvl"] >= MIN_TVL_USD:
                    pools.append(parsed)
        except Exception as e:
            pools.append({"protocol": "Orca", "error": str(e)})

        # Nach APR sortieren
        valid_pools = [p for p in pools if "error" not in p]
        error_pools = [p for p in pools if "error" in p]
        valid_pools.sort(key=lambda p: p.get("apr_24h", 0), reverse=True)

        return {
            "token": token,
            "mint": mint,
            "pool_count": len(valid_pools[:limit]),
            "min_tvl_filter": f"${MIN_TVL_USD:,}",
            "pools": valid_pools[:limit],
            "errors": error_pools if error_pools else None,
        }
