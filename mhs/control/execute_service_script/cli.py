import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from mhs.config import LOCAL_ROOT
from mhs.control.fleet.load_fleet.query import LoadFleetQuery
from mhs.output import print_error, print_info, print_success, print_warning
from mhs.sync import bidirectional_sync, ensure_remote_dir

logger = logging.getLogger(__name__)


def validate_executable(filepath: Path | str, services_dir: Path):
  """Validate that the given path is an executable service script.

  Returns:
    Absolute path to the executable.
  """
  executable_path = Path(filepath).resolve()

  if not executable_path.exists():
    raise RuntimeError(f"File does not exist: {executable_path}")

  if not executable_path.is_file():
    raise RuntimeError(f"Path is not a file: {executable_path}")

  if not executable_path.is_relative_to(services_dir):
    raise RuntimeError(f"Executable is outside services directory: {executable_path}")

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
    description="Execute a service script on a remote device.",
    add_help=False,
  )
  parser.add_argument(
    "executable", help="Relative path to executable script from `root`"
  )
  parser.add_argument(
    "--root", default=LOCAL_ROOT.as_posix(), help="Root directory of the project"
  )
  parser.add_argument(
    "--create-root",
    action="store_true",
    help="Create remote root directory if it does not exist",
  )
  args, remaining = parser.parse_known_args(argv)
  logger.debug(f"Parsed arguments: {args}, remaining: {remaining}")

  root_dir = Path(args.root).resolve()
  services_dir = root_dir / "services"
  executable_path = validate_executable(args.executable, services_dir)
  remote_executable_path = executable_path.relative_to(services_dir)
  service_key = remote_executable_path.parts[0]
  fleet_file = root_dir / "fleet.json"

  fleet = LoadFleetQuery(fleet_file).execute()
  hosting_device = fleet.servers.get_host(service_key)
  if hosting_device is None:
    raise RuntimeError(
      f"Service '{service_key}' is not hosted on any server in the fleet"
    )

  ssh_host = hosting_device.ssh_host
  if args.create_root:
    print_info(f"Ensuring remote root directory exists on {ssh_host}...")
    ensure_remote_dir(ssh_host, f"{root_dir.name}/")

  # Paths are relative to root dir
  from_remote_files = [
    f"services/{service_key}/.env",
  ]
  to_remote_files = [
    ".env",
    fleet_file.relative_to(root_dir).as_posix(),
  ]
  to_remote_files.extend(gather_files_to_sync("lib", root_dir))
  to_remote_files.extend(gather_files_to_sync(f"services/{service_key}", root_dir))

  print_info(msg=f"Syncing files with {ssh_host}...")
  if not bidirectional_sync(
    ssh_host=ssh_host,
    service_key=service_key,
    to_remote_files=to_remote_files,
    from_remote_files=from_remote_files,
    root_dir=root_dir,
  ):
    raise RuntimeError("File synchronization failed")

  print_success("File synchronization completed")

  remote_executable = remote_executable_path.as_posix()
  print_info(f"Executing {remote_executable} on {hosting_device.key}...")
  remote_cmd = (
    f"cd {root_dir.name} && services/{remote_executable} {' '.join(remaining)}"
  )
  ssh_exec_cmd = ["ssh", ssh_host, "-t", remote_cmd]
  try:
    # Use call instead of run to preserve interactive terminal behavior
    subprocess.call(ssh_exec_cmd)
  except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Remote execution failed: {e}")
  except KeyboardInterrupt:
    print_warning("Interrupted by user")
