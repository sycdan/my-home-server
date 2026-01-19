# Ubuntu

Common operating system used by network devices.

## Installation

Download an image from https://ubuntu.com/download/desktop?version=24.04&architecture=amd64&lts=true.

Write to flash drive (e.g. with Balena Etcher).

Restart machine and pick the flash drive as the boot device.

## Configure SSH

```bash
# update system
sudo apt update
sudo apt upgrade -y

# install openssh server
sudo apt install ssh -y

# start server on boot
sudo systemctl enable ssh

# verify status
sudo systemctl status ssh

# allow ssh through firewall
sudo ufw allow ssh
sudo ufw enable
```

Put your SSH pubkey in `~/ssh/authorized_keys`.

## Mounting Drives

```bash
# list device uuids
lsblk -f 

# add to fstab
```
