"""Safety-Tools — Token-Sicherheitschecks auf Solana."""

from mcp.server.fastmcp import FastMCP

from src.analytics import track_call
from src.clients.rugcheck import RugCheckClient
from src.clients.helius import HeliusClient

_rugcheck = RugCheckClient()
_helius = HeliusClient()


def register_safety_tools(mcp: FastMCP):
    """Sicherheits-bezogene MCP-Tools registrieren."""

    @mcp.tool()
    async def check_token_safety(token: str) -> dict:
        """Sicherheitscheck für einen Solana-Token durchführen.

        Prüft: RugCheck-Score, Mint/Freeze-Authority, Holder-Konzentration
        und bekannte Risiken. Hilfreich um Scam-Tokens und Honeypots
        zu erkennen.

        Args:
            token: Token-Symbol (z.B. "BONK") oder Mint-Adresse
        """
        track_call("check_token_safety")
        from src.tools.token import _resolve_token
        mint = _resolve_token(token)

        result = {
            "token": token,
            "mint": mint,
            "rugcheck": None,
            "authorities": None,
            "holder_concentration": None,
            "overall_risk": "unknown",
            "warnings": [],
        }

        # 1. RugCheck voller Report (öffentlich, kein Key nötig)
        rugcheck_report = None
        try:
            rugcheck_report = await _rugcheck.get_token_report(mint)

            result["rugcheck"] = {
                "score": rugcheck_report.get("score", None),
                "score_normalised": rugcheck_report.get("score_normalised", None),
                "risks": rugcheck_report.get("risks", []),
                "rugged": rugcheck_report.get("rugged", False),
                "total_market_liquidity": rugcheck_report.get("totalMarketLiquidity", 0),
            }

            # Hoher Risk-Score = Warnung
            score = rugcheck_report.get("score", 0)
            if score and score > 500:
                result["warnings"].append(
                    f"RugCheck Score ist hoch ({score}) — erhöhtes Risiko"
                )

            # Rugged?
            if rugcheck_report.get("rugged"):
                result["warnings"].append("Token wurde als RUGGED markiert!")

        except Exception as e:
            result["rugcheck"] = {"error": str(e)}

        # 2. Mint/Freeze Authority — aus RugCheck oder Helius DAS
        try:
            if rugcheck_report:
                # RugCheck Report hat diese Daten bereits
                token_data = rugcheck_report.get("token", {})
                mint_authority = rugcheck_report.get("mintAuthority") or token_data.get("mintAuthority")
                freeze_authority = rugcheck_report.get("freezeAuthority") or token_data.get("freezeAuthority")
                is_mutable = False
                token_meta = rugcheck_report.get("tokenMeta", {})
                if token_meta:
                    is_mutable = token_meta.get("mutable", False)
            else:
                # Fallback: Helius DAS API
                asset = await _helius.get_asset(mint)
                authorities = asset.get("authorities", [])
                mint_authority = None
                freeze_authority = None
                for auth in authorities:
                    scopes = auth.get("scopes", [])
                    if "full" in scopes:
                        mint_authority = auth.get("address")
                    if "freeze" in scopes:
                        freeze_authority = auth.get("address")
                is_mutable = asset.get("mutable", False)

            result["authorities"] = {
                "mint_authority": mint_authority,
                "freeze_authority": freeze_authority,
                "is_mutable": is_mutable,
            }

            if mint_authority:
                result["warnings"].append(
                    "Mint Authority ist aktiv — Token-Supply kann nachträglich erhöht werden"
                )
            if freeze_authority:
                result["warnings"].append(
                    "Freeze Authority ist aktiv — Token-Transfers können eingefroren werden"
                )
            if is_mutable:
                result["warnings"].append(
                    "Token-Metadaten sind veränderbar"
                )
        except Exception as e:
            result["authorities"] = {"error": str(e)}

        # 3. Holder-Konzentration — aus RugCheck topHolders
        try:
            top_holders_data = None
            if rugcheck_report:
                top_holders_data = rugcheck_report.get("topHolders")

            if top_holders_data:
                top_holders = []
                for h in top_holders_data[:10]:
                    top_holders.append({
                        "owner": h.get("owner", ""),
                        "percentage": round(h.get("pct", 0), 2),
                        "ui_amount": h.get("uiAmountString", ""),
                        "insider": h.get("insider", False),
                    })

                top10_total = sum(h["percentage"] for h in top_holders)
                insider_count = sum(1 for h in top_holders if h["insider"])

                result["holder_concentration"] = {
                    "top_10_holders_percentage": round(top10_total, 2),
                    "insider_count": insider_count,
                    "total_holders": rugcheck_report.get("totalHolders", 0),
                    "top_holders": top_holders,
                }

                if top10_total > 80:
                    result["warnings"].append(
                        f"Top 10 Holder besitzen {top10_total:.1f}% — extreme Konzentration"
                    )
                elif top10_total > 50:
                    result["warnings"].append(
                        f"Top 10 Holder besitzen {top10_total:.1f}% — hohe Konzentration"
                    )

                if insider_count > 0:
                    result["warnings"].append(
                        f"{insider_count} Insider unter den Top-Holdern erkannt"
                    )
            else:
                result["holder_concentration"] = {
                    "info": "Keine Top-Holder-Daten verfügbar (Token hat zu viele Holder)"
                }

        except Exception as e:
            result["holder_concentration"] = {"error": str(e)}

        # Gesamtrisiko bewerten
        warning_count = len(result["warnings"])
        if rugcheck_report and rugcheck_report.get("rugged"):
            result["overall_risk"] = "critical"
        elif warning_count == 0:
            result["overall_risk"] = "low"
        elif warning_count <= 2:
            result["overall_risk"] = "medium"
        else:
            result["overall_risk"] = "high"

        return result
