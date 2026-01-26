from dataclasses import dataclass

from mhs.device.server.entity import Server
from mhs.service.entity import Service


@dataclass
class DeployService:
  service: Service
  host: Server
  start_service: bool = True
  force_recreate: bool = False

  def execute(self):
    from mhs.control.deploy_service.handler import handle

    handle(self)
