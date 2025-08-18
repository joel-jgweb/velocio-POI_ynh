# src/exporter.py
# Export des résultats en CSV et GPX avec enrichissement (description, catégorie, symbole)
from lxml import etree
import csv
from config import OUTPUT_DIR, ALL_POI_TYPES, GPX_SYMBOLS  # ← On importe GPX_SYMBOLS depuis config.py


def get_category_by_label(label):
    """Retourne la catégorie d'un POI à partir de son label."""
    for poi_type in ALL_POI_TYPES:
        if poi_type["label"] == label:
            return poi_type["category"]
    return "Autre"


def export_gpx(trace, pois):
    """Exporte la trace et les POI au format GPX 1.1"""
    gpx = etree.Element(
        "gpx",
        version="1.1",
        creator="Velocio Traces & Spots",
        xmlns="http://www.topografix.com/GPX/1/1"
    )

    # Ajout de la trace
    trk = etree.SubElement(gpx, "trk")
    trkname = etree.SubElement(trk, "name")
    trkname.text = "Parcours cycliste"
    trkseg = etree.SubElement(trk, "trkseg")
    for lat, lon in trace:
        etree.SubElement(trkseg, "trkpt", lat=str(lat), lon=str(lon))

    # Ajout des POI
    for poi in pois:
        wpt = etree.SubElement(gpx, "wpt", lat=str(poi["lat"]), lon=str(poi["lon"]))
        name = etree.SubElement(wpt, "name")
        name.text = poi.get("name", "Sans nom")

        # Description
        desc = etree.SubElement(wpt, "desc")
        desc.text = poi.get("description", "")

        # Symbole GPX (affiché dans les logiciels comme QGIS, BaseCamp, etc.)
        sym = etree.SubElement(wpt, "sym")
        sym.text = GPX_SYMBOLS.get(poi["label"], "Waypoint")  # ✅ Utilisation depuis config.py

        # Type (label)
        typ = etree.SubElement(wpt, "type")
        typ.text = f"POI:{poi['label']}"

        # Catégorie dans une extension
        extensions = etree.SubElement(wpt, "extensions")
        category = etree.SubElement(extensions, "category")
        category.text = get_category_by_label(poi["label"])

    # Sauvegarde
    path = OUTPUT_DIR / "resultats_poi.gpx"
    tree = etree.ElementTree(gpx)
    tree.write(str(path), encoding="utf-8", xml_declaration=True, pretty_print=True)
    return str(path)


def export_csv(pois):
    """Exporte les POI en CSV avec toutes les informations enrichies"""
    csv_path = OUTPUT_DIR / "pois.csv"
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "lat", "lon", "name", "type", "label", "address", "city", "description", "category"
        ])
        for poi in pois:
            writer.writerow([
                poi.get("lat", ""),
                poi.get("lon", ""),
                poi.get("name", ""),
                poi.get("type", ""),
                poi.get("label", ""),
                poi.get("address", ""),
                poi.get("city", ""),
                poi.get("description", ""),
                get_category_by_label(poi["label"])
            ])
    return str(csv_path)