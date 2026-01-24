from dataclasses import dataclass
from pathlib import Path

from mhs.config import FLEET_FILE


@dataclass
class LoadMediaQuery:
  fleet_file: Path = FLEET_FILE
  data_key: str = "storages"
