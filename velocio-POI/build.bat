@echo off
:: ---------------------------------------------------------------------------
:: Script de compilation pour Velocio Traces & Spots (velocio-POI)
:: ---------------------------------------------------------------------------
cd /d "%~dp0"

echo ===[ DEBUT DU BUILD ]===

:: Vérification de Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installé ou pas dans le PATH.
    echo Installez Python depuis https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

:: Vérification de la version
for /f "delims=" %%i in ('python --version 2^>^&1') do set pyver=%%i
echo [INFO] Python détecté : %pyver%

:: === Suppression et recréation de ..\venv ===
if exist ..\venv (
    echo.
    echo [INFO] Suppression de l'ancien environnement virtuel...
    rd /s /q ..\venv
)

echo.
echo [INFO] Création d'un nouvel environnement virtuel dans ..\venv...
python -m venv ..\venv
if %errorlevel% neq 0 (
    echo [ERREUR] Échec de la création de l'environnement virtuel.
    echo Vérifiez que Python est correctement installé.
    pause
    exit /b 3
)
echo [OK] Environnement virtuel créé.

:: === Activation de l'environnement ===
echo.
echo [INFO] Activation de l'environnement virtuel...
if not exist ..\venv\Scripts\activate.bat (
    echo [ERREUR] Le fichier d'activation est manquant : ..\venv\Scripts\activate.bat
    echo Le venv n'a pas été créé correctement.
    pause
    exit /b 4
)
call ..\venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERREUR] Échec de l'activation de l'environnement virtuel.
    pause
    exit /b 4
)

:: Vérifie que l'on est bien dans le venv
python -c "import sys; print('Environnement actif : ' + sys.prefix)" | findstr /i "venv"
if %errorlevel% neq 0 (
    echo [ERREUR] Le venv semble ne pas être activé.
    pause
    exit /b 4
)

:: === Mise à jour de pip ===
echo.
echo [INFO] Mise à jour de pip...
python -m pip install --upgrade pip >nul
if %errorlevel% neq 0 (
    echo [ERREUR] Échec de la mise à jour de pip.
    deactivate
    pause
    exit /b 6
)

:: === Installation des dépendances ===
echo.
if exist requirements.txt (
    echo [INFO] Installation des dépendances...
    pip install -r requirements.txt
) else (
    echo [ERREUR] Fichier requirements.txt introuvable.
    pause
    exit /b 5
)

:: === Installation de PyInstaller ===
echo.
echo [INFO] Installation de PyInstaller...
pip install pyinstaller >nul

:: === Compilation avec PyInstaller ===
echo.
echo [INFO] Compilation avec PyInstaller (mode --onedir, sans console)...
pyinstaller ^
    --clean ^
    --onedir ^
    --windowed ^
    --noupx ^
    --name "velocio_T&S_V1.0.1" ^
    --add-data "src/templates;templates" ^
    --add-data "src/static;static" ^
    --add-data "src/uploads;uploads" ^
    --add-data "src/splash.html;." ^
    src/start.py

if %errorlevel% neq 0 (
    echo [ERREUR] La compilation a échoué.
    deactivate
    pause
    exit /b 8
)

echo.
echo [SUCCÈS] ✅ Compilation terminée !
echo.
echo    L'application se lance sans fenêtre de terminal.
echo    Exécutable : '%cd%\dist\velocio_T&S_V1.0.1\velocio_T&S_V1.0.1.exe'
echo.
echo 💡 Si Bit Defender bloque le fichier, ajoutez une exception dans les paramètres antivirus.
pause