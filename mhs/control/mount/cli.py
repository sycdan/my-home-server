"""Mount all configured storage media on all devices."""

from mhs.control.fleet.load_fleet.query import LoadFleet
from mhs.device.server.mount_storage.command import MountStorageCommand


def main():
  fleet = LoadFleet().execute()
  media = fleet.storages
  servers = fleet.servers.index
  for server in servers.values():
    for storage_key in server.mounts:
      storage = media.index.get(storage_key)
      if storage:
        print(f"Mounting storage '{storage.key}' on device '{server.key}'")
        MountStorageCommand(storage, server).execute()
        print(f"Successfully mounted storage '{storage.key}' on device '{server.key}'")
      else:
        print(f"Warning: Storage '{storage_key}' not found for device '{server.key}'")
