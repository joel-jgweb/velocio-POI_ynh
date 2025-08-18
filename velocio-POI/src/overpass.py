import requests
from config import USER_AGENT, OVERPASS_API_URLS
from cache import load_cache, save_cache

def build_query(selected_tags, bbox):
    """
    Construit une requête Overpass pour les tags sélectionnés et la bbox.
    Inclut les node, way et relation pour chaque type de POI.
    """
    query_parts = []
    for tag in selected_tags:
        query_parts.append(
            f'node[{tag["key"]}={tag["value"]}]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});'
        )
        query_parts.append(
            f'way[{tag["key"]}={tag["value"]}]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});'
        )
        query_parts.append(
            f'relation[{tag["key"]}={tag["value"]}]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});'
        )
    query = (
        "[out:json];("
        + "".join(query_parts)
        + ");out center;"
    )
    return query

def query_overpass(query):
    """
    Envoie la requête Overpass et retourne le résultat en JSON.
    Essaie chaque serveur Overpass disponible jusqu'à obtenir une réponse.
    Utilise le cache pour éviter les appels répétés.
    """
    cached = load_cache(query)
    if cached is not None:
        return cached

    last_exception = None
    for url in OVERPASS_API_URLS:
        try:
            response = requests.post(
                url,
                data={'data': query},
                headers={'User-Agent': USER_AGENT},
                timeout=20
            )
            response.raise_for_status()
            data = response.json()
            save_cache(query, data)
            return data
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur avec le serveur {url} : {e}")
            last_exception = e
        except requests.exceptions.JSONDecodeError as e:
            print(f"⚠️ Réponse JSON invalide du serveur {url} : {e}")
            last_exception = e
    raise Exception(f"Erreur lors de la requête à Overpass API : {last_exception}")