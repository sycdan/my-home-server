from pathlib import Path

from mhs.control.fleet.load_fleet.query import LoadFleet
from mhs.service.immich.restore_backup.command import RestoreBackup
from mhs.ssh.upload.command import UploadFile


def handle(command: RestoreBackup):
  if not command.database_backup_file.exists():
    raise FileNotFoundError(
      f"Database backup file {command.database_backup_file} does not exist"
    )

  fleet = LoadFleet().execute()
  immich_server = fleet.get_service_host_or_fail("immich")
  UploadFile(
    immich_server.ssh_host,
    command.database_backup_file,
    Path(command.database_backup_file.name),
  ).execute()
