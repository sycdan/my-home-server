# My Home Server

A unified home infrastructure system: Docker orchestration, DNS-based service discovery, reverse proxy routing, and device-specific configuration scripts.

## [Devices](docs/devices/)

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

**Note**: primary mac should be ethernet, if available; secondary (optional) can be wireless.

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

You need to figure out how to enable [SSH](<docs/SSH.md>) on the device, based on its OS.

Then, add an entry to your local `~/.ssh/config`, using the DNS hostname from the router:

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

### Shims

Add this to `.venv/Scripts/activate`:

```bash
if [ -f "$VIRTUAL_ENV/../.venvrc" ]; then
  source "$VIRTUAL_ENV/../.venvrc"
fi
```

Then add new services to your `$PATH` in `.venvrc` to allow direct execution in remote envs:

```bash
PATH="$PATH:./services/kopia/bin"
```

## [Domains](<docs/domains/>)

### Adding a new domain

Create a <domain_label>.md file in `docs/domains/`.

Add to [fleet](<fleet.json>)

TODO: what next? edit files in services/ingress probably

```bash
./run services/ingress/init
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
