import os
import subprocess
from pathlib import Path

from mhs.config import LOCAL_ROOT
from mhs.ssh.run_on.command import RunOn
from mhs.ssh.upload.command import UploadDirectory, UploadFile


def _delete_remote_directory(ssh_host: str, remote_path: Path):
  # TODO quote per os
  command = f"rm -rf {remote_path.as_posix()}"
  output, success = RunOn(
    ssh_host,
    command,
  ).execute()
  if not success:
    raise RuntimeError(f"Failed to delete remote directory: {output}")


def _create_remote_directory(ssh_host: str, remote_path: Path, host_is_windows: bool = False):
  # TODO quote per os
  if host_is_windows:
    command = f"mkdir {remote_path.as_posix().replace('/', '\\')}"
  else:
    command = f"mkdir -p {remote_path.as_posix()}"
  output, success = RunOn(
    ssh_host,
    command,
  ).execute()
  if not success:
    raise RuntimeError(f"Failed to create remote directory: {output}")


def handle_upload_directory(command: UploadDirectory):
  if command.clear:
    _delete_remote_directory(command.ssh_host, command.remote_dir)

  _create_remote_directory(command.ssh_host, command.remote_dir, command.host_is_windows)

  local_dir = command.local_dir
  if not local_dir.is_absolute():
    local_dir = LOCAL_ROOT / local_dir
  local_dir = local_dir.resolve()

  remote_dir = command.remote_dir
  if remote_dir.is_absolute():
    raise ValueError("Remote directory must be relative to SSH home")

  for dirname, dirnames, filenames in os.walk(local_dir):
    for filename in filenames:
      fp = Path(dirname) / filename
      UploadFile(
        ssh_host=command.ssh_host,
        local_file=fp,
        remote_file=remote_dir / fp.relative_to(local_dir),
      ).execute()


def handle_upload_file(command: UploadFile):
  if not command.local_file.is_absolute():
    raise ValueError("Local file path must be absolute")

  if command.remote_file.is_absolute():
    raise ValueError("Remote file path must be relative to SSH home")

  scp_cmd = [
    "scp",
    command.local_file.as_posix(),
    f"{command.ssh_host}:./{command.remote_file.as_posix()}",
  ]

  print("Uploading file:", " ".join(scp_cmd))
  result = subprocess.run(scp_cmd, capture_output=True, text=True)
  if result.returncode != 0:
    raise RuntimeError(f"Failed to upload file: {result.stderr}")


def handle(command: UploadDirectory | UploadFile):
  if isinstance(command, UploadDirectory):
    handle_upload_directory(command)
  elif isinstance(command, UploadFile):
    handle_upload_file(command)
  else:
    raise ValueError(f"Unknown upload command: {type(command)}")
