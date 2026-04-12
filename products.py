"""
DealKing — Catalogue produits + MSRP
Extrait et enrichi depuis pricesnipe-pro.html
"""

# ── MSRP de référence (prix conseillé fabricant en €) ─────────────────────────
MSRP: dict[str, float] = {
    # Gaming & Consoles
    "PS5 Pro":                  799.0,
    "PS5 Slim":                 449.0,
    "PS5":                      549.0,
    "PlayStation 5":            549.0,
    "Xbox Series X":            499.0,
    "Nintendo Switch 2":        449.0,
    "PC gaming":               1800.0,
    "PC gamer RTX":            2500.0,
    "gaming PC":               1800.0,
    "PC HP Omen":              1500.0,
    "Manette DualSense":         79.0,
    "DualSense":                 79.0,
    "GTA 6":                     70.0,
    "SSD NVMe":                 120.0,
    # Smartphones
    "iPhone 17 Pro Max":       1479.0,
    "iPhone 17 Pro":           1229.0,
    "iPhone 17":                969.0,
    "iPhone 16 Pro Max":       1479.0,
    "iPhone 16 Pro":           1229.0,
    "iPhone 16":                969.0,
    "Samsung Galaxy S26 Ultra":1449.0,
    "Samsung Galaxy S26":      1149.0,
    "Samsung Galaxy S25 Ultra":1349.0,
    "iPad Pro M4":             1119.0,
    "iPad Pro":                1119.0,
    "iPad 11":                  479.0,
    "MacBook Air M3":          1299.0,
    "MacBook Air":             1299.0,
    "MacBook Pro M4":          2199.0,
    "MacBook Pro M3":          1999.0,
    "MacBook Pro":             1999.0,
    "Xiaomi 15 Ultra":         1299.0,
    "Xiaomi 15":                999.0,
    "Google Pixel 10 Pro":     1099.0,
    "Google Pixel 10":          799.0,
    "Apple Watch Ultra 2":      899.0,
    "Apple Watch":              449.0,
    "Samsung Galaxy Watch 7":   309.0,
    # GPU
    "RTX 5090":                2499.0,
    "RTX 5080":                1299.0,
    "RTX 5070 Ti":              899.0,
    "RTX 5070":                 649.0,
    "RTX 4090":                1899.0,
    "RTX 4080 Super":          1079.0,
    "RTX 4070 Ti Super":        849.0,
    "RTX 4070 Super":           629.0,
    "RX 7900 XTX":              899.0,
    "Arc B580":                 299.0,
    # CPU
    "Ryzen 9 9950X":            649.0,
    "Ryzen 9 7950X":            599.0,
    "Ryzen 9":                  549.0,
    "Intel Core Ultra 9 285K":  629.0,
    "Intel Core i9-14900K":     589.0,
    # RAM / SSD
    "RAM DDR6 32Go":            149.0,
    "RAM DDR5 32Go":            119.0,
    "Samsung 990 Pro 2To":      179.0,
    "WD Black SN850X 2To":      169.0,
    # Écrans & TV
    "LG OLED C4 65":           1799.0,
    "LG OLED 65":              1799.0,
    "TV LG 65":                1499.0,
    "Samsung S95D OLED":       2499.0,
    "Sony Bravia XR A95L":     3299.0,
    "Écran OLED 4K 27":         799.0,
    "Samsung Odyssey Neo G8":   799.0,
    # Audio
    "Sony WH-1000XM5":          349.0,
    "Sony WH-1000XM6":          399.0,
    "AirPods Pro 2":            279.0,
    "AirPods Max":              599.0,
    "Bose QuietComfort Ultra":  449.0,
    "Bose QC45":                280.0,
    "Sonos Arc Ultra":          999.0,
    # Photo / Drone
    "Sony A7R V":              3799.0,
    "Canon EOS R5 Mark II":    4299.0,
    "Nikon Z8":                4299.0,
    "DJI Mavic 3 Pro":         2199.0,
    "DJI Mini 4 Pro":           959.0,
    # Électroménager
    "Dyson V15 Detect":         749.0,
    "Dyson V12":                599.0,
    "Réfrigérateur Samsung":    999.0,
    "Lave-linge":               599.0,
    "Machine à café DeLonghi":  399.0,
    "Nespresso":                249.0,
    # Mobilité
    "Trottinette électrique Xiaomi": 399.0,
    "Vélo électrique":         1299.0,
    "Meta Quest 3":             549.0,
    "Garmin Fenix 8":           999.0,
}


