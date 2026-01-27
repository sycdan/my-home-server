from dataclasses import dataclass, field

from mhs.device.server.entity import ServerRef
from mhs.service.entity import ServiceRef


@dataclass
class DeployService:
  service: ServiceRef
  host: ServerRef | None = field(default=None, kw_only=True)
  start_service: bool = True
  force_recreate: bool = False

  def execute(self):
    from mhs.control.deploy_service.handler import handle

    handle(self)
