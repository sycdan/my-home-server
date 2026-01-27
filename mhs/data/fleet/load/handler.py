import json
import sys

from mhs.config import DOMAIN_SUFFIX
from mhs.data.fleet.entity import Fleet
from mhs.data.fleet.load.query import LoadFleet
from mhs.device.server.entity import Server, ServerRepo
from mhs.device.storage.entity import Storage, StorageRepo
from mhs.output import print_error, print_warning
from mhs.service.entity import Service, ServiceRepo
from mhs.tools import validate_mac_address


def parse_services(data: dict, data_key: str = "services") -> ServiceRepo:
  services = ServiceRepo()
  for key, vars in data.get(data_key, {}).items():
    services[key] = Service(key, **vars)
  return services


def parse_servers(fleet: dict, data_key: str = "servers") -> ServerRepo:
  servers = ServerRepo()

  for key, definition in fleet.get(data_key, {}).items():
    services = parse_services(definition)
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
      host_os=definition.get("host_os", "linux"),
    )
    if not validate_mac_address(server.primary_mac):
      print_error(f"Invalid primary MAC address for device '{key}': {server.primary_mac}")
      sys.exit(1)
    if server.secondary_mac and not validate_mac_address(server.secondary_mac):
      print_warning(f"Invalid secondary MAC address for device '{key}': {server.secondary_mac}")
      continue
    servers[key] = server

  return servers


def parse_storages(fleet: dict, data_key: str = "storages") -> StorageRepo:
  storages = StorageRepo()
  for key, vars in fleet.get(data_key, {}).items():
    storages[key] = Storage(key, **vars)
  return storages


def handle(query: LoadFleet) -> Fleet:
  fleet_file = query.fleet_file.resolve()

  if not fleet_file.exists():
    raise RuntimeError(f"Fleet file does not exist: {fleet_file}")

  try:
    fleet = json.loads(fleet_file.read_text())
  except json.JSONDecodeError as e:
    raise RuntimeError(f"Failed to load fleet from {fleet_file}: {e}")

  storages = parse_storages(fleet, query.storages_key)
  servers = parse_servers(fleet, query.servers_key)

  services = ServiceRepo()
  for server in servers._index.values():
    for service_key, service in server.services._index.items():
      if service_key not in services._index:
        services[service_key] = service

  return Fleet(
    servers=servers,
    storages=storages,
    services=services,
  )
