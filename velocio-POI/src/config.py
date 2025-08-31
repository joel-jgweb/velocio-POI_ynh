# src/config.py
import os
from pathlib import Path

APP_NAME = "Velocio_POI"

# === 🔧 DOSSIER DE DONNÉES DANS /var/www/app/data (correction YunoHost) ===
USER_DATA_DIR = Path("/var/www/velocio-poi-ynh/data")
CACHE_DIR = USER_DATA_DIR / "cache"
OUTPUT_DIR = USER_DATA_DIR / "output"

# Créer les dossiers avec bons droits (www-data)
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# === FIN CORRECTION CHEMINS ===

USER_AGENT = "Velocio Traces & Spots v1.0"

OVERPASS_API_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter"
]

# === 🍽️ Se restaurer
RESTAURANT_TAGS = [{"key": "amenity", "value": "restaurant"}]
FAST_FOOD_TAGS = [{"key": "amenity", "value": "fast_food"}]
CAFE_TAGS = [{"key": "amenity", "value": "cafe"}]
PUB_TAGS = [{"key": "amenity", "value": "pub"}]
BAR_TAGS = [{"key": "amenity", "value": "bar"}]
BAKERY_TAGS = [{"key": "amenity", "value": "bakery"}]

# === 🛒 Faire ses courses
SUPERMARKET_TAGS = [{"key": "shop", "value": "supermarket"}]
CONVENIENCE_TAGS = [{"key": "shop", "value": "convenience"}]

# === ⛽️ Services
FUEL_TAGS = [{"key": "amenity", "value": "fuel"}]

# === 💧 Besoins essentiels
DRINKING_WATER_TAGS = [{"key": "amenity", "value": "drinking_water"}]
TOILETS_TAGS = [{"key": "amenity", "value": "toilets"}]

# === 🌳 Loisirs
PICNIC_SITE_TAGS = [{"key": "leisure", "value": "picnic_site"}]

# === 🏛️ Culture & Tourisme
MUSEUM_TAGS = [{"key": "tourism", "value": "museum"}]
ATTRACTION_TAGS = [{"key": "tourism", "value": "attraction"}]
VIEWPOINT_TAGS = [{"key": "tourism", "value": "viewpoint"}]
MARKETPLACE_TAGS = [{"key": "amenity", "value": "marketplace"}]

# === 🏁 Catégories regroupées (utilisé pour l'interface)
POI_CATEGORIES = {
    "Se restaurer": [
        {"name": "Restaurant", "tags": RESTAURANT_TAGS},
        {"name": "Fast-food", "tags": FAST_FOOD_TAGS},
        {"name": "Café", "tags": CAFE_TAGS},
        {"name": "Pub", "tags": PUB_TAGS},
        {"name": "Bar", "tags": BAR_TAGS},
        {"name": "Boulangerie", "tags": BAKERY_TAGS},
    ],
    "Faire ses courses": [
        {"name": "Épicerie", "tags": SUPERMARKET_TAGS + CONVENIENCE_TAGS},
    ],
    "Services": [
        {"name": "Station-service", "tags": FUEL_TAGS},
    ],
    "Besoins essentiels": [
        {"name": "Fontaine", "tags": DRINKING_WATER_TAGS},
        {"name": "Toilettes", "tags": TOILETS_TAGS},
    ],
    "Loisirs": [
        {"name": "Site pique-nique", "tags": PICNIC_SITE_TAGS},
    ],
    "Culture & Tourisme": [
        {"name": "Musée", "tags": MUSEUM_TAGS},
        {"name": "Attraction", "tags": ATTRACTION_TAGS},
        {"name": "Point de vue", "tags": VIEWPOINT_TAGS},
        {"name": "Place de marché", "tags": MARKETPLACE_TAGS},
    ],
}

# === 🔁 COMPATIBILITÉ : Recréer ALL_POI_TYPES pour server.py ===
ALL_POI_TYPES = {
    item["name"]: item["tags"]
    for category in POI_CATEGORIES.values()
    for item in category
}

# === ✅ POI_STYLES (pour la carte) ===
POI_STYLES = {
    "Restaurant": {"icon": "utensils", "color": "red"},
    "Fast-food": {"icon": "hamburger", "color": "orange"},
    "Café": {"icon": "coffee", "color": "beige"},
    "Pub": {"icon": "beer", "color": "darkred"},
    "Bar": {"icon": "glass-cheers", "color": "black"},
    "Boulangerie": {"icon": "bread-slice", "color": "orange"},
    "Épicerie": {"icon": "shopping-cart", "color": "green"},
    "Station-service": {"icon": "gas-pump", "color": "blue"},
    "Fontaine": {"icon": "fountain", "color": "lightblue"},
    "Toilettes": {"icon": "restroom", "color": "purple"},
    "Site pique-nique": {"icon": "utensils", "color": "green"},
    "Musée": {"icon": "building", "color": "brown"},
    "Attraction": {"icon": "flag", "color": "pink"},
    "Point de vue": {"icon": "binoculars", "color": "cadetblue"},
    "Place de marché": {"icon": "store", "color": "darkgreen"},
}