"""Konfiguration — lädt API-Keys aus .env und stellt Settings bereit."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

# .env oder keys.env aus dem Projektverzeichnis laden
_project_root = Path(__file__).resolve().parent.parent
_env_path = _project_root / "keys.env"
if not _env_path.exists():
    _env_path = _project_root / ".env"
load_dotenv(_env_path)


class Settings(BaseModel):
    """Zentrale Konfiguration für alle API-Clients."""

    # Helius (Solana On-Chain-Daten)
    helius_api_key: str = os.getenv("HELIUS_API_KEY", "")
    helius_base_url: str = "https://api.helius.xyz"
    helius_rpc_url: str = "https://mainnet.helius-rpc.com"

    # Jupiter (Token-Preise)
    jupiter_api_key: str = os.getenv("JUPITER_API_KEY", "")
    jupiter_base_url: str = "https://api.jup.ag"

    # CoinGecko (Preis-Fallback)
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"

    # Raydium (DeFi-Pools)
    raydium_base_url: str = "https://api-v3.raydium.io"

    # Orca (Whirlpools)
    orca_base_url: str = "https://api.orca.so"

    # RugCheck (Token-Sicherheit)
    rugcheck_api_key: str = os.getenv("RUGCHECK_API_KEY", "")
    rugcheck_base_url: str = "https://api.rugcheck.xyz/v1"

    # HTTP-Client Defaults
    http_timeout: float = 30.0


# Globale Settings-Instanz
settings = Settings()
