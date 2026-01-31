from dataclasses import dataclass


@dataclass
class DiscoverDevices:
  """attempts to discover all devices in the fleet on the network."""

  skip_dns_refresh: bool = False

  def execute(self):
    from mhs.control.discover_devices.handler import handle

    return handle(self)
