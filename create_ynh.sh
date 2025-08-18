#!/bin/bash
# create_ynh.sh - Création fiable de la structure YunoHost

set -euo pipefail  # Arrêt strict en cas d'erreur

echo "🚀 Création de la structure YunoHost"

# Créer les dossiers
mkdir -p scripts conf doc

# === manifest.json ===
cat << 'EOF' > manifest.json
{
  "name": "Velocio Traces & Spots",
  "id": "velocio_ynh",
  "description": "Recherche de POI OpenStreetMap autour d'une trace GPX",
  "description_fr": "Trouvez restaurants, hébergements, services vélo, etc.",
  "version": "1.0.0~ynh1",
  "maintainer": {
    "name": "joel-jgweb",
    "email": "ton-email@domaine.tld"
  },
  "urls": {
    "code": "https://github.com/joel-jgweb/velocio-POI_ynh"
  },
  "requirements": { "yunohost": ">= 4.0" },
  "multi_instance": true,
  "services": ["nginx", "uwsgi"]
}
EOF

# === scripts/install ===
cat << 'EOF' > scripts/install
#!/bin/bash
app=$1
final_path="/var/www/$app"
git clone https://github.com/joel-jgweb/Velocio-POI.git "$final_path"
python3 -m venv "$final_path/venv"
source "$final_path/venv/bin/activate"
pip install -r "$final_path/requirements.txt"
mkdir -p /home/yunohost.app/.velocio_poi/{cache,output}
chown -R yunohost.app:yunohost.app /home/yunohost.app/.velocio_poi "$final_path"
echo "✅ Installé"
EOF
chmod +x scripts/install

# === scripts/upgrade ===
cat << 'EOF' > scripts/upgrade
#!/bin/bash
app=$1
cd "/var/www/$app" || exit
git pull
source venv/bin/activate
pip install -r requirements.txt
systemctl reload nginx
systemctl restart uwsgi-app@$app
EOF
chmod +x scripts/upgrade

# === scripts/remove ===
cat << 'EOF' > scripts/remove
#!/bin/bash
app=$1
rm -rf "/var/www/$app"
systemctl stop uwsgi-app@$app || true
systemctl disable uwsgi-app@$app || true
rm -f "/etc/uwsgi/apps-available/$app.ini"
rm -f "/etc/uwsgi/apps-enabled/$app.ini"
rm -f "/etc/nginx/conf.d/*/$app.conf"
systemctl reload nginx
EOF
chmod +x scripts/remove

# === conf/nginx.conf ===
cat << 'EOF' > conf/nginx.conf
location ~ ^/___%APP_ID___(/.*)?$ {
    alias /var/www/%APP_ID%$1;
    uwsgi_pass %APP_ID%;
    include uwsgi_params;
    uwsgi_param SCRIPT_NAME /___%APP_ID___;
    uwsgi_modifier1 30;
}
EOF

# === conf/uwsgi.ini ===
cat << 'EOF' > conf/uwsgi.ini
[uwsgi]
chdir = /var/www/%(app)
module = src.server:app
home = /var/www/%(app)/venv
callable = app
master = true
processes = 2
socket = /run/uwsgi/app/%(app)/uwsgi.sock
chmod-socket = 666
vacuum = true
die-on-term = true
EOF

# === README.md ===
cat << 'EOF' > README.md
# Velocio Traces & Spots - App YunoHost

Application pour rechercher des POI OpenStreetMap autour d'une trace GPX.

## Installation
```bash
sudo yunohost app install https://ton-domaine.tld/git/joel/velocio-POI_ynh.git