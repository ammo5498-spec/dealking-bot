"""
DealKing — Système de notifications
Discord (webhook embed) + Telegram (MarkdownV2)
Envoi simultané < 5 secondes
"""

import asyncio
import time
from dataclasses import dataclass

import aiohttp
from loguru import logger


@dataclass
class Deal:
    product_name: str
    keyword: str
    price: float
    msrp: float
    discount_pct: int
    saving: float
    domain: str
    flag: str
    category: str
    emoji: str
    product_url: str
    source: str
    currency_sym: str = "€"

    @property
    def is_error_price(self) -> bool:
        return self.discount_pct >= 40


# Anti-spam : mémoriser les alertes récentes
_alerted_recently: dict[str, float] = {}


def _was_alerted(key: str, cooldown_minutes: int = 60) -> bool:
    t = _alerted_recently.get(key)
    if t and (time.time() - t) < cooldown_minutes * 60:
        return True
    return False


def _mark_alerted(key: str):
    _alerted_recently[key] = time.time()


# ── Discord ────────────────────────────────────────────────────────────────────

async def send_discord(session: aiohttp.ClientSession, webhook_url: str, deal: Deal) -> bool:
    if not webhook_url:
        return False

    color = 0xFF4444 if deal.discount_pct >= 50 else 0xFF8C00 if deal.discount_pct >= 30 else 0x22C55E

    embed = {
        "title": f"{deal.emoji} {'🚨 ERREUR DE PRIX' if deal.is_error_price else '💰 BONNE AFFAIRE'} — {deal.product_name}",
        "description": (
            f"**{deal.flag} [{deal.domain}]({deal.product_url})**\n\n"
            f"> ~~{deal.msrp:.2f} {deal.currency_sym}~~ → **{deal.price:.2f} {deal.currency_sym}**\n"
            f"> 📉 **-{deal.discount_pct}%** · Économie : **{deal.saving:.0f} {deal.currency_sym}**"
        ),
        "color": color,
        "fields": [
            {"name": "Catégorie",  "value": deal.category,             "inline": True},
            {"name": "Remise",     "value": f"-{deal.discount_pct}%",  "inline": True},
            {"name": "Source",     "value": deal.source.upper(),       "inline": True},
        ],
        "footer": {
            "text": f"DealKing · {deal.domain} · {time.strftime('%d/%m/%Y %H:%M:%S')}"
        },
    }

    payload = {
        "username": "DealKing 🚨",
        "embeds": [embed],
        "components": [{
            "type": 1,
            "components": [{
                "type": 2,
                "style": 5,
                "label": f"🛒 Voir sur {deal.domain}",
                "url": deal.product_url,
            }]
        }]
    }

    try:
        async with session.post(webhook_url, json=payload, timeout=aiohttp.ClientTimeout(total=8)) as r:
            if r.status in (200, 204):
                logger.success(f"[Discord] Alerte envoyée : {deal.product_name}")
                return True
            else:
                logger.warning(f"[Discord] HTTP {r.status}")
                return False
    except Exception as e:
        logger.error(f"[Discord] Erreur : {e}")
        return False


# ── Telegram ───────────────────────────────────────────────────────────────────

def _tg_escape(text: str) -> str:
    """Échappe les caractères spéciaux MarkdownV2."""
    for ch in r"_*[]()~`>#+-=|{}.!\\":
        text = text.replace(ch, f"\\{ch}")
    return text


async def send_telegram(session: aiohttp.ClientSession, token: str, chat_id: str, deal: Deal) -> bool:
    if not token or not chat_id:
        return False

    name   = _tg_escape(deal.product_name)
    domain = _tg_escape(deal.domain)
    msrp   = _tg_escape(f"{deal.msrp:.2f}")
    price  = _tg_escape(f"{deal.price:.2f}")
    sym    = _tg_escape(deal.currency_sym)
    saving = _tg_escape(f"{deal.saving:.0f}")
    pct    = _tg_escape(str(deal.discount_pct))
    cat    = _tg_escape(deal.category)
    date   = _tg_escape(time.strftime("%d/%m/%Y %H:%M"))

    header = "🚨 *ERREUR DE PRIX DÉTECTÉE*" if deal.is_error_price else "💰 *BONNE AFFAIRE*"

    text = (
        f"{deal.emoji} {header}\n\n"
        f"*{name}*\n"
        f"{deal.flag} {domain} · {cat}\n\n"
        f"~~{msrp} {sym}~~ → *{price} {sym}*\n"
        f"📉 *\\-{pct}%* · Économie : *{saving} {sym}*\n\n"
        f"[🛒 Voir le produit]({deal.product_url})\n"
        f"_{date}_"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": False,
    }

    try:
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=8)) as r:
            data = await r.json()
            if data.get("ok"):
                logger.success(f"[Telegram] Alerte envoyée : {deal.product_name}")
                return True
            else:
                logger.warning(f"[Telegram] Erreur API : {data.get('description')}")
                return False
    except Exception as e:
        logger.error(f"[Telegram] Erreur : {e}")
        return False


# ── Dispatcher principal ───────────────────────────────────────────────────────

async def dispatch_alert(
    deal: Deal,
    discord_webhook: str,
    telegram_token: str,
    telegram_chat_id: str,
    cooldown_minutes: int = 60,
) -> dict:
    """
    Envoie l'alerte sur Discord ET Telegram simultanément.
    Retourne un dict avec les résultats de chaque canal.
    Inclut un anti-doublon par produit/région.
    """
    alert_key = f"{deal.product_name}::{deal.domain}"

    if _was_alerted(alert_key, cooldown_minutes):
        logger.debug(f"[Notifier] Anti-doublon : {deal.product_name} sur {deal.domain}")
        return {"skipped": True}

    _mark_alerted(alert_key)

    async with aiohttp.ClientSession() as session:
        dc_task = send_discord(session, discord_webhook, deal)
        tg_task = send_telegram(session, telegram_token, telegram_chat_id, deal)

        dc_ok, tg_ok = await asyncio.gather(dc_task, tg_task)

    results = {"discord": dc_ok, "telegram": tg_ok, "skipped": False}
    sent = [k for k, v in results.items() if v is True]
    if sent:
        logger.info(f"[Notifier] Alertes envoyées via : {', '.join(sent)}")
    else:
        logger.warning(f"[Notifier] Aucun canal n'a reçu l'alerte pour {deal.product_name}")

    return results
