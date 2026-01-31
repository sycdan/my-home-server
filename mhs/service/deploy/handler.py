from pathlib import Path

from mhs.control.run_docker_compose.command import RunDockerCompose
from mhs.device.server.entity import Server
from mhs.output import print_info, print_success
from mhs.service.deploy.command import DeployService
from mhs.service.entity import Service
from mhs.ssh.upload.command import UploadDirectory


def determine_host(service: Service) -> Server:
  from mhs.data.fleet.load.query import LoadFleet

  fleet = LoadFleet().execute()
  host = fleet.get_service_host(service)
  return host


def _upload_service_files(service: Service, server: Server, remote_path: Path):
  """Upload all service files to remote directory via rsync"""
  local_service_dir = Path(f"etc/{service.key}")

  if not local_service_dir.exists():
    raise RuntimeError(f"Service directory {local_service_dir} does not exist")

  UploadDirectory(
    ssh_host=server.ssh_host,
    local_dir=local_service_dir,
    remote_dir=remote_path,
    host_is_windows=server.host_os == "windows",
    clear=True,
  ).execute()


def deploy_service(service: Service, server: Server, dc_args: list[str]):
  print_info(f"Deploying {service} to {server.key}...")

  remote_path = Path("my-home-server") / "etc" / service.key

  _upload_service_files(service, server, remote_path)

  if dc_args:
    print_info("Calling docker compose " + " ".join(dc_args))
    RunDockerCompose(
      server=server,
      remote_dir=remote_path,
      args=dc_args,
    ).execute()
  print_success(f"Deployed {service} to {server}.")


def handle(command: DeployService):
  service = command.service.hydrate()

  if command.host:
    host = command.host.hydrate()
  else:
    host = determine_host(service)

  dc_args = []

  if command.start_service:
    dc_args = ["up", "-d"]

  if command.force_recreate:
    dc_args.append("--force-recreate")

  deploy_service(service, host, dc_args)
