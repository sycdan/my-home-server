# Hostname-Based Routing Deployment

This guide walks through setting up the new `.lan` hostname-based routing architecture.

## Prerequisites

- RouterOS device with script and scheduler capabilities
- Reverse proxy server (Raspberry Pi) with nginx
- Services on LAN with consistent MAC addresses

## Step 1: Configure RouterOS DNS

Enable DNS resolution from within the LAN:

```bash
ssh router -x '/ip dns set allow-remote-requests=yes'
```

This allows the router to answer DNS queries for internal `.lan` hostnames from DHCP leases.

## Step 2: Deploy DNS Discovery Script

A single unified script handles discovering the reverse proxy and all services, pinging them to verify reachability, and updating DNS entries.

On your host machine:

```bash
# Deploy the unified discovery script to RouterOS
python devices/mikrotek-hex/deploy-service-script \
  devices/mikrotek-hex/scripts/discovery.rsc \
  --ssh-host router \
  --schedule "00:05:00" \
  --run
```

This will:
1. Create a script named `discovery` on the router
2. Schedule it to run every 5 minutes
3. Run it immediately to populate DNS entries
4. The script updates all `.lan` hostnames based on ping reachability

The script handles:
- `reverse-proxy.lan` → finds reachable IP of Raspberry Pi (tries ethernet, then wireless)
- `immich.lan` → finds reachable IP of Immich service
- `jellyfin.lan` → finds reachable IP of Jellyfin service

### Customizing for Your Services

Edit [discovery.rsc](devices/mikrotek-hex/scripts/discovery.rsc) to add more services:

```routeros
:local services {
  {
    "hostname"="service-name.lan";
    "macs"={
      {"AA:BB:CC:DD:EE:FF"; "ethernet"};
      {"AA:BB:CC:DD:EE:GG"; "wireless"};
    }
  };
}
```

## Step 3: Configure Reverse Proxy (nginx)

The DNS discovery script now automatically updates `.lan` hostnames, so nginx can use them directly.

On the Raspberry Pi:

```bash
# Copy the configuration script
cp devices/raspberry-pi/configure-reverse-proxy.sh ~/configure-reverse-proxy.sh

# Edit it with your services
nano ~/configure-reverse-proxy.sh
```

The `SERVICES` array format is:

```bash
declare -a SERVICES=(
  "external_domain|internal_hostname.lan|internal_port"
  "stream.sycdan.com|jellyfin.lan|8096"
  "photos.sycdan.com|immich.lan|2283"
)
```

Then run it:

```bash
bash ~/configure-reverse-proxy.sh
```

The script will:
1. Generate nginx upstream blocks for each `.lan` hostname
2. Create server blocks for each external domain  
3. Reload nginx

## Step 4: Configure Port Forwarding

On RouterOS, set up NAT rules to forward external traffic to the reverse proxy:

```bash
# The reverse proxy's IP is automatically maintained in DNS
# Run this script on the router:
{
  /ip firewall nat remove [find where comment~"[MHS]"]
  
  # Get the reverse proxy IP from DNS (updated by the discovery script)
  :local rpIp [/ip dns static get [find name="reverse-proxy.lan"] address]
  
  :if ($rpIp = "") do={
    :put "ERROR: reverse-proxy.lan not found in DNS"
  } else={
    :put "Setting up NAT rules for $rpIp"
    
    # HTTP
    /ip firewall nat add \
      comment="Ingress HTTP [MHS]" \
      chain=dstnat \
      in-interface=ether1 \
      protocol=tcp \
      dst-port=80 \
      action=dst-nat \
      to-addresses=$rpIp \
      to-ports=80
    
    # HTTPS
    /ip firewall nat add \
      comment="Ingress HTTPS [MHS]" \
      chain=dstnat \
      in-interface=ether1 \
      protocol=tcp \
      dst-port=443 \
      action=dst-nat \
      to-addresses=$rpIp \
      to-ports=443
    
    # Hairpin NAT (internal clients accessing via external domain)
    /ip firewall nat add \
      comment="Hairpin Ingress [MHS]" \
      chain=srcnat \
      src-address=192.168.1.0/24 \
      protocol=tcp \
      dst-port=80 \
      action=src-nat \
      to-addresses=192.168.1.1
    /ip firewall nat add \
      comment="Hairpin Ingress HTTPS [MHS]" \
      chain=srcnat \
      src-address=192.168.1.0/24 \
      protocol=tcp \
      dst-port=443 \
      action=src-nat \
      to-addresses=192.168.1.1
  }
}
```

## Step 5: Configure Split DNS

Internal clients resolve external domains to the reverse proxy:

```bash
# On RouterOS
{
  :local services {
    "photos.sycdan.com"
    "stream.sycdan.com"
  }
  
  :local rpIp [/ip dns static get [find name="reverse-proxy.lan"] address]
  
  :if ($rpIp != "") do={
    /ip dns static remove [find comment~"Internal Ingress"]
    
    :foreach service in=$services do={
      :put "Forwarding $service → $rpIp"
      /ip dns static add name=$service address=$rpIp comment="Internal Ingress"
    }
  }
}
```

### Verification

**Test RouterOS DNS:**

```bash
# From any machine on the LAN
nslookup immich.lan 192.168.1.1
nslookup reverse-proxy.lan 192.168.1.1

# If nslookup not available:
getent hosts reverse-proxy.lan
```

**Test nginx resolution:**

```bash
# SSH to reverse proxy
ssh pi@reverse-proxy.lan

# Test DNS resolution
nslookup immich.lan
nslookup jellyfin.lan
```

**Test reverse proxy routing:**

```bash
# From LAN client
curl -H "Host: photos.sycdan.com" http://reverse-proxy.lan

# From WAN (if configured with real domain)
curl https://photos.sycdan.com
```

### Troubleshooting

**DNS lookup fails:**
```bash
# Check if DNS is enabled
ssh router -x ':put [/ip dns get allow-remote-requests]'

# Check DNS cache
ssh router -x '/ip dns cache print'
```

**Reverse proxy IP not updating:**
```bash
# Check if discovery script ran
ssh router -x '/system script job print'

# Check script output
ssh router -x '/system script run reverse-proxy-discovery'

# Verify DNS entry was created
ssh router -x '/ip dns static print where name="reverse-proxy.lan"'
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

