from dataclasses import dataclass
from pathlib import Path

from mhs.config import FLEET_FILE


@dataclass
class LoadFleet:
  fleet_file: Path = FLEET_FILE
  servers_key: str = "devices"
  storages_key: str = "media"

  def __post_init__(self):
    self.fleet_file = Path(self.fleet_file)
    if not self.fleet_file.name == "fleet.json":
      raise ValueError("fleet_file must be named 'fleet.json'")

  def execute(self):
    from mhs.control.fleet.load_fleet.handler import handle

    return handle(self)