# ── Catalogue produits par catégorie ──────────────────────────────────────────
PRODUCTS: list[dict] = [

    # ── Gaming & Consoles ─────────────────────────────────────────────────────
    {"id": "ps5_pro",      "name": "PS5 Pro",         "category": "Console",   "emoji": "🎮",
     "keywords": ["PS5 Pro console", "PlayStation 5 Pro"]},
    {"id": "ps5_slim",     "name": "PS5 Slim",        "category": "Console",   "emoji": "🎮",
     "keywords": ["PS5 Slim console", "PlayStation 5 Slim"]},
    {"id": "xbox_sx",      "name": "Xbox Series X",   "category": "Console",   "emoji": "🎮",
     "keywords": ["Xbox Series X 1To", "Xbox Series X console"]},
    {"id": "switch2",      "name": "Nintendo Switch 2","category": "Console",  "emoji": "🎮",
     "keywords": ["Nintendo Switch 2"]},
    {"id": "dualsense",    "name": "Manette DualSense","category": "Gaming",   "emoji": "🕹",
     "keywords": ["DualSense manette PS5", "manette DualSense Edge"]},
    {"id": "gta6",         "name": "GTA 6",           "category": "Jeux",      "emoji": "🎯",
     "keywords": ["GTA 6 PS5", "Grand Theft Auto VI"]},

    # ── Smartphones ───────────────────────────────────────────────────────────
    {"id": "iphone17pm",   "name": "iPhone 17 Pro Max","category": "Smartphone","emoji": "📱",
     "keywords": ["iPhone 17 Pro Max 256Go", "iPhone 17 Pro Max"]},
    {"id": "iphone17p",    "name": "iPhone 17 Pro",   "category": "Smartphone","emoji": "📱",
     "keywords": ["iPhone 17 Pro 256Go"]},
    {"id": "iphone17",     "name": "iPhone 17",       "category": "Smartphone","emoji": "📱",
     "keywords": ["iPhone 17 128Go", "iPhone 17 256Go"]},
    {"id": "s26ultra",     "name": "Samsung S26 Ultra","category": "Smartphone","emoji": "📱",
     "keywords": ["Samsung Galaxy S26 Ultra 256Go"]},
    {"id": "pixel10pro",   "name": "Google Pixel 10 Pro","category": "Smartphone","emoji": "📱",
     "keywords": ["Google Pixel 10 Pro", "Pixel 10 Pro XL"]},
    {"id": "xiaomi15",     "name": "Xiaomi 15 Ultra", "category": "Smartphone","emoji": "📱",
     "keywords": ["Xiaomi 15 Ultra", "Xiaomi 15 Pro"]},

    # ── PC Portables ──────────────────────────────────────────────────────────
    {"id": "mbpro_m4",     "name": "MacBook Pro M4",  "category": "PC Portable","emoji": "💻",
     "keywords": ["MacBook Pro M4 14 pouces", "MacBook Pro M4 16"]},
    {"id": "mbair_m3",     "name": "MacBook Air M3",  "category": "PC Portable","emoji": "💻",
     "keywords": ["MacBook Air M3 15 pouces", "MacBook Air M3 13"]},
    {"id": "rog_zeph",     "name": "ASUS ROG Zephyrus G14","category": "PC Portable","emoji": "💻",
     "keywords": ["ASUS ROG Zephyrus G14 RTX 4070", "ROG Zephyrus G14 2024"]},
    {"id": "pc_omen",      "name": "PC HP Omen",      "category": "PC Gamer",  "emoji": "🖥",
     "keywords": ["HP Omen 45L RTX 4090", "PC HP Omen gaming"]},

    # ── GPU ───────────────────────────────────────────────────────────────────
    {"id": "rtx5090",      "name": "RTX 5090",        "category": "GPU",       "emoji": "⚡",
     "keywords": ["RTX 5090 24Go", "GeForce RTX 5090", "NVIDIA RTX 5090"]},
    {"id": "rtx5080",      "name": "RTX 5080",        "category": "GPU",       "emoji": "⚡",
     "keywords": ["RTX 5080 16Go", "GeForce RTX 5080"]},
    {"id": "rtx5070",      "name": "RTX 5070",        "category": "GPU",       "emoji": "⚡",
     "keywords": ["RTX 5070 12Go", "GeForce RTX 5070"]},
    {"id": "rtx4090",      "name": "RTX 4090",        "category": "GPU",       "emoji": "⚡",
     "keywords": ["RTX 4090 24Go", "GeForce RTX 4090"]},
    {"id": "rx7900xtx",    "name": "RX 7900 XTX",     "category": "GPU",       "emoji": "⚡",
     "keywords": ["RX 7900 XTX 24Go", "Radeon RX 7900 XTX"]},

    # ── CPU ───────────────────────────────────────────────────────────────────
    {"id": "r9_9950x",     "name": "Ryzen 9 9950X",   "category": "CPU",       "emoji": "🔩",
     "keywords": ["AMD Ryzen 9 9950X", "Ryzen 9 9950X BOX"]},
    {"id": "i9_14900k",    "name": "Intel i9-14900K", "category": "CPU",       "emoji": "🔩",
     "keywords": ["Intel Core i9-14900K", "i9 14900K BOX"]},

    # ── RAM / SSD ─────────────────────────────────────────────────────────────
    {"id": "ssd_990pro",   "name": "Samsung 990 Pro 2To","category": "SSD",    "emoji": "💾",
     "keywords": ["Samsung 990 Pro 2To NVMe", "MZ-V9P2T0BW"]},
    {"id": "ram_ddr5",     "name": "RAM DDR5 32Go",   "category": "RAM",       "emoji": "💾",
     "keywords": ["Corsair Vengeance DDR5 32Go 6000", "G.Skill Trident Z5 32Go DDR5"]},

    # ── TV & Moniteurs ────────────────────────────────────────────────────────
    {"id": "lg_c4_65",     "name": "LG OLED C4 65\"", "category": "TV",        "emoji": "📺",
     "keywords": ["LG OLED65C4 65 pouces 4K", "LG OLED C4 65"]},
    {"id": "samsung_s95d", "name": "Samsung S95D 65\"","category": "TV",       "emoji": "📺",
     "keywords": ["Samsung S95D OLED 65 pouces", "QE65S95D"]},
    {"id": "sony_a95l",    "name": "Sony Bravia XR A95L","category": "TV",     "emoji": "📺",
     "keywords": ["Sony Bravia XR A95L 65 pouces", "XR-65A95L"]},
    {"id": "ecran_oled",   "name": "Écran OLED 4K 27\"","category": "Moniteur","emoji": "🖥",
     "keywords": ["ASUS ROG Swift OLED PG27UCDM", "Samsung Odyssey OLED G8 27"]},

    # ── Tablettes ─────────────────────────────────────────────────────────────
    {"id": "ipad_pro_m4",  "name": "iPad Pro M4",     "category": "Tablette",  "emoji": "📲",
     "keywords": ["iPad Pro M4 11 pouces 256Go", "iPad Pro M4 13 pouces"]},
    {"id": "ipad_11",      "name": "iPad 11 pouces",  "category": "Tablette",  "emoji": "📲",
     "keywords": ["iPad 11 pouces 128Go 2024", "Apple iPad A16"]},

    # ── Audio ─────────────────────────────────────────────────────────────────
    {"id": "xm5",          "name": "Sony WH-1000XM5", "category": "Audio",     "emoji": "🎧",
     "keywords": ["Sony WH-1000XM5 casque", "WH-1000XM5"]},
    {"id": "airpods_pro2", "name": "AirPods Pro 2",   "category": "Audio",     "emoji": "🎧",
     "keywords": ["AirPods Pro 2 MagSafe USB-C", "MTJV3ZM/A"]},
    {"id": "bose_qcult",   "name": "Bose QC Ultra",   "category": "Audio",     "emoji": "🎧",
     "keywords": ["Bose QuietComfort Ultra casque", "Bose QC Ultra"]},

    # ── Photo & Drone ─────────────────────────────────────────────────────────
    {"id": "sony_a7rv",    "name": "Sony A7R V",      "category": "Photo",     "emoji": "📷",
     "keywords": ["Sony Alpha A7R V boîtier", "ILCE-7RM5"]},
    {"id": "dji_mini4",    "name": "DJI Mini 4 Pro",  "category": "Drone",     "emoji": "🚁",
     "keywords": ["DJI Mini 4 Pro drone", "DJI Mini 4 Pro fly more"]},

    # ── Montres ───────────────────────────────────────────────────────────────
    {"id": "aw_ultra2",    "name": "Apple Watch Ultra 2","category": "Montre",  "emoji": "⌚",
     "keywords": ["Apple Watch Ultra 2 49mm", "MQDY3QF/A"]},
    {"id": "garmin_f8",    "name": "Garmin Fenix 8",  "category": "Montre",    "emoji": "⌚",
     "keywords": ["Garmin Fenix 8 Solar 47mm", "Garmin Fenix 8 AMOLED"]},

    # ── Électroménager ────────────────────────────────────────────────────────
    {"id": "dyson_v15",    "name": "Dyson V15 Detect","category": "Maison",    "emoji": "🌀",
     "keywords": ["Dyson V15 Detect Absolute", "Dyson V15 Detect+"]},
    {"id": "meta_q3",      "name": "Meta Quest 3",    "category": "VR",        "emoji": "🥽",
     "keywords": ["Meta Quest 3 128Go", "Meta Quest 3 512Go"]},
    {"id": "trottinette",  "name": "Trottinette Xiaomi","category": "Mobilité","emoji": "🛵",
     "keywords": ["Xiaomi Electric Scooter 4 Ultra", "trottinette électrique Xiaomi 4"]},
    {"id": "velo_elec",    "name": "Vélo électrique", "category": "Mobilité",  "emoji": "🚲",
     "keywords": ["vélo électrique Decathlon Rockrider E-ST 520", "vélo électrique 250W"]},
]


def get_msrp(keyword: str) -> float | None:
    """Retourne le MSRP pour un mot-clé donné (insensible à la casse)."""
    kw_lower = keyword.lower()
    for key, price in MSRP.items():
        if key.lower() in kw_lower or kw_lower in key.lower():
            return price
    return None


def get_product_by_id(product_id: str) -> dict | None:
    return next((p for p in PRODUCTS if p["id"] == product_id), None)
