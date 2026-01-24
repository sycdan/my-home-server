from _collections_abc import dict_values
from dataclasses import dataclass, field


@dataclass
class Service:
  key: str
  port: int
  subdomain: str = field(default="")
  domain_key: str = field(default="")
  description: str = field(default="")


@dataclass
class ServiceCollection:
  index: dict[str, Service] = field(default_factory=dict)

  def __getitem__(self, key: str) -> Service:
    return self.index[key]

  def __setitem__(self, key: str, value: Service) -> None:
    self.index[key] = value

  def values(self) -> dict_values[str, Service]:
    return self.index.values()
