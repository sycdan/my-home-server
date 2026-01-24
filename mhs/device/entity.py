import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from mhs.config import DOMAIN_SUFFIX, FLEET_FILE
from mhs.output import print_error
from mhs.tools import validate_mac_address


@dataclass
class Device:
  key: str
  hostname: str
  ssh_host: str
  primary_mac: str
  secondary_mac: str
  description: str
  services: dict[str, dict]  # service_key -> service_definition
  mounts: list[str] = field(default_factory=list)  # storage keys to mount

  @classmethod
  def find_by_service(
    cls, service_key: str, devices: list["Device"]
  ) -> "Device | None":
    """Find the device that hosts the specified service"""
    for device in devices:
      if service_key in device.services:
        return device
    return None
