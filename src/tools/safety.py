"""Safety-Tools — Token-Sicherheitschecks auf Solana."""

from mcp.server.fastmcp import FastMCP

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

        # 1. RugCheck Report
        try:
            report = await _rugcheck.get_token_report_summary(mint)
            result["rugcheck"] = {
                "score": report.get("score", None),
                "risks": report.get("risks", []),
                "score_label": report.get("score_label", "unknown"),
            }

            # Hoher Risk-Score = Warnung
            score = report.get("score", 0)
            if score and score > 500:
                result["warnings"].append(
                    f"RugCheck Score ist hoch ({score}) — erhöhtes Risiko"
                )
        except Exception as e:
            result["rugcheck"] = {"error": str(e)}

        # 2. Mint/Freeze Authority über Helius DAS prüfen
        try:
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

            result["authorities"] = {
                "mint_authority": mint_authority,
                "freeze_authority": freeze_authority,
                "is_mutable": asset.get("mutable", False),
            }

            if mint_authority:
                result["warnings"].append(
                    "Mint Authority ist aktiv — Token-Supply kann nachträglich erhöht werden"
                )
            if freeze_authority:
                result["warnings"].append(
                    "Freeze Authority ist aktiv — Token-Transfers können eingefroren werden"
                )
            if asset.get("mutable", False):
                result["warnings"].append(
                    "Token-Metadaten sind veränderbar"
                )
        except Exception as e:
            result["authorities"] = {"error": str(e)}

        # 3. Holder-Konzentration prüfen (Top-Holder-Anteil)
        try:
            accounts = await _helius.get_token_accounts(mint, limit=20)
            token_accounts = accounts.get("token_accounts", [])

            if token_accounts:
                # Token-Info für Gesamtsupply
                asset_data = await _helius.get_asset(mint)
                token_info = asset_data.get("token_info", {})
                total_supply = token_info.get("supply", 0)

                if total_supply > 0:
                    top_holders = []
                    for acc in token_accounts[:10]:
                        amount = acc.get("amount", 0)
                        percentage = (amount / total_supply) * 100
                        top_holders.append({
                            "owner": acc.get("owner", ""),
                            "percentage": round(percentage, 2),
                        })

                    top10_total = sum(h["percentage"] for h in top_holders)
                    result["holder_concentration"] = {
                        "top_10_holders_percentage": round(top10_total, 2),
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
        except Exception as e:
            result["holder_concentration"] = {"error": str(e)}

        # Gesamtrisiko bewerten
        warning_count = len(result["warnings"])
        if warning_count == 0:
            result["overall_risk"] = "low"
        elif warning_count <= 2:
            result["overall_risk"] = "medium"
        else:
            result["overall_risk"] = "high"

        return result
