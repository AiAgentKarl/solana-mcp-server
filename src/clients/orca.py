"""Orca API Client — Whirlpool-Daten und APYs auf Solana."""

import httpx

from src.config import settings


class OrcaClient:
    """Async-Client für die Orca Whirlpool API."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.orca_base_url

    async def get_whirlpools(self, limit: int = 20) -> list[dict]:
        """Top-Whirlpools nach Volumen abrufen."""
        url = f"{self._base}/v2/whirlpool/list"
        params = {"sortBy": "volume", "sortOrder": "desc", "limit": limit}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("whirlpools", data if isinstance(data, list) else [])

    async def search_pools_by_token(self, token_mint: str) -> list[dict]:
        """Whirlpools suchen, die einen bestimmten Token enthalten."""
        url = f"{self._base}/v2/whirlpool/list"
        params = {"token": token_mint, "sortBy": "volume", "sortOrder": "desc"}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("whirlpools", data if isinstance(data, list) else [])

    async def close(self):
        """HTTP-Client schließen."""
        await self._client.aclose()
