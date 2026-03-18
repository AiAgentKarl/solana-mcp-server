"""CoinGecko API Client — Preis-Fallback wenn Jupiter nicht liefert."""

import httpx

from src.config import settings


class CoinGeckoClient:
    """Async-Client für die CoinGecko Free API."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.coingecko_base_url

    async def get_token_price(
        self, contract_addresses: list[str], vs_currency: str = "usd"
    ) -> dict:
        """Token-Preise über Contract-Adressen auf Solana abfragen.

        Gibt ein Dict zurück: {address: {usd: price}, ...}
        """
        addresses = ",".join(contract_addresses)
        url = f"{self._base}/simple/token_price/solana"
        params = {
            "contract_addresses": addresses,
            "vs_currencies": vs_currency,
        }
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        """HTTP-Client schließen."""
        await self._client.aclose()
