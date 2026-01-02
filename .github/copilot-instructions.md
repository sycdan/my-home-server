# AI Coding Instructions for my-home-server

## Project Overview

**my-home-server** is a unified Docker-based multi-service orchestration system for managing home server applications. It provides a centralized initialization system and control interface for independent Docker Compose services.

**Architecture principle:** Each service is self-contained with its own `docker-compose.yml` and idempotent `bootstrap.sh` setup script. The framework is designed to be service-agnostic and extensible.

## Key Files & Structure

- **`init`** - Main orchestration script; sources `lib/common.sh` and calls each service's `bootstrap.sh`. Handles OS detection, Docker installation, UFW firewall, fail2ban security hardening.
- **`ctl`** - Service control utility; delegates to `docker compose` commands with a consistent CLI interface across all services.
- **`lib/common.sh`** - Utility functions used by all scripts: `print_status()`, `print_success()`, `print_warning()`, `print_error()` for consistent colored output.
- **`services/<service>/`** - Each service directory contains:
  - `docker-compose.yml` - Service definition (read from upstream or adapted)
  - `bootstrap.sh` - Idempotent setup: creates `.env` from `example.env`, validates required vars, creates data directories
  - `example.env` - Template with required environment variables

## Critical Patterns & Conventions

### Idempotency First
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

### Status & Debugging
```bash
./ctl all status        # Show all services
./ctl immich shell      # Change into service directory (does _not_ start a shell in docker)
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
