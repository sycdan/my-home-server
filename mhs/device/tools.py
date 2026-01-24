from mhs.device.server.entity import Server


def find_by_service(service_key: str, devices: list[Server]) -> Server | None:
  """Find the device that hosts the specified service"""
  for device in devices:
    if service_key in device.services:
      return device
  return None
