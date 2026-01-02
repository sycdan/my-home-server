# My Home Server

A unified controller for managing multiple Docker-based services on my home server.

## Architecture

```
my-home-server/
├── init                  # Main initialization script
├── ctl                   # Service control utility
├── README.md
├── services/
│   ├── immich/           # Immich photo management service
│   │   ├── docker-compose.yml
│   │   ├── example.env
│   │   ├── bootstrap.sh  # Service-specific setup
│   │   └── ...           # Additional service files
│   ├── nextcloud/        # Future service example
│   │   ├── docker-compose.yml
│   │   ├── example.env
│   │   ├── bootstrap.sh
│   │   └── ...
│   └── [other-services]/
```

## Quick Start

### 1. Initial Setup (Bootstrap)

Run this once on a server machine to install Docker and initialize services:

```bash
# Initialize and setup Immich
bash init immich

# Or setup multiple services at once
bash init immich nextcloud
```

The init script will:

- Check your OS (Ubuntu recommended)
- Install Docker and Docker Compose if needed
- Call each service's bootstrap script (idempotent)

**Note:** You may need to log out and back in for Docker group permissions to take effect.

### 2. Configure Services

After setup, configure each service:

```bash
# Edit Immich configuration
nano services/immich/.env
```

Update required variables like:

- Database credentials
- Storage locations
- Service-specific settings

### 3. Start Services

Use the control script to manage services:

```bash
# Start a service
bash ctl.sh up immich

# View logs
bash ctl.sh logs immich

# Stop a service
bash ctl.sh down immich

# View service status
bash ctl.sh status

# Restart a service
bash ctl.sh restart immich
```

## Service Control (ctl.sh)

Quick reference for managing services:

```bash
# Available commands:
bash ctl.sh up <service>        # Start service (docker compose up -d)
bash ctl.sh down <service>      # Stop service (docker compose down)
bash ctl.sh restart <service>   # Restart service
bash ctl.sh logs <service>      # Follow service logs
bash ctl.sh ps <service>        # Show containers
bash ctl.sh status              # Show all service status
bash ctl.sh list                # List available services
bash ctl.sh shell <service>     # Open shell in service directory
```

### Examples:

```bash
# View last 100 lines of logs for Immich
bash ctl.sh logs immich -n 100

# Stop all containers in Immich without removing volumes
bash ctl.sh down immich

# Open shell in Immich directory
bash ctl.sh shell immich
```

## Adding a New Service

### 1. Create Service Directory

```bash
mkdir services/myservice
cd services/myservice
```

### 2. Create Docker Compose File

Create `docker-compose.yml` with your service definition.

### 3. Create Setup Script

Create `bootstrap.sh` that's idempotent (safe to run multiple times):

```bash
#!/bin/bash
set -e

# Your setup logic here
# - Create .env from example.env if it doesn't exist
# - Validate configuration
# - Create needed directories
# - etc.
```

**Key requirements:**
- Must be idempotent (safe to run multiple times)
- Should not run as root
- Should check for Docker availability
- Should create/validate `.env` from `example.env`

### 4. Create Example Configuration

Create `example.env` with all required variables and documentation.

### 5. Register Service

Just having a `services/myservice/bootstrap.sh` and `docker-compose.yml` is enough. It will automatically appear in:
- `bash init` (bootstrap)
- `bash ctl.sh list` (service listing)

## Idempotency

All setup scripts are designed to be **idempotent** - they can safely be run multiple times without side effects:

- Creating files: Only create if they don't exist
- Installing packages: Check if already installed
- Creating directories: Use `-p` flag or conditional checks
- Modifying configs: Only modify if needed

This means you can:
```bash
# Safe to run multiple times
bash init immich
bash init immich
bash init immich
```

## Configuration Management

Each service has:
- **example.env**: Template with all available options and documentation
- **.env**: Actual configuration (created from example.env, not in git)

To update service configuration:

```bash
# Edit the service's .env file
nano services/immich/.env

# Restart the service to apply changes
bash ctl.sh restart immich
```

## Storage Locations

Services use relative paths for data storage by default:
- **Immich photos**: `./immich-data`
- **Immich database**: `./immich-db`

These are relative to the service directory (`services/immich/`). To use absolute paths, edit the `.env` file.

## Troubleshooting

### Service won't start
```bash
# Check service logs
bash ctl.sh logs immich

# Check Docker status
docker ps -a

# Verify configuration
cat services/immich/.env
```

### Permission denied errors
```bash
# Docker requires group permissions
# Log out and back in, or run:
newgrp docker
```

### Port conflicts
If ports are already in use, edit `docker-compose.yml` to use different ports:
```yaml
ports:
  - '2283:2283'  # Change first number to new port
```

## Monitoring

Monitor all services:

```bash
# See all running containers
bash ctl.sh status

# Watch logs in real-time
bash ctl.sh logs immich

# Check specific container
docker ps | grep immich
docker logs immich_server
```

## Backup & Recovery

Each service manages its own data:

```bash
# Backup Immich data
tar czf immich-backup.tar.gz services/immich/immich-data services/immich/immich-db

# Restore
tar xzf immich-backup.tar.gz
```

## Contributing New Services

To add a new service:

1. Create the service directory
2. Add `docker-compose.yml`
3. Add `example.env` with all configuration options
4. Add `bootstrap.sh` (must be idempotent)
5. Test thoroughly

## License

MIT
