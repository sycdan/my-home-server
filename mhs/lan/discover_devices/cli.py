"""
Device discovery initializer.
Generates RouterOS scripts for each device and deploys them to the router.
Loads configuration from .env files.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from mhs import ROOT_DIR
from mhs.device.entity import Device
from mhs.lan.discover_devices import tools
from mhs.output import print_error, print_info, print_success, print_warning

DEVICE_SCRIPT_CACHE_DIR = ROOT_DIR / ".device-scripts"
FLEET_FILE = ROOT_DIR / "fleet.json"
EXAMPLE_ENV_FILE = ROOT_DIR / "example.env"
ENV_FILE = ROOT_DIR / ".env"


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
CONFIG = load_config(ROOT_DIR)
ROUTER_SSH_HOST = CONFIG["ROUTER_SSH_HOST"]
SCHEDULE_INTERVAL = CONFIG["SCHEDULE_INTERVAL"]
DOMAIN_SUFFIX = CONFIG["DOMAIN_SUFFIX"]


def run_ssh_command(
  host: str, command: str, user="", identity_file=""
) -> tuple[str, int]:
  """Returns (output, returncode)"""
  hostname = f"{user}@{host}" if user else host
  args = ["ssh", hostname]
  if identity_file:
    args.extend(["-i", identity_file])
  args.extend(["-x", command])
  try:
    result = subprocess.run(
      args,
      capture_output=True,
      text=True,
      check=True,
    )
    return result.stdout, result.returncode
  except Exception as e:
    print_error(f"SSH command failed: {e}")
    return "", -1


def run_on_router(command: str) -> tuple[str, int]:
  return run_ssh_command(
    ROUTER_SSH_HOST,
    command,
  )


def upload_script_to_router(script_file: Path, script_comment: str, run=False) -> bool:
  """Upload script file to router and create system script referencing the file."""
  print_info(f"Uploading '{script_file.name}' to {ROUTER_SSH_HOST}...")
  if not script_file.exists():
    print_error(f"Script file '{script_file}' does not exist")
    return False

  # Upload file to router
  scp_cmd = ["scp", str(script_file), f"{ROUTER_SSH_HOST}:/{script_file.name}"]
  try:
    subprocess.run(scp_cmd, capture_output=True, text=True, check=True)
    print_success(f"Uploaded '{script_file.name}' to router")
  except Exception as e:
    print_error(f"SCP failed: {e}")
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


def main(argv=None) -> int:
  parser = argparse.ArgumentParser(
    description="Deploy device discovery scripts to router"
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

  if args.debug:
    print_info(f"Using config: {CONFIG}")
    print_info(f"Fleet file: {FLEET_FILE}")

  DEVICE_SCRIPT_CACHE_DIR.mkdir(exist_ok=True)

  devices = Device.load_all(FLEET_FILE)
  if not devices:
    print_error(f"No devices configured in {FLEET_FILE}")
    return 1

  deployed_count = 0
  failed_count = 0

  for device in devices:
    if args.device and device.label != args.device:
      continue
    name = device.description.strip() or device.label
    print_info(f"Discovering {name} ({device.hostname})")

    script_name = f"discover-{device.label}"
    script_file = DEVICE_SCRIPT_CACHE_DIR / f"{script_name}.rsc"
    script_comment = f"Discover {name} ({device.hostname})"
    script_content = tools.generate_device_discovery_script(
      device.hostname,
      device.primary_mac,
      device.secondary_mac,
    )
    try:
      script_file.write_text(script_content)
      print_info(f"Generated {script_file.relative_to(ROOT_DIR)}")
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

  print()
  print_success(f"{deployed_count} deployed successfully")
  if failed_count > 0:
    print_warning(f"{failed_count} failed")
    return 1

  return 0
