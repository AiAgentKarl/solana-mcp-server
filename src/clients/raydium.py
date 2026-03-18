"""Raydium API Client — DeFi-Pool-Daten und APYs auf Solana."""

import httpx

from src.config import settings


class RaydiumClient:
    """Async-Client für die Raydium API v3."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.raydium_base_url

    async def get_pool_list(
        self,
        pool_type: str = "all",
        sort_field: str = "volume24h",
        sort_type: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Pool-Liste mit APR-Daten abrufen.

        Args:
            pool_type: "all", "standard", "concentrated"
            sort_field: "volume24h", "apr24h", "tvl", "fee24h"
            sort_type: "desc" oder "asc"
            page: Seitennummer
            page_size: Ergebnisse pro Seite
        """
        url = f"{self._base}/pools/info/list"
        params = {
            "poolType": pool_type,
            "poolSortField": sort_field,
            "sortType": sort_type,
            "page": page,
            "pageSize": page_size,
        }
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("data", {})

    async def get_pool_by_id(self, pool_ids: list[str]) -> dict:
        """Details zu spezifischen Pools abrufen."""
        url = f"{self._base}/pools/info/ids"
        params = {"ids": ",".join(pool_ids)}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("data", {})

    async def search_pools_by_mint(self, mint: str) -> dict:
        """Pools suchen, die einen bestimmten Token enthalten."""
        url = f"{self._base}/pools/info/mint"
        params = {"mint1": mint, "poolType": "all", "poolSortField": "volume24h", "sortType": "desc", "pageSize": 20}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("data", {})

    async def close(self):
        """HTTP-Client schließen."""
        await self._client.aclose()
