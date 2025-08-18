# Changelog - Velocio Traces & Spots

## [1.0.1] - 2025-08-18

### Améliorations majeures

- **Découpage intelligent de la trace GPX**  
  - Ajout de la fonction `split_trace_by_distance()` pour découper la trace en segments (par défaut 20km) et traiter les POI par segment, ce qui accélère la recherche et limite la charge pour les serveurs OSM.
  - La progression affiche le nombre de segments, le POI en cours, et le nom du POI pendant l’enrichissement d’adresse.

- **Système de cache avancé**  
  - Le cache des résultats Overpass et Nominatim gère maintenant une durée de vie (TTL) de 24h (voir `src/cache.py`).
  - Les requêtes pour chaque segment et chaque type de POI sont mises en cache indépendamment (clé basée sur hash GPX, radius, type et segment).
  - Les adresses sont mises en cache avec arrondi des coordonnées pour maximiser la réutilisation.

- **Export GPX enrichi**  
  - Les waypoints GPX incluent : description enrichie, catégorie du POI, symbole GPX adapté (`GPX_SYMBOLS`), et type.
  - Ajout d’une extension XML pour la catégorie du POI.

- **Export CSV enrichi**  
  - Ajout de la catégorie dans le fichier CSV.
  - Les colonnes CSV sont plus complètes : lat, lon, name, type, label, address, city, description, category.

- **Carte interactive améliorée**  
  - Les POI sont regroupés par catégorie (LayerControl dans Folium).
  - Légende visuelle dynamique avec icônes et couleurs (FontAwesome).
  - Les POI sont affichés avec une icône et une couleur selon leur type (voir `POI_STYLES` dans `config.py`).
  - Tooltip et popup affichent la description enrichie pour chaque POI.

- **Respect des CGU OSM/Nominatim**  
  - Ajout de temporisations et limitation de la fréquence des requêtes (sleep).
  - Réutilisation maximale du cache pour réduire les appels réseau.

### Corrections

- Correction du hash GPX pour le cache des segments.
- Correction de la clé de cache pour Nominatim avec arrondi des coordonnées.
- Nettoyage des anciens builds dans les scripts de compilation.
- Correction du nom de l’exécutable généré sous Linux : `velocio_T&S_V1.0.1`.

### Scripts de compilation

- **build.sh** :  
  - Refactoré pour gérer le venv, les dépendances, le nettoyage, la génération du .spec, et le lancement de PyInstaller.
  - Ajout de messages explicites sur chaque étape et gestion des erreurs.
  - Le nom de l’exécutable Linux est maintenant versionné.

- **Creer_distrilinux.sh** :  
  - Adaptation pour l’exécutable versionné.
  - L’icône est convertie en .png si nécessaire.
  - Installation plus robuste (menu, bureau, icône, désinstallation).

### Interface utilisateur

- **Splash screen** :  
  - Mise à jour du numéro de version affiché.
  - Popup “À propos” améliorée.

- **Templates HTML** :  
  - Amélioration de la progression (affichage du POI en cours).
  - Meilleure organisation des catégories et des types de POI.

### Divers

- Mise à jour des dépendances dans requirements.txt (même contenu, mais cohérent entre les versions).
- README.md :  
  - Ajout de la mention des nouvelles fonctionnalités avancées (cache, découpage, respect CGU).
  - Ajout du numéro de version dans le titre.

---

## [1.0.0] - Version initiale

- Première version publique avec :
    - Recherche de POI autour d’une trace GPX via Overpass API.
    - Export CSV/GPX des résultats.
    - Interface web locale avec Flask.
    - Compilation en exécutable Windows/Linux.
    - Licence GPLv3.

---

**Format changelog :**
- `[1.0.1]` = version modifiée (Travailencours)
- `[1.0.0]` = version origine
