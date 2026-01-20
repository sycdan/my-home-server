import argparse
import os
import subprocess
import sys
from pathlib import Path

from grpc import services

from mhs.config import ROOT_DIR
from mhs.device.entity import Device
from mhs.output import print_error, print_info, print_success, print_warning
from mhs.sync import bidirectional_sync, ensure_remote_dir


def validate_executable(filepath: str, services_dir: Path):
  """Validate that the given path is an executable service script.

  Returns:
    Absolute path to the executable.
  """
  executable_path = Path(filepath).resolve()

  if not executable_path.exists():
    print_error(f"File does not exist: {executable_path}")
    sys.exit(1)

  if not executable_path.is_file():
    print_error(f"Path is not a file: {executable_path}")
    sys.exit(1)

  if not executable_path.is_relative_to(services_dir):
    print_error(f"Executable is outside services directory: {executable_path}")
    sys.exit(1)

  if not os.access(executable_path, os.X_OK):
    print_warning(f"File is not marked as executable: {executable_path}")

  return executable_path


def gather_files_to_sync(src_dir: str, root_dir: Path):
  """filepaths must be strings relative to root_dir"""
  filepaths = []
  real_src_dir = (root_dir / src_dir).resolve()
  for root, _, files in os.walk(real_src_dir):
    for file in files:
      file_path = Path(root) / file
      filepaths.append(file_path.relative_to(root_dir).as_posix())
  return filepaths


def main(argv=None):
  parser = argparse.ArgumentParser(
    description="Execute service scripts on remote devices"
  )
  parser.add_argument(
    "executable_path", help="Relative path to executable script from `root`"
  )
  parser.add_argument(
    "--root", default=ROOT_DIR.as_posix(), help="Root directory of the project"
  )
  parser.add_argument(
    "--create-root",
    action="store_true",
    help="Create remote root directory if it does not exist",
  )
  parser.add_argument("--debug", action="store_true", help="Enable debug output")
  args, remaining = parser.parse_known_args(argv)

  root_dir = Path(args.root).resolve()
  services_dir = root_dir / "services"
  executable_path = validate_executable(args.executable_path, services_dir)
  relative_executable_path = executable_path.relative_to(services_dir)
  service_label = relative_executable_path.parts[0]

  fleet_file = root_dir / "fleet.json"
  devices = Device.load_all(fleet_file)
  hosting_device = Device.find_by_service(service_label, devices)
  if hosting_device is None:
    print_error(f"Service '{service_label}' is not hosted on any device")
    sys.exit(1)
  if args.debug:
    print_info(f"Found {service_label} service on {hosting_device.label}")

  ssh_host = hosting_device.ssh_host
  if args.create_root:
    print_info(f"Ensuring remote root directory exists on {ssh_host}...")
    ensure_remote_dir(ssh_host, f"{root_dir.name}/")

  # Paths are relative to root dir
  from_remote_files = [
    f"services/{service_label}/.env",
  ]
  to_remote_files = [
    ".env",
    fleet_file.relative_to(root_dir).as_posix(),
  ]
  to_remote_files.extend(gather_files_to_sync("lib", root_dir))
  to_remote_files.extend(gather_files_to_sync(f"services/{service_label}", root_dir))

  print_info(msg=f"Syncing files with {ssh_host}...")
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
  remote_cmd = (
    f"cd {root_dir.name} && services/{remote_executable} {' '.join(remaining)}"
  )
  ssh_exec_cmd = ["ssh", "-t", ssh_host, remote_cmd]
  try:
    # Use call instead of run to preserve interactive terminal behavior
    subprocess.call(ssh_exec_cmd)
  except subprocess.CalledProcessError as e:
    print_error(f"Remote execution failed: {e}")
    sys.exit(1)
  except KeyboardInterrupt:
    print_warning("Interrupted by user")
    sys.exit(-1)
