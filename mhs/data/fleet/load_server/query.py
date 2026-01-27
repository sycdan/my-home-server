from dataclasses import dataclass

from mhs.device.server.entity import Server, ServerRef


@dataclass
class LoadServer:
  ref: ServerRef

  def __post_init__(self):
    if not self.ref:
      raise ValueError("ref cannot be empty")

    if not isinstance(self.ref, ServerRef):
      self.ref = ServerRef(self.ref)

  def execute(self) -> Server:
    from mhs.data.fleet.load_server.handler import handle

    return handle(self)
