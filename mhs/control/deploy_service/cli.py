from argparse import ArgumentParser

from mhs.control.deploy_service.command import DeployService
from mhs.control.fleet.load_fleet.query import LoadFleet
from mhs.output import print_info, print_success


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

  print_info(f"Deploying service {service.key} to host {host.key}...")
  DeployService(
    service, host, start_service=True, force_recreate=args.force_recreate
  ).execute()
  print_success("Deployment complete.")
