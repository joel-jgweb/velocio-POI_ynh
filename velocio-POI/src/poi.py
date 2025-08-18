from shapely.geometry import LineString, Point
from geopy.distance import distance as geopy_distance

def trace_to_linestring(points):
    """
    Convertit une liste de points (lat, lon) en une LineString Shapely.
    Shapely travaille en (x, y) → (lon, lat)
    """
    return LineString([(lon, lat) for lat, lon in points])


def is_poi_near_trace(poi_lat, poi_lon, trace_line, max_distance_m=100):
    """
    Détermine si un POI est proche de la trace (en mètres), en tenant compte
    de la distance perpendiculaire à la trace et des extrémités (début/fin).
    
    Args:
        poi_lat (float): Latitude du POI
        poi_lon (float): Longitude du POI
        trace_line (LineString): La trace sous forme de ligne (Shapely)
        max_distance_m (int): Distance maximale en mètres

    Returns:
        bool: True si le POI est à moins de max_distance_m de la trace
    """
    poi_point = Point(poi_lon, poi_lat)

    # 1. Distance au segment le plus proche de la trace (distance orthogonale)
    nearest_point_on_trace = trace_line.interpolate(trace_line.project(poi_point))
    lon_near, lat_near = nearest_point_on_trace.x, nearest_point_on_trace.y  # ← CORRIGÉ ICI
    dist_to_line = geopy_distance((poi_lat, poi_lon), (lat_near, lon_near)).meters

    # 2. Distance au point de départ de la trace
    start_lon, start_lat = trace_line.coords[0]
    dist_to_start = geopy_distance((poi_lat, poi_lon), (start_lat, start_lon)).meters

    # 3. Distance au point d'arrivée de la trace
    end_lon, end_lat = trace_line.coords[-1]
    dist_to_end = geopy_distance((poi_lat, poi_lon), (end_lat, end_lon)).meters

    # On garde la plus petite des trois distances
    min_distance = min(dist_to_line, dist_to_start, dist_to_end)

    return min_distance <= max_distance_m

def deduplicate_pois(pois, merge_distance_m=10):
    """
    Élimine les doublons géographiques dans la liste des POI.
    Deux POI sont considérés comme doublons si leur distance est < merge_distance_m.
    On garde le premier trouvé, mais on pourrait fusionner les infos si besoin.
    """
    unique = []
    for poi in pois:
        lat, lon = poi["lat"], poi["lon"]
        is_dup = False
        for upoi in unique:
            if geopy_distance((lat, lon), (upoi["lat"], upoi["lon"])).meters < merge_distance_m:
                is_dup = True
                break
        if not is_dup:
            unique.append(poi)
    return unique