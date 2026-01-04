#!/bin/bash
# Generate nginx reverse proxy configuration from services array
# Services use .lan internal hostnames to locate actual services
# Format: "external_domain|internal_hostname|internal_port"

set -e

declare -a SERVICES=(
  # Example services - update these with your actual services
  "stream.sycdan.com|jellyfin.lan|8096"
  "photos.sycdan.com|immich.lan|2283"
)

echo "Generating reverse proxy configuration..."

# Build nginx config from services array
CONFIG=""
for service in "${SERVICES[@]}"; do
  IFS='|' read -r DOMAIN HOSTNAME PORT <<< "$service"
  
  CONFIG+="upstream ${HOSTNAME//./_}_backend {
    server $HOSTNAME:$PORT;
}

server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 4G;

    location / {
        proxy_pass http://${HOSTNAME//./_}_backend;
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
