# Server-PC

This is Nicole's old Ryzen 5 PC, in a Thermaltake case.

Ethernet MAC address: 70:85:C2:4F:35:AB

## Setup

Install [Ubuntu](<../Ubuntu.md>).

## Troubleshooting

### Machine Crashes

Try text only mode:

```bash
sudo systemctl set-default multi-user.target
sudo reboot
```

...restore with...

```bash
sudo systemctl set-default graphical.target
```

(didn't work)

### IOMMU

Disabling IOMMU didn't stop crashes:

```bash
sudo nano /etc/default/grub
# GRUB_CMDLINE_LINUX_DEFAULT="quiet splash iommu=off" <-- add iommu part
sudo update-grub
sudo reboot
```

### Try a conservative GPU kernel parameter

While we’re probing the graphics angle, add a conservative amdgpu flag.

Edit /etc/default/grub:

```bash
sudo nano /etc/default/grub
```

Change the line to:

bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash iommu=off amdgpu.dc=0"
Then:

```bash
sudo update-grub
sudo reboot
```
