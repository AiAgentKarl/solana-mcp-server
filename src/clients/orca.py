"""Orca API Client — Whirlpool-Daten und APYs auf Solana."""

import httpx

from src.config import settings


class OrcaClient:
    """Async-Client für die Orca Whirlpool API v2."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.orca_base_url

    async def get_whirlpools(self, limit: int = 20) -> list[dict]:
        """Top-Whirlpools auf Solana abrufen."""
        url = f"{self._base}/v2/solana/pools"
        resp = await self._client.get(url)
        resp.raise_for_status()
        data = resp.json()
        # API gibt eine Liste von Pools zurück
        pools = data if isinstance(data, list) else data.get("data", [])
        return pools[:limit]

    async def search_pools_by_token(self, token_mint: str) -> list[dict]:
        """Whirlpools suchen, die einen bestimmten Token enthalten."""
        url = f"{self._base}/v2/solana/pools/search"
        params = {"q": token_mint}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        pools = data if isinstance(data, list) else data.get("data", [])
        return pools

    async def close(self):
        """HTTP-Client schließen."""
        await self._client.aclose()
