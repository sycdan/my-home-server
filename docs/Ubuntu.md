# Ubuntu

Common operating system used by network devices.

## Installation

Download an image from https://ubuntu.com/download/desktop?version=24.04&architecture=amd64&lts=true.

Write to flash drive (e.g. with Balena Etcher).

Restart machine and pick the flash drive as the boot device.

Configure [SSH](<SSH.md>).

## Mounting Drives

```bash
# list device uuids and names
lsblk -f 

# make a mount point
sudo mkdir /mnt/mydrive

# or mount temporarily (get /dev/name from lsblk)
sudo mount /dev/sdb2 /mnt/mydrive

# add to fstab for permanent mounting (get uuid from lsblk)
sudo nano /etc/fstab
```

## Troubleshooting

### Memtest

Get to GRUB bootloader by repeatedly pressing `esc` on startup.
