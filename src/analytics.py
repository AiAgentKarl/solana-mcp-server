"""Analytics — einfaches Tracking der Tool-Nutzung.

Loggt jeden Tool-Aufruf in eine JSON-Datei (lokal).
Kann später um Remote-Analytics erweitert werden.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Analytics-Datei im Projektverzeichnis
_ANALYTICS_FILE = Path(__file__).resolve().parent.parent / "analytics.json"


def _load_stats() -> dict:
    """Aktuelle Stats laden oder leere Stats erstellen."""
    if _ANALYTICS_FILE.exists():
        try:
            return json.loads(_ANALYTICS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "total_calls": 0,
        "tools": {},
        "first_call": None,
        "last_call": None,
    }


def _save_stats(stats: dict):
    """Stats in Datei speichern."""
    try:
        _ANALYTICS_FILE.write_text(
            json.dumps(stats, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning(f"Analytics speichern fehlgeschlagen: {e}")


def track_call(tool_name: str):
    """Einen Tool-Aufruf tracken."""
    stats = _load_stats()
    now = datetime.now(timezone.utc).isoformat()

    stats["total_calls"] += 1
    stats["last_call"] = now
    if not stats["first_call"]:
        stats["first_call"] = now

    if tool_name not in stats["tools"]:
        stats["tools"][tool_name] = {"calls": 0, "last_used": None}

    stats["tools"][tool_name]["calls"] += 1
    stats["tools"][tool_name]["last_used"] = now

    _save_stats(stats)


def get_stats() -> dict:
    """Aktuelle Nutzungsstatistiken abrufen."""
    return _load_stats()
