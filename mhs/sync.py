import subprocess
from pathlib import Path

from .output import print_error, print_info, print_success


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


def ensure_remote_dir(ssh_host: str, remote_dir: str) -> bool:
  """Ensure that the specified directory exists on the remote host.
  Args:
    ssh_host: SSH host to connect to (e.g., user@hostname or SSH alias)
    remote_dir: Relative to SSH home directory
  Returns:
    True if the directory was created or already exists, False on error.
  """
  mkdir_cmd = [
    "ssh",
    ssh_host,
    f"mkdir -p {remote_dir}",
  ]
  try:
    subprocess.run(mkdir_cmd, check=True)
    return True
  except subprocess.CalledProcessError as e:
    print_error(f"Could not create remote directory '{remote_dir}': {e}")
    return False
  except Exception as e:
    print_error(f"Unexpected error creating remote directory '{remote_dir}': {e}")
    return False


def bidirectional_sync(
  ssh_host: str,
  from_remote_files: list[str],
  to_remote_files: list[str],
  service_key: str,
  root_dir: str | Path = ".",
  temp_dir_name: str = ".temp",
  debug=False,
):
  success = True
  root_dir = Path(root_dir).resolve()
  remote_root = root_dir.name
  temp_dir = root_dir / temp_dir_name
  temp_dir.mkdir(exist_ok=True)

  # Sync FROM remote first (pull updates)
  if from_remote_files:
    if debug:
      print_info(f"Pulling updated files from {ssh_host}...")

    down_includes = temp_dir / f"rsync_from-{service_key}.txt"
    down_includes.write_text("\n".join(from_remote_files))

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
