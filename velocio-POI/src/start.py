# src/start.py - Version finale : splash, double libération de port, démarrage contrôlé
import os
import sys
import webbrowser
import time
import socket
import threading
import subprocess
from pathlib import Path
from flask import Flask, send_file

# ✅ Import ajouté pour la gestion des signaux (Linux/macOS)
import signal

# === Configuration ===
MAIN_PORT = 5000
SPLASH_PORT = 5001
MAIN_URL = f"http://127.0.0.1:{MAIN_PORT}"
SPLASH_PATH = Path(__file__).parent / "splash.html"


# === Fonction pour libérer un port en tuant le processus qui l'utilise ===
def kill_process_on_port(port):
    """Tente de libérer le port en tuant le processus qui l'utilise."""
    system = os.name
    try:
        if system == 'nt':  # Windows
            result = subprocess.run(
                ['netstat', '-ano', '|', 'findstr', str(port)],
                shell=True,
                capture_output=True,
                text=True
            )
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if f":{port}" in line:
                    parts = line.split()
                    pid = parts[-1]
                    subprocess.run(['taskkill', '/PID', pid, '/F'], check=True)
                    print(f"✅ Processus (PID: {pid}) sur le port {port} terminé.")
                    return True

        else:  # Linux, macOS
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Ignorer l'en-tête
                    parts = line.split()
                    pid = parts[1]
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ Processus (PID: {pid}) sur le port {port} terminé.")
                    return True

    except Exception as e:
        print(f"⚠️ Impossible de libérer le port {port} : {e}")
        return False
    return False


# === Vérifie si le port est en usage ===
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


# === Mini-serveur pour le splash ===
splash_app = Flask("splash")

@splash_app.route("/")
def splash():
    return send_file(SPLASH_PATH)

@splash_app.route("/start-flask", methods=["POST"])
def start_flask():
    """Démarre le vrai serveur Flask dans un thread."""
    threading.Thread(target=run_main_app, daemon=True).start()
    return "OK", 200


def run_main_app():
    """Importe et lance le vrai serveur Flask."""
    from server import app
    print(f"✅ Démarrage du serveur principal sur {MAIN_URL}")
    app.run(port=MAIN_PORT, use_reloader=False, threaded=True)


def main():
    # === Libération des ports 5000 et 5001 ===
    for port in [MAIN_PORT, SPLASH_PORT]:
        if is_port_in_use(port):
            print(f"⚠️ Le port {port} semble déjà utilisé.")
            print(f"🔧 Tentative de libération du port {port}...")
            if kill_process_on_port(port):
                print(f"⏳ Attente que le port {port} se libère...")
                time.sleep(1.5)
            else:
                print(f"❌ Impossible de libérer le port {port}.")
                # On continue quand même, sauf si c'est le port 5000
                if port == MAIN_PORT:
                    input("Appuyez sur Entrée pour quitter...")
                    return

    # Lance le mini-serveur pour le splash
    splash_thread = threading.Thread(
        target=lambda: splash_app.run(port=SPLASH_PORT, use_reloader=False, threaded=True),
        daemon=True
    )
    splash_thread.start()

    # Attend que le mini-serveur soit prêt
    for _ in range(10):
        if is_port_in_use(SPLASH_PORT):
            break
        time.sleep(0.1)
    else:
        print("❌ Échec du mini-serveur splash")
        return

    # Ouvre le splash
    splash_url = f"http://127.0.0.1:{SPLASH_PORT}"
    print(f"🌐 Ouvrez : {splash_url}")
    webbrowser.open(splash_url)

    # Garde le processus vivant
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Arrêt du serveur.")
        os._exit(0)


if __name__ == "__main__":
    main()