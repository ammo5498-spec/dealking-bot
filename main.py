"""
DealKing — Bot de détection d'erreurs de prix
10 navigateurs Playwright en parallèle · 7 Amazon EU + Idealo
Alertes Discord & Telegram en < 5 secondes
"""

import asyncio
import sys
import time
from pathlib import Path

import yaml
from loguru import logger
from playwright.async_api import async_playwright

from products import PRODUCTS, get_msrp
from scraper import ScanWorker
from notifier import Deal, dispatch_alert


# ── Logger ─────────────────────────────────────────────────────────────────────
def setup_logger(cfg: dict):
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level=cfg["logging"]["level"],
        colorize=True,
    )
    logger.add(
        cfg["logging"]["file"],
        rotation=cfg["logging"]["rotation"],
        retention=cfg["logging"]["retention"],
        level="DEBUG",
    )


# ── Chargement config ──────────────────────────────────────────────────────────
def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


# ── Stats globales ─────────────────────────────────────────────────────────────
class Stats:
    def __init__(self):
        self.total_scans = 0
        self.total_errors = 0
        self.total_alerts = 0
        self.total_saved = 0.0
        self.start_time = time.time()
        self.cycle = 0

    def uptime(self) -> str:
        s = int(time.time() - self.start_time)
        h, r = divmod(s, 3600)
        m, s = divmod(r, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def scans_per_min(self) -> float:
        elapsed = max(1, (time.time() - self.start_time) / 60)
        return round(self.total_scans / elapsed, 1)

    def print_summary(self):
        logger.info(
            f"📊 Stats | Uptime: {self.uptime()} | "
            f"Scans: {self.total_scans} ({self.scans_per_min()}/min) | "
            f"Erreurs prix: {self.total_errors} | "
            f"Alertes: {self.total_alerts} | "
            f"Économies: {self.total_saved:.0f}€"
        )


stats = Stats()


# ── Analyseur de prix ──────────────────────────────────────────────────────────
async def analyze_result(
    result: dict,
    cfg: dict,
) -> None:
    """
    Analyse un résultat de scan et déclenche une alerte si le prix est anormal.
    """
    product = result.get("product", {})
    region  = result.get("region", {})
    price   = result.get("price", 0)
    name    = result.get("name", product.get("name", ""))
    url     = result.get("url", "")
    source  = result.get("source", "amazon")

    # Trouver le MSRP
    msrp = get_msrp(result.get("keyword", "")) or get_msrp(name)
    if not msrp:
        logger.debug(f"MSRP inconnu pour '{name}', ignoré")
        return

    # Calculer la remise
    if price >= msrp:
        return  # pas de remise

    discount_pct = int((msrp - price) / msrp * 100)
    saving = msrp - price

    stats.total_scans += 1

    min_discount = cfg["detection"]["min_discount_pct"]
    max_price    = cfg["detection"]["max_price_eur"]

    if discount_pct < min_discount:
        logger.debug(f"{region.get('flag','')} {result['domain']} | {name} | {price}€ (-{discount_pct}%) — en dessous du seuil")
        return

    if price > max_price:
        logger.debug(f"{name} | {price}€ dépasse le budget max ({max_price}€)")
        return

    # 🚨 Erreur de prix détectée !
    stats.total_errors += 1
    stats.total_saved += saving

    logger.warning(
        f"🚨 ERREUR PRIX | {region.get('flag','')} {result['domain']} | "
        f"{name} | {price}€ (MSRP: {msrp}€) | -{discount_pct}% | "
        f"Source: {source} | {url}"
    )

    # Construire le deal
    deal = Deal(
        product_name=name,
        keyword=result.get("keyword", ""),
        price=price,
        msrp=msrp,
        discount_pct=discount_pct,
        saving=saving,
        domain=result["domain"],
        flag=region.get("flag", "🌍"),
        category=product.get("category", ""),
        emoji=product.get("emoji", "🛒"),
        product_url=url,
        source=source,
        currency_sym=region.get("symbol", "€"),
    )

    # Envoyer les alertes
    notif_cfg = cfg["notifications"]
    result_notif = await dispatch_alert(
        deal=deal,
        discord_webhook=notif_cfg.get("discord_webhook", ""),
        telegram_token=notif_cfg.get("telegram_token", ""),
        telegram_chat_id=notif_cfg.get("telegram_chat_id", ""),
        cooldown_minutes=cfg["detection"]["cooldown_minutes"],
    )

    if not result_notif.get("skipped"):
        if result_notif.get("discord") or result_notif.get("telegram"):
            stats.total_alerts += 1


# ── Consommateur de résultats ──────────────────────────────────────────────────
async def result_consumer(result_queue: asyncio.Queue, cfg: dict):
    """Traite les résultats de scan en continu."""
    while True:
        result = await result_queue.get()
        if result is None:
            break
        try:
            await analyze_result(result, cfg)
        except Exception as e:
            logger.error(f"[Analyzer] Erreur: {e}")
        finally:
            result_queue.task_done()


# ── Générateur de tâches ───────────────────────────────────────────────────────
def build_task_list(cfg: dict) -> list[tuple]:
    """
    Construit la liste de toutes les tâches de scan :
    chaque combinaison (région × produit × keyword).
    """
    tasks = []
    regions = cfg["regions"]

    for product in PRODUCTS:
        for region in regions:
            for keyword in product["keywords"]:
                tasks.append((
                    region["domain"],
                    keyword,
                    region,
                    product,
                ))

    # Mélanger pour éviter de scanner toujours dans le même ordre
    import random
    random.shuffle(tasks)

    return tasks


# ── Cycle de scan ──────────────────────────────────────────────────────────────
async def run_cycle(
    task_queue: asyncio.Queue,
    cfg: dict,
) -> None:
    """Remplit la queue avec toutes les tâches du cycle."""
    stats.cycle += 1
    tasks = build_task_list(cfg)

    logger.info(
        f"══ Cycle #{stats.cycle} | "
        f"{len(tasks)} tâches | "
        f"{len(cfg['regions'])} régions × {len(PRODUCTS)} produits ══"
    )

    for task in tasks:
        await task_queue.put(task)


# ── Point d'entrée principal ───────────────────────────────────────────────────
async def main():
    cfg = load_config()
    setup_logger(cfg)

    logger.info("═" * 55)
    logger.info("  DealKing — Bot de détection d'erreurs de prix")
    logger.info(f"  {len(PRODUCTS)} produits · {len(cfg['regions'])} régions Amazon EU")
    logger.info(f"  {cfg['scanner']['concurrent_browsers']} workers parallèles")
    logger.info("═" * 55)

    # Vérification config notifications
    notif = cfg["notifications"]
    if notif.get("discord_webhook"):
        logger.success("Discord : ✓ configuré")
    else:
        logger.warning("Discord : ✗ non configuré (édite config.yaml)")

    if notif.get("telegram_token") and notif.get("telegram_chat_id"):
        logger.success("Telegram : ✓ configuré")
    else:
        logger.warning("Telegram : ✗ non configuré (édite config.yaml)")

    # Queues asyncio
    task_queue   = asyncio.Queue(maxsize=500)
    result_queue = asyncio.Queue()

    # Proxies
    proxies: list[str] = []
    if cfg["proxies"]["enabled"] and cfg["proxies"].get("list"):
        proxies = cfg["proxies"]["list"]
        logger.info(f"Proxies : {len(proxies)} configurés")

    n_workers = cfg["scanner"]["concurrent_browsers"]
    page_timeout = cfg["scanner"]["page_timeout_ms"]

    async with async_playwright() as playwright:
        # Créer et démarrer les workers
        workers = []
        for i in range(n_workers):
            proxy = proxies[i % len(proxies)] if proxies else None
            worker = ScanWorker(
                worker_id=i + 1,
                task_queue=task_queue,
                result_queue=result_queue,
                proxy=proxy,
                page_timeout=page_timeout,
            )
            await worker.setup(playwright)
            workers.append(worker)

        logger.success(f"{n_workers} workers démarrés ✓")

        # Démarrer le consommateur de résultats
        consumer_task = asyncio.create_task(result_consumer(result_queue, cfg))

        # Démarrer les workers
        worker_tasks = [asyncio.create_task(w.run()) for w in workers]

        scan_interval = cfg["scanner"]["scan_interval_sec"]

        try:
            while True:
                cycle_start = time.time()

                # Remplir la queue
                await run_cycle(task_queue, cfg)

                # Attendre que toutes les tâches soient traitées
                await task_queue.join()

                elapsed = time.time() - cycle_start
                stats.print_summary()
                logger.info(f"Cycle #{stats.cycle} terminé en {elapsed:.1f}s")

                # Pause avant le prochain cycle
                wait = max(0, scan_interval - elapsed)
                if wait > 0:
                    logger.info(f"Prochain cycle dans {wait:.0f}s…")
                    await asyncio.sleep(wait)

        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Arrêt demandé…")

        finally:
            # Arrêter les workers proprement
            for _ in workers:
                await task_queue.put(None)
            await asyncio.gather(*worker_tasks, return_exceptions=True)

            # Arrêter le consommateur
            await result_queue.put(None)
            await consumer_task

            # Fermer les navigateurs
            for worker in workers:
                await worker.teardown()

            stats.print_summary()
            logger.info("DealKing arrêté proprement.")


if __name__ == "__main__":
    asyncio.run(main())
