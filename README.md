# My Home Server

A unified home infrastructure system: Docker orchestration, DNS-based service discovery, reverse proxy routing, and protobuf configuration.

**Key Principle:** Services are addressed by `device.lan` hostnames and ports, not IPs. This allows devices to move/reboot with minimal reconfiguration.

## Devices

- [MikroTik hEX](./docs/MikroTik%20hEX.md) running [RouterOS](https://help.mikrotik.com/docs/spaces/ROS/pages/328059/RouterOS)
- [Netgear R7000P](./docs/Netgear%20R7000P.md) running [DD-WRT](https://dd-wrt.com/) (access point)
- [Old Lenovo Laptop](./docs/Lenovo%204446%2038U.md) running [Ubuntu](https://ubuntu.com/download/desktop?version=24.04&architecture=amd64&lts=true) (service host)
- [Raspberry Pi 3](./docs/Raspberry%20Pi%203.md) running Debian (reverse proxy)

### Adding a device or service

On your local machine, edit the [fleet file](./mhs/config/fleet.textproto):

```proto
devices {
  key: "my-laptop"
  value {
    macs: "AA:BB:CC:DD:EE:01"
    macs: "AA:BB:CC:DD:EE:02"
    services {
      key: "my-service"
      value {
        port: 59999
      }
    }
    comment: "Personal laptop"
  }
}
```

**Note**: The first MAC should be ethernet, if available; the second can be wireless.

### Discovering devices

Assign a static DNS hostname to the device:

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

### Install protobuf compiler

Get the [latest release for your system](https://github.com/protocolbuffers/protobuf/releases):

**Examples:**

- [Windows](https://github.com/protocolbuffers/protobuf/releases/download/v33.3/protoc-33.3-win64.zip)
  - Unzip to `C:\protoc` and ensure `C:\protoc\bin` is on your path.

Verify installation:

```bash
protoc --version
```

### Install buf (protobuf linter)

Download the [latest buf release](https://github.com/bufbuild/buf/releases) for your system:

**Examples:**

- **Windows:** Download `buf-Windows-x86_64.exe`, rename to `buf.exe`, and place in your PATH
- **macOS:** `brew install bufbuild/buf/buf`
- **Linux:** Download the appropriate binary and place in `/usr/local/bin/buf`

Verify installation:

```bash
# Note: If you have oh-my-bash installed, you may need to use the full path
# due to a naming conflict with the oh-my-bash 'buf' backup function
/path/to/buf --version
```

To lint protobuf files:

```bash
# Use full path if you have oh-my-bash naming conflict
/c/Users/Dan/bin/buf lint proto/
```

### Install python requirements

```bash
pip install -r requirements-dev.txt
```

[Protocol Buffers Releases](https://github.com/protocolbuffers/protobuf/releases)

Sync work-in-progress to a remote for testing with [rsync](./docs/Rsync.md):

```bash
rsync -avz ./services/ingress/ ingress:~/my-home-server/services/ingress/ && ssh ingress '~/my-home-server/services/ingress/init'
```

### Creating Actions

```bash
./call mhs/actions/create_action --help
```

## Troubleshooting

### Client can't reach services after moving hardware

If you've moved a device (e.g., from WiFi to ethernet) and changed its IP, the router's DNS records will update via the discovery script after a few minutes. However, **client machines may have cached the old DNS entry**. Clear your DNS cache:

- **Windows:** `ipconfig /flushdns` (in PowerShell/Command Prompt)
- **macOS:** `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder`
- **Linux:** `sudo systemctl restart systemd-resolved` or flush your resolver cache

After clearing the cache, DNS queries will hit the router again and resolve to the new IP.
