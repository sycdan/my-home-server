from dataclasses import dataclass
from pathlib import Path


@dataclass
class UploadDirectory:
  ssh_host: str
  local_dir: Path
  remote_dir: Path  # relative to ssh home
  # TODO exclude_patterns: list[str] = field(default_factory=list)
  host_is_windows: bool = False
  clear: bool = False

  def __post_init__(self):
    self.local_dir = Path(self.local_dir)
    self.remote_dir = Path(self.remote_dir)

  def execute(self):
    from mhs.ssh.upload.handler import handle_upload_directory

    return handle_upload_directory(self)


@dataclass
class UploadFile:
  ssh_host: str
  local_file: Path
  remote_file: Path  # relative to ssh home

  def __post_init__(self):
    self.local_file = Path(self.local_file)
    self.remote_file = Path(self.remote_file)

  def execute(self):
    from mhs.ssh.upload.handler import handle_upload_file

    return handle_upload_file(self)
