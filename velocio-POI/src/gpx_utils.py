import gpxpy
from geopy.distance import geodesic

def parse_gpx(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            gpx = gpxpy.parse(f)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((point.latitude, point.longitude))
        return points
    except Exception as e:
        raise Exception(f"Erreur lors du parsing du fichier GPX : {e}")

def split_trace_by_distance(points, segment_km=5):
    """
    Découpe la trace en segments de segment_km kilomètres.
    Retourne une liste de listes de points.
    """
    if not points:
        return []
    segments = []
    segment = [points[0]]
    cumu_dist = 0.0
    for i in range(1, len(points)):
        prev = segment[-1]
        curr = points[i]
        cumu_dist += geodesic(prev, curr).km
        segment.append(curr)
        if cumu_dist >= segment_km:
            segments.append(segment)
            segment = [curr]
            cumu_dist = 0.0
    if segment:
        segments.append(segment)
    return segments