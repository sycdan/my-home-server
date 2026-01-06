Acts as a reverse proxy to route traffic from the public internet to internal services.

```ssh-pubkey
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPE5wo15rZ8cS3J/cHTMpgCOZ8Q59DbIZ9YGIkDavl7B dan@my-home-server
```

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

The reverse proxy uses `.lan` internal hostnames to locate services. This allows services to move between IPs without changing the proxy configuration.

Edit the `configure-reverse-proxy.sh` script with your services, then run it:

```bash
# Edit the SERVICES array with your actual services
nano /path/to/configure-reverse-proxy.sh

# Run the script to generate and reload nginx
bash /path/to/configure-reverse-proxy.sh
```

**Service format:** `"external_domain|internal_hostname.lan|internal_port"`

Example:
```bash
declare -a SERVICES=(
  "stream.sycdan.com|jellyfin.lan|8096"
  "photos.sycdan.com|immich.lan|2283"
)
```

The reverse proxy will resolve `jellyfin.lan` and `immich.lan` via the router's DNS, which returns the IP of the actual service machine.
