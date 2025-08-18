# src/server.py - Velocio Traces & Spots
# Version améliorée : progression fine avec nom du POI pendant la géocodification
import time
import threading
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, abort
from config import ALL_POI_TYPES, USER_AGENT, OUTPUT_DIR
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

global_trace = []
global_pois = []
global_progress = {"progress": 0, "status": "Prêt", "done": False}
last_activity = time.time()
INACTIVITY_TIMEOUT = 300  # 5 minutes

def inactivity_watcher():
    while True:
        time.sleep(30)
        if time.time() - last_activity > INACTIVITY_TIMEOUT:
            print("\n[INACTIVITÉ] Arrêt automatique après 5 minutes.")
            os._exit(0)

@app.before_request
def before_request():
    global last_activity
    last_activity = time.time()

@app.route("/ready")
def ready():
    return jsonify({"ok": True})

@app.route("/splash")
def splash():
    return send_file(os.path.join(os.path.dirname(__file__), "splash.html"))

def group_pois():
    grouped = defaultdict(list)
    for i, poi in enumerate(ALL_POI_TYPES):
        grouped[poi["category"]].append({"index": i, "label": poi["label"]})
    ordered_titles = [
        "Se restaurer", "Café et bars", "Boutiques alimentaires", "Hébergement",
        "Services et vente de vélos", "Autres équipements", "Tourisme et culture"
    ]
    return [{"title": title, "items": grouped[title]} for title in ordered_titles if title in grouped]

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        tags_indices = request.form.getlist("poi_types")
        radius = int(request.form.get("radius", "200"))
        return redirect(url_for("upload", tags=",".join(tags_indices), radius=radius))
    grouped_pois = group_pois()
    return render_template("home.html", grouped_pois=grouped_pois)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    tags = request.args.get("tags", "")
    radius = int(request.args.get("radius", "200"))
    selected_tags = [ALL_POI_TYPES[int(i)] for i in tags.split(",") if i.isdigit()]
    selected_labels = [t["label"] for t in selected_tags]

    if request.method == "POST":
        if "gpxfile" not in request.files:
            return "Aucun fichier sélectionné", 400
        file = request.files["gpxfile"]
        if file.filename == "":
            return "Aucun fichier sélectionné", 400
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        def run_processing():
            global global_trace, global_pois, global_progress
            try:
                global_progress.update({"progress": 0, "status": "Chargement du fichier GPX...", "done": False})
                points = parse_gpx(file_path)
                global_trace = points
                total_points = len(points)
                global_progress.update({"status": f"Découpage du parcours en segments de 20km...", "progress": 10})
                time.sleep(0.3)

                segment_km = 20
                segments = split_trace_by_distance(points, segment_km=segment_km)
                num_segments = len(segments)
                global_progress.update({"status": f"{num_segments} segments à traiter (20km chacun)", "progress": 12})

                trace_line = trace_to_linestring(points)
                pois = []

                # === 🔍 Recherche des POI par segment et par type ===
                for tag_idx, tag in enumerate(selected_tags):
                    import hashlib
                    with open(file_path, 'rb') as f:
                        gpx_hash = hashlib.md5(f.read()).hexdigest()
                    tag_pois = []

                    for seg_idx, seg in enumerate(segments):
                        seg_lats = [p[0] for p in seg]
                        seg_lons = [p[1] for p in seg]
                        radius_deg = radius / 111000
                        bbox = [
                            min(seg_lats) - radius_deg,
                            min(seg_lons) - radius_deg,
                            max(seg_lats) + radius_deg,
                            max(seg_lons) + radius_deg
                        ]

                        cache_key = f"gpx:{gpx_hash}|radius:{radius}|tag:{tag['key']}={tag['value']}|seg:{seg_idx}"
                        cached = load_cache(cache_key)

                        if cached is not None:
                            print(f"✅ Cache trouvé pour segment {seg_idx} tag {tag['label']}")
                            tag_pois.extend(cached)
                        else:
                            query = build_query([tag], bbox)
                            data = query_overpass(query)
                            elements = data.get("elements", [])
                            seg_pois = []

                            for element in elements:
                                lat = element.get('lat') or (element.get('center', {}) or {}).get('lat')
                                lon = element.get('lon') or (element.get('center', {}) or {}).get('lon')
                                if lat is None or lon is None:
                                    continue
                                if is_poi_near_trace(lat, lon, trace_line, radius):
                                    seg_pois.append({
                                        "lat": lat,
                                        "lon": lon,
                                        "name": element.get('tags', {}).get("name", ""),
                                        "type": element["type"],
                                        "label": tag["label"],
                                        "category": tag["category"]  # ✅ Ajout de la catégorie
                                    })

                            save_cache(cache_key, seg_pois)
                            tag_pois.extend(seg_pois)

                        prog_base = 12 + int(60 * (tag_idx / max(1, len(selected_tags))))
                        prog = prog_base + int(20 * (seg_idx / max(1, num_segments)))
                        global_progress.update({
                            "progress": min(prog, 80),
                            "status": f"Requête OSM pour {tag['label']} (segment {seg_idx+1}/{num_segments})"
                        })

                    pois.extend(tag_pois)

                # === 🧹 Dédoublonnage des POI ===
                print(f"🔍 Avant dédoublonnage : {len(pois)} POI")
                pois = deduplicate_pois(pois, merge_distance_m=10)
                print(f"✅ Après dédoublonnage : {len(pois)} POI")
                total_pois = len(pois)

                # === 📍 Recherche des adresses avec progression détaillée ===
                if total_pois > 0:
                    global_progress.update({"status": "Recherche des adresses (0/0)...", "progress": 85})
                    for idx, poi in enumerate(pois):
                        name_display = poi.get("name") or "Sans nom"
                        label_display = poi.get("label", "POI")
                        status_text = f"{idx + 1}/{total_pois} - {name_display} ({label_display})"

                        lat_round = round(poi['lat'], 5)
                        lon_round = round(poi['lon'], 5)
                        cache_key = f"reverse:{lat_round},{lon_round}"
                        cached = load_cache(cache_key)

                        if cached is not None:
                            addr = cached
                        else:
                            try:
                                response = requests.get(
                                    "https://nominatim.openstreetmap.org/reverse",
                                    params={
                                        'lat': poi['lat'],
                                        'lon': poi['lon'],
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
                                print(f"❌ Erreur Nominatim pour {name_display} : {e}")
                                addr = {}
                            time.sleep(1)  # Respect des CGU

                        poi['address'] = (
                            addr.get('road') or addr.get('pedestrian') or
                            addr.get('residential') or addr.get('footway') or "Inconnue"
                        )
                        poi['city'] = (
                            addr.get('city') or addr.get('town') or
                            addr.get('village') or addr.get('hamlet') or 'Inconnue'
                        )
                        poi['description'] = f"{label_display}: {name_display} - {poi['address']}, {poi['city']}"

                        # Mise à jour de la progression
                        progress_percent = 85 + int(10 * (idx + 1) / total_pois)
                        global_progress.update({
                            "progress": progress_percent,
                            "status": status_text
                        })
                else:
                    global_progress.update({"status": "Aucun POI à géocoder", "progress": 85})

                # === 📤 Génération des résultats ===
                global_progress.update({"status": "Génération des résultats...", "progress": 95})
                export_csv(pois)
                generate_map(points, pois)
                export_gpx(points, pois)
                global_pois = pois
                global_progress.update({"progress": 100, "status": "Terminé !", "done": True})

            except Exception as e:
                global_progress.update({"status": f"Erreur : {str(e)}", "done": True})

        threading.Thread(target=run_processing, daemon=True).start()
        return redirect(url_for("progress"))

    return render_template("upload.html", radius=radius, selected_labels=selected_labels)

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

@app.route("/map")
def map_html():
    path = OUTPUT_DIR / "carte.html"
    if not path.exists():
        abort(404, "La carte n'existe pas.")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.route("/shutdown")
def shutdown():
    print("[Arrêt demandé via /shutdown]")
    os._exit(0)
