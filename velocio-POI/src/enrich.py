import requests
import time
from config import USER_AGENT
from cache import load_cache, save_cache

def enrich_poi_address(pois):
    url_base = "https://nominatim.openstreetmap.org/reverse"
    for p in pois:
        # Clé de cache basée sur les coordonnées arrondies (~1m de précision)
        lat_round = round(p['lat'], 5)
        lon_round = round(p['lon'], 5)
        cache_key = f"reverse:{lat_round},{lon_round}"
        cached = load_cache(cache_key)
        if cached is not None:
            addr = cached
        else:
            try:
                response = requests.get(
                    url_base,
                    params={
                        'lat': p['lat'],
                        'lon': p['lon'],
                        'format': 'json',
                        'accept-language': 'fr'
                    },
                    headers={'User-Agent': USER_AGENT},
                    timeout=5
                )
                if response.status_code == 200:
                    addr = response.json().get('address', {})
                    save_cache(cache_key, addr)
                else:
                    addr = {}
            except Exception as e:
                print(f"Erreur Nominatim pour {p['lat']},{p['lon']} : {e}")
                addr = {}
            time.sleep(1)  # Respect des CGU
        p['address'] = addr.get('road') or addr.get('pedestrian') or addr.get('residential') or addr.get('footway') or "Inconnue"
        p['city'] = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('hamlet') or 'Inconnue'
        p['description'] = f"{p.get('label', p.get('type','POI'))}: {p.get('name','Sans nom')} - {p['address']}, {p['city']}"
    return pois