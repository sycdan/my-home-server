import json
import shlex
from pathlib import Path

from mhs.config import FLEET_FILE
from mhs.control.discover_devices.command import DiscoverDevices
from mhs.data.fleet.load.query import LoadFleet
from mhs.device.discover.command import DiscoverDevice
from mhs.device.server.entity import Server, ServerRef
from mhs.output import print_error, print_success, print_warning
from mhs.ssh.run_on.command import RunOn


def load_domains(fleet_file: Path) -> dict[str, str]:
  """loads domain configurations from the fleet file"""
  domains: dict[str, str] = {}
  fleet = json.loads(fleet_file.read_text())
  for key, props in fleet.get("domains", {}).items():
    if domain := props.get("domain"):
      domains[key] = domain
  return domains


def get_public_hostnames(device: Server, domains: dict[str, str]) -> list[str]:
  """returns the public hostname for the device if configured with a domain"""
  hostnames: list[str] = []
  for service in device.services._index.values():
    if domain_key := service.domain_key:
      if domain := domains.get(domain_key):
        if subdomain := service.subdomain:
          hostname = f"{subdomain}.{domain}"
          hostnames.append(hostname)
  return hostnames


def clear_split_dns(hostname: str) -> None:
  """removes existing split DNS entries for the given hostname"""
  cmd = f'/ip dns static remove [find name~"{hostname}"]'
  output, success = RunOn("router", cmd).execute()
  if not success:
    print_warning(f"Failed to clear split DNS for {hostname}: {output}")


def configure_split_dns(hostname: str, ingress_ip: str) -> None:
  """avoids hairpinning by allowing LAN devices to resolve public hostnames via the router's DNS"""
  cmd = f'/ip dns static add name="{hostname}" address="{ingress_ip}" ttl=30m comment="Split DNS for {hostname}"'
  output, success = RunOn("router", cmd).execute()
  if not success:
    print_warning(f"Failed to configure split DNS for {hostname}: {output}")
  print_success(f"Configured split DNS for {hostname} to {ingress_ip}")


def get_ingress_ip(hostname="ingress.lan") -> str:
  """returns the IP address of the device running the public ingress service"""
  ip = ""
  output, success = RunOn(
    "router",
    f":put [/ip dns static get [find name={shlex.quote(hostname)}] address]",
  ).execute()
  if success:
    ip = output.strip()
  else:
    print_error("Failed to get ingress IP from router")
  return ip


def handle(command: DiscoverDevices):
  fleet = LoadFleet().execute()
  print(f"Discovering all devices in {fleet}...")

  public_hostnames: set[str] = set()
  domains = load_domains(FLEET_FILE)

  for device in fleet.servers._index.values():
    public_hostnames.update(get_public_hostnames(device, domains))
    DiscoverDevice(ServerRef(device.key)).execute()

  if not command.skip_dns_refresh:
    if ingress_ip := get_ingress_ip():
      for domain in domains.values():
        clear_split_dns(domain)
      for hostname in public_hostnames:
        configure_split_dns(hostname, ingress_ip)
    else:
      print_warning(
        "Could not configure split DNS: Ingress IP not found (you may have ingress issues on LAN)"
      )
