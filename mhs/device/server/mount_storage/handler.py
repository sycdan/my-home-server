from mhs.device.server.mount_storage.command import MountStorageCommand
from mhs.ssh.run.command import RunCommand


def handle(command: MountStorageCommand):
  storage = command.storage
  server = command.server
  print(f"Mounting storage '{storage.key}' on device '{server.key}'")
  raise NotImplementedError()
  RunCommand(host=server.ssh_host, command=f"mount {storage.key}").execute()
  print(f"Successfully mounted storage '{storage.key}' on device '{server.key}'")
