from dataclasses import dataclass

from mhs.device.server.entity import ServerCollection
from mhs.device.storage.entity import StorageCollection


@dataclass
class Fleet:
  servers: ServerCollection
  storages: StorageCollection
