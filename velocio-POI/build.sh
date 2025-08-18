#!/bin/bash

echo "🚀 Compilation de velocio_T&S en exécutable Linux"
echo "🔧 Création d'un environnement virtuel isolé"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/../compillinux/venv"
REQUIREMENTS="$PROJECT_DIR/requirements.txt"
SPEC_FILE="$PROJECT_DIR/velocio_T&S.spec"
DIST_DIR="$PROJECT_DIR/dist"

# === 1. Créer le dossier de compilation et l'environnement virtuel ===
cd "$PROJECT_DIR" || { echo "❌ Échec : répertoire projet introuvable"; exit 1; }

mkdir -p ../compillinux
cd ../compillinux || { echo "❌ Impossible d'accéder à ../compillinux"; exit 1; }

if [ -d "venv" ]; then
    echo "ℹ️  Environnement virtuel existant détecté. Réutilisation..."
else
    echo "📁 Création de l'environnement virtuel dans $VENV_DIR..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Échec de la création de l'environnement virtuel. Installez python3-venv."
        echo "   sudo apt install python3-venv"
        exit 1
    fi
fi

# === 2. Activer l'environnement virtuel ===
echo "🔌 Activation de l'environnement virtuel..."
source venv/bin/activate

# === 3. Mettre à jour pip ===
echo "📦 Mise à jour de pip..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "❌ Échec de la mise à jour de pip"
    deactivate
    exit 1
fi

# === 4. Installer les dépendances du projet ===
echo "💾 Installation des dépendances depuis $REQUIREMENTS..."
pip install -r "$REQUIREMENTS"
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation des dépendances"
    deactivate
    exit 1
fi

# === 5. Installer PyInstaller si absent ===
echo "🛠️  Vérification de PyInstaller..."
if ! python -c "import PyInstaller" &>/dev/null; then
    echo "📥 PyInstaller non trouvé. Installation..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "❌ Échec de l'installation de PyInstaller"
        deactivate
        exit 1
    fi
else
    echo "✅ PyInstaller déjà installé"
fi

# === 6. Retour au répertoire projet et nettoyage ancien build ===
cd "$PROJECT_DIR" || exit 1

echo "🧹 Nettoyage des anciens builds..."
rm -rf "$DIST_DIR" build/ "$SPEC_FILE"

# === 7. Génération du fichier .spec pour PyInstaller ===
echo "⚙️  Génération du fichier .spec..."
cat > "$SPEC_FILE" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/start.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/templates', 'templates'),
        ('src/static', 'static'),
        ('src/splash.html', '.'),
        ('src/uploads', 'uploads'),
    ],
    hiddenimports=[
        'flask',
        'gpxpy',
        'shapely',
        'folium',
        'requests',
        'lxml',
        'geopy',
        'markupsafe',
        'jinja2',
        'click',
        'itsdangerous',
        'werkzeug',
        'server',
        'cache',
        'overpass',
        'poi',
        'enrich',
        'gpx_utils',
        'exporter',
        'map',
        'config'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='velocio_T&S_V1.0.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
)
EOF

# === 8. Lancement de PyInstaller ===
echo "📦 Lancement de PyInstaller..."
pyinstaller --clean "$SPEC_FILE"

# === 9. Vérification du résultat ===
if [ $? -eq 0 ]; then
    echo "✅ Succès ! L'exécutable est prêt :"
    echo "    $DIST_DIR/velocio_T&S_V1.0.1"
    # Rendre exécutable
    chmod +x "$DIST_DIR/velocio_T&S_V1.0.1" 2>/dev/null || true
else
    echo "❌ Échec de la compilation."
    deactivate
    exit 1
fi

# === 10. Désactiver l'environnement virtuel ===
deactivate
echo "🔚 Environnement virtuel désactivé."

echo "🎉 Compilation terminée. Vous pouvez exécuter l'application avec :"
echo "   ./dist/velocio_T&S_V1.0.1"
