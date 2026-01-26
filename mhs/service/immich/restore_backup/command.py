from dataclasses import dataclass
from pathlib import Path


@dataclass
class RestoreBackup:
  database_backup_file: Path
  """rel path from ssh home; must exist on the remote"""

  def execute(self) -> None:
    from mhs.service.immich.restore_backup.handler import handle

    handle(self)
