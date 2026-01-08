# My Home Server

A unified home infrastructure system: Docker orchestration, DNS-based service discovery, reverse proxy routing, and device-specific configuration scripts.

**Key Principle:** Services are addressed by `device.lan` hostnames and ports, not IPs. This allows devices to move/reboot with minimal reconfiguration.

## [Devices](./fleet.json)

- [MikroTik hEX](./docs/MikroTik%20hEX.md) running [RouterOS](https://help.mikrotik.com/docs/spaces/ROS/pages/328059/RouterOS)
- [Netgear R7000P](./docs/Netgear%20R7000P.md) running [DD-WRT](https://dd-wrt.com/) (access point)
- [Old Lenovo Laptop](./docs/Lenovo%204446%2038U.md) running [Ubuntu](https://ubuntu.com/download/desktop?version=24.04&architecture=amd64&lts=true) (service host)
- [Raspberry Pi 3](./docs/Raspberry%20Pi%203.md) running Debian (reverse proxy)

### Adding a device

On your local machine, add the device to `./fleet.json`:

```json
{
  "devices": {
    "laptop": {
      "primary_mac": "AA:BB:CC:DD:EE:01",
      "secondary_mac": "AA:BB:CC:DD:EE:02",
      "description": "My Laptop"
    }
  }
}
```

**Note**: `primary_mac` should be ethernet, if available; `secondary_mac` can be wireless.

### Discovering devices

Assign a static DNS hostname to the device:

```bash
./discover
```

Check that the device was discovered:

```bash
ssh router '/ip dns static print' | grep laptop
```

### Configuring SSH access

Add an entry to `~/.ssh/config`:

```text
Host laptop
  HostName laptop.lan
  User me
```

### Running commands

```bash
ssh laptop 'whoami && hostname && hostname -A && hostname -I'
```

### Repo Access

To be able to clone the repo on service hosts, you need to add [Deploy Keys](https://github.com/sycdan/my-home-server/settings/keys).

For each device, run:

```bash
# Create (but don't overwrite) a new RSA key and list all public keys
ssh device 'ssh-keygen -t rsa -b 4096 -N "" -q <<< ""'
ssh device 'cat .ssh/*.pub'
```

## Domains

| Domain                   | Role           | Registrar                                                                                     |
| ------------------------ | -------------- | --------------------------------------------------------------------------------------------- |
| sycdan.com               | DDNS domain    | [DreamHost](https://panel.dreamhost.com/index.cgi?tree=domain.dashboard#/site/sycdan.com/dns) |
| wildharvesthomestead.com | Ingress domain | [Porkbun](https://porkbun.com/account)                                                        |
|                          |                |                                                                                               |

### Adding a new domain

From the `ingress.lan` machine, modify the [SERVICES array](./lib/services.sh) then run:

```bash
./services/ingress/init
```

---

# OLD

### 2. Deploy DNS Discovery

The discovery script auto-discovers all services and updates DNS every 5 minutes:

```bash
devices/mikrotek-hex/deploy-script \
  devices/mikrotek-hex/scripts/discovery.rsc \
  --ssh-host router \
  --run \
  --schedule "00:05:00"
```

This creates DNS entries (`.lan`), NAT port forwarding (80/443 → ingress), and split DNS for public domains.

**Edit [discovery.rsc](devices/mikrotek-hex/scripts/discovery.rsc)** to add service MAC addresses:

```bash
:local services {
  {"hostname"="myservice.lan"; "interfaces"={{"AA:BB:CC:DD:EE:FF"; "ethernet"}}};
}
```

### 3. Initialize Services on Each Host

On each Ubuntu machine that will run services:

```bash
git clone <repo> ~/my-home-server
cd ~/my-home-server
./services/init
```

This installs Docker, adds your user to the docker group, and sets up firewall rules. **You may need to log out/in for docker group permissions.**

### 4. Configure Each Service

For each service you want to run:

```bash
nano services/<service>/.env
./ctl <service> up
```

See individual service `example.env` for required variables.

### 5. Configure Reverse Proxy (Pi)

On the Raspberry Pi, edit the services list:

```bash
nano devices/raspberry-pi/configure-reverse-proxy.sh
```

Format:
```bash
declare -a SERVICES=(
  "stream.sycdan.com|jellyfin.lan|8096"
  "photos.sycdan.com|immich.lan|2283"
)
```

Run it:
```bash
bash devices/raspberry-pi/configure-reverse-proxy.sh
```

This generates nginx config with proper DNS resolution and reloads the proxy.

## Adding a New Service

1. **Create directory:**
   ```bash
   mkdir services/myservice && cd services/myservice
   ```

2. **Add docker-compose.yml** (use upstream sources when available)

3. **Create bootstrap.sh** (idempotent — safe to run multiple times):
   ```bash
   #!/bin/bash
   set -e
   
   SERVICE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
   ROOT_DIR="$( cd "$SERVICE_DIR/../../" && pwd )"
   source "$ROOT_DIR/lib/common.sh"
   
   # Create .env from example.env if missing
   [[ -f .env ]] && return
   cp example.env .env
   
   # Create data directories
   mkdir -p data
   
   # Validate required env vars
   grep -q "REQUIRED_VAR=" .env || {
     print_error "Set REQUIRED_VAR in .env"
     exit 1
   }
   ```

4. **Create example.env** with all required variables and defaults

5. **Test:**
   ```bash
   ./services/init myservice
   ./ctl myservice up
   ```

## Adding a New Domain

### 1. Register Domain & Add Free DNS

Go to [FreeDNS](https://freedns.afraid.org) and create A records for each service subdomain.

### 2. Update Reverse Proxy

Edit `devices/raspberry-pi/configure-reverse-proxy.sh`:

```bash
declare -a SERVICES=(
  "stream.sycdan.com|jellyfin.lan|8096"
  "photos.example-family.com|immich.lan|2283"  # New domain
  "files.example-family.com|navidrome.lan|4533"
)
```

Run it:
```bash
bash devices/raspberry-pi/configure-reverse-proxy.sh
```

### 3. Update Router Discovery (if needed)

If the service is on a new host, add its MAC to [discovery.rsc](devices/mikrotek-hex/scripts/discovery.rsc). The discovery script will find it and update DNS.

## Service Management

```bash
./ctl <service> up              # Start service
./ctl <service> down            # Stop service
./ctl <service> logs -n 50      # View last 50 log lines
./ctl <service> ps              # Show containers
./ctl <service> shell           # Enter service directory
./ctl all status                # Show all services
```

## Available Services

- **immich** — Photo management & library
- **jellyfin** — Video streaming
- **navidrome** — Music streaming
- **freedns** — Dynamic DNS updates for sycdan.com

## Key Files

- `services/init` — Bootstrap script (installs Docker, firewall setup)
- `services/ctl` — Service control CLI
- `lib/common.sh` — Shared bash utilities
- `devices/mikrotek-hex/scripts/discovery.rsc` — RouterOS DNS/NAT discovery (runs every 5 min)
- `devices/raspberry-pi/configure-reverse-proxy.sh` — nginx reverse proxy generator

## Device Notes

- **Raspberry Pi 3** — Reverse proxy (ingress.lan); nginx with dynamic DNS resolution
- **MikroTik hEX** — Network router; discovers services and updates `.lan` DNS
- **External Storage** — WD MyPassport automounts at `/mnt/mypassport`; symlinked for service data

## External Storage Setup

If you have external drives (e.g., for large photo/media libraries), add them to `/etc/fstab`:

```bash
# Find the UUID of your drive
sudo blkid

# Add to /etc/fstab (use nofail so boot doesn't hang if drive is disconnected)
UUID=448A4A818A4A700A /mnt/mypassport ntfs uid=1000,gid=1000,umask=0002,nofail 0 0

# Mount it
sudo mount /mnt/mypassport

# Symlink service data directories
ln -s /mnt/mypassport/immich-library services/immich/library
```

**Important:** Use `nofail` so the system boots normally even if the drive isn't connected. If the drive is unplugged when a service tries to access it, the service will fail until you reconnect the drive.

**Permissions:**
```bash
sudo chown -R $(whoami):docker /mnt/mypassport/
```

## Troubleshooting

**Services not accessible by hostname:**
- Check router DNS: `nslookup immich.lan 192.168.1.1`
- Force discovery update: `ssh router '/system script run discovery'`
- Clear client DNS cache if device moved IPs

**Reverse proxy won't start:**
- Ensure nginx config has `resolver 192.168.1.1` and `set $backend` variables (not static IPs)
- Check logs: `sudo systemctl status nginx`

**Service missing from discovery:**
- Verify MAC address in discovery.rsc
- Check device is on correct network/interface
- Run: `ssh router '/system script run discovery'` to force update

```bash
nslookup ingress.lan || getent hosts ingress.lan 
```

This should display the reverse-proxy IP.

**Test nginx resolution:**

From your local machine, verify the reverse proxy can resolve `.lan` hostnames:

```bash
# On Windows
nslookup immich.lan 192.168.1.1
nslookup jellyfin.lan 192.168.1.1

# Or from the Pi itself
ssh pi@ingress.lan
ping immich.lan
ping jellyfin.lan
```

**Test reverse proxy routing:**

```bash
# From LAN client
curl -H "Host: photos.sycdan.com" http://ingress.lan

# From WAN (if you can connect to a VPN)
curl http://photos.sycdan.com
```

**Verify NAT rules are configured:**

```bash
# SSH to router and check NAT rules
ssh router -x '/ip firewall nat print where comment~"[MHS]"'
```

#### Troubleshooting

**DNS lookup fails:**

```bash
# Check if DNS is enabled
ssh router -x ':put [/ip dns get allow-remote-requests]'

# Check DNS cache
ssh router -x '/ip dns cache print'
```

**Reverse proxy IP not updating or NAT rules outdated:**

```bash
# Check if discovery script ran recently
ssh router -x '/system script job print'

# Run discovery script manually to update DNS and NAT
ssh router -x '/system script run discovery'

# Verify DNS entry was created
ssh router -x '/ip dns static print where name="ingress.lan"'

# Check NAT rules were created
ssh router -x '/ip firewall nat print where comment~"[MHS]"'
```

**nginx can't resolve .lan hostnames:**

```bash
# Check nginx resolver config (should use router as upstream)
# On Raspberry Pi, check /etc/nginx/sites-available/reverse-proxy

# Test from Pi
ping immich.lan
ping jellyfin.lan

# Test nginx config
sudo nginx -t
```

**Client can't reach services after moving hardware:**

If you've moved a device (e.g., from WiFi to ethernet) and changed its IP, the router's DNS records will update via the discovery script. However, **client machines may have cached the old DNS entry**. Clear your DNS cache:

- **Windows:** `ipconfig /flushdns` (in PowerShell/Command Prompt)
- **macOS:** `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder`
- **Linux:** `sudo systemctl restart systemd-resolved` or flush your resolver cache

After clearing the cache, DNS queries will hit the router again and resolve to the new IP. The TTL is set to 5 minutes, so stale entries expire quickly even without manual flushing.
