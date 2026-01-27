from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Service:
  key: str
  port: int
  subdomain: str = field(default="")
  domain_key: str = field(default="")
  description: str = field(default="")
  mount_points: dict[str, Path] = field(default_factory=dict)
  """TODO: implement mount points"""

  def __str__(self) -> str:
    return self.key


@dataclass
class ServiceRef:
  key: Service | str

  def __post_init__(self):
    if not isinstance(self.key, str):
      self.key = self.key.key

    if not self.key:
      raise ValueError("key cannot be empty")

  def __hash__(self) -> int:
    return hash(self.key)

  def hydrate(self) -> Service:
    from mhs.data.fleet.load_service.query import LoadService

    return LoadService(self).execute()


@dataclass
class ServiceRepo:
  _index: dict[ServiceRef, Service] = field(default_factory=dict)

  def __getitem__(self, ref: ServiceRef) -> Service:
    if not isinstance(ref, ServiceRef):
      ref = ServiceRef(ref)
    return self._index[ref]

  def __setitem__(self, ref: ServiceRef, value: Service) -> None:
    if not isinstance(ref, ServiceRef):
      ref = ServiceRef(ref)
    self._index[ref] = value

  def get(self, ref: ServiceRef) -> Service | None:
    if not isinstance(ref, ServiceRef):
      ref = ServiceRef(ref)
    return self._index.get(ref)
