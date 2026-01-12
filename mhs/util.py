import re
from pathlib import Path


def to_snake_case(name):
  return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()


def to_camel_case(name):
  return "".join(word.capitalize() for word in re.split(r"[^a-zA-Z0-9]", name) if word)


def to_dot_path(path: Path):
  return ".".join(path.as_posix().split("/"))


def normalize_mac_address(mac: str):
  """Returns normalized MAC address if valid, else empty string."""
  if len(mac.split(":")) != 6:
    return ""
  for part in mac.split(":"):
    if len(part) != 2:
      return ""
    try:
      int(part, 16)
    except ValueError:
      return ""
  return mac.upper()
