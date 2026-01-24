from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoadMediaQuery:
  fleet_file: Path
  data_key: str = "storages"
  index: bool = False
