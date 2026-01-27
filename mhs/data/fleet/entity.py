from dataclasses import dataclass

from mhs.device.server.entity import Server, ServerRepo
from mhs.device.storage.entity import StorageRepo
from mhs.service.entity import Service, ServiceRef, ServiceRepo


@dataclass
class Fleet:
  servers: ServerRepo
  storages: StorageRepo
  services: ServiceRepo

  def get_service_host(self, service: Service, default: Server | None = None) -> Server:
    service_ref = ServiceRef(service)
    for server in self.servers._index.values():
      if server.services.get(service_ref):
        return server

    if default is not None:
      return default

    raise RuntimeError(f"No host found for service {service}")
