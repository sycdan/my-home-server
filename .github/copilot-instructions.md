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
  ├─ DNS discovery scripts to find & register .lan hostnames
  ├─ NAT rules - forwards ingress.lan:80/443 to Pi
  └─ Split DNS - resolves public domains to internal IPs for LAN clients
  ↓
Raspberry Pi 3
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

- **`lib/common.sh`** - Shared bash utilities for all scripts

## Key Files & Important Locations

### Configuration Files

- **`fleet.json`** - Central configuration defining domains and services across devices
  - `domains` - Domain registration and management info
  - `devices` - Hardware configs with MAC addresses and hosted services
- **`example.env`** - Project-level environment variables template

### Orchestration & Control

- **`services/<service>/init`** - Main bootstrap script; handles OS detection, Docker install, firewall setup, service setup

### Ingress System

- **`services/ingress/init`** - Ingress setup script that:
  - Loads domains and services from `fleet.json`
  - Validates domain registration via HTTP checks
  - Creates DNS CNAME records via Porkbun API
  - Configures nginx reverse proxy
- **`services/ingress/lib/load-services.sh`** - Extracts service configs from fleet.json
- **`services/ingress/lib/parse-and-validate-domains.sh`** - Domain validation and filtering

### Network & DNS

- **`bin/deploy-discovery-scripts`** - Creates a RouterOS script per device that:
  - Updates DNS `.lan` entries on the router (TTL: 5 minutes)

### Environment Configuration

- Service configuration lives in `.env` files (excluded from git via `.gitignore`)
- `example.env` serves as documentation and template
- Global config variables prefixed with `MHS_` and live in root `.env`

### Error Handling Pattern

All entrypoint scripts use `set -e` to exit on first error. Use the three-level messaging system:

```bash
print_status "Starting operation..."  # Blue [INFO]
print_success "Completed"             # Green [SUCCESS]
print_warning "Note this"             # Yellow [WARNING]
print_error "Failed"                  # Red [ERROR]
```

### Script Root Finding

Service-bootstrapping scripts locate their own directory and project root using:

```bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/../../" && pwd )"
source "$ROOT_DIR/lib/common.sh"
source "$SCRIPT_DIR/.env"
```

## Adding a New Service

1. **Add to fleet.json:** Update device entry with service definition:
   ```json
   "devices": {
     "mydevice": {
       "services": {
         "myservice": {
           "port": 8080
         }
       }
     }
   }
   ```
2. **Create service directory:** `mkdir services/myservice`
3. **Add docker-compose.yml:** Use upstream source when available
4. **Create example.env:** Document all configuration options

## Important Implementation Notes

- **Code formatting:** Use consistent indentation (2 spaces), lowercase variable names with underscores for python, and clear function names in bash scripts.

## Git Strategy

- `.env` files are git-ignored (user-specific configuration)
- `example.env` files are committed (documentation)
