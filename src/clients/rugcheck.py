"""RugCheck API Client — Token-Sicherheitschecks auf Solana."""

import httpx

from src.config import settings


class RugCheckClient:
    """Async-Client für die RugCheck API."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.rugcheck_base_url

    def _headers(self) -> dict:
        """Request-Headers mit optionalem API-Key.

        API ist öffentlich — Key nur nötig falls Rate-Limits erreicht werden.
        Placeholder-Werte werden ignoriert um 401-Fehler zu vermeiden.
        """
        headers = {}
        key = settings.rugcheck_api_key
        # Nur echte Keys senden, keine Placeholder
        if key and not key.startswith("dein-"):
            headers["X-API-KEY"] = key
        return headers

    async def get_token_report_summary(self, mint: str) -> dict:
        """Kurzfassung des Sicherheitsreports für einen Token.

        Enthält: Risk Score, identifizierte Risiken, Gesamtbewertung.
        """
        url = f"{self._base}/tokens/{mint}/report/summary"
        resp = await self._client.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def get_token_report(self, mint: str) -> dict:
        """Voller Sicherheitsreport für einen Token.

        Enthält: Detaillierte Risikoanalyse, Holder-Verteilung,
        Liquidity-Daten, Mint/Freeze-Authority-Status.
        """
        url = f"{self._base}/tokens/{mint}/report"
        resp = await self._client.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        """HTTP-Client schließen."""
        await self._client.aclose()
