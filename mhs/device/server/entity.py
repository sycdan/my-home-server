from dataclasses import dataclass, field

from mhs.service.entity import ServiceCollection


@dataclass
class Server:
  key: str
  hostname: str
  ssh_host: str
  primary_mac: str
  secondary_mac: str
  description: str
  services: ServiceCollection
  mounts: list[str] = field(default_factory=list)  # storage keys to mount
  host_os: str = "linux"

  def __str__(self) -> str:
    return self.key


@dataclass
class ServerCollection:
  index: dict[str, Server] = field(default_factory=dict)

  def __str__(self) -> str:
    return ", ".join(self.index.keys())

  def get_host(self, service_key: str) -> Server | None:
    for server in self.index.values():
      try:
        if server.services[service_key]:
          return server
      except KeyError:
        continue
    return None
