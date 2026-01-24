import json
import sys

from mhs.config import DOMAIN_SUFFIX
from mhs.control.fleet.entity import Fleet
from mhs.control.fleet.load_fleet.query import LoadFleetQuery
from mhs.device.server.entity import Server, ServerCollection
from mhs.device.storage.entity import Storage, StorageCollection
from mhs.output import print_error, print_warning
from mhs.service.entity import Service, ServiceCollection
from mhs.tools import validate_mac_address


def parse_services(data: dict, data_key: str = "services") -> ServiceCollection:
  services = ServiceCollection()
  for key, vars in data.get(data_key, {}).items():
    services.index[key] = Service(key, **vars)
  return services


def parse_servers(fleet: dict, data_key: str = "servers") -> ServerCollection:
  servers = ServerCollection()

  for key, definition in fleet.get(data_key, {}).items():
    # We'll only load devices that have services defined
    services = parse_services(definition)
    if not services.index:
      continue

    macs = definition.get("macs", [])
    server = Server(
      key=key,
      hostname=f"{key}.{DOMAIN_SUFFIX}",
      ssh_host=definition.get("ssh_host", key),
      primary_mac=macs[0] if macs else "",
      secondary_mac=macs[1] if len(macs) > 1 else "",
      description=definition.get("description", key),
      services=services,
      mounts=definition.get("mounts", []),
    )
    if not validate_mac_address(server.primary_mac):
      print_error(
        f"Invalid primary MAC address for device '{key}': {server.primary_mac}"
      )
      sys.exit(1)
    if server.secondary_mac and not validate_mac_address(server.secondary_mac):
      print_warning(
        f"Invalid secondary MAC address for device '{key}': {server.secondary_mac}"
      )
      continue
    servers.index[key] = server

  return servers


def parse_storages(fleet: dict, data_key: str = "storages") -> StorageCollection:
  storages = StorageCollection()
  for key, vars in fleet.get(data_key, {}).items():
    storages.index[key] = Storage(key, **vars)
  return storages


def handle(query: LoadFleetQuery) -> Fleet:
  fleet_file = query.fleet_file.resolve()

  if not fleet_file.exists():
    raise RuntimeError(f"Fleet file does not exist: {fleet_file}")

  try:
    fleet = json.loads(fleet_file.read_text())
  except json.JSONDecodeError as e:
    raise RuntimeError(f"Failed to load fleet from {fleet_file}: {e}")

  storages = parse_storages(fleet, query.storages_key)
  servers = parse_servers(fleet, query.servers_key)

  return Fleet(
    servers=servers,
    storages=storages,
  )
