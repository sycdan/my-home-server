# Raspberry Pi 3

Running Debian.

Acts as a reverse proxy to route traffic from the public internet to internal services.

```ssh-pubkey
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDIjFU/rXJfTI8caU0K1XAwEIasqluSuAp2ctKgKrrGUSS5M5TP7tuid0Nf1QDXQtSNkSf8KZRGiAxMvAPe4/ouO01ph8MltptMHFirxUEXCOuu4622gw1UsVlsW+exedFAckHIgGwGCksX1RX6r93Q2YXJoLbjB9kM+pl8M24hbjMh7E1V5CgYQHvEb/0ZQSxPB04N8Pxq1jGwYzheLZFRdu3r7G4njWJzo3T5gNiFujZqSf/SDoBFMT6Y2eKSpe8eXs37fbkzEC8mpuLSTJS47Plf4wKCPApJSkLWSkhPWQHqnLbkCF/tUGk5LKQS2WZ721hiOYaDnGhkqJ4TRMK07gIaYc1fykOCkr5SQ8JIa0S8xuvTuGNGHz4vF1alIMwFk30evJytlRNzmJuaysdj73kNd/LPCfyI//a4JmTLvIX+kBYYTkmOu5S+SZTYpgHbAiogQ3j3VPDPfqV3nmgm+iOrW7l/+G67UXUrOtNuhK7VYTzbX63VZ9aahnuDWI8= pi@raspberrypi
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
