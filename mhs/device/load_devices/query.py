from dataclasses import dataclass
from pathlib import Path

from mhs.config import FLEET_FILE


@dataclass
class LoadDevicesQuery:
  fleet_file: Path = FLEET_FILE
  index: bool = False
