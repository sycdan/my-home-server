from dataclasses import dataclass, field


@dataclass
class Storage:
  key: str
  uuid: str
  description: str = field(default="")


@dataclass
class StorageRef:
  key: str

  def __hash__(self) -> int:
    return hash(self.key)


@dataclass
class StorageRepo:
  _index: dict[StorageRef, Storage] = field(default_factory=dict)

  def __getitem__(self, ref: StorageRef) -> Storage:
    if not isinstance(ref, StorageRef):
      ref = StorageRef(ref)
    return self._index[ref]

  def __setitem__(self, ref: StorageRef, value: Storage) -> None:
    if not isinstance(ref, StorageRef):
      ref = StorageRef(ref)
    self._index[ref] = value
