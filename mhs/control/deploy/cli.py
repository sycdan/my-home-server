from argparse import ArgumentParser
from pathlib import Path

from mhs.control.fleet.load_fleet.query import LoadFleet
from mhs.control.run_docker_compose.command import RunDockerCompose
from mhs.device.server.entity import Server
from mhs.output import print_info, print_success
from mhs.service.entity import Service
from mhs.ssh.upload.command import UploadDirectory


def _upload_service_files(service: Service, server: Server, remote_path: Path):
  """Upload all service files to remote directory via rsync"""
  local_service_dir = Path(f"mhs/service/{service.key}/etc")

  if not local_service_dir.exists():
    raise RuntimeError(f"Service directory {local_service_dir} does not exist")

  print_info(f"Uploading {service.key} files to {server.key}...")

  UploadDirectory(
    ssh_host=server.ssh_host,
    local_dir=local_service_dir,
    remote_dir=remote_path,
    host_is_windows=server.host_os == "windows",
    clear=True,
  ).execute()


def deploy_service(service: Service, server: Server, force: bool = False):
  if not server:
    raise ValueError(f"Device {server} must be provided")

  if not service:
    raise ValueError(f"Service {service} must be provided")

  remote_path = Path("my-home-server") / "etc" / service.key

  _upload_service_files(service, server, remote_path)

  dc_args = ["up", "-d"]
  if force:
    dc_args.append("--force-recreate")

  print_info(f"Starting {service} on {server.key}...")
  RunDockerCompose(
    server=server,
    remote_dir=remote_path,
    args=dc_args,
  ).execute()
  print_success(f"Deployed {service} to {server}.")


def main(argv=None):
  parser = ArgumentParser(description="Deploy a docker service to its configured host.")
  parser.add_argument("service", help="Key of the service to deploy")
  parser.add_argument(
    "--device", help="Specific device to deploy to (overrides fleet config)"
  )
  parser.add_argument(
    "--force-recreate", action="store_true", help="Force recreate containers"
  )
  args = parser.parse_args(argv)

  fleet = LoadFleet().execute()

  try:
    service = fleet.services[args.service]
  except KeyError:
    raise RuntimeError(f"Unknown service {args.service}")

  if args.device:
    host = fleet.servers.index.get(args.device)
  else:
    host = fleet.servers.get_host(service.key)

  if not host:
    raise RuntimeError(f"No host configured for service {service.key}")

  deploy_service(service, host, args.force_recreate)
