"""Execute a service's script/binary on its hosting device."""

import os
import subprocess
import sys
from pathlib import Path

from mhs.config import ROOT_DIR
from mhs.devices import Device
from mhs.gen.external.core.run.v1.contracts_pb2 import RunRequest, RunResponse
from mhs.output import print_error, print_warning
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


def handle(msg: RunRequest) -> RunResponse:
  errors = []
  output_lines = []

  try:
    root_dir = Path(msg.root_directory).resolve() if msg.root_directory else ROOT_DIR
    relative_executable_path = validate_executable(msg.executable_path, root_dir)
    relative_service_dir = relative_executable_path.parent
    service_label = relative_service_dir.name

    fleet_file_path = root_dir / "fleet.json"
    devices = Device.load_all(fleet_file_path)
    hosting_device = Device.find_by_service(service_label, devices)
    if hosting_device is None:
      errors.append(f"Service '{service_label}' is not hosted on any device")
      return RunResponse(errors=errors)

    if msg.debug:
      output_lines.append(f"Found {service_label} service on {hosting_device.label}")

    ssh_host = hosting_device.ssh_host
    remote_base = root_dir.name
    if msg.create_root:
      output_lines.append(f"Ensuring remote root directory exists on {ssh_host}...")
      ensure_remote_dir(ssh_host, f"{remote_base}/")

    # All paths must be strings relative to root_dir, and dirs must have trailing slashes
    from_remote_files = [
      (relative_service_dir / ".env").as_posix(),
    ]
    to_remote_files = [
      "lib/",
      fleet_file_path.relative_to(root_dir).as_posix(),
      relative_service_dir.as_posix() + "/",
    ]

    output_lines.append(f"Syncing files with {ssh_host}...")
    if not bidirectional_sync(
      ssh_host=ssh_host,
      service_label=service_label,
      to_remote_files=to_remote_files,
      from_remote_files=from_remote_files,
      root_dir=root_dir,
      debug=msg.debug,
    ):
      errors.append("File synchronization failed")
      return RunResponse(errors=errors)

    output_lines.append("File synchronization completed")

    remote_executable = relative_executable_path.as_posix()
    output_lines.append(f"Executing {remote_executable} on {hosting_device.label}...")
    ssh_exec_cmd = ["ssh", "-t", ssh_host, f"cd {remote_base} && {remote_executable}"]
    result = subprocess.run(ssh_exec_cmd, capture_output=True, text=True)
    if result.returncode != 0:
      errors.append(f"Remote execution failed with code {result.returncode}: {result.stderr}")
    else:
      output_lines.append("Command executed successfully")
      if result.stdout:
        output_lines.append(result.stdout)

  except Exception as e:
    errors.append(str(e))

  return RunResponse(errors=errors, output="\n".join(output_lines))
