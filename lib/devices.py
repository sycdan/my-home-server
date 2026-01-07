import json
from dataclasses import dataclass
from pathlib import Path

from lib.common import print_error


@dataclass
class Device:
  host: str
  primary_mac: str
  secondary_mac: str
  description: str

  @classmethod
  def load_all(cls, devices_file: Path):
    devices: list[Device] = []

    if not devices_file.exists():
      print_error(f"{devices_file} does not exist")
      return devices

    try:
      data = json.loads(devices_file.read_text())

      for host, device_info in data.get("devices", {}).items():
        device = cls(
          host=host,
          primary_mac=device_info.get("primary_mac", ""),
          secondary_mac=device_info.get("secondary_mac", ""),
          description=device_info.get("description", ""),
        )
        devices.append(device)
    except json.JSONDecodeError as e:
      print_error(f"Failed to parse devices.json: {e}")

    return devices
