# AI Coding Instructions for my-home-server

## Project Overview

**my-home-server** is a unified home infrastructure system combining:

1. **Docker orchestration** - Multi-service containerized apps
2. **Network routing** - DNS-based service discovery and reverse proxy
3. **Hardware management** - Device-specific configs for machines running different services

**Core principle:** Self-contained services with automatic discovery, hostname-based routing, and idempotent setup.

## Architecture Overview

### Network & Routing Stack

```
External Traffic (WAN)
  ↓
MikroTik Router (ether1 = WAN, ether2-5 = LAN bridge)
  ├─ DNS discovery script (discovery.rsc) - finds & registers .lan hostnames
  ├─ NAT rules - forwards ingress.lan:80/443 to Pi
  └─ Split DNS - resolves public domains to internal IPs for LAN clients
  ↓
Raspberry Pi 3 (192.168.1.99, ethernet on ether5)
  ├─ nginx reverse proxy - routes domains to internal services
  └─ Uses resolver directive for runtime DNS resolution
  ↓
Services (Immich, Jellyfin, etc.) on different machines
```

**Key detail:** Services are located by `.lan` hostnames (immich.lan, jellyfin.lan) not static IPs. This allows devices to move/reboot without reconfiguring reverse proxy.

### Service Structure

- **`services/*/`** - Containerized applications

  - `docker-compose.yml` - Service definition
  - `bootstrap.sh` - Idempotent setup (env, directories, validation)
  - `example.env` - Configuration template

- **`devices/*/`** - Non-container hardware configurations

  - `mikrotek-hex/` - Router scripts and discovery logic
  - `raspberry-pi/` - Reverse proxy configuration
  - Others - Device-specific setup docs

- **`lib/common.sh`** - Shared bash utilities for all scripts

## Key Files & Important Locations

### Orchestration & Control

- **`services/init`** - Main bootstrap script; handles OS detection, Docker install, firewall setup, then calls each service's `bootstrap.sh`
- **`services/ctl`** - Service control CLI; wraps `docker compose` for consistent interface

### Network & DNS

- **`devices/mikrotek-hex/scripts/discovery.rsc`** - RouterOS script that:
  - Discovers reverse proxy (Pi) and services via MAC address + ping
  - Updates DNS `.lan` entries on the router (TTL: 5 minutes)
  - Sets up NAT port forwarding (80/443 → ingress.lan)
  - Configures split DNS for external domains
  - Runs every 5 minutes automatically
- **`devices/raspberry-pi/configure-reverse-proxy.sh`** - Generates nginx config from service list with:
  - `resolver 192.168.1.1` - Uses router as upstream DNS
  - Variables (`set $backend`) for runtime hostname resolution (critical for startup reliability)
    All setup scripts must be safe to run multiple times. Use `[[ -f file ]] && return` patterns to skip already-done work. This is enforced in `services/*/bootstrap.sh` (see `create_env_file()` pattern).

### Environment Configuration

- Service configuration lives in `.env` files (excluded from git via `.gitignore`)
- `example.env` serves as documentation and template
- `bootstrap.sh` validates required variables and exits with clear errors if missing
- Never hardcode credentials or paths in compose files

### Error Handling Pattern

All scripts use `set -e` to exit on first error. Use the three-level messaging system:

```bash
print_status "Starting operation..."  # Blue [INFO]
print_success "Completed"             # Green [SUCCESS]
print_warning "Note this"             # Yellow [WARNING]
print_error "Failed"                  # Red [ERROR]
```

### Script Root Finding

Service-bootstrapping scripts locate their own directory and project root using:

```bash
SERVICE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SERVICE_DIR/../../" && pwd )"
source "$ROOT_DIR/lib/common.sh"
```

## Troubleshooting Quick Reference

### Services Not Accessible by Hostname

1. **Ping the router DNS:** `nslookup immich.lan 192.168.1.1` - should resolve to current IP
2. **Check discovery script:** `ssh router '/system script run discovery'` - forces DNS/NAT update
3. **Client DNS cache:** If device moved, clear local DNS cache (`ipconfig /flushdns` on Windows, etc.)
4. **Nginx startup:** `ssh pi@192.168.1.99 'sudo systemctl status nginx'` - check for "host not found" errors

### Reverse Proxy Not Starting

- Error: `nginx: [emerg] host not found in upstream` → requires resolver + variables, not static upstream blocks
- Fix: Ensure `configure-reverse-proxy.sh` generates config with `resolver 192.168.1.1` and `set $backend` variables

### Device Moved IPs

- The discovery script auto-finds devices via MAC address and updates DNS within 5 minutes
- Force immediate update: `ssh router '/system script run discovery'`
- If still can't reach: clear client DNS cache (see above)

## Adding a New Service

1. **Create directory:** `mkdir services/myservice`
2. **Add docker-compose.yml:** Use upstream source when available (e.g., official project releases)
3. **Create bootstrap.sh:**
   - Source `lib/common.sh` for utilities
   - Create `.env` from `example.env` (idempotently)
   - Create required data directories
   - Validate all required env vars present
4. **Create example.env:** Document all configuration options with commented examples

## Development Workflows

### Bootstrap New Service

```bash
./init myservice
```

Runs `./services/myservice/bootstrap.sh` after system-level setup.

### Service Lifecycle

```bash
./ctl immich up         # Start (docker compose up -d)
./ctl immich logs -n 50 # Follow logs
./ctl immich down       # Stop (docker compose down)
./ctl immich ps         # View container status
```

**`.env` files** - Git-ignored (user/environment specific)

- **`example.env` files** - Committed (configuration documentation)
- **`services/*/library/`, `services/*/postgres/`** - Likely git-annexed (large media/DB files)
- **`devices/*/scripts/*.rsc`** - Committed (RouterOS scripts are text-based configs)
- **Updated `.github/copilot-instructions.md`** - After major changes to architecture or patterns
  ./ctl all status # Show all services
  ./ctl immich shell # Change into service directory (does _not_ start a shell in docker)

```

## Important Implementation Notes

- **WSL2 Detection:** Scripts detect WSL and skip systemd-dependent operations (UFW, fail2ban). Used in `init` script.
- **Docker Group:** User must be in Docker group for non-sudo access. `init` sets this but requires logout/login.
- **Compose Files:** Reference `docker-compose.yml` from upstream projects when possible to enable easy updates. Document any local customizations.
- **Service Ports:** Each service declares its own ports in `docker-compose.yml`. No centralized port mapping—services are exposed directly or via reverse proxy.
- **Data Persistence:** Services define volumes for data directories. Immich example: `UPLOAD_LOCATION` and `DB_DATA_LOCATION` env vars control storage paths.

## Git Strategy

- `.env` files are git-ignored (user-specific configuration)
- `example.env` files are committed (documentation)
- `services/*/library/` and `services/*/postgres/` are likely annexed (large media/database files)
```
