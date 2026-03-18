"""Jupiter API Client — Token-Preise und Swap-Quotes auf Solana."""

import httpx

from src.config import settings


class JupiterClient:
    """Async-Client für die Jupiter Price API."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.jupiter_base_url

    async def get_price(self, mint_addresses: list[str]) -> dict:
        """Aktuelle USD-Preise für eine Liste von Token-Mint-Adressen.

        Gibt ein Dict zurück: {mint_address: {usdPrice, ...}, ...}
        Nutzt Jupiter Price API v3.
        """
        ids = ",".join(mint_addresses)
        url = f"{self._base}/price/v3"
        params = {"ids": ids}
        headers = {}
        if settings.jupiter_api_key:
            headers["x-api-key"] = settings.jupiter_api_key
        resp = await self._client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def search_token(self, query: str) -> list[dict]:
        """Token-Suche nach Name oder Symbol."""
        url = f"{self._base}/tokens/v1/search"
        params = {"query": query}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        """HTTP-Client schließen."""
        await self._client.aclose()
