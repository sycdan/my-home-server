#!/bin/bash
# Generate nginx reverse proxy configuration from services array
# Services use .lan internal hostnames to locate actual services
# Format: "external_domain|internal_hostname|internal_port"

set -e

declare -a SERVICES=(
  "photos.sycdan.com|immich.lan|2283"
  "stream.sycdan.com|jellyfin.lan|8096"
)

echo "Generating reverse proxy configuration..."

# Build nginx config from services array
# Note: We use resolver directive and variables for dynamic DNS resolution
# This allows nginx to resolve .lan hostnames at request time rather than startup
CONFIG="# Resolve .lan hostnames using the router's DNS
resolver 192.168.1.1 valid=10s;
resolver_timeout 5s;

"

for service in "${SERVICES[@]}"; do
  IFS='|' read -r DOMAIN HOSTNAME PORT <<< "$service"
  
  CONFIG+="server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 4G;

    location / {
        set \$backend \"http://$HOSTNAME:$PORT\";
        proxy_pass \$backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_read_timeout 86400;
    }
}

"
done

echo "Writing configuration to /etc/nginx/sites-available/reverse-proxy..."
sudo tee /etc/nginx/sites-available/reverse-proxy >/dev/null <<EOF
$CONFIG
EOF

echo "Enabling reverse proxy config..."
sudo ln -sf /etc/nginx/sites-available/reverse-proxy /etc/nginx/sites-enabled/reverse-proxy

echo "Removing default site..."
sudo rm -f /etc/nginx/sites-enabled/default

echo "Testing NGINX config..."
sudo nginx -t

echo "Reloading NGINX..."
sudo systemctl reload nginx

echo ""
echo "✓ Reverse proxy is active"
echo ""
echo "Services configured:"
for service in "${SERVICES[@]}"; do
  IFS='|' read -r DOMAIN HOSTNAME PORT <<< "$service"
  echo "  $DOMAIN → $HOSTNAME:$PORT"
done
