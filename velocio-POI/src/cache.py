import json
from pathlib import Path
from hashlib import md5
from datetime import datetime, timedelta
from config import CACHE_DIR

CACHE_TTL = timedelta(hours=24)  # Durée de vie du cache

def get_cache_path(query: str) -> Path:
    # La clé query peut maintenant inclure le segment index
    return CACHE_DIR / (md5(query.encode()).hexdigest() + ".json")

def load_cache(query: str):
    path = get_cache_path(query)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            timestamp = datetime.fromisoformat(data.get("timestamp", ""))
            if datetime.now() - timestamp > CACHE_TTL:
                path.unlink()  # Supprime le cache expiré
                return None
            return data["data"]
    except Exception:
        return None
    return None

def save_cache(query: str, data):
    path = get_cache_path(query)
    try:
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Échec de sauvegarde du cache : {e}")