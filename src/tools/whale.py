"""Whale-Tools — Portfolio-Analyse, Whale-Tracking und Smart-Money-Erkennung."""

from mcp.server.fastmcp import FastMCP

from src.analytics import track_call
from src.clients.helius import HeliusClient
from src.clients.jupiter import JupiterClient
from src.clients.rugcheck import RugCheckClient

_helius = HeliusClient()
_jupiter = JupiterClient()
_rugcheck = RugCheckClient()


def register_whale_tools(mcp: FastMCP):
    """Whale-Tracking und Portfolio-Analyse MCP-Tools registrieren."""

    @mcp.tool()
    async def analyze_wallet_portfolio(wallet_address: str) -> dict:
        """Komplette Portfolio-Analyse einer Solana-Wallet.

        Zeigt: Gesamtwert in USD, Top-Holdings nach Wert, SOL-Balance,
        Diversifikation und Token-Verteilung. Perfekt um eine Wallet
        schnell einzuschätzen.

        Args:
            wallet_address: Solana-Wallet-Adresse im Base58-Format
        """
        track_call("analyze_wallet_portfolio")
        try:
            # Alle Balances holen
            data = await _helius.get_balances(wallet_address)
            native_lamports = data.get("nativeBalance", 0)
            sol_balance = native_lamports / 1_000_000_000
            raw_tokens = data.get("tokens", [])

            # Token-Beträge in lesbares Format
            tokens_with_amounts = []
            mint_list = []
            for t in raw_tokens:
                amount = t.get("amount", 0)
                decimals = t.get("decimals", 0)
                if amount == 0:
                    continue
                human_amount = amount / (10 ** decimals) if decimals > 0 else amount
                mint = t.get("mint", "")
                tokens_with_amounts.append({
                    "mint": mint,
                    "amount": human_amount,
                    "decimals": decimals,
                })
                mint_list.append(mint)

            # Preise für alle Tokens + SOL in einem Batch holen
            from src.tools.token import KNOWN_TOKENS
            sol_mint = KNOWN_TOKENS["SOL"]
            all_mints = [sol_mint] + mint_list[:25]  # Max 25 Tokens (API-Limit)

            prices = {}
            try:
                price_data = await _jupiter.get_price(all_mints)
                for mint_addr, info in price_data.items():
                    p = info.get("usdPrice")
                    if p is not None:
                        prices[mint_addr] = float(p)
            except Exception:
                pass

            # SOL-Wert berechnen
            sol_price = prices.get(sol_mint, 0)
            sol_value_usd = sol_balance * sol_price

            # Token-Werte berechnen
            holdings = []
            total_token_value = 0
            for t in tokens_with_amounts:
                mint = t["mint"]
                price = prices.get(mint, 0)
                value_usd = t["amount"] * price
                total_token_value += value_usd
                holdings.append({
                    "mint": mint,
                    "amount": t["amount"],
                    "price_usd": price,
                    "value_usd": round(value_usd, 2),
                })

            # Nach Wert sortieren, Top 15 zeigen
            holdings.sort(key=lambda x: x["value_usd"], reverse=True)
            top_holdings = holdings[:15]

            # Token-Namen über DAS holen für Top-Holdings
            for h in top_holdings[:10]:
                if h["value_usd"] > 0:
                    try:
                        asset = await _helius.get_asset(h["mint"])
                        meta = asset.get("content", {}).get("metadata", {})
                        h["name"] = meta.get("name", "")
                        h["symbol"] = meta.get("symbol", "")
                    except Exception:
                        h["name"] = ""
                        h["symbol"] = ""

            total_value = sol_value_usd + total_token_value

            return {
                "wallet": wallet_address,
                "total_value_usd": round(total_value, 2),
                "sol_balance": round(sol_balance, 4),
                "sol_value_usd": round(sol_value_usd, 2),
                "sol_price_usd": round(sol_price, 2),
                "token_count": len(tokens_with_amounts),
                "top_holdings": top_holdings,
                "portfolio_summary": {
                    "sol_percentage": round((sol_value_usd / total_value * 100) if total_value > 0 else 0, 1),
                    "top_5_percentage": round(
                        (sum(h["value_usd"] for h in top_holdings[:5]) / total_value * 100) if total_value > 0 else 0,
                        1
                    ),
                },
            }
        except Exception as e:
            return {"error": f"Portfolio-Analyse fehlgeschlagen: {e}"}

    @mcp.tool()
    async def get_whale_transactions(
        token: str, min_usd_value: float = 10000, limit: int = 10
    ) -> dict:
        """Große Whale-Transaktionen für einen Token finden.

        Analysiert die Top-Holder eines Tokens und zeigt deren letzte
        große Bewegungen. Perfekt um zu sehen, was die Großen machen.

        Args:
            token: Token-Symbol (z.B. "SOL", "WIF") oder Mint-Adresse
            min_usd_value: Mindest-USD-Wert pro Transaktion (Standard: 10.000)
            limit: Maximale Anzahl Transaktionen (Standard: 10, Max: 25)
        """
        track_call("get_whale_transactions")
        from src.tools.token import _resolve_token
        mint = _resolve_token(token)
        limit = min(limit, 25)

        try:
            # Token-Preis holen
            token_price = 0
            try:
                price_data = await _jupiter.get_price([mint])
                if mint in price_data:
                    p = price_data[mint].get("usdPrice")
                    if p is not None:
                        token_price = float(p)
            except Exception:
                pass

            # Top-Holder über RugCheck holen
            report = await _rugcheck.get_token_report(mint)
            top_holders = report.get("topHolders") or []
            token_info = report.get("token", {})
            decimals = token_info.get("decimals", 6)
            token_name = report.get("tokenMeta", {}).get("symbol", token)

            if not top_holders:
                return {
                    "token": token,
                    "info": "Keine Top-Holder-Daten verfügbar für diesen Token.",
                }

            # Transaktionen der Top 5 Whales analysieren
            whale_txs = []
            whales_checked = 0

            for holder in top_holders[:5]:
                owner = holder.get("owner", "")
                holder_pct = holder.get("pct", 0)
                if not owner:
                    continue

                whales_checked += 1
                try:
                    txs = await _helius.get_transaction_history(owner, limit=10)
                    for tx in txs:
                        # Nur Token-Transfers dieses Tokens filtern
                        for transfer in tx.get("tokenTransfers", []):
                            if transfer.get("mint") != mint:
                                continue

                            amount = transfer.get("tokenAmount", 0)
                            if isinstance(amount, str):
                                amount = float(amount)

                            usd_value = amount * token_price
                            if usd_value < min_usd_value:
                                continue

                            is_buy = transfer.get("toUserAccount") == owner
                            whale_txs.append({
                                "whale": owner,
                                "whale_holding_pct": round(holder_pct, 2),
                                "action": "BUY" if is_buy else "SELL",
                                "amount": round(amount, 2),
                                "usd_value": round(usd_value, 2),
                                "timestamp": tx.get("timestamp", 0),
                                "signature": tx.get("signature", ""),
                                "description": tx.get("description", ""),
                            })
                except Exception:
                    continue

            # Nach Wert sortieren
            whale_txs.sort(key=lambda x: x["usd_value"], reverse=True)
            whale_txs = whale_txs[:limit]

            # Zusammenfassung: Kaufen oder Verkaufen die Whales?
            buys = [t for t in whale_txs if t["action"] == "BUY"]
            sells = [t for t in whale_txs if t["action"] == "SELL"]
            buy_volume = sum(t["usd_value"] for t in buys)
            sell_volume = sum(t["usd_value"] for t in sells)

            if buy_volume > sell_volume * 1.5:
                sentiment = "BULLISH — Whales akkumulieren"
            elif sell_volume > buy_volume * 1.5:
                sentiment = "BEARISH — Whales verkaufen"
            else:
                sentiment = "NEUTRAL — gemischte Signale"

            return {
                "token": token_name,
                "mint": mint,
                "token_price_usd": token_price,
                "whales_analyzed": whales_checked,
                "whale_sentiment": sentiment,
                "buy_volume_usd": round(buy_volume, 2),
                "sell_volume_usd": round(sell_volume, 2),
                "transactions": whale_txs,
            }
        except Exception as e:
            return {"error": f"Whale-Tracking fehlgeschlagen: {e}"}

    @mcp.tool()
    async def track_smart_wallet(wallet_address: str) -> dict:
        """Eine bekannte Whale-Wallet tracken und analysieren.

        Zeigt: Aktuelle Top-Holdings, letzte Käufe/Verkäufe,
        welche Tokens akkumuliert oder abgestoßen werden.
        Perfekt um Smart Money zu folgen.

        Args:
            wallet_address: Solana-Wallet-Adresse des Whales
        """
        track_call("track_smart_wallet")
        try:
            # Aktuelle Balances
            data = await _helius.get_balances(wallet_address)
            native_lamports = data.get("nativeBalance", 0)
            sol_balance = native_lamports / 1_000_000_000
            raw_tokens = data.get("tokens", [])

            # Nur Tokens mit Bestand
            held_tokens = []
            mint_list = []
            for t in raw_tokens:
                amount = t.get("amount", 0)
                decimals = t.get("decimals", 0)
                if amount == 0:
                    continue
                human_amount = amount / (10 ** decimals) if decimals > 0 else amount
                mint = t.get("mint", "")
                held_tokens.append({"mint": mint, "amount": human_amount})
                mint_list.append(mint)

            # Preise holen
            from src.tools.token import KNOWN_TOKENS
            sol_mint = KNOWN_TOKENS["SOL"]
            price_mints = [sol_mint] + mint_list[:25]
            prices = {}
            try:
                price_data = await _jupiter.get_price(price_mints)
                for m, info in price_data.items():
                    p = info.get("usdPrice")
                    if p is not None:
                        prices[m] = float(p)
            except Exception:
                pass

            # Holdings mit Wert
            holdings = []
            for t in held_tokens:
                price = prices.get(t["mint"], 0)
                value = t["amount"] * price
                holdings.append({
                    "mint": t["mint"],
                    "amount": t["amount"],
                    "value_usd": round(value, 2),
                })
            holdings.sort(key=lambda x: x["value_usd"], reverse=True)

            # Namen für Top 10
            for h in holdings[:10]:
                if h["value_usd"] > 0:
                    try:
                        asset = await _helius.get_asset(h["mint"])
                        meta = asset.get("content", {}).get("metadata", {})
                        h["name"] = meta.get("name", "")
                        h["symbol"] = meta.get("symbol", "")
                    except Exception:
                        pass

            # Letzte Transaktionen analysieren
            txs = await _helius.get_transaction_history(wallet_address, limit=20)
            recent_activity = []
            tokens_bought = {}
            tokens_sold = {}

            for tx in txs:
                for transfer in tx.get("tokenTransfers", []):
                    mint = transfer.get("mint", "")
                    amount = transfer.get("tokenAmount", 0)
                    if isinstance(amount, str):
                        amount = float(amount)
                    if amount == 0:
                        continue

                    is_buy = transfer.get("toUserAccount") == wallet_address
                    price = prices.get(mint, 0)
                    usd_value = amount * price

                    if is_buy:
                        tokens_bought[mint] = tokens_bought.get(mint, 0) + usd_value
                    else:
                        tokens_sold[mint] = tokens_sold.get(mint, 0) + usd_value

                    recent_activity.append({
                        "action": "BUY" if is_buy else "SELL",
                        "mint": mint,
                        "amount": round(amount, 4),
                        "usd_value": round(usd_value, 2),
                        "timestamp": tx.get("timestamp", 0),
                        "description": tx.get("description", ""),
                    })

            # Akkumulation vs. Distribution erkennen
            accumulating = sorted(tokens_bought.items(), key=lambda x: x[1], reverse=True)[:5]
            distributing = sorted(tokens_sold.items(), key=lambda x: x[1], reverse=True)[:5]

            # Token-Namen für Akkumulation/Distribution
            acc_list = []
            for mint, vol in accumulating:
                name = mint[:8] + "..."
                for h in holdings:
                    if h["mint"] == mint and h.get("symbol"):
                        name = h["symbol"]
                        break
                acc_list.append({"token": name, "mint": mint, "buy_volume_usd": round(vol, 2)})

            dist_list = []
            for mint, vol in distributing:
                name = mint[:8] + "..."
                for h in holdings:
                    if h["mint"] == mint and h.get("symbol"):
                        name = h["symbol"]
                        break
                dist_list.append({"token": name, "mint": mint, "sell_volume_usd": round(vol, 2)})

            sol_price = prices.get(sol_mint, 0)
            total_value = sol_balance * sol_price + sum(h["value_usd"] for h in holdings)

            return {
                "wallet": wallet_address,
                "total_value_usd": round(total_value, 2),
                "sol_balance": round(sol_balance, 4),
                "token_count": len(held_tokens),
                "top_holdings": holdings[:10],
                "recent_activity": recent_activity[:15],
                "accumulating": acc_list,
                "distributing": dist_list,
            }
        except Exception as e:
            return {"error": f"Smart-Wallet-Tracking fehlgeschlagen: {e}"}
