# src/config.py
import os
from pathlib import Path

APP_NAME = "Velocio_POI"
USER_DATA_DIR = Path.home() / ".velocio_poi"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = USER_DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = USER_DATA_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

ALL_POI_TYPES = [
    # 🍽️ Se restaurer
    {"key": "amenity", "value": "restaurant", "label": "Restaurant", "category": "Se restaurer"},
    {"key": "amenity", "value": "fast_food", "label": "Fast-food", "category": "Se restaurer"},

    # Café et bars
    {"key": "amenity", "value": "cafe", "label": "Café", "category": "Café et bars"},
    {"key": "amenity", "value": "pub", "label": "Pub", "category": "Café et bars"},
    {"key": "amenity", "value": "bar", "label": "Bar", "category": "Café et bars"},

    # 🥐 Boutiques alimentaires
    {"key": "shop", "value": "bakery", "label": "Boulangerie", "category": "Boutiques alimentaires"},
    {"key": "shop", "value": "convenience", "label": "Épicerie de quartier", "category": "Boutiques alimentaires"},
    {"key": "shop", "value": "supermarket", "label": "Supermarché", "category": "Boutiques alimentaires"},
    {"key": "shop", "value": "grocery", "label": "Épicerie", "category": "Boutiques alimentaires"},
    {"key": "shop", "value": "organic", "label": "Magasin bio", "category": "Boutiques alimentaires"},
    {"key": "shop", "value": "deli", "label": "Charcuterie / Traiteur", "category": "Boutiques alimentaires"},
    {"key": "shop", "value": "vegetarian", "label": "Magasin végétarien", "category": "Boutiques alimentaires"},
    {"key": "shop", "value": "health_food", "label": "Alimentation santé", "category": "Boutiques alimentaires"},

    # 🏨 Hébergement
    {"key": "tourism", "value": "hotel", "label": "Hôtel", "category": "Hébergement"},
    {"key": "tourism", "value": "hostel", "label": "Auberge de jeunesse", "category": "Hébergement"},
    {"key": "tourism", "value": "guest_house", "label": "Chambre d'hôte", "category": "Hébergement"},
    {"key": "tourism", "value": "motel", "label": "Motel", "category": "Hébergement"},
    {"key": "tourism", "value": "apartment", "label": "Appartement touristique", "category": "Hébergement"},
    {"key": "tourism", "value": "camp_site", "label": "Camping", "category": "Hébergement"},
    {"key": "tourism", "value": "caravan_site", "label": "Aire de camping-car", "category": "Hébergement"},

    # 🚲 Services et vente de vélos
    {"key": "amenity", "value": "bicycle_repair_station", "label": "Réparation vélo", "category": "Services et vente de vélos"},
    {"key": "amenity", "value": "bicycle_parking", "label": "Stationnement vélo", "category": "Services et vente de vélos"},
    {"key": "shop", "value": "bicycle", "label": "Magasin de vélos", "category": "Services et vente de vélos"},  # Vente, réparation, accessoires

    # ⚡ Autres équipements
    {"key": "amenity", "value": "drinking_water", "label": "Eau potable", "category": "Autres équipements"},
    {"key": "amenity", "value": "toilets", "label": "Toilettes", "category": "Autres équipements"},
    {"key": "amenity", "value": "shelter", "label": "Abri", "category": "Autres équipements"},
    {"key": "tourism", "value": "picnic_site", "label": "Site pique-nique", "category": "Autres équipements"},

    # 🌍 Tourisme et culture
    {"key": "tourism", "value": "museum", "label": "Musée", "category": "Tourisme et culture"},
    {"key": "tourism", "value": "attraction", "label": "Attraction", "category": "Tourisme et culture"},
    {"key": "tourism", "value": "viewpoint", "label": "Point de vue", "category": "Tourisme et culture"},
    {"key": "amenity", "value": "marketplace", "label": "Place de marché", "category": "Tourisme et culture"},
]

USER_AGENT = f"{APP_NAME}_Tool/1.0"

