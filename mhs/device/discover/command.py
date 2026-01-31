from dataclasses import dataclass

from mhs.device.server.entity import ServerRef


@dataclass
class DiscoverDevice:
  """searches for the device on the network and ensures it has a static DNS name."""

  ref: ServerRef

  def execute(self):
    from mhs.device.discover.handler import handle

    return handle(self)
