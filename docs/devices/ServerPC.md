# Server-PC

This is Nicole's old Ryzen 5 PC, in a Thermaltake case.

Ethernet MAC address: 70:85:C2:4F:35:AB

## Setup

Install [Ubuntu](<../Ubuntu.md>).

## Troubleshooting

TODO: iommu stuff about crashing (still not fixerd)

```bash
sudo nano /etc/default/grub
# GRUB_CMDLINE_LINUX_DEFAULT="quiet splash iommu=off" <-- add iommu config
sudo update-grub
sudo reboot
```

--- ai said
```text
1. Try fully disabling the IOMMU
This is the next logical step after passthrough mode.

Edit your GRUB line:

Code
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash amd_iommu=off"
Then:

Code
sudo update-grub
sudo reboot
If the freezes stop, you’ve confirmed the root cause.

You lose PCIe device isolation and VFIO passthrough, but for a homelab server that isn’t doing GPU passthrough, it’s usually fine.

🌿 2. Update BIOS + AGESA
This matters more than people expect.

X370 boards had years of IOMMU fixes in AGESA updates.
If your BIOS is older than mid‑2020, you’re running with known bugs.

Update to the newest BIOS your board vendor offers.

🌳 3. Switch to a newer kernel
Ubuntu’s HWE kernel or a 6.x kernel often stabilizes Ryzen IOMMU behavior.

On Ubuntu:

Code
sudo apt install linux-generic-hwe-22.04
(or the equivalent for your release)

Then reboot.

🌲 4. Disable ASPM (PCIe power management)
Some Ryzen/X370 boards freeze when ASPM + IOMMU are both active.

Add:

Code
pcie_aspm=off
to your kernel flags.

This one has saved a lot of early‑Ryzen systems.

🌵 5. Disable Global C‑States in BIOS
This is another classic Ryzen stability fix.

BIOS → Advanced → AMD CBS → Global C‑States → Disabled

This prevents deep sleep states that sometimes interact badly with IOMMU.

🌾 6. Check for USB controllers or SATA controllers misbehaving
Your logs showed AMD‑Vi faults. Often the culprit is:

ASMedia USB controllers

ASMedia SATA controllers

PCIe WiFi cards

NVMe drives on early firmware

You can test by temporarily unplugging or disabling devices in BIOS.

🌟 The short version
If iommu=pt didn’t fix it, the next step is:

amd_iommu=off → BIOS update → newer kernel → ASPM off → C‑states off.

That sequence solves 99% of Ryzen/X370 IOMMU lockups.

If you want, I can help you pick the exact kernel flags based on your motherboard model and Ryzen 5 CPU.
```