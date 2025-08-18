# Velocio Traces & Spots (Velocio-POI) V1.0.1 

Outil Python pour rechercher et afficher des Points d’Intérêt (POI) autour d’une trace GPX, basé sur OpenStreetMap et Overpass API.

## Fonctionnalités

- Sélection des POI à rechercher (restaurants, hébergements, vélos, etc.)
- Import de trace GPX
- Recherche et affichage des POI sur carte interactive
- Export en CSV et GPX
- Exécutable Windows fourni (voir section Téléchargement)

## Installation (version Python)

1. **Cloner le dépôt**
    ```bash
    git clone https://github.com/joel-jgweb/Velocio-POI.git
    cd Velocio-POI
    ```

2. **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

3. **Lancer l’application**
    ```bash
    cd src
    python start.py
    ```

4. **Utiliser l’exécutable Windows**
    - Téléchargez `Velocio_T&S_Installer.exe` depuis la section [Releases](https://github.com/joel-jgweb/Velocio-POI/releases).
    - Double-cliquez pour installer et utiliser le logiciel sans Python.

## Compilation
- **Windows :**  
    Lancez `build.bat` (Python requis)
- **Linux :**  
    Lancez `build.sh` (Python requis)

## Fonctionnalités avancées
- Cache intelligent des POI (24h)
- Réutilisation des adresses entre traces
- Respect des CGU OpenStreetMap

## Téléchargement

Retrouvez les exécutables Windows dans la section [Releases](https://github.com/joel-jgweb/Velocio-POI/releases).

## Licence

Ce projet est distribué sous licence **GNU GPLv3**.  
Vous êtes libre de l'utiliser, le modifier et le redistribuer, à condition que toute version modifiée soit également distribuée sous licence GPLv3.  
Voir le fichier [LICENSE](LICENSE) pour le texte complet de la licence.

## Contribuer

Les contributions sont les bienvenues !  
Ouvrez une issue ou une pull request sur GitHub.

---

### À propos de la licence

La **GPLv3** impose que tout logiciel dérivé ou toute redistribution soit également sous licence GPLv3.  
Pour plus d'informations, consultez [https://www.gnu.org/licenses/gpl-3.0.fr.html](https://www.gnu.org/licenses/gpl-3.0.fr.html).
