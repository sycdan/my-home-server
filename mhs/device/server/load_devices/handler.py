import json

from mhs.config import DOMAIN_SUFFIX
from mhs.device.load_devices.query import LoadDevicesQuery
from mhs.device.server.entity import Server, ServerCollection
from mhs.output import print_error, print_warning
from mhs.tools import validate_mac_address


def handle(query: LoadDevicesQuery) -> ServerCollection:
  devices: list[Server] = []

  if not query.fleet_file.exists():
    print_warning(f"{query.fleet_file} does not exist")
    return ServerCollection()

  try:
    data = json.loads(query.fleet_file.read_text())

    for key, definition in data.get(query.data_key, {}).items():
      macs = definition.get("macs", [])
      device = Server(
        key=key,
        hostname=f"{key}.{DOMAIN_SUFFIX}",
        ssh_host=definition.get("ssh_host", key),
        primary_mac=macs[0] if macs else "",
        secondary_mac=macs[1] if len(macs) > 1 else "",
        description=definition.get("description", key),
        services=definition.get("services", {}),
        mounts=definition.get("mounts", []),
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
    print_error(f"Failed to load {query.data_key} from {query.fleet_file}: {e}")

  return ServerCollection(devices)
