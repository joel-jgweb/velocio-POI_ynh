# src/server.py - Velocio Traces & Spots
# Version complète et corrigée pour YunoHost
import time
import threading
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, abort
from pathlib import Path

# === 🔧 CORRECTION : DOSSIER DE DONNÉES DANS /var/www/app/data ===
# Remplace Path.home() / ".velocio_poi" → évite les erreurs de permission
DATA_DIR = Path("/var/www/velocio-poi-ynh/data")
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = DATA_DIR / "output"

# Créer les dossiers avec bons droits
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# === FIN DE LA CORRECTION ===

from config import ALL_POI_TYPES, USER_AGENT
from gpx_utils import parse_gpx, split_trace_by_distance
from overpass import build_query, query_overpass
from poi import trace_to_linestring, is_poi_near_trace, deduplicate_pois
from exporter import export_csv, export_gpx
from map import generate_map
from cache import load_cache, save_cache
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "velocio_poi_temp_key_2025"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Variables globales pour le suivi
global_trace = []
global_pois = []
global_progress = {"progress": 0, "status": "Prêt", "done": False}


def start_processing():
    """Traite la trace GPX et recherche les POI en arrière-plan."""
    global global_trace, global_pois, global_progress

    try:
        # 1. Parser le fichier GPX
        gpx_path = os.path.join(app.config['UPLOAD_FOLDER'], "trace.gpx")
        if not os.path.exists(gpx_path):
            global_progress["status"] = "Erreur : fichier GPX manquant"
            global_progress["done"] = True
            return

        global_progress["status"] = "Analyse de la trace GPX..."
        global_trace = parse_gpx(gpx_path)
        if not global_trace:
            global_progress["status"] = "Erreur : trace vide ou invalide"
            global_progress["done"] = True
            return

        global_progress["progress"] = 10

        # 2. Convertir la trace en LineString Shapely
        trace_line = trace_to_linestring(global_trace)
        bounds = trace_line.bounds  # (min_lon, min_lat, max_lon, max_lat)
        global_progress["progress"] = 15

        # 3. Découper la trace pour le cache
        segments = split_trace_by_distance(global_trace, 5000)  # 5 km
        total_segments = len(segments)
        global_progress["status"] = "Recherche des POI autour de la trace..."
        time.sleep(0.5)

        # 4. Rechercher les POI pour chaque type sélectionné
        selected_types = request.form.getlist("poi_types")
        if not selected_types:
            selected_types = list(ALL_POI_TYPES.keys())

        total_tasks = len(selected_types)
        task_num = 0

        all_pois = []

        for type_name in selected_types:
            tags = ALL_POI_TYPES[type_name]
            global_progress["status"] = f"Recherche : {type_name}..."

            for i, segment in enumerate(segments):
                seg_line = trace_to_linestring(segment)
                bounds = seg_line.bounds
                query = build_query(tags, bounds)
                try:
                    result = query_overpass(query)
                    for element in result.get("elements", []):
                        lat, lon = element["lat"], element["lon"]
                        if is_poi_near_trace(lat, lon, seg_line, max_distance_m=100):
                            all_pois.append({
                                "type": type_name,
                                "name": element.get("tags", {}).get("name", "Inconnu"),
                                "lat": lat,
                                "lon": lon,
                                "address": ""  # sera complété plus tard si nécessaire
                            })
                except Exception as e:
                    print(f"Erreur sur segment {i} pour {type_name}: {e}")

                # Mise à jour de la progression
                progress = 15 + int((task_num / total_tasks) * 85) + int((i + 1) / total_segments * (85 / total_tasks))
                global_progress["progress"] = min(100, progress)

            task_num += 1

        # 5. Supprimer les doublons
        global_progress["status"] = "Nettoyage des doublons..."
        global_pois = deduplicate_pois(all_pois)
        global_progress["progress"] = 95

        # 6. Exporter les résultats
        export_csv(global_trace, global_pois)
        export_gpx(global_trace, global_pois)
        generate_map(global_trace, global_pois)

        global_progress["progress"] = 100
        global_progress["status"] = "Terminé !"
        global_progress["done"] = True

    except Exception as e:
        global_progress["status"] = f"Erreur : {str(e)}"
        global_progress["done"] = True
        print(f"Erreur dans start_processing : {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Sauvegarder le fichier GPX
        if 'gpx_file' not in request.files:
            return redirect(request.url)
        file = request.files['gpx_file']
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.endswith('.gpx'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], "trace.gpx")
            file.save(filepath)

            # Réinitialiser l'état
            global global_trace, global_pois, global_progress
            global_trace = []
            global_pois = []
            global_progress = {"progress": 0, "status": "Préparation...", "done": False}

            # Démarrer le traitement en arrière-plan
            thread = threading.Thread(target=start_processing)
            thread.daemon = True
            thread.start()

            return redirect(url_for('progress'))
    return render_template("index.html", poi_types=ALL_POI_TYPES)


@app.route("/progress")
def progress():
    return render_template("progress.html")


@app.route("/progress/status")
def progress_status():
    return jsonify(global_progress)


@app.route("/results")
def results():
    return render_template("results.html", pois=global_pois)


@app.route("/download_csv")
def download_csv():
    path = OUTPUT_DIR / "pois.csv"
    if not path.exists():
        abort(404, "Le fichier CSV n'existe pas.")
    return send_file(path, as_attachment=True)


@app.route("/download_gpx")
def download_gpx():
    path = OUTPUT_DIR / "resultats_poi.gpx"
    if not path.exists() and global_trace and global_pois:
        export_gpx(global_trace, global_pois)
    if not path.exists():
        abort(404, "Le fichier GPX n'existe pas.")
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)