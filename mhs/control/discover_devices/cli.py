"""
Device discovery initializer.
Generates RouterOS scripts for each device and deploys them to the router.
Loads configuration from .env files.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

from mhs import LOCAL_ROOT
from mhs.control.discover_devices import tools
from mhs.control.fleet.load_fleet.query import LoadFleetQuery
from mhs.device.server.entity import Server
from mhs.output import print_error, print_info, print_success, print_warning
from mhs.ssh.run.command import RunCommand

DEBUG = os.getenv("MHS_DEBUG", "0") == "1"
DEVICE_SCRIPT_CACHE_DIR = LOCAL_ROOT / ".device-scripts"
FLEET_FILE = LOCAL_ROOT / "fleet.json"
EXAMPLE_ENV_FILE = LOCAL_ROOT / "example.env"
ENV_FILE = LOCAL_ROOT / ".env"


def set_debug(value: bool) -> None:
  global DEBUG
  DEBUG = value


def ensure_env_file() -> None:
  if not ENV_FILE.exists():
    ENV_FILE.write_text(EXAMPLE_ENV_FILE.read_text())
    print(
      f"Created default .env file at {ENV_FILE}. Customize it as necessary, then rerun."
    )
    sys.exit(0)


def load_env_file(filepath: Path) -> dict[str, str]:
  env_vars = {}
  if not filepath.exists():
    return env_vars

  for line in filepath.read_text().splitlines():
    line = line.strip()
    # Skip empty lines and comments
    if not line or line.startswith("#"):
      continue
    # Parse KEY=VALUE
    if "=" in line:
      key, value = line.split("=", 1)
      env_vars[key.strip()] = value.strip()

  return env_vars


def load_config(source_dir: Path) -> dict[str, str]:
  """Load configuration from service .env file with environment variable overrides."""
  config = load_env_file(source_dir / ".env")

  # Environment variables override .env values
  for key in config:
    if key in os.environ:
      config[key] = os.environ[key]

  return config


ensure_env_file()
CONFIG = load_config(LOCAL_ROOT)
ROUTER_SSH_HOST = CONFIG["ROUTER_SSH_HOST"]
SCHEDULE_INTERVAL = CONFIG["SCHEDULE_INTERVAL"]
DOMAIN_SUFFIX = CONFIG["DOMAIN_SUFFIX"]


def run_on_router(command: str, as_script=False) -> tuple[str, bool]:
  """uploads the command as a script and runs it on the router"""
  if DEBUG:
    print_info(f"Running on router: {command}")
  if as_script:
    with tempfile.NamedTemporaryFile(
      "w",
      delete=False,
    ) as temp_script:
      temp_script.write(command)
      temp_script_path = Path(temp_script.name)
    if script_name := _upload_script_to_router(temp_script_path):
      command = f"/import {shlex.quote(script_name)}; /file remove [find where name={shlex.quote(script_name)}]"
    temp_script_path.unlink(missing_ok=True)
  return RunCommand(
    ROUTER_SSH_HOST,
    command,
  ).execute()


def _upload_script_to_router(script_file: Path, name: str = "") -> str:
  """returns the script name if it was uploaded successfully"""
  print_info(f"Uploading '{script_file.name}' to {ROUTER_SSH_HOST}...")
  real_path = script_file.resolve()
  if not real_path.exists():
    print_error(f"Script file '{script_file}' does not exist")
    return ""

  if not name:
    name = f"{script_file.name}.rsc"
  scp_cmd = ["scp", real_path.as_posix(), f"{ROUTER_SSH_HOST}:/{name}"]
  try:
    subprocess.run(scp_cmd, capture_output=True, text=True, check=True)
    print_success(f"Uploaded '{script_file.name}' to router")
    return name
  except Exception as e:
    print_error(f"SCP failed: {e}")
    return ""


def upload_script_to_router(
  script_file: Path,
  script_comment: str,
  run=False,
) -> bool:
  """Upload script file to router and create system script referencing the file."""
  if not _upload_script_to_router(script_file):
    return False

  # Create or update system script referencing the uploaded file
  print_info(f"Installing system script '{script_file.stem}'...")
  cmd = (
    f"{{:local src [/file get {script_file.name} contents]; "
    f':local sid [/system script find name="{script_file.stem}"]; '
    f':if ([:len $sid] > 0) do={{ /system script set $sid source=$src comment="{script_comment}" }} '
    f'else={{ /system script add name="{script_file.stem}" source=$src comment="{script_comment}" }} }}'
  )
  run_on_router(cmd)
  print_success(f"System script '{script_file.stem}' installed")

  if run:
    run_on_router(f'/system script run "{script_file.stem}"')

  return True


def create_schedule(script_name: str, schedule_spec: str, user="admin") -> bool:
  """Set up a scheduler entry to run the script."""
  # Validate format: hh:mm:ss
  parts = schedule_spec.split(":")
  if len(parts) != 3:
    print_error(
      f"Invalid schedule format: '{schedule_spec}'. Expected hh:mm:ss (e.g., '00:05:00')"
    )
    return False

  try:
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    if not (0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
      raise ValueError()
  except (ValueError, IndexError):
    print_error(
      f"Invalid schedule format: '{schedule_spec}'. Hours must be 0-23, minutes 0-59, seconds 0-59"
    )
    return False

  schedule_name = f"{script_name}_schedule"

  # Remove existing schedule if it exists
  run_on_router(f'/system scheduler remove [find name="{schedule_name}"]')

  # Add new schedule
  run_on_router(
    f'/system scheduler add name="{schedule_name}" on-event="/system script run \\"{script_name}\\"" interval="{schedule_spec}"',
  )

  return True


def load_domains(fleet_file: Path) -> dict[str, str]:
  """loads domain configurations from the fleet file"""
  domains: dict[str, str] = {}
  fleet = json.loads(fleet_file.read_text())
  for key, props in fleet.get("domains", {}).items():
    if domain := props.get("domain"):
      domains[key] = domain
  return domains


def get_ingress_ip(hostname="ingress.lan") -> str:
  """returns the IP address of the device running the public ingress service"""
  ip = ""
  output, success = run_on_router(
    f":put [/ip dns static get [find name={shlex.quote(hostname)}] address]"
  )
  if success:
    ip = output.strip()
  else:
    print_error("Failed to get ingress IP from router")
  return ip


def get_public_hostnames(device: Server, domains: dict[str, str]) -> list[str]:
  """returns the public hostname for the device if configured with a domain"""
  hostnames: list[str] = []
  for service in device.services.values():
    if domain_key := service.get("domain_key"):
      if domain := domains.get(domain_key):
        if subdomain := service.get("subdomain"):
          hostname = f"{subdomain}.{domain}"
          hostnames.append(hostname)
  return hostnames


def clear_split_dns(hostname: str) -> None:
  """removes existing split DNS entries for the given hostname"""
  # find everything where the name ends with the hostname
  # cmd = f'/ip dns static remove [find name~"\\.wildharvesthomestead\\.com\$"]'
  cmd = f'/ip dns static remove [find name~"{hostname}"]'
  output, success = run_on_router(cmd)
  if not success:
    print_warning(f"Failed to clear split DNS for {hostname}: {output}")


def configure_split_dns(hostname: str, ingress_ip: str) -> None:
  """avoids hairpinning by allowing LAN devices to resolve public hostnames via the router's DNS"""
  cmd = f'/ip dns static add name="{hostname}" address="{ingress_ip}" ttl=30m comment="Split DNS for {hostname}"'
  output, success = run_on_router(cmd)
  if not success:
    print_warning(f"Failed to configure split DNS for {hostname}: {output}")
  print_success(f"Configured split DNS for {hostname} to {ingress_ip}")


