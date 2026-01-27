from argparse import ArgumentParser

from mhs.control.deploy_service.command import DeployService
from mhs.data.fleet.load.query import LoadFleet
from mhs.device.server.entity import ServerRef
from mhs.output import print_info, print_success
from mhs.service.entity import ServiceRef


def main(argv=None):
  parser = ArgumentParser(description="Deploy a docker service to its configured host.")
  parser.add_argument("service", help="Which service to deploy")
  parser.add_argument("--device", help="Specific device to deploy to (overrides fleet config)")
  parser.add_argument("--force-recreate", action="store_true", help="Force recreate containers")
  args = parser.parse_args(argv)

  fleet = LoadFleet().execute()
  service = ServiceRef(args.service).hydrate()

  if args.device:
    host = ServerRef(args.device).hydrate()
  else:
    host = fleet.servers.get_host(service)

  if not host:
    raise RuntimeError(f"No host configured for service {service}")

  print_info(f"Deploying {service} to {host}...")
  DeployService(
    ServiceRef(service),
    ServerRef(host),
    start_service=True,
    force_recreate=args.force_recreate,
  ).execute()
  print_success("Deployment complete.")
