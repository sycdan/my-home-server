from mhs.device import load_devices
from mhs.storage import load_media


def handle():
  media = load_media.index()
  servers = load_devices.index()
  for server in servers.values():
    if not server.mounts:
      continue
    for storage_key in server.mounts:
      storage = media.get(storage_key)
      if storage:
        server.mount_storage(storage)
