# Raspberry Pi 3

Acts as a reverse proxy to route traffic from the public internet to internal services.

## Access

Username: pi
Password hint: spiderweb

(ssh access is not configured)

## Setting up reverse proxy

### Install and enable nginx

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx
sudo systemctl enable --now nginx
```

### Configure nginx

Copy and paste this into a terminal on the Pi:

```bash
# Format: "sub.domain.com|internal_ip|port"
declare -a SERVICES=(
  "stream.sycdan.com|192.168.1.10|8096"
  "photos.sycdan.com|192.168.1.11|2283"
)

echo "Creating reverse proxy config..."

# Build nginx config from services array
CONFIG=""
for service in "${SERVICES[@]}"; do
  IFS='|' read -r DOMAIN IP PORT <<< "$service"
  
  CONFIG+="server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 4G;

    location / {
        proxy_pass http://$IP:$PORT;
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

echo "Done! Reverse proxy is active."
echo ""
echo "Services configured:"
for service in "${SERVICES[@]}"; do
  IFS='|' read -r DOMAIN IP PORT <<< "$service"
  echo "  $DOMAIN -> $IP:$PORT"
done
```
