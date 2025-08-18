# src/map.py - Velocio Traces & Spots
import folium
from config import OUTPUT_DIR, POI_STYLES  # Utilise POI_STYLES depuis config

def generate_map(trace, pois):
    """Génère une carte interactive avec :
    - Filtre par catégorie (LayerControl)
    - Légende visuelle (icônes + couleurs)
    - Tooltip = description enrichie
    """
    m = folium.Map(location=trace[0], zoom_start=13, tiles="OpenStreetMap")

    # Ajout de la trace
    folium.PolyLine(trace, color="blue", weight=2.5, opacity=0.8).add_to(m)

    # Regroupement des POI par catégorie
    categories = {}
    for poi in pois:
        category = poi.get("category", "Autre")
        if category not in categories:
            fg = folium.FeatureGroup(name=category, show=True)
            categories[category] = fg
            m.add_child(fg)

    # Suivi des labels déjà utilisés pour la légende
    used_labels = set()

    # Ajout des marqueurs
    for poi in pois:
        label = poi.get("label", "POI")
        name_display = poi.get("name") or "Sans nom"
        description = poi.get("description", f"{label}: {name_display}")

        # ✅ Utilisation de POI_STYLES depuis config.py
        style = POI_STYLES.get(label, {"icon": "question", "color": "gray"})
        icon_name = style["icon"]
        color = style["color"]

        popup = folium.Popup(description, max_width=300)
        tooltip = folium.Tooltip(description)

        marker = folium.Marker(
            location=[poi["lat"], poi["lon"]],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color=color, icon=icon_name, prefix="fa")
        )
        marker.add_to(categories[poi.get("category", "Autre")])

        used_labels.add(label)

    # === Contrôle des couches ===
    folium.LayerControl(collapsed=False).add_to(m)

    # === Légende visuelle ===
    legend_html = '''
    <div id="legend" style="position: fixed; bottom: 50px; right: 10px; z-index: 1000; 
        background: white; padding: 10px; border: 2px solid #ccc; border-radius: 8px;">
        <div style="font-size:14px; font-weight:bold; margin-bottom:6px;">Légende</div>
    '''
    for label in sorted(used_labels):
        style = POI_STYLES.get(label, {"icon": "question", "color": "gray"})
        icon = style["icon"]
        color = style["color"]
        legend_html += f'''
        <div style="display:flex; align-items:center; margin:4px 0;">
            <i class="fa fa-{icon}" style="color:{color}; width:24px; text-align:center;"></i>
            <span style="font-size:13px;">{label}</span>
        </div>
        '''
    legend_html += '</div>'

    m.get_root().html.add_child(folium.Element(legend_html))

    # Chargement de Font Awesome
    m.get_root().header.add_child(folium.Element(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    ))

    # Sauvegarde
    map_path = OUTPUT_DIR / "carte.html"
    m.save(map_path)
    return str(map_path)