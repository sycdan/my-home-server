# Server-PC

This is Nicole's old Ryzen 5 PC, in a Thermaltake case.

Ethernet MAC address: 70:85:C2:4F:35:AB

## Setup

Install [Ubuntu](<../Ubuntu.md>).

## Troubleshooting

### Machine Crashes

trying text only mode

```
sudo systemctl set-default multi-user.target
sudo reboot
```

restore with


```
sudo systemctl set-default graphical.target
```


### Learnings

Disabling IOMMU didn't stop crashes:

```bash
sudo nano /etc/default/grub
# GRUB_CMDLINE_LINUX_DEFAULT="quiet splash iommu=off" <-- add iommu part
sudo update-grub
sudo reboot
```
