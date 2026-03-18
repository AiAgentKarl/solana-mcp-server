"""Helius API Client — zentrale Datenquelle für Solana On-Chain-Daten."""

import httpx

from src.config import settings


class HeliusClient:
    """Async-Client für die Helius API (Wallet, Transactions, DAS)."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.helius_base_url
        self._rpc = settings.helius_rpc_url

    @property
    def _api_key(self) -> str:
        return settings.helius_api_key

    def _rpc_url(self) -> str:
        """RPC-URL mit API-Key."""
        return f"{self._rpc}/?api-key={self._api_key}"

    # --- Wallet API ---

    async def get_balances(self, address: str) -> dict:
        """SOL- und Token-Balances einer Wallet abfragen."""
        url = f"{self._base}/v0/addresses/{address}/balances"
        params = {"api-key": self._api_key}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_transaction_history(
        self, address: str, limit: int = 20
    ) -> list[dict]:
        """Letzte Transaktionen einer Wallet (Enhanced Transactions API)."""
        url = f"{self._base}/v0/addresses/{address}/transactions"
        params = {"api-key": self._api_key, "limit": limit}
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    # --- DAS API (Digital Asset Standard) ---

    async def _das_request(self, method: str, params: dict) -> dict:
        """Generischer DAS-API-Aufruf über JSON-RPC."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        resp = await self._client.post(self._rpc_url(), json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"DAS API Fehler: {data['error']}")
        return data.get("result", {})

    async def get_asset(self, mint: str) -> dict:
        """Token-Metadaten über DAS API abrufen (Name, Symbol, Supply etc.)."""
        return await self._das_request("getAsset", {"id": mint})

    async def get_assets_by_owner(
        self, owner: str, page: int = 1, limit: int = 50
    ) -> dict:
        """Alle Assets einer Wallet über DAS API abrufen."""
        return await self._das_request(
            "getAssetsByOwner",
            {"ownerAddress": owner, "page": page, "limit": limit},
        )

    async def get_token_accounts(
        self, mint: str, page: int = 1, limit: int = 20
    ) -> dict:
        """Token-Holder über DAS API abrufen."""
        return await self._das_request(
            "getTokenAccounts",
            {"mint": mint, "page": page, "limit": limit},
        )

    async def close(self):
        """HTTP-Client schließen."""
        await self._client.aclose()
