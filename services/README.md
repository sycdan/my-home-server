# Services

Tools for managing multiple Docker-based services on a home server.

## Quick Start

### 1. Initial Setup (Bootstrap)

Run this once on a server machine to install Docker and initialize services:

```bash
# Initialize and setup Immich
./init immich
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
# Start Immich
./ctl immich up
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
- Should create/validate `.env` from `example.env`

### 4. Create Example Configuration

Create `example.env` with all required variables and documentation.

## Idempotency

All bootstrapping scripts are designed to be **idempotent** - they can safely be run multiple times without side effects:

- Creating files: Only create if they don't exist
- Installing packages: Check if already installed
- Creating directories: Use `-p` flag or conditional checks
- Modifying configs: Only modify if needed

This means you can:

```bash
# Safe to run multiple times
./init immich
./init immich
./init immich
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
./ctl immich restart
```

## Storage & Backup with Git Annex

Service data files are managed with git annex, and _not_ checked in:

- **Immich library**: `services/immich/library/`
- **Immich database**: `services/immich/postgres/`
- **Immich config**: `services/immich/.env`

## Troubleshooting

### Can't run scripts

```bash
$ ./init
-bash: ./init: Permission denied

chmod +x ./init
chmod +x ./ctl
```

### Service won't start

```bash
# Check status of all services
./ctl all status

# Check service logs
./ctl immich logs

# Verify configuration
cat services/immich/.env
```
