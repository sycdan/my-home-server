from dataclasses import dataclass

from mhs.device.server.entity import Server, ServerRepo
from mhs.device.storage.entity import StorageRepo
from mhs.service.entity import Service, ServiceRepo


@dataclass
class Fleet:
  servers: ServerRepo
  storages: StorageRepo
  services: ServiceRepo

  def get_service_host_or_fail(self, service: Service | str) -> Server:
    if isinstance(service, str):
      try:
        service = self.services[service]
      except KeyError:
        raise RuntimeError(f"Unknown service {service}")

    for server in self.servers._index.values():
      if service.key in server.services._index:
        return server

    raise RuntimeError(f"No host found for service {service}")
