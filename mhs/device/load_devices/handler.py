import json
import sys

from mhs.config import DOMAIN_SUFFIX
from mhs.device.entity import Device
from mhs.device.load_devices.query import LoadDevicesQuery
from mhs.output import print_error
from mhs.tools import validate_mac_address


def handle(query: LoadDevicesQuery) -> list[Device]:
  devices: list[Device] = []

  if not query.fleet_file.exists():
    print_error(f"{query.fleet_file} does not exist")
    return devices

  try:
    data = json.loads(query.fleet_file.read_text())

    for key, definition in data.get("devices", {}).items():
      macs = definition.get("macs", [])
      device = cls(
        key=key,
        hostname=f"{key}.{DOMAIN_SUFFIX}",
        ssh_host=definition.get("ssh_host", key),
        primary_mac=macs[0] if macs else "",
        secondary_mac=macs[1] if len(macs) > 1 else "",
        description=definition.get("description", key),
        services=definition.get("services", {}),
      )
      if not validate_mac_address(device.primary_mac):
        print_error(
          f"Invalid primary MAC address for device '{key}': {device.primary_mac}"
        )
      if device.secondary_mac and not validate_mac_address(device.secondary_mac):
        print_error(
          f"Invalid secondary MAC address for device '{key}': {device.secondary_mac}"
        )
        continue
      devices.append(device)
  except json.JSONDecodeError as e:
    print_error(f"Failed to parse devices.json: {e}")

  if not devices and not empty_ok:
    print_error(f"No devices loaded from {devices_file.name}")
    sys.exit(1)

  return devices
