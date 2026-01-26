from dataclasses import dataclass

from mhs.device.server.entity import Server, ServerCollection
from mhs.device.storage.entity import StorageCollection
from mhs.service.entity import Service, ServiceCollection


@dataclass
class Fleet:
  servers: ServerCollection
  storages: StorageCollection
  services: ServiceCollection

  def get_service_host_or_fail(self, service: Service | str) -> Server:
    if isinstance(service, str):
      try:
        service = self.services[service]
      except KeyError:
        raise RuntimeError(f"Unknown service {service}")

    for server in self.servers.index.values():
      if service.key in server.services.index:
        return server

    raise RuntimeError(f"No host found for service {service}")
