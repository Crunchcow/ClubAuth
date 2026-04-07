#!/bin/bash
# Deploy-Skript für ClubAuth auf Hetzner-Server
# Verwendung: ./deploy.sh

set -e

SERVER="root@89.167.0.28"
APP_DIR="/var/www/clubauth"
SERVICE="clubauth"

echo "→ Push zu GitHub..."
git push origin main

echo "→ Deploy auf Server..."
ssh "$SERVER" "
  cd $APP_DIR &&
  git pull origin main &&
  .venv/bin/pip install -r requirements.txt -q &&
  .venv/bin/python manage.py migrate --noinput &&
  .venv/bin/python manage.py collectstatic --noinput &&
  systemctl restart $SERVICE &&
  systemctl is-active $SERVICE
"

echo "✓ ClubAuth wurde erfolgreich deployed."
