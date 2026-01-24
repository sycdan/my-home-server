from dataclasses import dataclass, field


@dataclass
class Storage:
  key: str
  uuid: str
  description: str = field(default="")


@dataclass
class StorageCollection:
  index: dict[str, Storage] = field(default_factory=dict)
