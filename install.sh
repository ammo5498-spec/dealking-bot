#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  DealKing — Script d'installation automatique (Ubuntu 22/24)
#  Usage : bash install.sh
# ─────────────────────────────────────────────────────────────

set -e
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   DealKing — Installation automatique   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

INSTALL_DIR="/opt/dealking"
SERVICE_USER="ubuntu"

# 1. Dépendances système
echo "→ Installation des dépendances système..."
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip python3-venv \
    libglib2.0-0 libnss3 libnspr4 libdbus-1-3 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 2>/dev/null || true

# 2. Créer le répertoire d'installation
echo "→ Création du répertoire $INSTALL_DIR..."
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$USER $INSTALL_DIR
cp -r . $INSTALL_DIR/
cd $INSTALL_DIR

# 3. Environnement virtuel Python
echo "→ Création de l'environnement virtuel Python..."
python3 -m venv venv
source venv/bin/activate

# 4. Dépendances Python
echo "→ Installation des dépendances Python..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 5. Playwright : téléchargement de Chromium
echo "→ Installation de Chromium (Playwright)..."
playwright install chromium
playwright install-deps chromium 2>/dev/null || true

# 6. Répertoires de logs
mkdir -p $INSTALL_DIR/logs $INSTALL_DIR/data

# 7. Service systemd
echo "→ Configuration du service systemd..."
sudo cp dealking.service /etc/systemd/system/
sudo sed -i "s/User=ubuntu/User=$USER/" /etc/systemd/system/dealking.service
sudo systemctl daemon-reload
sudo systemctl enable dealking

echo ""
echo "✅ Installation terminée !"
echo ""
echo "─────────────────────────────────────────────"
echo "  ÉTAPES SUIVANTES :"
echo ""
echo "  1. Éditer la configuration :"
echo "     nano $INSTALL_DIR/config.yaml"
echo ""
echo "  2. Renseigner Discord et/ou Telegram :"
echo "     notifications:"
echo "       discord_webhook: 'https://discord.com/api/webhooks/...'"
echo "       telegram_token: '123456789:ABCDEF...'"
echo "       telegram_chat_id: '-100123456789'"
echo ""
echo "  3. Démarrer le bot :"
echo "     sudo systemctl start dealking"
echo ""
echo "  4. Voir les logs en direct :"
echo "     sudo journalctl -u dealking -f"
echo "     # ou :"
echo "     tail -f $INSTALL_DIR/logs/dealking.log"
echo ""
echo "  5. Arrêter / Redémarrer :"
echo "     sudo systemctl stop dealking"
echo "     sudo systemctl restart dealking"
echo "─────────────────────────────────────────────"
