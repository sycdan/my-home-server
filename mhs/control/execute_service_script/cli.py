import argparse
import logging
import os
import subprocess
from pathlib import Path

from mhs.config import LOCAL_ROOT
from mhs.data.fleet.load.query import LoadFleet
from mhs.device.server.entity import Server
from mhs.output import print_error, print_info, print_success, print_warning
from mhs.ssh.run_on.command import RunOn

logger = logging.getLogger(__name__)


def ensure_remote_dir(server: Server, remote_dir: str):
  print_info(f"Ensuring {remote_dir} exists on {server.description}...")
  if server.host_os == "windows":
    mkdir_cmd = f'powershell -Command "New-Item -ItemType Directory -Path {remote_dir} -Force"'
  else:
    mkdir_cmd = f"mkdir -p {remote_dir}"

  RunOn(
    server.ssh_host,
    mkdir_cmd,
  ).execute()


def run_rsync(
  cmd: list[str],
  local_base: Path,
  operation: str,
  debug: bool = False,
  allow_missing: bool = False,
) -> bool:
  """
  Helper function to execute rsync commands with consistent error handling.

  Args:
    cmd: The rsync command as a list of arguments
    local_base: Base directory to run the command from
    operation: Description of the operation for logging (e.g., "pull", "push")
    debug: Enable debug output
    allow_missing: If True, treat rsync exit code 23 (missing files) as success

  Returns:
    True if operation succeeded, False if it failed
  """
  if debug:
    print_info(f"Running {operation} command: {' '.join(cmd)}")

  result = subprocess.run(
    cmd,
    check=False,
    cwd=local_base,
    capture_output=True,
    text=True,
  )

  if debug:
    print_info(f"rsync stdout: {result.stdout}")
    print_info(f"rsync stderr: {result.stderr}")

  if result.returncode == 0:
    if debug:
      print_success(f"Files {operation}ed successfully")
    return True
  elif result.returncode == 23 and allow_missing:
    if debug:
      print_info(f"Some remote files not found during {operation} (this may be normal)")
    return True
  else:
    print_error(f"Error during {operation}: {result.stderr}")
    return False


def bidirectional_sync(
  server: Server,
  from_remote_files: list[str],
  to_remote_files: list[str],
  service_key: str,
  root_dir: str | Path = ".",
  temp_dir_name: str = ".temp",
  debug=False,
  scp_only=False,
):
  success = True
  root_dir = Path(root_dir).resolve()
  remote_root = root_dir.name
  temp_dir = root_dir / temp_dir_name
  temp_dir.mkdir(exist_ok=True)
  ssh_host = server.ssh_host

  # Sync FROM remote first (pull updates)
  if from_remote_files:
    if debug:
      print_info(f"Pulling updated files from {ssh_host}...")

    down_includes = temp_dir / f"rsync_from-{service_key}.txt"
    down_includes.write_text("\n".join(from_remote_files))

    if scp_only:
      pass  # not implemented yet
    else:
      pullback_cmd = [
        "rsync",
        "-auz",
        "-vv" if debug else "-v",
        "--relative",
        "--files-from",
        down_includes.relative_to(root_dir).as_posix(),
        f"{ssh_host}:{remote_root}/",
        "./",
      ]

      if not run_rsync(pullback_cmd, root_dir, "pull", debug, allow_missing=True):
        success = False

  # Sync TO remote (push changes)
  if to_remote_files:
    if debug:
      print_info(f"Pushing files to {ssh_host}...")

    # Create files list for rsync
    up_includes = temp_dir / f"rsync_to-{service_key}.txt"
    up_includes.write_text("\n".join(to_remote_files))

    if scp_only:
      # create dir structure on remote
      dir_set = set()
      for file_rel in to_remote_files:
        local_path = root_dir / file_rel
        parent_dir = local_path.parent
        if parent_dir != root_dir and parent_dir.as_posix() not in dir_set:
          rel_dir = parent_dir.relative_to(root_dir)
          ensure_remote_dir(server, f"{remote_root}/{rel_dir.as_posix()}")
          dir_set.add(parent_dir.as_posix())
      # use scp to copy files individually to the remote
      for file_rel in to_remote_files:
        local_path = root_dir / file_rel
        remote_path = f"{ssh_host}:{remote_root}/{file_rel}"
        scp_cmd = ["scp", local_path.as_posix(), remote_path]
        try:
          if debug:
            print_info(f"Running SCP command: {' '.join(scp_cmd)}")
          subprocess.run(
            scp_cmd,
            check=True,
            capture_output=True,
            text=True,
          )
          if debug:
            print_success(f"Uploaded '{file_rel}' to {ssh_host}")
        except Exception as e:
          print_error(f"SCP failed for '{file_rel}': {e}")
          success = False
    else:
      push_cmd = [
        "rsync",
        "-az",
        "-vv" if debug else "-v",
        "--delete",
        "--relative",
        "--files-from",
        up_includes.relative_to(root_dir).as_posix(),
        "./",
        f"{ssh_host}:{remote_root}/",
      ]

      if not run_rsync(push_cmd, root_dir, "push", debug):
        success = False

  return success


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
  parser.add_argument("executable", help="Relative path to executable script from `root`")
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

  fleet = LoadFleet(fleet_file).execute()
  server = fleet.servers.get_host(service_key)
  if server is None:
    raise RuntimeError(f"Service '{service_key}' is not hosted on any server in the fleet")

  ssh_host = server.ssh_host
  if args.create_root:
    ensure_remote_dir(server, f"{root_dir.name}/")

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
    server,
    service_key=service_key,
    to_remote_files=to_remote_files,
    from_remote_files=from_remote_files,
    root_dir=root_dir,
    scp_only=server.host_os == "windows",
  ):
    raise RuntimeError("File synchronization failed")

  print_success("File synchronization completed")

  remote_executable = remote_executable_path.as_posix()
  print_info(f"Executing {remote_executable} on {server.key}...")
  remote_cmd = f"cd {root_dir.name} && services/{remote_executable} {' '.join(remaining)}"
  ssh_exec_cmd = ["ssh", ssh_host, "-t", remote_cmd]
  try:
    # Use call instead of run to preserve interactive terminal behavior
    subprocess.call(ssh_exec_cmd)
  except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Remote execution failed: {e}")
  except KeyboardInterrupt:
    print_warning("Interrupted by user")