def main(argv=None):
  parser = argparse.ArgumentParser(
    description="Deploy device discovery scripts to router."
  )
  parser.add_argument(
    "device", nargs="?", default=None, help="Specific device to discover."
  )
  parser.add_argument(
    "--debug",
    action="store_true",
    help="Enable debug output",
  )
  args = parser.parse_args(argv)

  set_debug(args.debug)

  if DEBUG:
    print_info(f"Using config: {CONFIG}")
    print_info(f"Fleet file: {FLEET_FILE}")

  DEVICE_SCRIPT_CACHE_DIR.mkdir(exist_ok=True)

  fleet = LoadFleetQuery(FLEET_FILE).execute()
  if not fleet.servers.index:
    raise RuntimeError(f"No devices configured in {FLEET_FILE}")

  public_hostnames: set[str] = set()
  domains = load_domains(FLEET_FILE)

  deployed_count = 0
  failed_count = 0
  for device in devices:
    if args.device and device.key != args.device:
      continue
    name = device.description.strip() or device.key
    print_info(f"Discovering {name} ({device.hostname})")

    public_hostnames.update(get_public_hostnames(device, domains))

    script_name = f"discover-{device.key}"
    script_file = DEVICE_SCRIPT_CACHE_DIR / f"{script_name}.rsc"
    script_comment = f"Discover {name} ({device.hostname})"
    script_content = tools.generate_device_discovery_script(
      device.hostname,
      device.primary_mac,
      device.secondary_mac,
    )
    try:
      script_file.write_text(script_content)
      print_info(f"Generated {script_file.relative_to(LOCAL_ROOT)}")
    except Exception as e:
      print_error(f"Failed to generate script for {name}: {e}")
      failed_count += 1
      continue

    if upload_script_to_router(script_file, script_comment, run=True):
      if create_schedule(script_file.stem, SCHEDULE_INTERVAL):
        print_success(f"Deployed {script_file.stem} to {ROUTER_SSH_HOST}")
        deployed_count += 1
      else:
        print_error(f"Failed to schedule {script_file.stem}")
        failed_count += 1
    else:
      print_error(f"Failed to deploy {script_name}")
      failed_count += 1

  if ingress_ip := get_ingress_ip():
    for domain in domains.values():
      clear_split_dns(domain)
    for hostname in public_hostnames:
      configure_split_dns(hostname, ingress_ip)
  else:
    print_warning(
      "Could not configure split DNS: Ingress IP not found (you may have ingress issues on LAN)"
    )

  print()
  print_success(f"{deployed_count} deployed successfully")
  if failed_count > 0:
    print_warning(f"{failed_count} failed")
