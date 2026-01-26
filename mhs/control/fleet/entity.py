from dataclasses import dataclass

from mhs.device.server.entity import ServerCollection
from mhs.device.storage.entity import StorageCollection
from mhs.service.entity import ServiceCollection


@dataclass
class Fleet:
  servers: ServerCollection
  storages: StorageCollection
  services: ServiceCollection
