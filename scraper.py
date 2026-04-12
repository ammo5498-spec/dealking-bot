"""
DealKing — Moteur de scraping Playwright async
Scrape Amazon EU + Idealo avec 10 navigateurs en parallèle.
Anti-ban : rotation user-agent, délais aléatoires, stealth mode.
"""

import asyncio
import random
import re
import time
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger

from products import get_msrp


# ── User-agents réalistes ──────────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


def parse_price(text: str) -> Optional[float]:
    """Extrait un prix depuis une chaîne de caractères."""
    if not text:
        return None
    # Supprimer tout sauf chiffres, virgules, points
    cleaned = re.sub(r"[^\d,\.]", "", text.strip())
    # Gérer les séparateurs (1.234,56 → 1234.56 / 1,234.56 → 1234.56)
    if "," in cleaned and "." in cleaned:
        # Format européen : 1.234,56
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        # Format US : 1,234.56
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    try:
        val = float(cleaned)
        return val if 0.5 < val < 100_000 else None
    except ValueError:
        return None


# ── Stealth : masque les traces d'automatisation ──────────────────────────────
STEALTH_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
Object.defineProperty(navigator, 'languages', {get: () => ['fr-FR','fr','en-US','en']});
window.chrome = {runtime: {}};
"""


async def create_browser_context(
    browser: Browser,
    proxy: Optional[str] = None,
    locale: str = "fr-FR",
) -> BrowserContext:
    """Crée un contexte navigateur avec stealth et proxy optionnel."""
    ua = random.choice(USER_AGENTS)

    kwargs = {
        "user_agent": ua,
        "locale": locale,
        "viewport": {"width": random.randint(1280, 1920), "height": random.randint(720, 1080)},
        "java_script_enabled": True,
        "ignore_https_errors": True,
        "extra_http_headers": {
            "Accept-Language": f"{locale},{locale[:2]};q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "DNT": "1",
        },
    }

    if proxy:
        kwargs["proxy"] = {"server": proxy}

    context = await browser.new_context(**kwargs)
    await context.add_init_script(STEALTH_SCRIPT)

    # Bloquer les ressources inutiles (images, fonts) → +50% de vitesse
    await context.route(
        "**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,otf,mp4,mp3,pdf}",
        lambda route: route.abort()
    )

    return context


# ── Scraper Amazon ─────────────────────────────────────────────────────────────

AMAZON_PRICE_SELECTORS = [
    ".a-price .a-offscreen",
    "#priceblock_ourprice",
    "#priceblock_dealprice",
    ".apexPriceToPay .a-offscreen",
    "#corePrice_desktop .a-price .a-offscreen",
    ".a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen",
    "#price_inside_buybox",
    ".a-color-price",
]

AMAZON_TITLE_SELECTORS = [
    "#productTitle",
    "h1.a-size-large",
    "#title span",
]


async def scrape_amazon_search(
    page: Page,
    domain: str,
    keyword: str,
    timeout_ms: int = 20000,
) -> Optional[dict]:
    """
    Scrape la page de recherche Amazon pour un mot-clé.
    Retourne le premier résultat avec son prix et son lien direct.
    """
    url = f"https://www.{domain}/s?k={keyword.replace(' ', '+')}&sort=price-asc-rank"

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        await asyncio.sleep(random.uniform(0.5, 1.5))  # délai humain

        # Extraire les résultats de recherche
        results = await page.query_selector_all('[data-component-type="s-search-result"]')

        for result in results[:5]:  # Vérifier les 5 premiers
            try:
                # Prix
                price_el = await result.query_selector(".a-price .a-offscreen")
                if not price_el:
                    price_el = await result.query_selector(".a-color-price")
                if not price_el:
                    continue

                price_text = await price_el.inner_text()
                price = parse_price(price_text)
                if not price:
                    continue

                # Titre
                title_el = await result.query_selector("h2 a span")
                title = await title_el.inner_text() if title_el else keyword

                # Lien direct vers la fiche produit
                link_el = await result.query_selector("h2 a")
                href = await link_el.get_attribute("href") if link_el else None
                if href:
                    product_url = f"https://www.{domain}{href}" if href.startswith("/") else href
                    # Nettoyer les paramètres de tracking
                    product_url = re.sub(r"/ref=.*", "", product_url)
                else:
                    product_url = url

                return {
                    "name": title.strip(),
                    "price": price,
                    "url": product_url,
                    "source": "amazon",
                }

            except Exception:
                continue

    except Exception as e:
        logger.debug(f"[Amazon/{domain}] Erreur scraping '{keyword}': {e}")

    return None


async def scrape_amazon_product(
    page: Page,
    product_url: str,
    timeout_ms: int = 20000,
) -> Optional[float]:
    """
    Scrape directement une fiche produit Amazon pour obtenir le prix exact.
    Plus précis que la page de recherche.
    """
    try:
        await page.goto(product_url, wait_until="domcontentloaded", timeout=timeout_ms)
        await asyncio.sleep(random.uniform(0.3, 0.8))

        for selector in AMAZON_PRICE_SELECTORS:
            el = await page.query_selector(selector)
            if el:
                text = await el.inner_text()
                price = parse_price(text)
                if price:
                    return price

    except Exception as e:
        logger.debug(f"[Amazon] Erreur fiche produit: {e}")

    return None


# ── Scraper Idealo ─────────────────────────────────────────────────────────────

async def scrape_idealo(
    page: Page,
    keyword: str,
    timeout_ms: int = 15000,
) -> Optional[dict]:
    """
    Scrape Idealo.fr pour trouver le meilleur prix actuel d'un produit.
    Idealo agrège les prix de centaines de marchands.
    """
    url = f"https://www.idealo.fr/prix/{keyword.replace(' ', '-')}.html"
    search_url = f"https://www.idealo.fr/search?q={keyword.replace(' ', '+')}"

    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=timeout_ms)
        await asyncio.sleep(random.uniform(0.5, 1.0))

        # Cliquer sur le premier résultat
        first = await page.query_selector(".productOffers-listItem, .sr-resultList a")
        if first:
            href = await first.get_attribute("href")
            if href:
                product_page = f"https://www.idealo.fr{href}" if href.startswith("/") else href
                await page.goto(product_page, wait_until="domcontentloaded", timeout=timeout_ms)
                await asyncio.sleep(0.5)

        # Extraire le meilleur prix
        price_selectors = [
            ".oopStage-priceMin",
            ".productOffers-listItemPrice",
            "[class*='priceMin']",
            ".sr-price",
        ]

        for selector in price_selectors:
            el = await page.query_selector(selector)
            if el:
                text = await el.inner_text()
                price = parse_price(text)
                if price:
                    # Titre
                    title_el = await page.query_selector("h1")
                    title = await title_el.inner_text() if title_el else keyword

                    return {
                        "name": title.strip()[:100],
                        "price": price,
                        "url": page.url,
                        "source": "idealo",
                    }

    except Exception as e:
        logger.debug(f"[Idealo] Erreur pour '{keyword}': {e}")

    return None


# ── Worker : un navigateur = un thread de scan ────────────────────────────────

class ScanWorker:
    """
    Un worker = un navigateur Playwright dédié.
    Il reçoit des tâches de scan via une queue asyncio.
    """

    def __init__(
        self,
        worker_id: int,
        task_queue: asyncio.Queue,
        result_queue: asyncio.Queue,
        proxy: Optional[str] = None,
        page_timeout: int = 20000,
    ):
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.proxy = proxy
        self.page_timeout = page_timeout
        self.scan_count = 0
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def setup(self, playwright):
        """Lance le navigateur headless."""
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--disable-extensions",
            ],
        )
        self.context = await create_browser_context(self.browser, self.proxy)
        logger.info(f"[Worker {self.worker_id}] Prêt")

    async def run(self):
        """Boucle principale du worker : traite les tâches jusqu'à None."""
        page = await self.context.new_page()

        while True:
            task = await self.task_queue.get()
            if task is None:
                break  # signal d'arrêt

            domain, keyword, region_info, product_info = task
            start = time.time()

            try:
                # Choisir le scraper selon le domaine
                if "idealo" in domain:
                    result = await scrape_idealo(page, keyword, self.page_timeout)
                else:
                    result = await scrape_amazon_search(page, domain, keyword, self.page_timeout)

                elapsed = time.time() - start
                self.scan_count += 1

                if result:
                    result["domain"] = domain
                    result["keyword"] = keyword
                    result["region"] = region_info
                    result["product"] = product_info
                    result["elapsed"] = elapsed
                    await self.result_queue.put(result)

                    logger.debug(
                        f"[Worker {self.worker_id}] {domain} '{keyword}' "
                        f"→ {result['price']}€ ({elapsed:.1f}s)"
                    )
                else:
                    logger.debug(f"[Worker {self.worker_id}] {domain} '{keyword}' → aucun résultat")

            except Exception as e:
                logger.error(f"[Worker {self.worker_id}] Erreur: {e}")
            finally:
                self.task_queue.task_done()

            # Délai aléatoire anti-ban entre chaque requête
            await asyncio.sleep(random.uniform(0.3, 1.2))

        await page.close()

    async def teardown(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
