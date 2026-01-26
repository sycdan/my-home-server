from pathlib import Path

from mhs.control.deploy_service.cli import deploy_service
from mhs.control.fleet.load_fleet.query import LoadFleet
from mhs.output import print_info
from mhs.service.immich.restore_backup.command import RestoreBackup
from mhs.ssh.run_on.command import RunOn


def handle(command: RestoreBackup):
  fleet = LoadFleet().execute()
  immich_server = fleet.get_service_host_or_fail("immich")
  ssh_host = immich_server.ssh_host
  service_dir = Path("my-home-server") / "etc" / "immich"
  command = f"./restore-backup {command.database_backup_file}"

  print_info(f"Restoring Immich backup on {immich_server.key}...")
  deploy_service
  RunOn(ssh_host, command).execute()
