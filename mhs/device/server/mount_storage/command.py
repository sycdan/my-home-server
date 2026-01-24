from dataclasses import dataclass

from mhs.device.server.entity import Server
from mhs.device.storage.entity import Storage


@dataclass
class MountStorageCommand:
  storage: Storage
  server: Server

  def execute(self):
    from mhs.device.server.mount_storage.handler import handle

    return handle(self)
