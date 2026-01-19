import argparse
import os
import subprocess
import sys
from pathlib import Path

from mhs.config import FLEET_FILE, ROOT_DIR
from mhs.device.entity import Device
from mhs.output import print_error, print_info, print_success, print_warning
from mhs.sync import bidirectional_sync, ensure_remote_dir


def validate_executable(filepath: str, root_dir: Path):
  """Validate that the given path is an executable script/binary.

  Returns:
    Relative path to the executable within the root directory.
  """
  executable_path = Path(filepath).resolve()

  if not executable_path.exists():
    print_error(f"File does not exist: {executable_path}")
    sys.exit(1)

  if not executable_path.is_file():
    print_error(f"Path is not a file: {executable_path}")
    sys.exit(1)

  try:
    relative_path = executable_path.relative_to(root_dir)

    if relative_path.parent.parent.name != "services":
      print_error(f"Executable is not in a service directory: {executable_path}")
      sys.exit(1)

  except ValueError:
    print_error(f"Executable is outside project directory: {executable_path}")
    sys.exit(1)

  if not os.access(executable_path, os.X_OK):
    print_warning(f"File is not marked as executable: {executable_path}")

  return relative_path


def main(argv=None):
  parser = argparse.ArgumentParser(
    description="Execute service scripts on remote devices"
  )
  parser.add_argument("executable_path", help="Path to executable script to run")
  parser.add_argument("--root", default="", help="Root directory of the project")
  parser.add_argument(
    "--create-root",
    action="store_true",
    help="Create remote root directory if it does not exist",
  )
  parser.add_argument("--debug", action="store_true", help="Enable debug output")
  args = parser.parse_args(argv)

  if args.root:
    root_dir = Path(args.root).resolve()
  else:
    root_dir = ROOT_DIR

  relative_executable_path = validate_executable(args.executable_path, root_dir)
  relative_service_dir = relative_executable_path.parent
  service_label = relative_service_dir.name
  fleet_file = root_dir / "fleet.json"

  devices = Device.load_all(fleet_file)
  hosting_device = Device.find_by_service(service_label, devices)
  if hosting_device is None:
    print_error(f"Service '{service_label}' is not hosted on any device")
    sys.exit(1)
  if args.debug:
    print_info(f"Found {service_label} service on {hosting_device.label}")

  ssh_host = hosting_device.ssh_host
  remote_base = root_dir.name
  if args.create_root:
    print_info(f"Ensuring remote root directory exists on {ssh_host}...")
    ensure_remote_dir(ssh_host, f"{remote_base}/")

  # All paths must be strings relative to root_dir, and dirs must have trailing slashes
  from_remote_files = [
    (relative_service_dir / ".env").as_posix(),
  ]
  to_remote_files = [
    ".env",
    "lib/",
    fleet_file.relative_to(root_dir).as_posix(),
    relative_service_dir.as_posix() + "/",
  ]

  print_info(f"Syncing files with {ssh_host}...")
  if not bidirectional_sync(
    ssh_host=ssh_host,
    service_label=service_label,
    to_remote_files=to_remote_files,
    from_remote_files=from_remote_files,
    root_dir=root_dir,
    debug=args.debug,
  ):
    print_error("File synchronization failed")
    sys.exit(1)

  print_success("File synchronization completed")

  remote_executable = relative_executable_path.as_posix()
  print_info(f"Executing {remote_executable} on {hosting_device.label}...")
  ssh_exec_cmd = ["ssh", "-t", ssh_host, f"cd {remote_base} && {remote_executable}"]
  try:
    # Use call instead of run to preserve interactive terminal behavior
    subprocess.call(ssh_exec_cmd)
  except subprocess.CalledProcessError as e:
    print_error(f"Remote execution failed: {e}")
    sys.exit(1)
  except KeyboardInterrupt:
    print_warning("Interrupted by user")
    sys.exit(-1)
