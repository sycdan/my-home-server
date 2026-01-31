# AI Coding Instructions for my-home-server

**MOST IMPORTANT RULE:** Keep your responses concise and relevant to the context of the my-home-server project. Avoid unnecessary elaboration. Minimize verbosity, just the relevant/actionable details.

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
  ├─ NAT rules - forwards ingress.lan:80/443
  └─ Split DNS - resolves public domains to internal IPs for LAN clients
  ↓
Ingress Server
  ├─ nginx reverse proxy - routes domains to internal services
  └─ Uses resolver directive for runtime DNS resolution
  ↓
Services (Immich, Jellyfin, etc.) on different machines
```

**Key detail:** Devices are located by `.lan` hostnames (ingress.lan, router.lan) not static IPs. This allows devices to move/reboot without reconfiguring reverse proxy.
