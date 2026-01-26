from mhs.device.server.mount_storage.command import MountStorageCommand
from mhs.ssh.run_on.command import RunOn


def handle(command: MountStorageCommand):
  storage = command.storage
  server = command.server
  print(f"Mounting storage '{storage.key}' on device '{server.key}'")
  raise NotImplementedError()
  RunOn(ssh_host=server.ssh_host, command=f"mount {storage.key}").execute()
  print(f"Successfully mounted storage '{storage.key}' on device '{server.key}'")
