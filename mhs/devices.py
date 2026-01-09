import json
import sys
from dataclasses import dataclass
from pathlib import Path

from mhs.config import DOMAIN_SUFFIX, FLEET_FILE
from mhs.output import print_error


def validate_mac_address(mac: str) -> bool:
  """Validate MAC address format"""
  if len(mac.split(":")) != 6:
    return False
  for part in mac.split(":"):
    if len(part) != 2:
      return False
    try:
      int(part, 16)
    except ValueError:
      return False
  return True


@dataclass
class Device:
  label: str
  hostname: str
  ssh_host: str
  primary_mac: str
  secondary_mac: str
  description: str
  services: dict[str, dict]  # service_label -> service_definition

  @classmethod
  def load_all(cls, devices_file: Path = FLEET_FILE, empty_ok=False):
    devices: list[Device] = []

    if not devices_file.exists():
      print_error(f"{devices_file} does not exist")
      return devices

    try:
      data = json.loads(devices_file.read_text())

      for label, definition in data.get("devices", {}).items():
        macs = definition.get("macs", [])
        device = cls(
          label=label,
          hostname=f"{label}.{DOMAIN_SUFFIX}",
          ssh_host=definition.get("ssh_host", label),
          primary_mac=macs[0] if macs else "",
          secondary_mac=macs[1] if len(macs) > 1 else "",
          description=definition.get("description", label),
          services=definition.get("services", {}),
        )
        if not validate_mac_address(device.primary_mac):
          print_error(
            f"Invalid primary MAC address for device '{label}': {device.primary_mac}"
          )
          continue
        devices.append(device)
    except json.JSONDecodeError as e:
      print_error(f"Failed to parse devices.json: {e}")

    if not devices and not empty_ok:
      print_error(f"No devices loaded from {devices_file.name}")
      sys.exit(1)

    return devices

  @classmethod
  def find_by_service(
    cls, service_label: str, devices: list["Device"]
  ) -> "Device | None":
    """Find the device that hosts the specified service"""
    for device in devices:
      if service_label in device.services:
        return device
    return None
