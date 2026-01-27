from dataclasses import dataclass

from mhs.service.entity import Service, ServiceRef


@dataclass
class LoadService:
  ref: ServiceRef

  def __post_init__(self):
    if not self.ref:
      raise ValueError("ref cannot be empty")

    if not isinstance(self.ref, ServiceRef):
      self.ref = ServiceRef(self.ref)

  def execute(self) -> Service:
    from mhs.data.fleet.load_service.handler import handle

    return handle(self)
