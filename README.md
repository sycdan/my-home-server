# My Home Server

A unified home infrastructure system: Docker orchestration, DNS-based service discovery, reverse proxy routing, and device-specific configuration scripts.

## [Devices](./docs/devices/)

**Note:** follow first-time setup docs for each device before continuing.

### Adding a device

On your local machine, add the device to `./fleet.json`:

```json
{
  "devices": {
    "laptop": {
      "macs": ["AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02"],
      "description": "My Laptop"
    }
  }
}
```

**Note**: `primary_mac` should be ethernet, if available; `secondary_mac` can be wireless.

### Discovering devices

Run this when adding a device, or if IPs have changed:

```bash
./discover
```

Check that the device was discovered:

```bash
ssh router '/ip dns static print' | grep laptop
```

### Configuring SSH access

You need to figure out how to enable SSH on the device, and add your SSH public key to its `~/.ssh/authorized_keys`.

Then, add an entry to your local `~/.ssh/config`:

```text
Host laptop
  HostName laptop.lan
  User me
```

Open a shell to ensure you can connect:

```bash
ssh laptop -v
```

Press `Ctrl+D` to exit.

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

## [Domains](./domains.json)

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

## Development

Sync work-in-progress to a remote for testing with [rsync](./docs/Rsync.md):

```bash
rsync -avz ./services/ingress/ ingress:~/my-home-server/services/ingress/ && ssh ingress '~/my-home-server/services/ingress/init'
```

## Troubleshooting

### Client can't reach services after moving hardware

If you've moved a device (e.g., from WiFi to ethernet) and changed its IP, the router's DNS records will update via the discovery script after a few minutes. However, **client machines may have cached the old DNS entry**. Clear your DNS cache:

- **Windows:** `ipconfig /flushdns` (in PowerShell/Command Prompt)
- **macOS:** `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder`
- **Linux:** `sudo systemctl restart systemd-resolved` or flush your resolver cache

After clearing the cache, DNS queries will hit the router again and resolve to the new IP.
