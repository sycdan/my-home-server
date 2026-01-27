from pathlib import Path

from mhs.control.deploy_service.command import DeployService
from mhs.data.fleet.load.query import LoadFleet
from mhs.output import print_info, print_success
from mhs.service.immich.restore_backup.command import RestoreBackup
from mhs.ssh.run_on.command import RunOn


def handle(command: RestoreBackup):
  fleet = LoadFleet().execute()
  if not (service := fleet.services._index.get("immich")):
    raise RuntimeError("Immich service is not configured in the fleet")
  host = fleet.get_service_host(service)
  service_dir = Path("my-home-server") / "etc" / "immich"
  steps = [
    f"cd {service_dir.as_posix()}",
    f"./restore-backup {command.database_backup_file}",
  ]

  DeployService(service, host, start_service=False).execute()
  print_info(f"Restoring Immich backup on {host.key}...")
  output, success = RunOn(host.ssh_host, " && ".join(steps)).execute()
  if success:
    print_success(output)
  raise RuntimeError(f"Failed to restore backup: {output}")
