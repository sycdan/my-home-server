# Hostname-Based Routing Deployment

This guide walks through setting up the new `.lan` hostname-based routing architecture.

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
devices/mikrotek-hex/deploy-script \
  devices/mikrotek-hex/scripts/discovery.rsc \
  --ssh-host router \
  --run \
  --schedule "00:05:00"
```

This will:

1. Create a script named `discovery` on the router
2. Schedule it to run every 5 minutes
3. Run it immediately to populate DNS entries for all services (including ingress)
4. Automatically set up port forwarding NAT rules
5. Automatically configure split DNS for external domains

### Customizing for Your Services

Edit [discovery.rsc](devices/mikrotek-hex/scripts/discovery.rsc) to add more services:

```bash
:local services {
  {
    "hostname"="service-name.lan";
    "interfaces"={
      {"AA:BB:CC:DD:EE:FF"; "ethernet"};
      {"AA:BB:CC:DD:EE:GG"; "wireless"};
    }
  };
}
```

## Step 3: Configure Reverse Proxy (nginx)

The DNS discovery script automatically updates `.lan` hostnames, so nginx can use them directly.

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
  "example.sycdan.com|example.lan|7777"
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

## Verification

**Test RouterOS DNS:**

From any machine on the LAN:

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

### Troubleshooting

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