# Liste des serveurs Overpass à tester dans l'ordre
OVERPASS_API_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter"
]

# === ✅ NOUVEAU : POI_STYLES (étape 1) ===
# Ne sera utilisé que plus tard dans map.py
# Pour l'instant, on le déclare seulement ici.
POI_STYLES = {
    "Restaurant": {"icon": "utensils", "color": "red"},
    "Fast-food": {"icon": "hamburger", "color": "orange"},
    "Café": {"icon": "coffee", "color": "beige"},
    "Pub": {"icon": "beer", "color": "darkred"},
    "Bar": {"icon": "glass-cheers", "color": "black"},
    "Boulangerie": {"icon": "bread-slice", "color": "orange"},
    "Épicerie de quartier": {"icon": "shopping-cart", "color": "lightgreen"},
    "Supermarché": {"icon": "shopping-cart", "color": "green"},
    "Épicerie": {"icon": "shopping-cart", "color": "lightgreen"},
    "Magasin bio": {"icon": "leaf", "color": "green"},
    "Charcuterie / Traiteur": {"icon": "hotdog", "color": "red"},
    "Magasin végétarien": {"icon": "seedling", "color": "green"},
    "Alimentation santé": {"icon": "pills", "color": "lightgreen"},
    "Hôtel": {"icon": "hotel", "color": "purple"},
    "Auberge de jeunesse": {"icon": "bed", "color": "pink"},
    "Chambre d'hôte": {"icon": "home", "color": "lightblue"},
    "Motel": {"icon": "building", "color": "cadetblue"},
    "Appartement touristique": {"icon": "building", "color": "lightgray"},
    "Camping": {"icon": "campground", "color": "green"},
    "Aire de camping-car": {"icon": "van-shuttle", "color": "darkgreen"},
    "Réparation vélo": {"icon": "wrench", "color": "blue"},
    "Stationnement vélo": {"icon": "bicycle", "color": "gray"},
    "Magasin de vélos": {"icon": "bicycle", "color": "darkblue"},
    "Eau potable": {"icon": "tint", "color": "lightblue"},
    "Toilettes": {"icon": "toilet", "color": "orange"},
    "Abri": {"icon": "umbrella", "color": "brown"},
    "Site pique-nique": {"icon": "utensils", "color": "green"},
    "Musée": {"icon": "university", "color": "purple"},
    "Attraction": {"icon": "flag", "color": "red"},
    "Point de vue": {"icon": "binoculars", "color": "orange"},
    "Place de marché": {"icon": "store", "color": "lightred"},
}

# === ✅ NOUVEAU : GPX_SYMBOLS (étape 1) ===
# Pour une migration future dans exporter.py
GPX_SYMBOLS = {
    "Restaurant": "Restaurant",
    "Fast-food": "Fast Food",
    "Café": "Coffee Shop",
    "Pub": "Bar",
    "Bar": "Bar",
    "Boulangerie": "Bakery",
    "Épicerie de quartier": "Convenience Store",
    "Supermarché": "Supermarket",
    "Épicerie": "Convenience Store",
    "Magasin bio": "Health Food Store",
    "Charcuterie / Traiteur": "Delicatessen",
    "Magasin végétarien": "Health Food Store",
    "Alimentation santé": "Health Food Store",
    "Hôtel": "Hotel",
    "Auberge de jeunesse": "Hostel",
    "Chambre d'hôte": "Guest House",
    "Motel": "Motel",
    "Appartement touristique": "Lodging",
    "Camping": "Campsite",
    "Aire de camping-car": "Caravan Site",
    "Réparation vélo": "Bicycle Repair Station",
    "Stationnement vélo": "Bicycle Parking",
    "Magasin de vélos": "Bicycle Shop",
    "Eau potable": "Drinking Water",
    "Toilettes": "Toilets",
    "Abri": "Shelter",
    "Site pique-nique": "Picnic Site",
    "Musée": "Museum",
    "Attraction": "Attraction",
    "Point de vue": "Viewpoint",
    "Place de marché": "Marketplace",
}