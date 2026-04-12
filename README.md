# DealKing — Bot Python de détection d'erreurs de prix

Bot professionnel H24 avec 10 navigateurs Playwright en parallèle.
Scanne 7 Amazon EU + Idealo · Alertes Discord & Telegram en < 5 secondes.

## Architecture

```
dealking/
├── main.py          ← Orchestrateur principal (10 workers asyncio)
├── scraper.py       ← Playwright async : Amazon EU + Idealo
├── notifier.py      ← Alertes Discord + Telegram simultanées
├── products.py      ← 40+ produits + MSRP de référence
├── config.yaml      ← Configuration complète
├── requirements.txt ← Dépendances Python
├── dealking.service ← Service systemd Ubuntu
└── install.sh       ← Script d'installation automatique
```

## Installation rapide (VPS Ubuntu)

```bash
# Cloner / copier les fichiers sur ton VPS
git clone <repo> && cd dealking

# Lancer l'installation automatique (installe Python, Chromium, systemd)
bash install.sh
```

## Installation manuelle

```bash
# Python + venv
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Playwright : télécharger Chromium
playwright install chromium
playwright install-deps chromium

# Configurer
cp config.yaml config.yaml  # éditer discord/telegram
```

## Configuration (config.yaml)

```yaml
notifications:
  discord_webhook: "https://discord.com/api/webhooks/XXX/YYY"
  telegram_token: "123456789:ABCDEF..."
  telegram_chat_id: "-100123456789"

detection:
  min_discount_pct: 40    # alerter si remise >= 40%
  cooldown_minutes: 60    # anti-doublon : 1h entre 2 alertes même produit

scanner:
  concurrent_browsers: 10  # navigateurs en parallèle
  scan_interval_sec: 30    # pause entre cycles
```

## Lancement

```bash
# Test direct
python main.py

# Via systemd (H24, redémarre automatiquement)
sudo systemctl start dealking
sudo systemctl status dealking

# Logs en direct
sudo journalctl -u dealking -f
tail -f logs/dealking.log
```

## Produits surveillés (40+)

| Catégorie     | Produits                                          |
|---------------|---------------------------------------------------|
| 🎮 Consoles   | PS5 Pro/Slim, Xbox Series X, Switch 2, DualSense |
| 📱 Smartphones| iPhone 17, Samsung S26 Ultra, Pixel 10, Xiaomi 15|
| 💻 PC/Mac     | MacBook Pro M4, ASUS ROG, HP Omen                |
| ⚡ GPU        | RTX 5090/5080/5070, RX 7900 XTX                  |
| 📺 TV         | LG OLED C4, Samsung S95D, Sony Bravia XR         |
| 🎧 Audio      | Sony XM5, AirPods Pro 2, Bose QC Ultra           |
| 🚁 Drone      | DJI Mini 4 Pro, DJI Mavic 3 Pro                  |

## Ajouter un produit

Dans `products.py` :

```python
{"id": "mon_produit", "name": "Nom affiché", "category": "Catégorie",
 "emoji": "📦", "keywords": ["terme de recherche exact"]}
```

Et dans `MSRP` :
```python
"Nom du produit": 299.0,
```

## Prérequis VPS

- Ubuntu 22.04 ou 24.04
- 2 Go RAM minimum (4 Go recommandé pour 10 workers)
- 2 vCPU minimum
- 10 Go stockage
- Python 3.11+
