from dataclasses import dataclass, field

from mhs.service.entity import Service, ServiceRef, ServiceRepo


@dataclass
class Server:
  key: str
  hostname: str
  ssh_host: str
  primary_mac: str
  secondary_mac: str
  description: str
  services: ServiceRepo
  mounts: list[str] = field(default_factory=list)  # storage keys to mount
  host_os: str = "linux"

  def __str__(self) -> str:
    return self.key


@dataclass
class ServerRef:
  key: Server | str

  def __post_init__(self):
    if not isinstance(self.key, str):
      self.key = self.key.key

    if not self.key:
      raise ValueError("key cannot be empty")

  def __hash__(self) -> int:
    return hash(self.key)

  def hydrate(self):
    from mhs.data.fleet.load_server.query import LoadServer

    return LoadServer(self).execute()


@dataclass
class ServerRepo:
  _index: dict[ServerRef, Server] = field(default_factory=dict)

  def __getitem__(self, ref: ServerRef) -> Server:
    if not isinstance(ref, ServerRef):
      ref = ServerRef(ref)
    return self._index[ref]

  def __setitem__(self, ref: ServerRef, value: Server) -> None:
    if not isinstance(ref, ServerRef):
      ref = ServerRef(ref)
    self._index[ref] = value

  def get_host(self, service_ref: Service | ServiceRef) -> Server | None:
    if not isinstance(service_ref, ServiceRef):
      service_ref = ServiceRef(service_ref)
    for server in self._index.values():
      try:
        if server.services[service_ref]:
          return server
      except KeyError:
        continue
    return None
