# Ubuntu

Common operating system used by network devices.

## Installation

Download an image from https://ubuntu.com/download/desktop?version=24.04&architecture=amd64&lts=true.

Write to flash drive (e.g. with Balena Etcher).

Restart machine and pick the flash drive as the boot device.

Configure [SSH](<SSH.md>).

## Mounting Drives

```bash
# list device uuids
lsblk -f 

# add to fstab
```
