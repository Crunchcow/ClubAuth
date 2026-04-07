#!/bin/bash
set -e
cd /var/www/clubauth

python3 -c "
import secrets, pathlib
key = secrets.token_urlsafe(50)
env = '\n'.join([
    'SECRET_KEY=' + key,
    'DEBUG=False',
    'ALLOWED_HOSTS=auth.westfalia-osterwick.de,localhost,127.0.0.1',
    'OIDC_RSA_PRIVATE_KEY_FILE=private.pem',
    'MS_CLIENT_ID=',
    'MS_CLIENT_SECRET=',
    'MS_TENANT_ID=common',
    ''
])
pathlib.Path('.env').write_text(env)
print('.env geschrieben')
"

echo "--- Migrate ---"
.venv/bin/python3 manage.py migrate --noinput

echo "--- Collectstatic ---"
.venv/bin/python3 manage.py collectstatic --noinput

echo "--- systemd Service (als root) ---"
sed 's|User=www-data|User=root|g' clubauth.service > /etc/systemd/system/clubauth.service
mkdir -p /var/log/clubauth

systemctl daemon-reload
systemctl enable clubauth
systemctl start clubauth
sleep 2
systemctl is-active clubauth

echo "--- Nginx ---"
cp nginx.conf /etc/nginx/sites-enabled/clubauth
nginx -t && systemctl reload nginx

echo "=== ClubAuth erfolgreich deployed ==="
